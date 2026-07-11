"""Matrix invariant + universe helpers.

Cell-level invariant per refresh cycle: every (active_modelId, coreBenchKey)
must end up in exactly one of FILLED | GAP (N/A retired 2026-05-25 — an
unmeasured cell becomes a gap and is re-researched every cycle). Silent
omission is a contract violation that merge.py blocks via .bak rollback.

Stdlib-only.
"""

from __future__ import annotations

from typing import Any, Iterable


def active_models(models: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Models in the RESEARCH universe = status 'active' only. `deprecated` and
    `archived` are EXCLUDED (2026-06-27): their data is FROZEN — never re-fetched —
    but NEVER stripped. The frontend still RENDERS them (faded via .is-deprecated /
    .is-archived) from their last-known data; the matrix/dispatch/gap pipeline just
    stops surveying them so a retired model can't reopen gaps or consume fetch
    budget. Storage retention vs. research universe are deliberately separate.

    Also EXCLUDED: `benchMirrorOf` models — a serving-speed variant with byte-for-byte
    identical weights + precision to a base model (e.g. kimi-k2-7-code-highspeed).
    Its benchmark QUALITY scores are identical to the base by construction, so the
    frontend mirrors them at load; researching it separately would waste fetch
    budget re-finding numbers that are definitionally the base's. Its own bench map
    stays empty in storage (SSOT: it has no independent measurements)."""
    return [
        m
        for m in models
        if (m.get("status") or "active") == "active" and not m.get("benchMirrorOf")
    ]


def total_universe(
    active: Iterable[dict[str, Any]], core_keys: Iterable[str]
) -> set[tuple[str, str]]:
    keys = list(core_keys)
    return {(m["id"], k) for m in active for k in keys}


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
    """|active_models| × |core_bench_keys|. N/A retired 2026-05-25, so the
    target is the full cell universe — every cell is FILLED or GAP."""
    return len(list(active)) * len(list(core_keys))


def priority_cells(
    active: list[dict[str, Any]],
    core_keys: list[str],
    limit: int = 200,
    verification_map: dict[str, Any] | None = None,
    required_keys: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Top-N most starved (modelId, benchKey) cells — ORDERING (advisory).

    FAZ 4.A (2026-05-08): this list is the ORDERING within an agent's slice,
    NOT the scope. Agent target = `target_model_ids × coreBenchKeys` (full
    slice); priorityCells just says "do these FIRST, then sweep the rest."
    See agent.md "Matrix awareness" section.

    The FAZ 2.3 AUTHORITATIVE rule was retired after the 2026-05-08 cycle
    showed it clamped agents to ~33% of their tool-call budget (top-200
    queue ÷ 18 batches ≈ 11 cells/batch). Wallclock + tool-call caps
    independently prevent runaway sweep.

    Ranking heuristic (descending priority):
      1. cells whose gapHistory shows ≥2 consecutive un-filled cycles (starved)
      2. cells that are a ranking-required bench (`required_keys`, from
         `_schema.presets.*.requiredBenches`) for a model missing at most one
         other required bench — filling this ONE cell would flip the model
         from rank-gated to ranked (2026-07-11: raw starvation buried these
         behind high-coverage models missing many low-value cells, e.g. a
         flagship missing only `lcb` sorted near the back of a 446-cell queue)
      3. cells where the bench has fewer total filled hits → starve-the-bench bias
      4. cells in models with fewer total filled hits → starve-the-model bias
      5. lex order on (modelId, benchKey) for deterministic tie-break

    `verification_map` (optional) drives ONLY the starvation re-ordering below
    (gapHistory). There is no time-based confirmed-cell skip here: this function
    enumerates EMPTY cells (`bench[k] is None`), and a confirmed cell is by
    definition FILLED, so it never appears in this queue. The FILLED+confirmed
    skip lives in lib.freshness.compute_skip_cells (→ idea_context.skipCells).

    Returns: [{modelId, benchKey, benchFillRatio, modelFillRatio}], capped at limit.
    """
    keys = list(core_keys)
    req_keys = required_keys or set()
    bench_filled = {k: 0 for k in keys}
    model_filled = {m["id"]: 0 for m in active}
    model_missing_required: dict[str, int] = {}
    for m in active:
        bench = m.get("bench") or {}
        for k in keys:
            v = bench.get(k)
            if v is not None:
                bench_filled[k] += 1
                model_filled[m["id"]] += 1
        model_missing_required[m["id"]] = sum(1 for rk in req_keys if bench.get(rk) is None)

    vm_cells: dict[str, Any] = {}
    if verification_map and isinstance(verification_map, dict):
        vm_cells = verification_map.get("cells") or {}

    # FAZ 8.A.3d (2026-05-18): starvation queue — cells whose gapHistory
    # shows ≥2 consecutive cycles of being un-filled get pulled to the
    # front of the queue with a -1.0 priority key, so they're always
    # researched FIRST regardless of bench/model fill ratios. Prevents
    # the same 90-cell auto-gap cluster from recurring cycle after cycle.
    #
    # 2026-07-11: a -0.5 tier sits between starved and normal — a
    # ranking-required cell whose model is missing at most 1 required bench
    # TOTAL (i.e. this fill would be the last one needed to become ranked).
    # Tuple shape: (starve_key, bench_ratio, model_ratio, modelId, benchKey).
    candidates: list[tuple[float, float, float, str, str]] = []
    n_models = max(len(active), 1)
    for m in active:
        for k in keys:
            v = (m.get("bench") or {}).get(k)
            if v is not None:
                continue
            cell_key = f"{m['id']}.{k}"
            vm_entry = vm_cells.get(cell_key) or {} if vm_cells else {}
            # Starvation flag: ≥2 consecutive gap cycles -> -1.0 (front).
            gap_hist = vm_entry.get("gapHistory") or []
            if len(gap_hist) >= 2:
                starve_key = -1.0
            elif k in req_keys and model_missing_required[m["id"]] <= 1:
                starve_key = -0.5
            else:
                starve_key = 0.0
            bench_ratio = bench_filled[k] / n_models
            model_ratio = model_filled[m["id"]] / max(len(keys), 1)
            candidates.append((starve_key, bench_ratio, model_ratio, m["id"], k))
    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3], t[4]))
    out = []
    for starve_key, bench_ratio, model_ratio, mid, k in candidates[:limit]:
        entry = {
            "modelId": mid,
            "benchKey": k,
            "benchFillRatio": round(bench_ratio, 3),
            "modelFillRatio": round(model_ratio, 3),
        }
        if starve_key <= -1.0:
            entry["starved"] = True
        elif starve_key <= -0.5:
            entry["rankCritical"] = True
        out.append(entry)
    return out


def matrix_snapshot(active: list[dict[str, Any]], core_keys: list[str]) -> dict[str, Any]:
    """Pre-agent snapshot: counts + per-bench / per-model fill, plus expected total."""
    keys = list(core_keys)
    filled = filled_cells_from_models(active, keys)
    by_bench: dict[str, dict[str, int]] = {}
    by_model: dict[str, dict[str, int]] = {}
    for m in active:
        mid = m["id"]
        bench = m.get("bench") or {}
        m_filled = sum(1 for k in keys if bench.get(k) is not None)
        by_model[mid] = {"filled": m_filled, "total": len(keys)}
    for k in keys:
        k_filled = sum(1 for m in active if (m.get("bench") or {}).get(k) is not None)
        by_bench[k] = {"filled": k_filled, "total": len(active)}
    return {
        "activeModels": len(active),
        "coreKeys": len(keys),
        "totalCells": len(active) * len(keys),
        "filledCells": len(filled),
        "expectedTotal": len(active) * len(keys),
        "fillRatio": round(len(filled) / max(len(active) * len(keys), 1), 3),
        "byBench": by_bench,
        "byModel": by_model,
    }


def verify_matrix_invariant(
    filled: set[tuple[str, str]],
    gaps: set[tuple[str, str]],
    universe: set[tuple[str, str]],
) -> dict[str, Any]:
    """Compute filled/gap coverage of the universe and surface missing cells.

    Every (active_modelId, coreBenchKey) cell must end up in exactly one of
    FILLED | GAP (N/A retired 2026-05-25). Silent omission or a filled∩gap
    overlap is a contract violation merge.py blocks via .bak rollback."""
    accounted = filled | gaps
    missing = universe - accounted
    overlap_filled_gap = filled & gaps
    return {
        "ok": (not missing) and (not overlap_filled_gap),
        "totalCells": len(universe),
        "filled": len(filled),
        "gaps": len(gaps),
        "missing": sorted(missing),
        "overlap": {
            "filled_gap": sorted(overlap_filled_gap),
        },
    }
