"""Confirmed-cell skip — verification-map-driven, time-independent.

Doctrine (TTL removed 2026-06-27): a released model's published benchmark score
(SWE-bench, GPQA, …) is FROZEN — once a cell is `confirmed` it never changes, so
re-fetching it on a clock has no benefit and only slows + complicates the cycle.
The skip rule is therefore a single condition:

  SKIP (T2): confirmed=true AND not contradicted   → emit cached value, no fetch.
  FETCH (T1): everything else — unconfirmed, contradicted, or never-seen.

The `confirmed`/`contradicted` flags are DERIVED in verification-map.py from
accumulated provenance (count + agreement; `confirmed` already requires
MIN_VERIFICATIONS_FOR_SKIP agreeing sources). This module just reads them.

Re-validation is EVENT-triggered, not time-triggered: detect-anomalies.py runs on
live data every cycle, and a contradiction / peer-outlier / fresh-divergence
flips `contradicted` (or clears `confirmed`), re-opening the cell next cycle. The
prior age>FRESHNESS_TTL_DAYS / verifs-threshold branches are gone — they added a
clock that the frozen-score model makes pointless.

Usage:
    from lib.freshness import compute_skip_cells

    skip = compute_skip_cells(
        verification_map, today, active_model_ids, core_bench_keys,
    )
    # → { "<modelId>": { "<benchKey>": {value, sources, lastChecked} } }

Stdlib-only.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any


def _parse_iso_date(s: Any) -> date | None:
    if not isinstance(s, str):
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def classify_cell(
    cell: dict[str, Any] | None,
    today: date,
) -> dict[str, Any]:
    """Classify a single verification-map cell into T1 (re-fetch) or T2 (skip).

    SKIP (T2) iff `confirmed` AND not `contradicted` — a confirmed cell holds a
    frozen published score, so it is never re-fetched on age. Everything else is
    T1. `ageDays` is informational only (no longer drives the tier).

    Returns:
      {
        "tier": "T1" | "T2",
        "skip": bool,
        "reason": str,        # human-readable why
        "ageDays": int | None # null if no lastChecked
      }
    """
    if not isinstance(cell, dict):
        return {"tier": "T1", "skip": False, "reason": "no-map-entry", "ageDays": None}

    confirmed = cell.get("confirmed") is True
    contradicted = cell.get("contradicted") is True
    last_checked = _parse_iso_date(cell.get("lastChecked"))
    age = None if last_checked is None else (today - last_checked).days

    if not confirmed:
        return {"tier": "T1", "skip": False, "reason": "unconfirmed", "ageDays": age}
    if contradicted:
        return {
            "tier": "T1",
            "skip": False,
            "reason": "unresolved-contradiction",
            "ageDays": age,
        }

    return {"tier": "T2", "skip": True, "reason": "confirmed", "ageDays": age}


def compute_skip_cells(
    verification_map: dict[str, Any],
    today: date,
    active_model_ids: list[str],
    core_bench_keys: list[str],
) -> dict[str, Any]:
    """Walk every (active_model × core_bench_key) cell, classify via the
    verification map, and return the skip set.

    Returns:
      {
        "<modelId>": {
          "<benchKey>": {
            "value": <map value>,
            "sources": [<list of {source,url,tier,value,fetched}>],
            "lastChecked": "<YYYY-MM-DD>",
            "ageDays": <int>,
            "verifications": <int>
          },
          ...
        },
        ...
      }
      Plus a "_meta" key with summary counts:
      "_meta": { "t1Count": <int>, "t2Count": <int>, "totalConsidered": <int> }
    """
    cells = (verification_map or {}).get("cells") or {}
    skip: dict[str, Any] = {}
    t1 = 0
    t2 = 0
    total = 0

    for mid in active_model_ids:
        for bk in core_bench_keys:
            total += 1
            key = f"{mid}.{bk}"
            entry = cells.get(key)
            cls = classify_cell(entry, today)
            if cls["tier"] == "T2":
                t2 += 1
                skip.setdefault(mid, {})[bk] = {
                    "value": (entry or {}).get("value"),
                    "sources": (entry or {}).get("verifications") or [],
                    "lastChecked": (entry or {}).get("lastChecked"),
                    "ageDays": cls["ageDays"],
                    "verifications": len((entry or {}).get("verifications") or []),
                }
            else:
                t1 += 1

    skip["_meta"] = {"t1Count": t1, "t2Count": t2, "totalConsidered": total}
    return skip


if __name__ == "__main__":
    # CLI: print today's skip set for the current verification map.
    import json
    import sys
    from pathlib import Path

    PROJECT = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(PROJECT / "scripts"))
    from lib.matrix import active_models  # noqa: E402
    from lib.constants import VERIFICATION_MAP_PATH  # noqa: E402
    from lib.util import configure_utf8_output  # noqa: E402
    from lib.whitelist import core_bench_keys, load_whitelist  # noqa: E402

    configure_utf8_output()

    vm_path = PROJECT / VERIFICATION_MAP_PATH
    vm: dict[str, Any] = {"cells": {}}
    if vm_path.exists():
        with vm_path.open(encoding="utf-8") as f:
            vm = json.load(f)

    wl = load_whitelist()
    keys = core_bench_keys(wl)
    with (PROJECT / "data" / "models.json").open(encoding="utf-8") as f:
        models = json.load(f)
    active = active_models(models)
    active_ids = [m["id"] for m in active]

    skip = compute_skip_cells(vm, date.today(), active_ids, keys)
    meta = skip.pop("_meta")
    print("=== FRESHNESS-TIER SKIP ===")
    print(
        f"considered: {meta['totalConsidered']}  T1 (re-fetch): {meta['t1Count']}  "
        f"T2 (skip): {meta['t2Count']}"
    )
    print(f"skipRatio: {meta['t2Count'] / max(meta['totalConsidered'], 1):.1%}")
    if skip:
        print("\nSample T2 cells:")
        for mid in list(skip.keys())[:5]:
            for bk, e in list(skip[mid].items())[:2]:
                print(
                    f"  {mid}.{bk} = {e['value']} (verifs={e['verifications']}, age={e['ageDays']}d)"
                )
