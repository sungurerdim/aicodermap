"""Canonical synth-pipeline shared library (F2.2).

Single implementation of the cluster→winner→contradiction flow shared by:
  - scripts/local-synth.py     (deterministic fallback)
  - scripts/lib/synth.py       (FAZ 4.D python synth)
  - scripts/gather-union.py    (deprecated — use local-synth.py instead)

All callers use cluster_observations() + select_winner() from here.
Decision logic lives in scripts/lib/winner.py (pick_winner).

Stdlib-only.
"""

from __future__ import annotations

import datetime
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .tiers import trust_score as _trust_score
from .winner import build_contradiction_entry, pick_winner


def cluster_observations(
    observations: list[dict[str, Any]],
    agreement_pp: float = 1.5,
    today: datetime.date | None = None,
) -> dict[str, Any]:
    """Cluster observations for a single (modelId, benchKey) cell.

    Returns the pick_winner result dict directly. Thin wrapper that adds
    trust-score computation before calling winner.pick_winner().

    Parameters
    ----------
    observations:
        Raw obs dicts with {value, tier, sourceUrl, fetched}.
    agreement_pp:
        Clustering tolerance in percentage points (or ELO points).
    today:
        Reference date for recency decay. Defaults to today().
    """
    return pick_winner(
        observations,
        agreement_pp=agreement_pp,
        today=today,
    )


def recency_decay(date_str: Any) -> float:
    """Re-export for callers that import from synth_core (backwards compat)."""
    from .tiers import recency_decay as _rd

    return _rd(date_str)


def trust_score(tier: str, verifications: int, date_str: Any) -> float:
    """Re-export canonical trust_score formula."""
    return _trust_score(tier, verifications, date_str)


def aggregate_observations(
    artifacts: list[tuple[str, dict[str, Any]]],
    *,
    canonical_bench_keys: set[str] | None = None,
    active_ids: set[str] | None = None,
    unhealthy_urls: set[str] | None = None,
) -> dict[tuple[str, str], list[dict[str, Any]]]:
    """Pool observations from multiple gather artifacts by (modelId, benchKey).

    Drops:
    - Observations with None values
    - Non-canonical bench keys (when canonical_bench_keys provided)
    - Models not in active_ids (when provided)
    - Citations of unhealthy URLs (FAZ 6.A SPA guard)

    Returns:
        {(modelId, benchKey): [obs, ...]}
    """
    skip_urls = {
        (u or "").strip().rstrip("/").lower() for u in (unhealthy_urls or set())
    }
    cells: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    rejected = 0

    for _path, art in artifacts:
        for obs in art.get("observations") or []:
            if not isinstance(obs, dict):
                continue
            mid = obs.get("modelId")
            bk = obs.get("benchKey")
            val = obs.get("value")
            if not (isinstance(mid, str) and isinstance(bk, str) and val is not None):
                continue
            if active_ids is not None and mid not in active_ids:
                continue
            if canonical_bench_keys is not None and bk not in canonical_bench_keys:
                continue
            try:
                val = float(val)
            except (TypeError, ValueError):
                continue
            url = (obs.get("sourceUrl") or "").strip().rstrip("/").lower()
            if url and url in skip_urls:
                rejected += 1
                continue
            cells[(mid, bk)].append({**obs, "value": val})

    if rejected:
        print(f"⚠ synth_core SPA guard: dropped {rejected} unhealthy-URL observations")
    return cells


def synthesize(
    artifacts: list[tuple[str, dict[str, Any]]],
    *,
    canonical_bench_keys: set[str],
    active_ids: set[str] | None = None,
    agreement_pp: float = 1.5,
    warn_pp: float = 3.0,
    block_pp: float = 5.0,
    unhealthy_urls: set[str] | None = None,
    historical_pool: dict[tuple[str, str], list[dict[str, Any]]] | None = None,
) -> tuple[
    dict[
        str, dict[str, Any]
    ],  # models_by_id: {modelId: {updates, sourcesAdded, notApplicable}}
    list[dict[str, Any]],  # contradictions[]
    set[tuple[str, str]],  # filled_cells
]:
    """Run full synthesis for all (modelId, benchKey) cells.

    Merges historical pool observations into live gather observations before
    clustering (prevents new low-tier obs from overriding strong historical
    consensus — cycle 2026-05-11 root cause).

    Returns (models_by_id, contradictions, filled_cells).
    """
    today = datetime.date.today()
    cells = aggregate_observations(
        artifacts,
        canonical_bench_keys=canonical_bench_keys,
        active_ids=active_ids,
        unhealthy_urls=unhealthy_urls,
    )

    # Inject historical observations for cells that got new obs this cycle
    if historical_pool:
        for cell_key, new_obs in list(cells.items()):
            for h in historical_pool.get(cell_key, []):
                url = h.get("sourceUrl") or ""
                already = any(
                    o.get("sourceUrl") == url and o.get("value") == h.get("value")
                    for o in new_obs
                )
                if not already:
                    cells[cell_key].append(h)

    models_by_id: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "updates": {"bench": {}, "lastUpdated": today.isoformat()},
            "sourcesAdded": [],
            "notApplicable": [],
        }
    )
    contradictions: list[dict[str, Any]] = []
    filled_cells: set[tuple[str, str]] = set()

    for (mid, bk), obs_list in cells.items():
        if bk not in canonical_bench_keys:
            continue
        result = pick_winner(
            obs_list,
            bench_key=bk,
            agreement_pp=agreement_pp,
            warn_pp=warn_pp,
            block_pp=block_pp,
            today=today,
        )
        if result["winner_value"] is None:
            continue

        models_by_id[mid]["id"] = mid
        models_by_id[mid]["updates"]["bench"][bk] = result["winner_value"]
        filled_cells.add((mid, bk))

        for s in result["scored"]:
            models_by_id[mid]["sourcesAdded"].append(
                {
                    "key": f"{mid}.{bk}",
                    "value": s["value"],
                    "source": (s.get("sourceUrl") or "")[:100] or "synth-aggregated",
                    "url": s.get("sourceUrl") or "",
                    "tier": s.get("tier", "C"),
                    "fetched": s.get("fetched") or today.isoformat(),
                    "verifications": len(result["scored"]),
                    "trustScore": s["trustScore"],
                }
            )

        if result["is_contradiction"]:
            entry = build_contradiction_entry(mid, bk, result)
            if result.get("override_mode"):
                entry["contradictionMode"] = result["override_mode"]
            contradictions.append(entry)

    return dict(models_by_id), contradictions, filled_cells


def load_historical_pool(
    sources_path: str | Path,
    core_keys: set[str],
    active_ids: set[str] | None = None,
) -> dict[tuple[str, str], list[dict[str, Any]]]:
    """Load historical sources.json entries into a (modelId, benchKey) pool.

    Prevents new low-tier observations from overriding strong historical
    consensus (cycle 2026-05-11 deepseek-v4-pro.swePro regression).
    """
    pool: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    try:
        data = json.loads(Path(sources_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return pool

    for full_key, entries in data.items():
        if "." not in full_key:
            continue
        mid, bk = full_key.split(".", 1)
        if bk not in core_keys:
            continue
        if active_ids is not None and mid not in active_ids:
            continue
        for e in entries:
            v = e.get("value")
            if v is None:
                continue
            try:
                v = float(v)
            except (TypeError, ValueError):
                continue
            pool[(mid, bk)].append(
                {
                    "value": v,
                    "sourceUrl": e.get("url") or "",
                    "tier": (e.get("tier") or "C").upper(),
                    "fetched": e.get("date") or "2026-01-01",
                    "source": e.get("source") or "",
                    "_historical": True,
                }
            )
    return pool
