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
ARTIFACT = PROJECT / ".aicodermap-agent-out.json"
MAP_PATH = PROJECT / ".aicodermap-verification-map.json"

VERIFICATION_AGREEMENT_THRESHOLD = (
    3  # number of agreeing sources before audit-only `confirmed=true`
)
VERIFICATION_AGREEMENT_PP = 1.5
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

    appended = 0
    for model in artifact.get("models", []) or []:
        for src in model.get("sourcesAdded", []) or []:
            key = src.get("key")
            if not key or "bench" not in key:
                continue
            parsed = parse_cell_key(key)
            if not parsed:
                continue
            mid, bk = parsed
            cell_key = f"{mid}.{bk}"
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
    """Bench-key universe = whitelist._schema.coreBenchKeys ∪ every
    leaderboard's publishes[] entry. Mirrors merge.py."""
    wl_path = PROJECT / "data" / "sources-whitelist.json"
    if not wl_path.exists():
        return set()
    try:
        wl = json.loads(wl_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return set()
    universe = set()
    schema = wl.get("_schema") or {}
    for k in schema.get("coreBenchKeys", []) or []:
        universe.add(k)
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
