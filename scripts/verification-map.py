#!/usr/bin/env python3
"""Verification-map manager — historical audit log (reformed 2026-04-29).

Two operations:
  - `update`: read .aicodermap-agent-out.json sourcesAdded[] across all
    models, group by (modelId, benchKey), append NEW provenance entries
    (deduped by url) to the audit log.
  - `read`:  print the map (for skill orchestrator inline injection into
    idea_context).

The map is the provenance audit log AND the freshness-skip source of truth.
2026-06-16: the FAZ 2.2 reliability-driven skip was reactivated. Each cell
carries a DERIVED `confirmed` flag (≥VERIFICATION_AGREEMENT_THRESHOLD distinct
numeric sources agreeing within VERIFICATION_AGREEMENT_PP) and a `contradicted`
flag (≥2 numeric sources disagreeing). `freshness.compute_skip_cells` reads
these to drop well-covered cells from the research sweep (re-validated only
after FRESHNESS_TTL_DAYS or when a new contradiction surfaces). The flag had
been wrongly retired as "nothing reads it" — freshness.py + matrix.py both do,
so retiring it left the skip set permanently empty and every confirmed cell was
re-fetched every cycle for zero benefit.

`contested`/`confirmed` counts surface in stats so reviewers can spot drift.

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

# Cap the gapHistory ledger so a perma-empty cell does not grow it unbounded
# across years of cycles. Only the trailing-run length matters to lib.matrix's
# starvation queue (>=2), so keeping the most-recent dates is sufficient.
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


def _make_empty_cell(last_checked=None):
    """Return a zero-valued cell dict with all additive fields initialised."""
    return {
        "value": None,
        "verifications": [],
        "lastChecked": last_checked if last_checked is not None else TODAY,
        "gapHistory": [],
        "gapSince": None,
        "confidence": 0.0,
        "stability": None,
        "bayesianPoint": None,
    }


def _backfill_cell_fields(cell):
    """Idempotently add additive fields to older cells that may lack them."""
    cell.setdefault("gapHistory", [])
    cell.setdefault("gapSince", None)
    cell.setdefault("confidence", 0.0)
    cell.setdefault("stability", None)
    cell.setdefault("bayesianPoint", None)


def _load_artifact_and_cells():
    """Load the agent artifact and the existing verification-map cells.

    Returns (artifact dict, cells dict) on success, or None on missing artifact.
    """
    if not ARTIFACT.exists():
        print(f"no artifact at {ARTIFACT}; nothing to update", file=sys.stderr)
        return None
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if MAP_PATH.exists():
        m = json.loads(MAP_PATH.read_text(encoding="utf-8"))
        cells = m.get("cells", {})
    else:
        cells = {}
    return artifact, cells


def _append_verifications(artifact, cells, bench_universe):
    """Walk artifact.models[].sourcesAdded and append new provenance entries.

    Returns (appended count, set of cell keys that received a fill this cycle).
    """
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
            cell = cells.setdefault(cell_key, _make_empty_cell())
            _backfill_cell_fields(cell)
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
    return appended, filled_keys


def _stamp_gap_history(artifact, cells, filled_keys):
    """Update gapHistory/gapSince for cells reported as gaps in the artifact.

    Feeds ONLY the starvation queue in lib.matrix (a cell empty for >=2
    consecutive cycles is pulled to the front of the research queue).
    A cell filled this cycle has its gap run reset; a cell still in the
    artifact's gaps[] has the current cycle appended to its history.
    NOT a skip mechanism — every gap cell is re-queried every full run.
    A cell that is neither filled nor gapped this cycle is left untouched.
    """
    for ck in filled_keys:
        cell = cells.get(ck)
        if cell is not None:
            cell["gapHistory"] = []
            cell["gapSince"] = None
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
        cell = cells.setdefault(ck, _make_empty_cell(last_checked=None))
        cell.setdefault("gapHistory", [])
        if not cell.get("gapSince"):
            cell["gapSince"] = TODAY
        hist = cell["gapHistory"]
        hist.append(TODAY)
        if len(hist) > _GAP_HISTORY_CAP:
            del hist[: len(hist) - _GAP_HISTORY_CAP]
        gap_stamped += 1
    return gap_stamped


def _recompute_consensus(cells):
    """Derive confirmed/contradicted flags and consensus value for every cell.

    2026-06-16: `confirmed` UN-retired — the FAZ 2.2 freshness-tier skip
    (freshness.compute_skip_cells + matrix.priority_cells) reads this flag.
    It is DERIVED from accumulated provenance (≥THRESHOLD distinct numeric
    sources agreeing within VERIFICATION_AGREEMENT_PP), not stored by an agent.

    Returns (confirmed_count, contested_count).
    """
    contested_count = 0
    confirmed_count = 0
    for cell in cells.values():
        verifs = cell.get("verifications", [])
        nums = [
            v.get("value") for v in verifs if isinstance(v.get("value"), (int, float))
        ]
        agree = values_agree(nums)
        confirmed = len(nums) >= VERIFICATION_AGREEMENT_THRESHOLD and agree
        contradicted = len(nums) >= 2 and not agree
        cell["confirmed"] = confirmed
        cell["contradicted"] = contradicted
        if confirmed:
            nums_sorted = sorted(nums)
            cell["value"] = nums_sorted[len(nums_sorted) // 2]
            confirmed_count += 1
        elif contradicted:
            cell["value"] = None
            contested_count += 1
    return confirmed_count, contested_count


def update_map():
    loaded = _load_artifact_and_cells()
    if loaded is None:
        return 1
    artifact, cells = loaded

    # B (2026-06-07): bench-universe filter. The prior `"bench" not in key`
    # guard was a latent bug — sourcesAdded keys are `<modelId>.<benchKey>`
    # (e.g. "opus-4-7.sweV") which contain no "bench" substring, so EVERY entry
    # was skipped and the incremental update appended 0 verifications every
    # cycle. (T2 filled-skip stayed dormant regardless because the `confirmed`
    # flag is retired — so fixing this does NOT activate filled-cell skipping;
    # it only restores correct audit-history append + powers B's fill-reset.)
    bench_universe = _load_bench_key_universe()

    appended, filled_keys = _append_verifications(artifact, cells, bench_universe)
    _stamp_gap_history(artifact, cells, filled_keys)
    confirmed_count, contested_count = _recompute_consensus(cells)

    m_out = {
        "lastUpdate": TODAY,
        "stats": {
            "totalCells": len(cells),
            "contested": contested_count,
            "confirmed": confirmed_count,
        },
        "cells": cells,
    }
    MAP_PATH.write_text(json.dumps(m_out, indent=2) + "\n", encoding="utf-8")
    print(
        f"verification-map: appended {appended} verifications | "
        f"{len(cells)} total cells, {confirmed_count} confirmed, "
        f"{contested_count} contested"
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


def _build_cells_from_sources(sources, bench_keys):
    """Iterate sources.json entries and build the verification-map cells dict.

    Returns cells dict with verifications populated (no consensus flags yet).
    """
    cells = {}
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
        cell = cells.setdefault(f"{mid}.{bk}", _make_empty_cell())
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
    return cells


def bootstrap_from_sources():
    """Rebuild verification map from data/sources.json (the on-disk provenance
    log accumulated across all prior cycles). Use once when introducing the
    map mid-project, then incremental updates take over."""
    sources_path = PROJECT / "data" / "sources.json"
    if not sources_path.exists():
        print("no data/sources.json — nothing to bootstrap from", file=sys.stderr)
        return 1
    sources = json.loads(sources_path.read_text(encoding="utf-8"))
    bench_keys = _load_bench_key_universe()

    cells = _build_cells_from_sources(sources, bench_keys)
    confirmed_count, contested = _recompute_consensus(cells)

    m_out = {
        "lastUpdate": TODAY,
        "stats": {
            "totalCells": len(cells),
            "contested": contested,
            "confirmed": confirmed_count,
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
