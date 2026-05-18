"""Unified escalation decision matrix (F3.1).

Replaces two separate escalation passes in SKILL.md:
  - FAZ 2.4 (lines 283-314): 0-fill batch auto-retry
  - FAZ 4.C.2 (lines 322-363): weak-batch retry (avg_obs < HAIKU_GATHER_MIN_AVG_OBS)

Both conditions are now evaluated in ONE classify_batch() call after each
wave completes. Batches requiring escalation are collected, then dispatched
in a SINGLE parallel retry wave — eliminating the double-escalation race
condition where a batch could qualify for BOTH paths and get two separate
sonnet retries.

Environment override:
  AICODERMAP_ESC_MIN_OBS=<int>  — override HAIKU_GATHER_MIN_AVG_OBS (default 3)

Stdlib-only.
"""

from __future__ import annotations

import json
import os
from enum import Enum
from pathlib import Path
from typing import Any


class EscalationAction(str, Enum):
    NONE = "none"  # batch is good — no retry needed
    RETRY_SONNET = "retry_sonnet"  # escalate to sonnet gather retry


def _env_min_obs() -> float:
    """Read AICODERMAP_ESC_MIN_OBS env override; fallback to 3."""
    try:
        return float(os.environ.get("AICODERMAP_ESC_MIN_OBS", "3"))
    except (TypeError, ValueError):
        return 3.0


def classify_batch(
    artifact: dict[str, Any],
    batch_spec: dict[str, Any],
    *,
    min_avg_obs: float | None = None,
) -> dict[str, Any]:
    """Determine escalation action for a single batch artifact.

    Parameters
    ----------
    artifact:
        Parsed gather artifact dict (from .aicodermap-agent-out-<batchId>.gather.json).
        May be an empty/stub dict if the file was missing or unreadable.
    batch_spec:
        Batch spec dict from dispatch.compute_dispatch_plan() — must contain
        at minimum {batchId, modelIds}.
    min_avg_obs:
        Minimum average observations per target model. Below → sonnet retry.
        Defaults to env AICODERMAP_ESC_MIN_OBS (fallback 3).

    Returns
    -------
    dict with keys:
        action      EscalationAction
        reason      str   — human-readable escalation reason
        batchId     str
        avg_obs     float — computed avg obs/model
        fills       int   — fills count from artifact
        cells_attempted int
    """
    effective_min_obs = min_avg_obs if min_avg_obs is not None else _env_min_obs()
    batch_id = batch_spec.get("batchId") or artifact.get("_batchId") or "unknown"
    model_ids = batch_spec.get("modelIds") or []
    n_models = max(len(model_ids), 1)

    runtime = artifact.get("runtime") or {}
    fills = int(runtime.get("fills", 0) or runtime.get("cellsFilled", 0))
    cells_attempted = int(runtime.get("cellsAttempted", 0))

    # Count total observations across all models in artifact
    all_obs = artifact.get("observations") or []
    total_obs = len(all_obs)
    avg_obs = total_obs / n_models

    already_retried = bool(artifact.get("_retry_attempted"))

    # Condition A — 0-fill: agent ran but found nothing
    # (cells_attempted > 0 distinguishes "ran but failed" from "crashed before fetch")
    zero_fill = fills == 0 and (
        cells_attempted > 0 or total_obs > 0 or len(all_obs) == 0
    )

    # Condition B — weak gather: avg observations per model below threshold
    weak_gather = avg_obs < effective_min_obs

    if already_retried:
        return {
            "action": EscalationAction.NONE,
            "reason": "already retried this cycle — accept result",
            "batchId": batch_id,
            "avg_obs": round(avg_obs, 2),
            "fills": fills,
            "cells_attempted": cells_attempted,
        }

    if zero_fill:
        return {
            "action": EscalationAction.RETRY_SONNET,
            "reason": f"zero fills (cellsAttempted={cells_attempted}) — 0-fill escalation",
            "batchId": batch_id,
            "avg_obs": round(avg_obs, 2),
            "fills": fills,
            "cells_attempted": cells_attempted,
        }

    if weak_gather:
        return {
            "action": EscalationAction.RETRY_SONNET,
            "reason": (
                f"haiku gather avg_obs={avg_obs:.1f} < {effective_min_obs} "
                f"— weak-gather escalation"
            ),
            "batchId": batch_id,
            "avg_obs": round(avg_obs, 2),
            "fills": fills,
            "cells_attempted": cells_attempted,
        }

    return {
        "action": EscalationAction.NONE,
        "reason": f"ok (avg_obs={avg_obs:.1f} ≥ {effective_min_obs}, fills={fills})",
        "batchId": batch_id,
        "avg_obs": round(avg_obs, 2),
        "fills": fills,
        "cells_attempted": cells_attempted,
    }


def classify_wave(
    wave_artifacts: list[tuple[dict[str, Any], dict[str, Any]]],
    *,
    min_avg_obs: float | None = None,
) -> list[dict[str, Any]]:
    """Classify all batches in a wave and return those needing escalation.

    Parameters
    ----------
    wave_artifacts:
        List of (artifact, batch_spec) pairs for the completed wave.

    Returns
    -------
    List of classify_batch results where action != NONE.
    """
    escalations: list[dict[str, Any]] = []
    for artifact, batch_spec in wave_artifacts:
        result = classify_batch(artifact, batch_spec, min_avg_obs=min_avg_obs)
        if result["action"] != EscalationAction.NONE:
            escalations.append(result)
    return escalations


def load_artifact(path: str | Path) -> dict[str, Any]:
    """Load a gather artifact from disk. Returns {} on any error."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
