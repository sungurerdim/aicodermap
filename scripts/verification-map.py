#!/usr/bin/env python3
"""Verification-map manager — historical audit log (reformed 2026-04-29).

Two operations:
  - `update`: read .aicodermap-agent-out.json sourcesAdded[] across all
    models, group by (modelId, benchKey), append NEW provenance entries
    (deduped by url) to the audit log.
  - `read`:  print the map (for skill orchestrator inline injection into
    idea_context).

The map is HISTORICAL audit-only — never read for skip decisions, never
gates a fetch. Every cell is re-fetched every cycle per the
UNCAPPED + UNCACHED doctrine. The previous `confirmed` flag was retired
(P9 YAGNI: nothing read it; agreement is recomputed on demand by
contradiction analysis from the verifications[] history).

`contested` cells (multi-source disagreement) still surface in stats so
human reviewers can spot drift across cycles.

`lastChecked` is updated to TODAY only when at least one new verification
was appended this cycle (i.e., a successful fetch contributed). Cycles
that produced no new verification for a cell leave `lastChecked` alone.

Map shape (canonical, mirrored in agent.md DATA_CONTRACT):
  {
    "lastUpdate": "YYYY-MM-DD",
    "stats": {"totalCells": N, "contested": N},
    "cells": {
      "<modelId>.<benchKey>": {
        "value": <number | null>,            // last consensus value (null on contradiction)
        "verifications": [{source, url, tier, fetched}, ...],
        "lastChecked": "YYYY-MM-DD",
        // FAZ 8.A.3b additive fields (2026-05-18) — readers safe-default
        // via .get(k, default) when older maps lack them.
        "gapHistory": [<cycleId>, ...],     // chronological cycles where cell was a gap
        "gapSince":   "YYYY-MM-DD"|null,    // first gap cycle of the current run
        "confidence": <float [0,1]>,        // last pick_winner.confidence
        "stability":  <float [0,1]>|null,   // bayesian variance (≥3 cycles)
        "bayesianPoint": <float|null>       // posterior mean (≥3 cycles)
      }
    }
  }
"""

import json
import sys
from datetime import date
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "scripts"))
from lib.constants import (  # noqa: E402
    MIN_VERIFICATIONS_FOR_SKIP as VERIFICATION_AGREEMENT_THRESHOLD,
)
from lib.constants import VERIFICATION_AGREEMENT_PP  # noqa: E402  (SSOT)
from lib.whitelist import all_bench_keys, load_whitelist  # noqa: E402

# B (2026-06-07): cap the gapHistory audit trail so a perma-empty cell does not
# grow its ledger unbounded across years of cycles. gapCycles (int) is the
# authoritative counter; gapHistory keeps only the most-recent dates for audit.
_GAP_HISTORY_CAP = 8

ARTIFACT = PROJECT / ".aicodermap-agent-out.json"
MAP_PATH = PROJECT / ".aicodermap-verification-map.json"

TODAY = date.today().isoformat()


def parse_cell_key(source_added_key: str):
    """sourcesAdded entry keys are `<modelId>.<benchKey>` (DATA_CONTRACT
    Provenance shape). Returns (modelId, benchKey) or None."""
    parts = source_added_key.split(".")
    if len(parts) < 2:
        return None
    return ".".join(parts[:-1]), parts[-1]


def values_agree(values, threshold_pp=VERIFICATION_AGREEMENT_PP):
    """All numeric values agree within `threshold_pp` of the median."""
    nums = [v for v in values if isinstance(v, (int, float))]
    if not nums:
        return False
    nums_sorted = sorted(nums)
    median = nums_sorted[len(nums_sorted) // 2]
    return all(abs(v - median) <= threshold_pp for v in nums)


def update_map():
    if not ARTIFACT.exists():
        print(f"no artifact at {ARTIFACT}; nothing to update", file=sys.stderr)
        return 1

    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if MAP_PATH.exists():
        m = json.loads(MAP_PATH.read_text(encoding="utf-8"))
        cells = m.get("cells", {})
    else:
        cells = {}

    # B (2026-06-07): bench-universe filter. The prior `"bench" not in key`
    # guard was a latent bug — sourcesAdded keys are `<modelId>.<benchKey>`
    # (e.g. "opus-4-7.sweV") which contain no "bench" substring, so EVERY entry
    # was skipped and the incremental update appended 0 verifications every
    # cycle. (T2 filled-skip stayed dormant regardless because the `confirmed`
    # flag is retired — so fixing this does NOT activate filled-cell skipping;
    # it only restores correct audit-history append + powers B's fill-reset.)
    bench_universe = _load_bench_key_universe()

    appended = 0
    filled_keys: set[str] = set()
    for model in artifact.get("models", []) or []:
        for src in model.get("sourcesAdded", []) or []:
            key = src.get("key")
            if not key:
                continue
            parsed = parse_cell_key(key)
            if not parsed:
                continue
            mid, bk = parsed
            if bench_universe and bk not in bench_universe:
                continue
            cell_key = f"{mid}.{bk}"
            filled_keys.add(cell_key)
            cell = cells.setdefault(
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
            # Backfill additive fields on older cells (idempotent).
            cell.setdefault("gapHistory", [])
            cell.setdefault("gapSince", None)
            cell.setdefault("confidence", 0.0)
            cell.setdefault("stability", None)
            cell.setdefault("bayesianPoint", None)
            # `confirmed` field retired — strip on read so legacy maps don't
            # leak the field forward.
            cell.pop("confirmed", None)
            # Append this verification (dedupe by url). lastChecked stamps
            # only when a NEW verification actually lands this cycle — empty
            # cycles leave the prior date intact (per-cell freshness contract).
            url = src.get("url", "")
            existing_urls = {v.get("url") for v in cell["verifications"]}
            if url not in existing_urls:
                cell["verifications"].append(
                    {
                        "value": src.get("value"),
                        "source": src.get("source"),
                        "url": url,
                        "tier": src.get("tier"),
                        "fetched": src.get("fetched") or TODAY,
                    }
                )
                appended += 1
                cell["lastChecked"] = TODAY

    # B (2026-06-07): gap-history stamping. Drives the gap-freshness-tier
    # (lib.freshness.compute_gap_skip_cells). A cell filled this cycle has its
    # gap run reset; a cell still in the artifact's gaps[] has its consecutive
    # gap counter bumped + its triedSources count recorded so the skip gate can
    # require >=GAP_SKIP_MIN_SOURCES distinct sources tried per gap cycle.
    # A cell that is neither filled nor gapped this cycle is left untouched
    # (its run is neither extended nor reset).
    for ck in filled_keys:
        cell = cells.get(ck)
        if cell is not None:
            cell["gapCycles"] = 0
            cell["gapHistory"] = []
            cell["gapSince"] = None
            cell["gapTriedSources"] = 0
    gap_stamped = 0
    for gap in artifact.get("gaps", []) or []:
        key = gap.get("key")
        if not key:
            continue
        parsed = parse_cell_key(key)
        if not parsed:
            continue
        ck = f"{parsed[0]}.{parsed[1]}"
        if ck in filled_keys:
            continue  # filled wins over a stale carried gap in the same artifact
        tried = gap.get("triedSources") or []
        n_tried = len(tried) if isinstance(tried, list) else 0
        cell = cells.setdefault(
            ck,
            {
                "value": None,
                "verifications": [],
                "lastChecked": None,
                "gapHistory": [],
                "gapSince": None,
                "confidence": 0.0,
                "stability": None,
                "bayesianPoint": None,
            },
        )
        cell.setdefault("gapHistory", [])
        prev = cell.get("gapCycles") or 0
        cell["gapCycles"] = prev + 1
        if not cell.get("gapSince"):
            cell["gapSince"] = TODAY
        hist = cell["gapHistory"]
        hist.append(TODAY)
        if len(hist) > _GAP_HISTORY_CAP:
            del hist[: len(hist) - _GAP_HISTORY_CAP]
        # Record the MINIMUM triedSources across the current gap run — the skip
        # gate is conservative (a single low-effort cycle keeps the cell T1).
        prev_min = cell.get("gapTriedSources")
        cell["gapTriedSources"] = (
            n_tried if prev_min in (None, 0) else min(prev_min, n_tried)
        )
        gap_stamped += 1

    # Recompute consensus value (median when ≥ THRESHOLD agree); flag
    # contested cells for stats. No `confirmed` flag — readers compute on
    # demand from verifications[].
    contested_count = 0
    for cell_key, cell in cells.items():
        verifs = cell.get("verifications", [])
        values = [v.get("value") for v in verifs if v.get("value") is not None]
        if len(verifs) >= VERIFICATION_AGREEMENT_THRESHOLD and values_agree(values):
            nums = sorted(v for v in values if isinstance(v, (int, float)))
            cell["value"] = nums[len(nums) // 2] if nums else None
        elif len(verifs) >= 2 and not values_agree(values):
            cell["value"] = None
            contested_count += 1

    m_out = {
        "lastUpdate": TODAY,
        "stats": {
            "totalCells": len(cells),
            "contested": contested_count,
        },
        "cells": cells,
    }
    MAP_PATH.write_text(json.dumps(m_out, indent=2) + "\n", encoding="utf-8")
    print(
        f"verification-map: appended {appended} verifications | "
        f"{len(cells)} total cells, {contested_count} contested"
    )
    return 0


def read_map():
    if not MAP_PATH.exists():
        print("{}")
        return 0
    print(MAP_PATH.read_text(encoding="utf-8"))
    return 0


def _load_bench_key_universe():
    """Bench-value universe = all_bench_keys (core ∪ emerging SSOT) ∪ every
    leaderboard's publishes[] entry. Was a hand-rolled copy that diverged from
    merge.py by omitting emergingBenchKeys (mcpA/sweMulti) — fixed 2026-06-06."""
    try:
        wl = load_whitelist()
    except (json.JSONDecodeError, OSError, FileNotFoundError):
        return set()
    universe = set(all_bench_keys(wl))
    for lb in wl.get("leaderboards", []) or []:
        for k in lb.get("publishes", []) or []:
            universe.add(k)
    return universe


def bootstrap_from_sources():
    """Rebuild verification map from data/sources.json (the on-disk provenance
    log accumulated across all prior cycles). Use once when introducing the
    map mid-project, then incremental updates take over."""
    sources_path = PROJECT / "data" / "sources.json"
    if not sources_path.exists():
        print("no data/sources.json — nothing to bootstrap from", file=sys.stderr)
        return 1
    sources = json.loads(sources_path.read_text(encoding="utf-8"))
    cells = {}
    bench_keys = _load_bench_key_universe()
    for key, entries in sources.items():
        if not isinstance(entries, list):
            continue
        parts = key.split(".")
        # Bench keys live as "modelId.benchKey" (sources.json schema) — only those interest us here
        if len(parts) != 2:
            continue
        mid, bk = parts
        # Skip non-bench fields — only known bench keys go in the verification map
        if bk not in bench_keys:
            continue
        cell = cells.setdefault(
            f"{mid}.{bk}",
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
        seen_urls = set()
        for e in entries:
            url = e.get("url", "")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            cell["verifications"].append(
                {
                    "value": e.get("value"),
                    "source": e.get("source"),
                    "url": url,
                    "tier": e.get("tier"),
                    "fetched": e.get("date") or e.get("fetched") or TODAY,
                }
            )
    contested = 0
    for cell in cells.values():
        verifs = cell["verifications"]
        values = [v["value"] for v in verifs if v["value"] is not None]
        if len(verifs) >= VERIFICATION_AGREEMENT_THRESHOLD and values_agree(values):
            nums = sorted(v for v in values if isinstance(v, (int, float)))
            cell["value"] = nums[len(nums) // 2] if nums else None
        elif len(verifs) >= 2 and not values_agree(values):
            cell["value"] = None
            contested += 1
    m_out = {
        "lastUpdate": TODAY,
        "stats": {
            "totalCells": len(cells),
            "contested": contested,
        },
        "cells": cells,
    }
    MAP_PATH.write_text(json.dumps(m_out, indent=2) + "\n", encoding="utf-8")
    print(
        f"verification-map: bootstrapped from data/sources.json — "
        f"{len(cells)} cells, {contested} contested"
    )
    return 0


def main():
    op = sys.argv[1] if len(sys.argv) > 1 else "update"
    if op == "update":
        return update_map()
    if op == "read":
        return read_map()
    if op == "bootstrap":
        return bootstrap_from_sources()
    print("usage: verification-map.py [update|read|bootstrap]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
