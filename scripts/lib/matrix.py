"""Matrix invariant + universe helpers.

Cell-level invariant per refresh cycle: every (active_modelId, coreBenchKey)
must end up in exactly one of FILLED | GAP | NOT_APPLICABLE. Silent omission
is a contract violation that merge.py blocks via .bak rollback.

Stdlib-only.
"""

from __future__ import annotations

from typing import Any, Iterable


def active_models(models: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [m for m in models if (m.get("status") or "active") != "archived"]


def total_universe(
    active: Iterable[dict[str, Any]], core_keys: Iterable[str]
) -> set[tuple[str, str]]:
    keys = list(core_keys)
    return {(m["id"], k) for m in active for k in keys}


def na_cells(
    active: Iterable[dict[str, Any]], core_keys: Iterable[str]
) -> set[tuple[str, str]]:
    """`notApplicableBenchKeys` her model entry'sinde tutulur."""
    out: set[tuple[str, str]] = set()
    keys = set(core_keys)
    for m in active:
        for k in m.get("notApplicableBenchKeys", []) or []:
            if k in keys:
                out.add((m["id"], k))
    return out


def filled_cells_from_models(
    active: Iterable[dict[str, Any]], core_keys: Iterable[str]
) -> set[tuple[str, str]]:
    out: set[tuple[str, str]] = set()
    keys = set(core_keys)
    for m in active:
        bench = m.get("bench") or {}
        for k, v in bench.items():
            if k in keys and v is not None:
                out.add((m["id"], k))
    return out


def parse_gap_cell(g: dict[str, Any]) -> tuple[str, str] | None:
    """Gap entries may carry either `key="<modelId>.<benchKey>"` or the agent
    contract's `{modelId, field}` shape. Both are normalized to (modelId, benchKey)."""
    key = g.get("key")
    if isinstance(key, str) and "." in key:
        mid, _, bk = key.partition(".")
        if mid and bk and "." not in bk:
            return (mid, bk)
    mid = g.get("modelId")
    bk = g.get("field")
    if isinstance(mid, str) and isinstance(bk, str) and "." not in bk:
        return (mid, bk)
    return None


def gap_cells_from_artifact(
    artifact: dict[str, Any], core_keys: Iterable[str]
) -> set[tuple[str, str]]:
    keys = set(core_keys)
    out: set[tuple[str, str]] = set()
    for g in artifact.get("gaps", []) or []:
        cell = parse_gap_cell(g)
        if cell and cell[1] in keys:
            out.add(cell)
    return out


def expected_total(active: Iterable[dict[str, Any]], core_keys: Iterable[str]) -> int:
    """|active_models| × |core_bench_keys| - |na_cells|."""
    active = list(active)
    keys = list(core_keys)
    return len(active) * len(keys) - len(na_cells(active, keys))


def verify_matrix_invariant(
    filled: set[tuple[str, str]],
    gaps: set[tuple[str, str]],
    na: set[tuple[str, str]],
    universe: set[tuple[str, str]],
) -> dict[str, Any]:
    """Compute filled/gap/na coverage of the universe and surface missing cells."""
    accounted = filled | gaps | na
    missing = universe - accounted
    overlap_filled_gap = filled & gaps
    overlap_filled_na = filled & na
    overlap_gap_na = gaps & na
    return {
        "ok": (not missing)
        and (not overlap_filled_gap)
        and (not overlap_filled_na)
        and (not overlap_gap_na),
        "totalCells": len(universe),
        "filled": len(filled),
        "gaps": len(gaps),
        "notApplicable": len(na),
        "missing": sorted(missing),
        "overlap": {
            "filled_gap": sorted(overlap_filled_gap),
            "filled_na": sorted(overlap_filled_na),
            "gap_na": sorted(overlap_gap_na),
        },
    }
