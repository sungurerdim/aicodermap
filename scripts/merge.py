#!/usr/bin/env python3
"""
Merge an aicodermap-research-agent return into data/{models,sources}.json
+ append CHANGELOG entry.

Reads .aicodermap-agent-out.json (the agent's return JSON saved by the skill).
Performs schema-complete merge per SKILL.md MERGE_RULES:
- Multi-provider pricing.api array dedupe by provider
- Recompute pricing.range from merged api[]
- Subscription array merge by tier
- Contradiction auto-resolution: write autoResolveWinner, append all candidates
  to data/sources.json with trustScores
- sourcesAdded entries append to data/sources.json (dedupe by url+value)
- Lifecycle: status field, deprecation transitions
- Backup rotation: bak2 dropped, bak -> bak2, current -> bak (preserve bak3)
- lastUpdated touched only on models with deltas
"""

import json
import logging
import os
import re
import shutil
import sys
from datetime import date, datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Force UTF-8 stdout so non-ASCII chars (✗, —, ×, →, Δ) don't crash on Windows cp1254.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
TODAY = date.today().isoformat()
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
ARTIFACT = f"{PROJECT}/.aicodermap-agent-out.json"
WHITELIST = f"{PROJECT}/data/sources-whitelist.json"

# Allow `from lib.whitelist import ...` when invoked from any cwd.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.matrix import active_models as _matrix_active  # noqa: E402
from lib.matrix import expected_total as _matrix_expected_total  # noqa: E402
from lib.matrix import filled_cells_from_models as _matrix_filled  # noqa: E402
from lib.matrix import gap_cells_from_artifact as _matrix_gaps  # noqa: E402
from lib.matrix import total_universe as _matrix_universe  # noqa: E402
from lib.matrix import verify_matrix_invariant as _matrix_verify  # noqa: E402
from lib.whitelist import _load_unhealthy_urls as _wl_load_unhealthy  # noqa: E402
from lib.whitelist import all_bench_keys as _wl_all_bench_keys  # noqa: E402
from lib.whitelist import contracts as _wl_contracts  # noqa: E402
from lib.whitelist import core_bench_keys as _wl_core_bench_keys  # noqa: E402
from lib.whitelist import hostname_index as _wl_hostname_index  # noqa: E402
from lib.whitelist import load_whitelist as _wl_load  # noqa: E402
from lib.constants import FORMAT_WEIGHTS as _FORMAT_WEIGHTS  # noqa: E402
from lib.constants import VERIFICATION_AGREEMENT_PP as _AGREEMENT_PP  # noqa: E402
from lib.tiers import TIER_RANK as _TIER_RANK  # noqa: E402
from lib.tiers import TIER_WEIGHT as _TIER_WEIGHT  # noqa: E402
from lib.util import canonical_display_name as _canonical_name  # noqa: E402
from lib.util import extract_domain as _extract_domain  # noqa: E402
from lib.changelog import render_changelog_markdown as _render_changelog  # noqa: E402
from lib.telemetry import build_meta as _telemetry_build_meta  # noqa: E402
from lib.telemetry import (  # noqa: E402
    metadata_changelog_row as _telemetry_changelog_row,
)
from lib.telemetry import (  # noqa: E402
    write_meta_and_history as _telemetry_write,
)
from lib import reliability as _reliability  # type: ignore  # noqa: E402


LEDGER_PATH = Path(PROJECT) / "data" / "source-reliability.json"
BYPASS_FLOOR_CHECK = "--bypass-floor-check" in sys.argv

# Formats whose primary fetch is "skip" — fetching their canonical URL directly
# should be rare. A sourcesAdded entry that points at one of these formats and
# claims a high tier deserves a non-blocking warning so an operator can verify
# the agent reached the data via the documented fallback chain (mirror /
# WebSearch / image OCR) rather than scraping the SPA directly.
SKIP_PRIMARY_FORMATS = {"spa_full", "bot_blocked", "image_embedded"}


def rotate_backup(path):
    bak = path + ".bak"
    bak2 = path + ".bak2"
    if os.path.exists(bak2):
        os.remove(bak2)
    if os.path.exists(bak):
        os.rename(bak, bak2)
    shutil.copy2(path, bak)


def restore_from_bak(paths):
    """Roll back the just-written files to the .bak snapshot taken before the
    merge. Used when post-write SSOT audit detects drift — leaves the working
    tree in the pre-merge state so the user can investigate without polluted
    data files. Returns the list of paths that were rolled back."""
    rolled = []
    for p in paths:
        bak = p + ".bak"
        if os.path.exists(bak):
            shutil.copy2(bak, p)
            rolled.append(p)
    return rolled


def run_post_write_audits(models_path, sources_path, project):
    """Run the post-write HARD-BLOCK audits against the just-written data files:
    SSOT coherence (audit-data-coherence.py) then bench-source mapping
    (audit-bench-source-mapping.py). On the FIRST failure, roll the data files
    back to their .bak snapshots, print the loud abort block to stderr, and
    return False. No sys.exit inside — the caller owns the fail-fast exit so the
    skill orchestrator sees a non-zero return. Returns True when both pass."""
    import subprocess

    sep = "=" * 72

    # 1. SSOT coherence audit.
    proc = subprocess.run(
        [sys.executable, f"{project}/scripts/audit-data-coherence.py"],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if proc.returncode != 0:
        rolled = restore_from_bak([models_path, sources_path])
        print("\n" + sep, file=sys.stderr)
        print("✗ MERGE ABORTED — SSOT coherence drift in artifact", file=sys.stderr)
        print(sep, file=sys.stderr)
        for line in (proc.stderr or "").strip().splitlines():
            print(f"  {line}", file=sys.stderr)
        print("", file=sys.stderr)
        if rolled:
            print(
                f"  Rolled back {len(rolled)} file(s) from .bak so the working tree "
                f"matches the pre-merge state:",
                file=sys.stderr,
            )
            for p in rolled:
                print(f"    - {os.path.relpath(p, project)}", file=sys.stderr)
        print("", file=sys.stderr)
        print(
            "  Fix the drift in .aicodermap-agent-out.json (the agent's artifact) "
            "or the underlying SSOT files, then re-run merge. Commit is blocked "
            "until audit passes.",
            file=sys.stderr,
        )
        print(sep, file=sys.stderr)
        return False

    # 2. Bench-source mapping audit — HARD BLOCK on AC6/AC7 drift.
    bench_proc = subprocess.run(
        [sys.executable, f"{project}/scripts/audit-bench-source-mapping.py"],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if bench_proc.returncode != 0:
        rolled = restore_from_bak([models_path, sources_path])
        print("\n" + sep, file=sys.stderr)
        print("✗ MERGE ABORTED — bench-source mapping drift (AC6/AC7)", file=sys.stderr)
        print(sep, file=sys.stderr)
        for line in (bench_proc.stderr or "").strip().splitlines():
            print(f"  {line}", file=sys.stderr)
        if rolled:
            print(f"\n  Rolled back {len(rolled)} file(s) from .bak.", file=sys.stderr)
        print(sep, file=sys.stderr)
        return False

    return True


def _deep_merge_inplace(dst, src):
    """Recursively merge src into dst in place. Arrays are replaced unless handled specially."""
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_merge_inplace(dst[k], v)
        else:
            dst[k] = v


def merge_pricing(dst_pricing, src_pricing):
    """Multi-provider pricing array merge: dedupe api[] by provider, recompute range."""
    if "api" in src_pricing and isinstance(src_pricing["api"], list):
        existing = dst_pricing.get("api") or []
        if not isinstance(existing, list):
            existing = []
        merged_by_provider = {e.get("provider"): e for e in existing}
        for entry in src_pricing["api"]:
            prov = entry.get("provider")
            if not prov:
                continue
            cur = merged_by_provider.get(prov, {})
            cur_fetched = cur.get("fetched") or "1970-01-01"
            new_fetched = entry.get("fetched") or "1970-01-01"
            if (prov not in merged_by_provider) or (new_fetched >= cur_fetched):
                merged_by_provider[prov] = entry
        dst_pricing["api"] = list(merged_by_provider.values())
    if "subscription" in src_pricing:
        if (
            isinstance(src_pricing["subscription"], list)
            or src_pricing["subscription"] is None
        ):
            dst_pricing["subscription"] = src_pricing["subscription"]
    api = dst_pricing.get("api") or []
    if isinstance(api, list) and api:
        ins = [e["in"] for e in api if e.get("in") is not None]
        outs = [e["out"] for e in api if e.get("out") is not None]
        chs = [e["cacheHit"] for e in api if e.get("cacheHit") is not None]
        dst_pricing["range"] = {
            "in": [min(ins), max(ins)] if ins else None,
            "out": [min(outs), max(outs)] if outs else None,
            "cacheHit": [min(chs), max(chs)] if chs else None,
        }


def _load_vmap(project: str) -> dict:
    """Load or initialise the verification-map JSON from disk.

    Returns the parsed dict with a `cells` key guaranteed present. On a missing
    or corrupt file returns a fresh `{"cells": {}}` so callers always get a
    consistent shape.
    """
    vmap_path = Path(project) / ".aicodermap-verification-map.json"
    if vmap_path.exists():
        try:
            vmap = json.loads(vmap_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            vmap = {"cells": {}}
    else:
        vmap = {"cells": {}}
    vmap.setdefault("cells", {})
    return vmap


def _stamp_gap_history(cell_entry: dict, cycle_id: str) -> int:
    """Stamp the gap ledger on cell_entry in place for lib.matrix starvation queue.

    Returns 1 when gapSince is freshly set this call (used to accumulate
    gap_stamps in the caller), 0 otherwise.
    """
    # Stamp the gap ledger for lib.matrix's starvation queue only —
    # a long gap raises a cell's research priority, it NEVER
    # quarantines or N/A-flags it (gap-age policy retired 2026-06-07).
    hist = cell_entry["gapHistory"]
    if not hist or hist[-1] != cycle_id:
        hist.append(cycle_id)
    if not cell_entry.get("gapSince"):
        cell_entry["gapSince"] = cycle_id
        return 1
    return 0


def _apply_cell_verdict(
    m: dict,
    bk: str,
    val,
    bench: dict,
    cell_key: str,
    cell_entry: dict,
    sources: dict,
    cycle_id: str,
    pick_winner,
    compute_cell_confidence,
    reliability_ledger,
) -> int:
    """Run pick_winner on the cumulative provenance pool for one (model, benchKey) cell.

    Stamps cell_entry["confidence"], mutates m["benchQuarantine"] and
    m["benchReconciled"] in place, and may update bench[bk] on reconciliation.

    Returns 1 when the cell is quarantined this call, 0 otherwise.
    """
    # Confidence from the CUMULATIVE provenance pool — every entry in
    # sources.json for this cell, historical ∪ this-cycle (5.5: the pool
    # must include historical observations, not just the fresh ones, so
    # a long-confirmed cell keeps its high confidence even on a cycle that
    # re-cites only one source). sources.json is append/dedupe, so this
    # get() already spans all cycles.
    obs = sources.get(cell_key) or []
    if not (isinstance(obs, list) and obs):
        return 0
    pw_obs = [
        {
            "value": e.get("value"),
            "tier": (e.get("tier") or "C").upper(),
            "sourceUrl": e.get("url") or "",
            "fetched": e.get("date") or e.get("fetched") or "",
            "verifications": e.get("verifications") or 1,
            "source": e.get("source") or "",
        }
        for e in obs
        if isinstance(e, dict) and e.get("value") is not None
    ]
    if not pw_obs:
        return 0
    result = pick_winner(
        pw_obs,
        bench_key=bk,
        reliability_ledger=reliability_ledger,
    )
    conf = compute_cell_confidence(result)
    cell_entry["confidence"] = conf
    # SSOT/DRY (2026-06-06): use pick_winner's quarantine verdict
    # (lib.winner.should_quarantine) instead of re-deriving the
    # `conf < 0.2` rule inline. The previous inline copy bypassed
    # should_quarantine's I-tier exemption, so clean canonical-
    # leaderboard cells (AA aaCoding, Scale SEAL swePro) stayed
    # quarantined here even though winner.py cleared them. One
    # quarantine decision, one source of truth.
    if result.get("quarantine"):
        m.setdefault("benchQuarantine", {})[bk] = True
        return 1
    else:
        # Quarantine is a CURRENT-state verdict, not a permanent
        # mark (2026-06-06). Authoritatively CLEAR a stale flag
        # when the cell is now trusted — a 2nd source arrived, a
        # contradiction resolved, or the I-tier exemption applies.
        # Without this, the old "never clear" policy let flags
        # accumulate forever (319 stuck cells), so improving the
        # evidence never lifted a model's score.
        bq = m.get("benchQuarantine")
        if isinstance(bq, dict):
            bq.pop(bk, None)
    # Winner-authoritative reconciliation (fix: synth-emitted
    # single-observation values can disagree with the
    # multi-source consensus across data/sources.json).
    # pick_winner already aggregates the full provenance
    # cluster (sum trustScore + recency + reliability ledger);
    # apply its winner_value when it confidently differs from
    # what the artifact merge wrote.
    wv = result.get("winner_value")
    wc = result.get("winning_cluster") or {}
    # Only reconcile when consensus is real:
    #   - winner has multi-source backing (>=2 distinct urls)
    #   - OR exceptional-source-override (Phase R4) fired
    # Single-source winners cannot evict an existing value
    # (they go to data/sources.json for audit; the existing
    # value stays canonical until a 2nd source confirms).
    multi_source = wc.get("distinct_sources", 0) >= 2
    is_override = result.get("override_mode") in (
        "exceptional-source-override",
        "independent-override",
    )
    if (
        wv is not None
        and conf >= 0.2
        and not result.get("quarantine")
        and val is not None
        and isinstance(wv, (int, float))
        and isinstance(val, (int, float))
        and abs(float(wv) - float(val)) > 0.05
        and (multi_source or is_override)
    ):
        bench[bk] = wv
        reconciled = m.setdefault("benchReconciled", {})
        reconciled[bk] = {
            "from": val,
            "to": wv,
            "cycle": cycle_id,
            "confidence": conf,
            "winning_cluster_sum_trust": round(
                (result.get("winning_cluster") or {}).get("sum_trust", 0.0),
                3,
            ),
            "winning_cluster_distinct_sources": (
                result.get("winning_cluster") or {}
            ).get("distinct_sources", 0),
        }
    return 0


def apply_quarantine_and_gap_policy(
    models, sources, cycle_id, *, reliability_ledger=None
):
    """FAZ 8.A.3d (2026-05-18): merge-time quarantine + gap policy.

    Read .aicodermap-verification-map.json (additive fields, safe on
    missing) and, for every (modelId, benchKey) cell that satisfies one
    of the trigger conditions below, stamp the appropriate flag.

    Triggers:
      - pick_winner.quarantine  (dispersion / <2 sources / confidence)
                                                          -> benchQuarantine[bk]=True
    A CURRENT-state verdict from the cumulative provenance pool — never a
    permanent or gap-age-based mark. (Gap-age force-quarantine + auto-na were
    retired 2026-06-07: a cell being empty for N cycles is a coverage gap to
    re-query, not evidence of bad data.) gapHistory/gapSince are still stamped
    for the starvation-queue prioritization in lib.matrix.

    Returns the mutated verification map dict so the caller can write it
    back to disk.
    """
    sys.path.insert(0, f"{PROJECT}/scripts")
    from lib.winner import compute_cell_confidence, pick_winner  # noqa: E402

    vmap = _load_vmap(PROJECT)
    cells = vmap["cells"]

    quarantined_count = 0
    gap_stamps = 0

    for m in models:
        mid = m.get("id")
        if not mid or m.get("status") not in (None, "active"):
            continue
        bench = m.get("bench") or {}
        for bk, val in bench.items():
            cell_key = f"{mid}.{bk}"
            cell_entry = cells.setdefault(
                cell_key,
                {
                    "value": None,
                    "verifications": [],
                    "lastChecked": TODAY,
                    "gapHistory": [],
                    "gapSince": None,
                    "confidence": 0.0,
                    "stability": None,
                    "bayesianPoint": None,
                },
            )
            cell_entry.setdefault("gapHistory", [])
            cell_entry.setdefault("gapSince", None)
            cell_entry.setdefault("confidence", 0.0)

            is_gap = val is None
            if is_gap:
                gap_stamps += _stamp_gap_history(cell_entry, cycle_id)
            else:
                # Cell filled this cycle — clear the gap run.
                cell_entry["gapHistory"] = []
                cell_entry["gapSince"] = None

            quarantined_count += _apply_cell_verdict(
                m,
                bk,
                val,
                bench,
                cell_key,
                cell_entry,
                sources,
                cycle_id,
                pick_winner,
                compute_cell_confidence,
                reliability_ledger,
            )

    print(
        f"quarantine + gap policy: quarantined={quarantined_count} "
        f"new_gap_stamps={gap_stamps}"
    )
    return vmap


def apply_model_update(model, updates):
    touched = False
    for k, v in updates.items():
        if k == "pricing" and isinstance(v, dict):
            if "pricing" not in model or not isinstance(model["pricing"], dict):
                model["pricing"] = {"api": [], "subscription": None, "range": None}
            merge_pricing(model["pricing"], v)
            touched = True
        elif k == "bench" and isinstance(v, dict):
            if "bench" not in model:
                model["bench"] = {}
            if "benchUpdated" not in model or not isinstance(
                model.get("benchUpdated"), dict
            ):
                model["benchUpdated"] = {}
            for bk, bv in v.items():
                if isinstance(bv, dict) and "value" in bv:
                    bv = bv["value"]
                # Per-cell lastUpdated: stamp ONLY when the agent successfully
                # extracted a value for this (model, bench) pair this cycle.
                # Null / missing returns leave the prior date untouched.
                if bv is None:
                    continue
                if model["bench"].get(bk) != bv:
                    model["bench"][bk] = bv
                    touched = True
                model["benchUpdated"][bk] = TODAY
        elif k == "benchQuarantine" and isinstance(v, dict):
            # FAZ 8.A.3d (2026-05-18): dict-merge quarantine flags. Never
            # silently clear existing flags — only the explicit setter (or
            # apply_quarantine_and_gap_policy) clears them by setting False.
            if "benchQuarantine" not in model or not isinstance(
                model.get("benchQuarantine"), dict
            ):
                model["benchQuarantine"] = {}
            for bk, flag in v.items():
                if model["benchQuarantine"].get(bk) != bool(flag):
                    model["benchQuarantine"][bk] = bool(flag)
                    touched = True
        elif k == "ollama" and isinstance(v, dict):
            model["ollama"] = v
            touched = True
        elif k == "privacy" and isinstance(v, dict):
            # Per-field dict merge — preserves previously-known fields when
            # the current cycle only resolves a subset. Bad values are caught
            # by audit-data-coherence.py (AC11) and trigger merge rollback.
            if "privacy" not in model or not isinstance(model.get("privacy"), dict):
                model["privacy"] = {}
            for pk, pv in v.items():
                if model["privacy"].get(pk) != pv:
                    model["privacy"][pk] = pv
                    touched = True
        elif k == "lastUpdated":
            continue
        else:
            if model.get(k) != v:
                model[k] = v
                touched = True
    # Model-level lastUpdated: full ISO 8601 datetime (UTC, e.g.
    # "2026-04-28T17:23:45Z"). Stamping with the wallclock cycle time — not
    # the per-bench date — disambiguates same-day reruns. Lex-sortable since
    # ISO 8601 with Z preserves chronological order and beats date-only
    # strings when compared via max().
    bu = model.get("benchUpdated")
    bench_max = max(bu.values()) if isinstance(bu, dict) and bu else None
    if touched:
        model["lastUpdated"] = NOW
    elif bench_max:
        model["lastUpdated"] = max(model.get("lastUpdated") or "", bench_max)
    return touched


# Whitelist parsed once per merge run — it was previously re-read and
# re-parsed 6× per run (4× _wl_load + 2 direct open()s on the same file).
# merge.py is a one-shot process, so a module-level memo is safe; raises
# exactly like load_whitelist on a missing/corrupt file (callers needing
# graceful degradation keep their existing try/except).
_WL_CACHE = None


def _wl_cached():
    global _WL_CACHE
    if _WL_CACHE is None:
        _WL_CACHE = _wl_load()
    return _WL_CACHE


def _is_unhealthy_source(entry, unhealthy_urls):
    """True when `entry.url` matches the SPA-shell unhealthy set (after norm)."""
    if not unhealthy_urls:
        return False
    url = (entry.get("url") or "").strip().rstrip("/").lower()
    return bool(url) and url in unhealthy_urls


def format_consistency_warn(source_entry, wl_idx):
    """Log non-blocking warning when a sourcesAdded entry's URL hostname is
    classified as a 'skip primary' format (spa_full / bot_blocked /
    image_embedded) yet the artifact tags it as a high-tier source. Either
    the agent reached the data via the documented fallback chain (fine — but
    the URL recorded should reflect the mirror), or the agent fetched the
    SPA/blocked page directly (suspect)."""
    url = source_entry.get("url") or ""
    if not url:
        return None
    host = _extract_domain(url)
    info = wl_idx.get(host)
    if not info:
        return None
    fmt, _wl_tier = info
    if fmt in SKIP_PRIMARY_FORMATS and source_entry.get("tier") in ("I", "S"):
        return (
            f"format-consistency: url={url} format={fmt} but tier="
            f"{source_entry.get('tier')} — confirm this came via fallback "
            f"chain (mirror/WebSearch/OCR) and not direct SPA scrape"
        )
    return None


def _build_bench_advertised_count():
    """For each bench key, count high-weight (>=0.7) leaderboards advertising
    it in publishes[]. Used by adaptive gate."""
    try:
        wl = _wl_cached()
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        logging.warning("_build_bench_advertised_count: loaded empty (%s)", exc)
        return {}
    counts = {}
    for lb in wl.get("leaderboards", []) or []:
        fmt = lb.get("format", "static_html_table")
        if _FORMAT_WEIGHTS.get(fmt, 0.5) < 0.7:
            continue
        for k in lb.get("publishes", []) or []:
            counts[k] = counts.get(k, 0) + 1
    return counts


def _load_bench_key_universe():
    """Bench-value universe = coreBenchKeys ∪ emergingBenchKeys (== frontend
    BENCH_KEYS / all_bench_keys SSOT) ∪ every leaderboard's publishes[] entry.
    Emerging keys are explicit members so an emerging cell with no dedicated
    leaderboard publisher (e.g. a vendor-only mcpA/sweMulti) still passes through
    instead of being filtered out. Re-read once per merge run (via _wl_cached) so
    a leaderboard adding a new publishes[] key also flows through automatically.
    SoC: coverage/matrix uses coreBenchKeys (_wl_core_bench_keys); value
    passthrough uses this."""
    try:
        wl = _wl_cached()
    except (FileNotFoundError, json.JSONDecodeError):
        return set()
    # core ∪ emerging via the SSOT accessor, then any extra leaderboard publishes[].
    universe = set(_wl_all_bench_keys(wl))
    for lb in wl.get("leaderboards", []) or []:
        for k in lb.get("publishes", []) or []:
            universe.add(k)
    return universe


def _extract_bench_key(g):
    """Per the agent contract a gap entry carries `field` as the bare bench
    key (e.g. "swePro"). Returns the bare key as-is."""
    return g.get("field") or ""


# Stub tokens for repaired gap provenance (3.3 reform). Distinct, greppable
# strings so a human auditor can find every machine-repaired gap.
GAP_REPAIR_STUB_SOURCE = "repaired:no-triedSources-emitted-by-agent"
GAP_REPAIR_STUB_QUERY = "repaired:no-triedQuery-emitted-by-agent"
GAP_REPAIR_STUB_FORMAT = "repaired:no-triedFormat-emitted-by-agent"


def validate_gaps(out):
    """GAP_VALIDITY_GATE — repair + audit (3.3 reform, 2026-05-29).

    Hard rule (MX3): every `gaps[]` entry MUST carry triedSources[] >= 1
    (and ideally triedQueries[] >= 2, triedFormats[] >= 1).

    A malformed gap (missing provenance arrays) is now **REPAIRED in place** —
    its missing arrays stubbed so the cell stays a valid GAP — rather than
    STRIPPED. Stripping turned the cell into a silent omission, which MX1
    (matrix invariant, no warn-only override) then used to roll the ENTIRE
    merge back: one lazy/broken gap entry nuked a whole cycle's productive
    work. Repair preserves the cycle; every repaired entry is loudly recorded
    in `runtime.repairedGaps[]` AND flagged in `runtime.fabricatedSuspicions[]`
    for human review (the stub tokens are greppable).

    Soft rule (audit suspicion): triedQueries[] < 2 OR triedFormats[] < 1 OR
    triedSources[] below the advertised floor flags `fabricatedSuspicions[]`
    but the entry stays in gaps[].

    Returns the suspicion list (audit) for the orchestrator's diff summary.
    """
    bench_advertised = _build_bench_advertised_count()
    raw = out.get("gaps", []) or []
    kept = []
    repaired = []
    suspicions = []
    for g in raw:
        ts = list(g.get("triedSources") or [])
        tq = list(g.get("triedQueries") or [])
        tf = list(g.get("triedFormats") or [])

        bench_key = _extract_bench_key(g)

        # MX3 REPAIR — stub missing provenance arrays instead of stripping the
        # gap (which would cascade to an MX1 full-merge rollback).
        repaired_fields = []
        if len(ts) < 1:
            ts = [GAP_REPAIR_STUB_SOURCE]
            repaired_fields.append("triedSources")
        if len(tq) < 2:
            while len(tq) < 2:
                tq.append(GAP_REPAIR_STUB_QUERY)
            repaired_fields.append("triedQueries")
        if len(tf) < 1:
            tf = [GAP_REPAIR_STUB_FORMAT]
            repaired_fields.append("triedFormats")

        if repaired_fields:
            g["triedSources"] = ts
            g["triedQueries"] = tq
            g["triedFormats"] = tf
            g["_repaired"] = repaired_fields
            repaired.append(
                {
                    "modelId": g.get("modelId"),
                    "field": g.get("field"),
                    "bench_key": bench_key,
                    "reason": g.get("reason"),
                    "repairedFields": repaired_fields,
                }
            )

        ts_n, tq_n, tf_n = len(ts), len(tq), len(tf)
        kept.append(g)

        # Soft suspicion: low query/format effort, OR any machine repair.
        n_advertised = bench_advertised.get(bench_key, 0)
        suggested_floor = min(max(n_advertised, 3), 5)
        if repaired_fields or tq_n < 2 or tf_n < 1 or ts_n < suggested_floor:
            suspicions.append(
                {
                    "modelId": g.get("modelId"),
                    "field": g.get("field"),
                    "bench_key": bench_key,
                    "reason": g.get("reason"),
                    "counts": {
                        "triedSources": ts_n,
                        "triedQueries": tq_n,
                        "triedFormats": tf_n,
                    },
                    "n_advertised": n_advertised,
                    "suggested_floor": suggested_floor,
                    "repairedFields": repaired_fields,
                }
            )

    out["gaps"] = kept
    runtime = out.setdefault("runtime", {})
    if repaired:
        runtime.setdefault("repairedGaps", []).extend(repaired)
    if suspicions:
        runtime.setdefault("fabricatedSuspicions", []).extend(suspicions)
    return suspicions


def append_source(sources, key, entry):
    if ".bench." in key or key.startswith("bench."):
        raise ValueError(
            f"append_source: legacy bench.X key rejected: {key!r}. "
            "Use canonical 'model_id.bench_key' (single dot)."
        )
    if key not in sources:
        sources[key] = []
    arr = sources[key]
    sig = (entry.get("url"), entry.get("value"))
    for existing in arr:
        if (existing.get("url"), existing.get("value")) == sig:
            for k in ("trustScore", "tier", "fetched", "verifications", "source"):
                if entry.get(k) is not None:
                    existing[k] = entry[k]
            return False
    arr.append(entry)
    return True


def _verify_matrix_invariant(models, artifact):
    """MX1 — every (active_modelId, coreBenchKey) cell ends up in exactly one
    of FILLED | GAP (N/A retired 2026-05-25). Silent omission is a contract
    violation.

    Returns (ok: bool, diagnostic: dict).
    On failure the orchestrator rolls models.json + sources.json back to .bak
    and exits non-zero before CHANGELOG is touched.
    """
    wl = _wl_cached()
    core = _wl_core_bench_keys(wl)
    active = _matrix_active(models)
    universe = _matrix_universe(active, core)
    filled = _matrix_filled(active, core)
    gaps = _matrix_gaps(artifact, core)
    diag = _matrix_verify(filled, gaps, universe)
    diag["expectedTotal"] = _matrix_expected_total(active, core)
    diag["coreBenchKeys"] = list(core)
    diag["activeModelCount"] = len(active)
    return diag["ok"], diag


def _green_cell_reliability_sweep(
    sources: dict,
    contradicted_cells: set,
    agreement_pp: float,
    reliability_ledger: dict,
    today: str,
) -> None:
    """R1: credit non-contradicted cells where >=2 fresh sources agree.

    GREEN-cell sweep — runs after the contradictions loop. Historical entries
    (date != today) are never re-credited; they were tallied in their original
    cycle.
    """
    for cell_key, entries in sources.items():
        if not isinstance(cell_key, str) or "." not in cell_key:
            continue
        try:
            mid_parsed, bench_key = cell_key.rsplit(".", 1)
        except ValueError:
            continue
        if (mid_parsed, bench_key) in contradicted_cells:
            continue
        fresh = [
            e
            for e in (entries or [])
            if isinstance(e, dict)
            and (e.get("date") or "") == today
            and e.get("value") is not None
        ]
        if len(fresh) < 2:
            continue
        try:
            vals = [float(e["value"]) for e in fresh]
        except (TypeError, ValueError):
            continue
        if max(vals) - min(vals) > agreement_pp:
            # Latent contradiction not flagged by the agent — don't credit.
            continue
        for e in fresh:
            url = e.get("url")
            if not url:
                continue
            _reliability.update_reliability(
                reliability_ledger,
                url,
                bench_key,
                True,
                today,
                source_label=e.get("source") or "",
            )


def _process_lineup_changes(
    out: dict,
    models_by_id: dict,
    log: dict,
    today: str,
    now: str,
) -> None:
    """Apply lineup deprecations and renames from the artifact to models and log."""
    lineup = out.get("lineupChanges", {}) or {}
    for d in lineup.get("deprecated", []) or []:
        target = models_by_id.get(d.get("id"))
        if target is not None:
            target["status"] = "deprecated"
            target["deprecatedAt"] = d.get("deprecationDate") or today
            if d.get("successor"):
                target["successor"] = d["successor"]
            target["lastUpdated"] = now
            log["lineup_deprecated"].append(d["id"])
    for r in lineup.get("renamed", []) or []:
        log["lineup_renamed"].append(f"{r.get('from')} -> {r.get('to')}")


def _audit_run_metadata(out: dict) -> str:
    """FAZ C: validate runMetadata telemetry fields; return warning string or ''."""
    rm = out.get("runMetadata") or {}
    rm_required = ("toolCallCount", "fetchAttemptCount", "batchCount")
    rm_missing = [k for k in rm_required if k not in rm]
    if rm_missing:
        return f" [WARN: runMetadata missing fields {rm_missing}]"
    rm_warn = ""
    tc = rm.get("toolCallCount", 0)
    bc = rm.get("batchCount", 0)
    # Heuristic alarms — surface to CHANGELOG without blocking merge.
    if isinstance(tc, int) and tc >= 80:
        rm_warn += f" [WARN: toolCallCount={tc} near agent ceiling — priority cascade likely starved]"
    if isinstance(bc, int) and bc < 5:
        rm_warn += f" [WARN: batchCount={bc}<5 — multi-agent fan-out collapsed]"
    return rm_warn


def _format_partial_reason(out: dict) -> str:
    """F8: format structured partialReason telemetry for CHANGELOG; returns string or ''."""
    partial_reason = out.get("partialReason")
    if not partial_reason:
        return ""
    if isinstance(partial_reason, dict):
        code = partial_reason.get("code", "unknown")
        attempted: int | None = partial_reason.get("cellsAttempted")
        filled: int | None = partial_reason.get("cellsFilled")
        blockers: list = partial_reason.get("topBlockingSources") or []
        parts = [f"code={code}"]
        if attempted is not None:
            fill_ratio = (
                round(filled / attempted, 2)
                if (attempted and filled is not None)
                else "?"
            )
            parts.append(f"attempted={attempted} filled={filled} ({fill_ratio})")
        if blockers:
            parts.append(f"blockers=[{', '.join(blockers[:3])}]")
        return f" [partial: {'; '.join(parts)}]"
    return f" [partial: {partial_reason}]"


def _print_merge_summary(
    log: dict,
    matrix,
    matrix_warn: str,
    cov_pct: float,
    issues: list,
    models: list,
) -> None:
    """Print the end-of-merge human-readable summary to stdout."""
    print("merge complete:")
    print(f"  added:      {len(log['added'])} -> {log['added']}")
    print(f"  updated:    {len(log['updated'])}")
    print(f"  deprecated: {len(log['lineup_deprecated'])}")
    print(f"  renamed:    {len(log['lineup_renamed'])}")
    print(f"  contradictions auto-resolved: {len(log['contradictions'])}")
    print(f"  sources appended: {log['sources_appended']}")
    print(f"  coverage:   {cov_pct}%{' (PARTIAL WARN)' if cov_pct < 50 else ''}")
    if matrix_warn:
        print(f"  audit:     {matrix_warn.lstrip(' [').rstrip(']')}")
    elif isinstance(matrix, dict):
        print(
            f"  audit:      coverageMatrix OK "
            f"(filled={matrix.get('filledCells')}/{matrix.get('totalCells')}, "
            f"gaps={matrix.get('gapsRecorded')})"
        )
    print("  coherence:  OK SSOT (bench keys + model ids aligned across surfaces)")
    if log["format_warnings"]:
        print(f"  format warnings: {len(log['format_warnings'])} (non-blocking)")
        for w in log["format_warnings"][:5]:
            print(f"    - {w}")
        if len(log["format_warnings"]) > 5:
            print(f"    - ... and {len(log['format_warnings']) - 5} more")
    if log.get("fabricated_suspicions"):
        n = len(log["fabricated_suspicions"])
        print(
            f"  low-effort gap suspicions: {n} (advisory only — "
            f"suggested triedSources = clamp(advertised_high_weight, 3, 5)). "
            f"Originals retained in gaps[]."
        )
        for fg in log["fabricated_suspicions"][:8]:
            print(
                f"    - {fg.get('modelId')}.{fg.get('bench_key', fg.get('field'))}: "
                f"triedSources={fg['counts']['triedSources']} "
                f"suggested>={fg.get('suggested_floor', 3)} "
                f"(advertised_high_weight={fg.get('n_advertised', 0)})"
            )
        if n > 8:
            print(f"    - ... and {n - 8} more")
    if issues:
        print("self-check issues:")
        for i in issues:
            print(f"  - {i}")
    else:
        print("self-check: PASS")
    print(f"total models: {len(models)}")


def main():
    import subprocess as _sp

    # Schema validation — HARD BLOCK before any file writes.
    _val = _sp.run(
        [sys.executable, f"{PROJECT}/scripts/validate-agent-out.py", ARTIFACT],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if _val.returncode != 0:
        print("\n" + "=" * 72, file=sys.stderr)
        print(
            "✗ MERGE ABORTED — agent artifact fails schema validation", file=sys.stderr
        )
        print("=" * 72, file=sys.stderr)
        for line in (_val.stderr or _val.stdout or "").strip().splitlines():
            print(f"  {line}", file=sys.stderr)
        print("=" * 72, file=sys.stderr)
        sys.exit(1)

    with open(ARTIFACT, encoding="utf-8") as fp:
        out = json.load(fp)

    fabricated_suspicions = validate_gaps(out)

    models_path = f"{PROJECT}/data/models.json"
    sources_path = f"{PROJECT}/data/sources.json"
    rotate_backup(models_path)
    rotate_backup(sources_path)

    with open(models_path, encoding="utf-8") as fp:
        models = json.load(fp)
    with open(sources_path, encoding="utf-8") as fp:
        sources = json.load(fp)

    wl_idx = _wl_hostname_index(_wl_cached())
    unhealthy_urls = _wl_load_unhealthy(Path(PROJECT))

    # O(1) id lookup — replaces the old find() linear scan that ran inside
    # three loops. Kept in sync manually at the single place models grows
    # (the newModels append below).
    models_by_id = {m.get("id"): m for m in models if isinstance(m, dict)}

    log = {
        "updated": [],
        "added": [],
        "lineup_deprecated": [],
        "lineup_renamed": [],
        "contradictions": [],
        "sources_appended": 0,
        "format_warnings": [],
        "gaps": [],
        "fabricated_suspicions": fabricated_suspicions,
        "spa_guard_rejections": 0,
    }
    if unhealthy_urls:
        print(f"FAZ 6.A SPA guard active: {len(unhealthy_urls)} unhealthy URL(s)")

    for upd in out.get("models", []):
        mid = upd["id"]
        m = models_by_id.get(mid)
        if m is None:
            log["gaps"].append(f"unknown id in updates: {mid}")
            continue
        if apply_model_update(m, upd.get("updates", {})):
            log["updated"].append(mid)
        # N/A retired 2026-05-25: inline notApplicable[] is no longer promoted
        # into models[].notApplicableBenchKeys. Every (model, bench) cell is
        # FILLED or GAP; unmeasured cells stay gaps and are re-researched each
        # cycle (freshness-skip is the only skip). See tasks.md.
        for s in upd.get("sourcesAdded", []) or []:
            if _is_unhealthy_source(s, unhealthy_urls):
                log["spa_guard_rejections"] += 1
                log["format_warnings"].append(
                    f"{mid}: SPA-guard reject {s.get('key')} url={s.get('url')}"
                )
                continue
            warn = format_consistency_warn(s, wl_idx)
            if warn:
                log["format_warnings"].append(f"{mid}: {warn}")
            # 4.4 — SWE-variant ambiguity penalty. An observation the agent tagged
            # `_variantAmbiguous` (a bare "SWE-bench" with no Verified/Pro/Multi
            # qualifier) gets −0.5 trustScore (clamped ≥0) so a properly-qualified
            # value out-ranks it, and the cell is recorded anomaly-visible.
            _ts = s.get("trustScore")
            _ambiguous = bool(s.get("_variantAmbiguous"))
            if _ambiguous and isinstance(_ts, (int, float)):
                _ts = max(0.0, float(_ts) - 0.5)
            _entry = {
                "value": s.get("value"),
                "source": s.get("source"),
                "url": s.get("url"),
                "date": s.get("fetched") or TODAY,
                "tier": s.get("tier"),
                "verifications": s.get("verifications", 1),
                "trustScore": _ts,
            }
            if _ambiguous:
                _entry["_variantAmbiguous"] = True
                out.setdefault("runtime", {}).setdefault("variantAmbiguous", []).append(
                    s["key"]
                )
            if append_source(sources, s["key"], _entry):
                log["sources_appended"] += 1

    for nm in out.get("newModels", []) or []:
        if nm["id"] not in models_by_id:
            models.append(nm)
            models_by_id[nm["id"]] = nm
            log["added"].append(nm["id"])

    BENCH_KEYS = _load_bench_key_universe()
    # FAZ 6.B (2026-05-10): cluster-consensus winner override. The agent
    # may emit autoResolveWinner per single-argmax trustScore, which lets
    # a high-tier outlier override multi-source consensus. Re-cluster the
    # candidates here and prefer the cluster with max sum(trustScore).
    sys.path.insert(0, f"{PROJECT}/scripts")
    from lib.cluster import _cluster_observations  # noqa: E402

    AGREEMENT_PP = _AGREEMENT_PP  # SSOT: lib.constants
    MIN_DISTINCT_SAFE = 3
    MIN_DISTINCT_PAIRED = 2
    MIN_SUM_TRUST_PAIRED = 1.5

    def _consensus_winner(
        candidates_list: list[dict], fallback: dict | None
    ) -> tuple[dict | None, str]:
        """Return (winner, reason). When candidates form a stronger
        cluster than `fallback` is part of, return cluster's winner.
        Otherwise return fallback unchanged."""
        obs = []
        tier_w = _TIER_WEIGHT  # SSOT: lib.tiers
        for c_ in candidates_list:
            if c_.get("value") is None:
                continue
            ts = c_.get("trustScore")
            if ts is None:
                tw = tier_w.get((c_.get("tier") or "C").upper(), 0.4)
                v = max(1, min(int(c_.get("verifications") or 1), 3))
                ts = round(tw * (v / 3), 3)
            obs.append(
                {
                    "value": float(c_["value"]),
                    "trustScore": float(ts),
                    "sourceUrl": c_.get("url") or "",
                    "tier": (c_.get("tier") or "C").upper(),
                    "fetched": c_.get("fetched") or c_.get("date") or "",
                    "_orig": c_,
                }
            )
        if not obs:
            return fallback, "no observations"
        clusters = _cluster_observations(obs, AGREEMENT_PP)
        if not clusters:
            return fallback, "no clusters"
        best = clusters[0]
        d = best["distinct_sources"]
        s = best["sum_trust"]
        gate_passed = d >= MIN_DISTINCT_SAFE or (
            d >= MIN_DISTINCT_PAIRED and s >= MIN_SUM_TRUST_PAIRED
        )
        if not gate_passed:
            return fallback, f"weak cluster d={d} s={s} — keep fallback"
        cluster_winner = max(
            best["members"],
            key=lambda m: (m["trustScore"], m.get("fetched") or ""),
        )
        # If fallback's value is in this winning cluster, keep fallback.
        if fallback is not None and fallback.get("value") is not None:
            try:
                if (
                    abs(float(fallback["value"]) - float(best["centroid"]))
                    <= AGREEMENT_PP
                ):
                    return fallback, f"fallback in winning cluster (d={d}, s={s})"
            except (TypeError, ValueError):
                pass
        return cluster_winner["_orig"], f"cluster d={d} s={s} overrode fallback"

    # R1 (Source Reliability v2): load + decay the per-(source, bench) ledger
    # at cycle start. Phase R1 is BEHAVIOR-NEUTRAL — the multiplier is not yet
    # wired into trust_score (that happens in Phase R3); we only populate the
    # ledger here so the Bayesian posterior accumulates across cycles.
    reliability_ledger = _reliability.load_ledger(LEDGER_PATH)
    _reliability.decay_counters(reliability_ledger, TODAY)
    # Track (modelId, benchKey) pairs processed by the contradictions loop so
    # the GREEN-cell sweep below does not double-credit the same observations.
    _contradicted_cells: set[tuple[str, str]] = set()

    for c in out.get("contradictions", []) or []:
        mid = c["modelId"]
        # Agent contract: `field` is the bare bench key, `autoResolveWinner` is
        # the wrapped {value, trustScore, sourceUrl, tier} dict — Storage extracts
        # `.value` for models.json, full dict goes into sources.json provenance.
        bench_field = c["field"]
        winner = c.get("autoResolveWinner")
        if winner is None:
            continue
        all_candidates = c.get("candidates") or []
        # FAZ 6.A: drop unhealthy SPA-shell URLs from candidate pool.
        healthy_candidates = [
            cand
            for cand in all_candidates
            if not _is_unhealthy_source(cand, unhealthy_urls)
            and cand.get("value") is not None
        ]
        if _is_unhealthy_source(winner, unhealthy_urls):
            log["spa_guard_rejections"] += 1
            if not healthy_candidates:
                log["format_warnings"].append(
                    f"{mid}.{bench_field}: SPA-guard dropped winner; no healthy candidate — skipping"
                )
                continue
            # Provisional fallback if cluster doesn't override.
            tier_rank = _TIER_RANK  # SSOT: lib.tiers
            winner = max(
                healthy_candidates,
                key=lambda x: (
                    float(x.get("trustScore") or 0),
                    tier_rank.get(x.get("tier") or "", 0),
                    str(x.get("fetched") or x.get("date") or ""),
                ),
            )
        # FAZ 6.B: re-cluster + prefer multi-source consensus.
        new_winner, reason = _consensus_winner(healthy_candidates, winner)
        if new_winner is not winner and new_winner is not None:
            log["format_warnings"].append(
                f"{mid}.{bench_field}: consensus override — {reason}"
            )
            winner = new_winner
        winner_value = winner["value"]
        m = models_by_id.get(mid)
        if m is not None and bench_field in BENCH_KEYS:
            if "bench" not in m:
                m["bench"] = {}
            if "benchUpdated" not in m or not isinstance(m.get("benchUpdated"), dict):
                m["benchUpdated"] = {}
            prev_value = m["bench"].get(bench_field)
            m["bench"][bench_field] = winner_value
            m["benchUpdated"][bench_field] = TODAY
            if prev_value != winner_value:
                m["lastUpdated"] = NOW
        key = f"{mid}.{bench_field}"
        for cand in all_candidates:
            if _is_unhealthy_source(cand, unhealthy_urls):
                # Drop unhealthy candidates entirely from provenance — keeps
                # sources.json from re-accumulating SPA-shell entries.
                log["spa_guard_rejections"] += 1
                continue
            append_source(
                sources,
                key,
                {
                    "value": cand.get("value"),
                    "source": cand.get("source") or "auto-resolution candidate",
                    "url": cand.get("url"),
                    "date": cand.get("fetched") or TODAY,
                    "tier": cand.get("tier"),
                    "verifications": cand.get("verifications", 1),
                    "trustScore": cand.get("trustScore"),
                    "contradictionRole": "winner"
                    if cand.get("value") == winner_value
                    else "loser",
                },
            )
            log["sources_appended"] += 1
        # R1: credit healthy candidates' reliability based on agreement with
        # the resolved winner. Only healthy_candidates (SPA-guard-filtered)
        # contribute to the Beta-Binomial posterior.
        _winner_val_raw = winner.get("value") if isinstance(winner, dict) else None
        if _winner_val_raw is not None:
            try:
                _winner_val = float(_winner_val_raw)
            except (TypeError, ValueError):
                _winner_val = None
            if _winner_val is not None:
                _contradicted_cells.add((mid, bench_field))
                for cand in healthy_candidates:
                    cand_url = cand.get("url")
                    if not cand_url:
                        continue
                    try:
                        cand_val = float(cand.get("value"))
                    except (TypeError, ValueError):
                        continue
                    agreed = abs(cand_val - _winner_val) <= AGREEMENT_PP
                    _reliability.update_reliability(
                        reliability_ledger,
                        cand_url,
                        bench_field,
                        agreed,
                        TODAY,
                    )
        log["contradictions"].append(
            f"{key}: winner={winner} (severity={c.get('severity') or 'GREEN'}, Δ{c.get('delta')})"
        )

    # R1: GREEN-cell sweep — credit non-contradicted cells where >=2 fresh
    # (date == TODAY) sources agree within AGREEMENT_PP. Skips cells already
    # processed by the contradictions loop. Historical entries (date != TODAY)
    # never get re-credited; they were tallied in their original cycle.
    _green_cell_reliability_sweep(
        sources, _contradicted_cells, AGREEMENT_PP, reliability_ledger, TODAY
    )

    _process_lineup_changes(out, models_by_id, log, TODAY, NOW)

    # FAZ 8.A.3d (2026-05-18): quarantine + gap policy must run BEFORE the
    # final models.json write so the stamps appear in the persisted shape
    # the frontend reads.
    vmap_updated = apply_quarantine_and_gap_policy(
        models,
        sources,
        cycle_id=TODAY,
        reliability_ledger=reliability_ledger,
    )
    vmap_path = Path(PROJECT) / ".aicodermap-verification-map.json"
    vmap_path.write_text(
        json.dumps(vmap_updated, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Model-agnostic display-name canonicalization: fix version-dot anomalies
    # ("Qwen3 7 Max" -> "Qwen3.7 Max") AND repair raw id-slug names that leaked
    # from lineup discovery ("minimax-m3" -> "MiniMax M3", brand cased from
    # provider) so every refresh self-corrects without per-model patches. No-op
    # for already-canonical names.
    for m in models:
        nm = m.get("name")
        if isinstance(nm, str):
            canon = _canonical_name(nm, m.get("provider"))
            if canon != nm:
                m["name"] = canon
                log.setdefault("name_canonicalized", []).append(f"{nm} -> {canon}")

    issues = []
    for m in models:
        p = m.get("pricing")
        if isinstance(p, dict):
            if "api" in p and not isinstance(p["api"], list):
                issues.append(f"{m['id']}: pricing.api not array")
            if "subscription" in p and isinstance(p.get("subscription"), str):
                issues.append(f"{m['id']}: pricing.subscription still string")
        if m.get("status") not in (None, "active", "deprecated", "archived"):
            issues.append(f"{m['id']}: invalid status {m.get('status')}")

    with open(models_path, "w", encoding="utf-8") as fp:
        json.dump(models, fp, indent=2, ensure_ascii=False)
        fp.write("\n")
    with open(sources_path, "w", encoding="utf-8") as fp:
        json.dump(sources, fp, indent=2, ensure_ascii=False)
        fp.write("\n")
    # R1: persist the source-reliability ledger after sources.json is on disk.
    _reliability.save_ledger(LEDGER_PATH, reliability_ledger)

    coverage = out.get("validationCoverage", 0)
    cov_pct = round(coverage * 100, 1)
    coverage_warn = ""
    if coverage < 0.50:
        coverage_warn = f" [WARN: very low cumulative provenance coverage {cov_pct}%]"
    elif coverage < 0.85:
        coverage_warn = (
            f" [WARN: cumulative provenance coverage {cov_pct}% below 85% target]"
        )

    # MX1 — Cell-level matrix invariant (HARD BLOCK, no override).
    # Every (active_modelId, coreBenchKey) cell must end up in exactly one
    # of FILLED | GAP | NOT_APPLICABLE. Silent omission = contract violation.
    contracts_block = _wl_contracts(_wl_cached())
    matrix_warn = ""
    invariant_ok, mx_diag = _verify_matrix_invariant(models, out)
    if not invariant_ok:
        missing = mx_diag.get("missing") or []
        overlap = mx_diag.get("overlap") or {}
        msg_parts = []
        if missing:
            sample = ", ".join(f"{m}.{b}" for m, b in missing[:5])
            extra = f" ...+{len(missing) - 5}" if len(missing) > 5 else ""
            msg_parts.append(
                f"{len(missing)} cell(s) silently missing ({sample}{extra})"
            )
        for okey, items in overlap.items():
            if items:
                msg_parts.append(f"{okey}={len(items)}")
        matrix_warn = " [MX1: matrix invariant violated — " + "; ".join(msg_parts) + "]"

    # Surface the agent's self-reported coverageMatrix (informational; the
    # canonical truth is the recomputed mx_diag above).
    matrix = out.get("coverageMatrix")
    if not isinstance(matrix, dict):
        matrix_warn = (
            (matrix_warn + " [WARN: artifact missing coverageMatrix]")
            if matrix_warn
            else " [WARN: artifact missing coverageMatrix; agent skipped self-audit]"
        )

    if matrix_warn:
        coverage_warn = (coverage_warn + matrix_warn) if coverage_warn else matrix_warn

    # MX1 HARD BLOCK gate.
    if not invariant_ok:
        rolled = restore_from_bak([models_path, sources_path])
        print("\n" + "=" * 72, file=sys.stderr)
        print("✗ MERGE ABORTED — MX1 matrix invariant violated", file=sys.stderr)
        print("=" * 72, file=sys.stderr)
        print(
            "  filled+gaps does NOT cover the (active × core_bench) "
            "universe. Silent omission is a contract violation.",
            file=sys.stderr,
        )
        print(
            f"  totalCells={mx_diag.get('totalCells')} "
            f"filled={mx_diag.get('filled')} "
            f"gaps={mx_diag.get('gaps')} "
            f"missing={len(mx_diag.get('missing') or [])}",
            file=sys.stderr,
        )
        if mx_diag.get("missing"):
            print("  missing cells (first 10):", file=sys.stderr)
            for m, b in (mx_diag.get("missing") or [])[:10]:
                print(f"    - {m}.{b}", file=sys.stderr)
        if rolled:
            print(f"  rolled back {len(rolled)} file(s) from .bak", file=sys.stderr)
        print(
            "  fix the artifact: every missing cell must land in models[].bench "
            "or gaps[] (with triedSources/triedQueries/triedFormats).",
            file=sys.stderr,
        )
        print("=" * 72, file=sys.stderr)
        sys.exit(1)

    # MX2 — Absolute coverage floor (HARD BLOCK by default; regression guard).
    # Override: AICODERMAP_MX2_WARN_ONLY=1 (transition periods only) or the
    # documented one-shot --bypass-floor-check CLI flag.
    floor = float(contracts_block.get("ABSOLUTE_COVERAGE_FLOOR") or 0.30)
    if mx_diag.get("totalCells"):
        ratio = mx_diag.get("filled", 0) / max(mx_diag["totalCells"], 1)
        if ratio < floor:
            floor_msg = (
                f" [MX2: coverage {round(ratio * 100, 1)}% < absolute floor "
                f"{int(floor * 100)}%]"
            )
            coverage_warn = (coverage_warn or "") + floor_msg
            mx2_warn_only = os.environ.get("AICODERMAP_MX2_WARN_ONLY") == "1"
            if not mx2_warn_only and not BYPASS_FLOOR_CHECK:
                rolled = restore_from_bak([models_path, sources_path])
                print("\n" + "=" * 72, file=sys.stderr)
                print(
                    "✗ MERGE ABORTED — MX2 absolute coverage floor breached",
                    file=sys.stderr,
                )
                print("=" * 72, file=sys.stderr)
                print(
                    f"  fill ratio {round(ratio * 100, 1)}% < floor "
                    f"{int(floor * 100)}% (filled={mx_diag.get('filled')}, "
                    f"total={mx_diag.get('totalCells')})",
                    file=sys.stderr,
                )
                if rolled:
                    print(
                        f"  rolled back {len(rolled)} file(s) from .bak",
                        file=sys.stderr,
                    )
                print(
                    "  override paths: AICODERMAP_MX2_WARN_ONLY=1 env "
                    "(logs warning, continues) or --bypass-floor-check CLI flag.",
                    file=sys.stderr,
                )
                print("=" * 72, file=sys.stderr)
                sys.exit(1)

    # Post-write HARD-BLOCK audits (SSOT coherence + bench-source mapping).
    # The helper runs both against the just-written data files, rolls back to
    # .bak + prints the loud abort block on drift, and returns False. No
    # CHANGELOG entry, no commit-eligible state — drift never reaches main.
    if not run_post_write_audits(models_path, sources_path, PROJECT):
        sys.exit(1)

    # FAZ C audit — research-pipeline telemetry from runMetadata.
    # MANDATORY fields (toolCallCount, fetchAttemptCount, batchCount). Missing
    # fields are surfaced as a CHANGELOG warning so the next cycle's prelude
    # picks them up; the merge is NOT rolled back (legacy artifacts may
    # predate FAZ C).
    rm_warn = _audit_run_metadata(out)
    if rm_warn:
        coverage_warn = (coverage_warn or "") + rm_warn

    # F8: Emit structured partialReason telemetry to CHANGELOG for root-cause analysis.
    partial_info = _format_partial_reason(out)

    # FAZ D — write data/_meta.json + append data/refresh-history.json
    # ring-buffer. The browser's freshness.js + verify-deploy.py both consume
    # data/_meta.json; the ring buffer is human-review fodder.
    contradictions_resolved = len(log.get("contradictions") or [])
    prev_etag = None
    try:
        existing_meta = json.loads(
            (Path(f"{PROJECT}/data/_meta.json")).read_text(encoding="utf-8")
        )
        prev_etag = existing_meta.get("etag") or existing_meta.get("prevPushEtag")
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        prev_etag = None
    meta_row = _telemetry_build_meta(
        models=models,
        bench_keys=_wl_core_bench_keys(_wl_cached()),
        matrix_diag=mx_diag,
        artifact=out,
        contradictions_resolved=contradictions_resolved,
        prev_push_etag=prev_etag,
    )
    try:
        _telemetry_write(meta_row)
    except OSError as exc:  # never abort the merge on telemetry I/O
        print(f"WARN: telemetry write failed: {exc}", file=sys.stderr)
    metadata_row = _telemetry_changelog_row(meta_row)

    cl_path = f"{PROJECT}/CHANGELOG.md"
    cl_blob = _render_changelog(
        log, out, metadata_row, coverage_warn, partial_info, TODAY
    )
    if os.path.exists(cl_path):
        with open(cl_path, encoding="utf-8") as fp:
            existing = fp.read()
        # CONSOLIDATE same-day re-runs (FIX 2026-06-06). A full cycle calls merge
        # MORE THAN ONCE (anomaly verdicts + stub additions each re-finalize), and
        # each run regenerates the WHOLE entry from the current data — so a naive
        # prepend stacked 3 identical-date blocks in one cycle. Strip any existing
        # leading `## [TODAY]` block(s) before prepending the freshest one: the
        # last merge of a cycle is authoritative. SoC: only same-day blocks are
        # touched; prior dates are immutable history.
        existing = re.sub(
            r"(?ms)^## \[" + re.escape(TODAY) + r"\].*?(?=^## \[|\Z)", "", existing
        )
        with open(cl_path, "w", encoding="utf-8") as fp:
            fp.write(cl_blob + "\n" + existing.lstrip("\n"))
    else:
        with open(cl_path, "w", encoding="utf-8") as fp:
            fp.write("# Changelog\n\n" + cl_blob)

    _print_merge_summary(log, matrix, matrix_warn, cov_pct, issues, models)


if __name__ == "__main__":
    main()
