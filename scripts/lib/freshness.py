"""Freshness-tiered skip — verification-map-driven.

FAZ 2.2 (2026-05-07): partial retirement of the UNCAPPED+UNCACHED doctrine.
Prior policy was "every (modelId, benchKey) cell re-fetched every cycle"
because vendor scores can change overnight. Reform: cells with strong
agreement (≥3 sources confirming) AND recent verification (≤7 days) earn a
"skip this cycle" pass; everything else still re-fetches per the original
contract.

Two tiers:
  T1 — re-fetch (every cycle):
       confirmed=false OR verifs<3 OR age>FRESHNESS_TTL_DAYS
       OR cell has unresolved contradiction OR cell missing from map
       (default for never-seen cells).
  T2 — skip (copy from map):
       confirmed=true AND verifs≥3 AND age≤FRESHNESS_TTL_DAYS
       AND no unresolved contradiction.

T1 ALWAYS dominates uncertainty: any of the disqualifiers triggers a
re-fetch. The "vendor scores can change overnight" guarantee is preserved
because the freshness window is 7 days max — drift takes at most one cycle
to surface in low-verification cells (they're T1 always) and the next
cycle for confirmed cells (their freshness expires).

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

# Default freshness window. Configurable via _schema.contracts.FRESHNESS_TTL_DAYS.
DEFAULT_FRESHNESS_TTL_DAYS = 7
DEFAULT_MIN_VERIFICATIONS = 3


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
    *,
    ttl_days: int = DEFAULT_FRESHNESS_TTL_DAYS,
    min_verifs: int = DEFAULT_MIN_VERIFICATIONS,
) -> dict[str, Any]:
    """Classify a single verification-map cell into T1 (re-fetch) or T2 (skip).

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
    verifs = cell.get("verifications") or []
    nv = len(verifs) if isinstance(verifs, list) else 0
    last_checked_str = cell.get("lastChecked")
    last_checked = _parse_iso_date(last_checked_str)

    age = None if last_checked is None else (today - last_checked).days

    # T1 disqualifiers (any one triggers re-fetch)
    if not confirmed:
        return {"tier": "T1", "skip": False, "reason": "unconfirmed", "ageDays": age}
    if nv < min_verifs:
        return {
            "tier": "T1",
            "skip": False,
            "reason": f"verifs<{min_verifs} (have {nv})",
            "ageDays": age,
        }
    if age is None:
        return {
            "tier": "T1",
            "skip": False,
            "reason": "no-lastChecked",
            "ageDays": None,
        }
    if age > ttl_days:
        return {
            "tier": "T1",
            "skip": False,
            "reason": f"stale (age {age}d > {ttl_days}d)",
            "ageDays": age,
        }
    if cell.get("contradicted") is True:
        return {
            "tier": "T1",
            "skip": False,
            "reason": "unresolved-contradiction",
            "ageDays": age,
        }

    return {
        "tier": "T2",
        "skip": True,
        "reason": f"confirmed; verifs={nv}; age={age}d",
        "ageDays": age,
    }


def compute_skip_cells(
    verification_map: dict[str, Any],
    today: date,
    active_model_ids: list[str],
    core_bench_keys: list[str],
    *,
    ttl_days: int = DEFAULT_FRESHNESS_TTL_DAYS,
    min_verifs: int = DEFAULT_MIN_VERIFICATIONS,
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
            cls = classify_cell(entry, today, ttl_days=ttl_days, min_verifs=min_verifs)
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
    from lib.whitelist import core_bench_keys, load_whitelist  # noqa: E402

    for stream in (sys.stdout, sys.stderr):
        reconf = getattr(stream, "reconfigure", None)
        if callable(reconf):
            try:
                reconf(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass

    vm_path = PROJECT / ".aicodermap-verification-map.json"
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
