"""Per-batch idea_context builder (FAZ 7.B / 7.C / 7.D, 2026-05-10).

Single source of truth for the slim per-batch context dict the skill
orchestrator passes to each haiku gather agent. Replaces the in-prompt
inline build that inflated each batch ctx file to 156-160 KB
(verificationMap full inline + full whitelist + snapshot metadata).

Slim contract per batch:
  total_models        copy
  last_refresh        copy (ISO timestamp)
  currentIds          copy (full list — needed for cross-batch lineup checks)
  cycleStartedUnix    epoch (FAZ 7.A — drives validator stale check)
  sourcesWhitelist    filtered_for_batch(...)  — vendors of this batch +
                                                   _schema in full + filtered
                                                   leaderboards/aggregators/local
  matrixState         per-batch slice (byModel filtered to batch's modelIds)
  priorityCells       only entries whose modelId in batch's modelIds
  contracts           full (numeric thresholds — small)
  bannedFetchPatterns full (regex list — small)
  leaderboardSnapshots url -> path mapping ONLY (drop contentLength, contentType,
                                                  fetchedAt, etag — agent does
                                                  not need these)
  skipCells           per-batch slice (T2 filled-cell freshness skip; GAP cells
                      are never skipped — every empty cell is re-queried each run)
  verificationMap     CELLS slice for batch's modelIds only
                      (drop the rest — was 93 KB inline previously)
  lineup              copy (small, may be {})

Token impact (cycle 2026-05-10 measured):
  Before: 156-160 KB × 15 batches = 2.4 MB total ctx I/O
  After:  ~24-30 KB × 12 batches  = ~330 KB total ctx I/O (~7× cheaper)

Quality: every field still surfaces — the agent sees the universe of bench
keys via _schema, the format taxonomy, notApplicableRules, every leaderboard
URL relevant to its bench keys, and the full verification slice for ITS
models. The only thing dropped is unrelated vendors and other models'
verification cells.

Stdlib-only.
"""

from __future__ import annotations

from typing import Any

from .whitelist import filter_for_batch


def slim_snapshots(snapshots: dict[str, Any] | None) -> dict[str, str]:
    """leaderboardSnapshots map → url -> path only.

    Drops `contentLength`, `contentType`, `fetchedAt`, `etag`. Saves ~10-15 KB
    per batch ctx.
    """
    if not snapshots:
        return {}
    out: dict[str, str] = {}
    for url, info in snapshots.items():
        if isinstance(info, str):
            out[url] = info
            continue
        if isinstance(info, dict):
            path = info.get("path")
            if isinstance(path, str):
                out[url] = path
    return out


def slim_verification_slice(
    verification_map: dict[str, Any] | None,
    model_ids: set[str] | list[str],
) -> dict[str, Any]:
    """Return only the cells whose modelId is in model_ids.

    Verification map shape: {"cells": {"<modelId>.<benchKey>": {...}}, ...}.
    Falls back to {} on missing/malformed input. Output schema mirrors the
    input so existing agent code paths remain compatible.
    """
    if not verification_map:
        return {"cells": {}}
    mids = set(model_ids)
    cells = (verification_map or {}).get("cells") or {}
    sliced: dict[str, Any] = {}
    for k, v in cells.items():
        # Cell key format: "<modelId>.<benchKey>". Be tolerant of missing dot.
        mid = k.split(".", 1)[0] if isinstance(k, str) else None
        if mid in mids:
            sliced[k] = v
    return {"cells": sliced}


def slim_priority_cells(
    priority_cells: list[dict[str, Any]] | None,
    model_ids: set[str] | list[str],
) -> list[dict[str, Any]]:
    if not priority_cells:
        return []
    mids = set(model_ids)
    return [
        c for c in priority_cells if isinstance(c, dict) and c.get("modelId") in mids
    ]


def slim_skip_cells(
    skip_cells: dict[str, Any] | None,
    model_ids: set[str] | list[str],
) -> dict[str, Any]:
    if not skip_cells:
        return {}
    mids = set(model_ids)
    sliced: dict[str, Any] = {k: v for k, v in skip_cells.items() if k in mids}
    if "_meta" in skip_cells:
        sliced["_meta"] = skip_cells["_meta"]
    return sliced


def slim_matrix_state(
    matrix_state: dict[str, Any] | None,
    model_ids: set[str] | list[str],
) -> dict[str, Any]:
    if not matrix_state:
        return {}
    mids = set(model_ids)
    by_model = matrix_state.get("byModel") or {}
    out = {
        "activeModels": matrix_state.get("activeModels"),
        "coreKeys": matrix_state.get("coreKeys"),
        "expectedTotal": matrix_state.get("expectedTotal"),
        "filledCells": matrix_state.get("filledCells"),
        "fillRatio": matrix_state.get("fillRatio"),
        "byBench": matrix_state.get("byBench") or {},
        "byModel": {mid: by_model.get(mid, {}) for mid in mids},
    }
    return out


def build_per_batch_ctx(
    *,
    batch_spec: dict[str, Any],
    full_whitelist: dict[str, Any],
    matrix_state: dict[str, Any],
    priority_cells: list[dict[str, Any]],
    skip_cells: dict[str, Any],
    verification_map: dict[str, Any],
    leaderboard_snapshots: dict[str, Any],
    contracts: dict[str, Any],
    banned_fetch_patterns: list[str],
    cycle_started_unix: float,
    total_models: int,
    last_refresh: str | None,
    current_ids: list[str],
    lineup: dict[str, Any] | None = None,
    bench_keys: list[str] | None = None,
) -> dict[str, Any]:
    """Compose the slim per-batch idea_context dict.

    Mutates nothing; returns a fresh dict. Caller writes JSON to
    `.aicodermap-ctx-<batchId>.json` for the agent to Read.
    """
    model_ids = batch_spec.get("modelIds") or []
    providers = batch_spec.get("providers") or []
    fwl = filter_for_batch(
        full_whitelist,
        providers,
        bench_keys=set(bench_keys) if bench_keys else None,
    )
    return {
        "title": "AICoderMap",
        "total_models": total_models,
        "last_refresh": last_refresh,
        "currentIds": current_ids,
        "cycleStartedUnix": cycle_started_unix,
        "sourcesWhitelist": fwl,
        "matrixState": slim_matrix_state(matrix_state, model_ids),
        "priorityCells": slim_priority_cells(priority_cells, model_ids),
        "contracts": contracts,
        "bannedFetchPatterns": banned_fetch_patterns,
        "leaderboardSnapshots": slim_snapshots(leaderboard_snapshots),
        "skipCells": slim_skip_cells(skip_cells, model_ids),
        "verificationMap": slim_verification_slice(verification_map, model_ids),
        "lineup": lineup or {},
        "_batchSpec": {
            "batchId": batch_spec.get("batchId"),
            "waveIndex": batch_spec.get("waveIndex"),
            "modelIds": list(model_ids),
            "providers": list(providers),
            "expectedCells": batch_spec.get("expectedCells"),
        },
    }
