#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cycle-level telemetry helper.

Writes:
  data/_meta.json            — single-row latest cycle snapshot, served by
                               GitHub Pages. freshness.js + verify-deploy.py
                               read this for cache-bust + deploy parity.
  data/refresh-history.json  — ring-buffer of the last RING_BUFFER_SIZE
                               cycles for human review + telemetry plots.

Pure stdlib; called from scripts/merge.py during the post-write phase.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT = Path(__file__).resolve().parents[2]
META_PATH = PROJECT / "data" / "_meta.json"
HISTORY_PATH = PROJECT / "data" / "refresh-history.json"

RING_BUFFER_SIZE = 30
SCHEMA_VERSION = "v1"


def _git_head_short() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=PROJECT,
            capture_output=True,
            text=True,
            check=True,
        )
        return (out.stdout or "").strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _norm_ts(value: Any) -> str | None:
    """Normalize a runtime timestamp to an ISO-8601 UTC string.

    Gather artifacts store runtime.startedAt/endedAt inconsistently — some as
    int/float epoch seconds, some as ISO strings. Coercing here keeps the
    later min()/max() comparison type-homogeneous (a mixed list raises
    TypeError: '<' not supported between 'int' and 'str').
    """
    if value is None:
        return None
    if isinstance(value, bool):  # guard: bool is an int subclass
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    if isinstance(value, str):
        return value
    return None


def _read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def build_meta(
    *,
    models: list,
    bench_keys: list,
    matrix_diag: dict,
    artifact: dict,
    contradictions_resolved: int,
    prev_push_etag: str | None = None,
) -> dict:
    """Compose the single-row snapshot. Pure: no I/O."""
    rm = artifact.get("runMetadata") or {}
    total = matrix_diag.get("totalCells", 0)
    filled = matrix_diag.get("filled", 0)
    gaps = matrix_diag.get("gaps", 0)
    na = matrix_diag.get("notApplicable", 0)
    return {
        "schemaVersion": SCHEMA_VERSION,
        "updatedAt": _utc_iso(),
        "buildSha": _git_head_short(),
        "cycleId": rm.get("startedAt") or _utc_iso(),
        "modelCount": len(models),
        "benchKeyCount": len(bench_keys),
        "totalCells": total,
        "filledCells": filled,
        "gapCells": gaps,
        "naCells": na,
        "fillRatio": round(filled / total, 4) if total else 0.0,
        "contradictionsResolved": int(contradictions_resolved or 0),
        "lastCycleToolCallCount": rm.get("toolCallCount"),
        "lastCycleFetchAttemptCount": rm.get("fetchAttemptCount"),
        "lastCycleBatchCount": rm.get("batchCount"),
        "lastCycleElapsedMs": rm.get("elapsedMs"),
        "prevPushEtag": prev_push_etag,
    }


def write_meta_and_history(meta: dict) -> None:
    """Write data/_meta.json + append to data/refresh-history.json ring."""
    META_PATH.parent.mkdir(parents=True, exist_ok=True)
    META_PATH.write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    history = _read_json(
        HISTORY_PATH, default={"schemaVersion": SCHEMA_VERSION, "cycles": []}
    )
    if not isinstance(history, dict):
        history = {"schemaVersion": SCHEMA_VERSION, "cycles": []}
    cycles = history.setdefault("cycles", [])
    if not isinstance(cycles, list):
        cycles = []
    # Append + truncate to ring size (FIFO: drop oldest).
    cycles.append(
        {
            k: meta[k]
            for k in (
                "updatedAt",
                "buildSha",
                "cycleId",
                "modelCount",
                "benchKeyCount",
                "totalCells",
                "filledCells",
                "gapCells",
                "naCells",
                "fillRatio",
                "contradictionsResolved",
                "lastCycleToolCallCount",
                "lastCycleFetchAttemptCount",
                "lastCycleBatchCount",
                "lastCycleElapsedMs",
            )
            if k in meta
        }
    )
    if len(cycles) > RING_BUFFER_SIZE:
        cycles[:] = cycles[-RING_BUFFER_SIZE:]
    history["cycles"] = cycles
    HISTORY_PATH.write_text(
        json.dumps(history, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _count_fills_and_gaps(
    art: dict, mode: str | None
) -> tuple[int, int, int, int, int]:
    """FAZ 7.C (2026-05-10): mode-aware fill/gap counting.

    Gather artifacts use FLAT schema (observations[], rawGaps[]). Synth/full
    use models[].updates.bench + gaps[]. Prior version always read FULL schema,
    so gather-only cycles reported fills=0/gaps=0 (cycle 2026-05-10).

    Returns (fills, gaps, agent_gaps, orch_gaps, na).
    """
    if mode == "gather":
        fills = len(art.get("observations") or [])
        all_gaps = art.get("rawGaps") or []
        gaps = len(all_gaps)
        agent_gaps = gaps  # gather rawGaps are always agent-emitted
        orch_gaps = 0
        # N/A retired: gather artifacts never carry naCandidates (forbidden by
        # the gather schema). Kept as 0 for telemetry-schema stability.
        na = 0
    else:
        models = art.get("models") or []
        fills = sum(
            len((m.get("updates") or {}).get("bench") or {})
            for m in models
            if isinstance(m, dict)
        )
        all_gaps = art.get("gaps") or []
        gaps = len(all_gaps)
        # FAZ 4.B (2026-05-08): split by source — 'agent' = real research,
        # 'orchestrator' = auto-stub placeholder. Legacy entries default 'agent'.
        agent_gaps = sum(
            1
            for g in all_gaps
            if isinstance(g, dict) and g.get("source") != "orchestrator"
        )
        orch_gaps = gaps - agent_gaps
        na = sum(
            len(m.get("notApplicable") or []) for m in models if isinstance(m, dict)
        )
    return fills, gaps, agent_gaps, orch_gaps, na


def _extract_batch_entry(art: dict) -> tuple:
    """Extract a single per-batch telemetry row from one batch artifact.

    Returns (entry dict, wallclock, tool_call_count, fills, gaps, na,
             started_ts, ended_ts) — side-channel timing strings are used by
    the caller for cycle-level min/max aggregation.
    """
    rm = art.get("runtime") or art.get("runMetadata") or {}
    # Source priority for batch_id:
    #   1. art.batchId (agent emits it)
    #   2. runtime.batchId / runMetadata.batchId
    #   3. art._batchId (orchestrator-injected from artifact filename)
    #   4. partialReason.batchId (when partialReason is a dict)
    partial_reason = art.get("partialReason")
    partial_batch_id = (
        partial_reason.get("batchId") if isinstance(partial_reason, dict) else None
    )
    batch_id = (
        art.get("batchId")
        or rm.get("batchId")
        or art.get("_batchId")
        or partial_batch_id
        or "unknown"
    )

    fills, gaps, agent_gaps, orch_gaps, na = _count_fills_and_gaps(art, art.get("mode"))

    wallclock = float(
        art.get("_wallclockSec")
        or rm.get("wallclockSec")
        or rm.get("elapsedSec")
        or 0.0
    )
    tool_call_count = int(rm.get("toolCallCount") or 0)
    started_ts = _norm_ts(rm.get("startedAt"))
    ended_ts = _norm_ts(rm.get("endedAt"))

    entry = {
        "batchId": batch_id,
        "wallclockSec": wallclock,
        "toolCallCount": tool_call_count,
        "fills": fills,
        "gaps": gaps,
        "agentGaps": agent_gaps,
        "orchestratorGaps": orch_gaps,
        "naCount": na,
        "partialReason": partial_reason,
    }
    return entry, wallclock, tool_call_count, fills, gaps, na, started_ts, ended_ts


def _compute_wallclock_stats(wallclocks: list[float]) -> tuple[float, float]:
    """Return (wc_max, wc_p95) from a list of per-batch wallclock seconds."""
    if not wallclocks:
        return 0.0, 0.0
    wc_sorted = sorted(wallclocks)
    wc_max = wc_sorted[-1]
    wc_p95 = wc_sorted[int(len(wc_sorted) * 0.95)] if len(wc_sorted) > 1 else wc_max
    return wc_max, wc_p95


def aggregate_per_batch_telemetry(per_batch_artifacts: list[dict]) -> dict:
    """FAZ 2.4 (2026-05-07): walk per-batch artifacts, compute cycle telemetry.

    Reads each batch artifact's `runtime.phaseTimings`, `runtime.toolCallCount`,
    `partialReason`, and fill counts. Returns a single dict suitable for
    `data/_telemetry/<cycleDate>.json`.

    Returns:
      {
        "cycleStartedAt": <iso>,        # earliest batch start
        "cycleEndedAt": <iso>,          # latest batch end
        "totalBatches": <int>,
        "zeroFillBatches": [<batchId>, ...],  # candidates for retry
        "perBatch": [
          { "batchId", "wallclockSec", "toolCallCount",
            "fills", "gaps", "naCount", "partialReason" }
        ],
        "totals": {
          "fills": int, "gaps": int, "na": int,
          "wallclockSecMax": float,    # slowest batch dominates wave wallclock
          "wallclockSecP95": float,    # tail latency
          "toolCallSum": int
        }
      }
    """
    per_batch: list[dict] = []
    fills_total = 0
    gaps_total = 0
    na_total = 0
    tool_sum = 0
    wallclocks: list[float] = []
    started: list[str] = []
    ended: list[str] = []

    for art in per_batch_artifacts or []:
        if not isinstance(art, dict):
            continue
        entry, wallclock, tool_call_count, fills, gaps, na, started_ts, ended_ts = (
            _extract_batch_entry(art)
        )
        fills_total += fills
        gaps_total += gaps
        na_total += na
        tool_sum += tool_call_count
        if wallclock > 0:
            wallclocks.append(wallclock)
        if started_ts:
            started.append(started_ts)
        if ended_ts:
            ended.append(ended_ts)
        per_batch.append(entry)

    zero_fill = [pb["batchId"] for pb in per_batch if pb["fills"] == 0]
    wc_max, wc_p95 = _compute_wallclock_stats(wallclocks)

    return {
        "cycleStartedAt": min(started) if started else _utc_iso(),
        "cycleEndedAt": max(ended) if ended else _utc_iso(),
        "totalBatches": len(per_batch),
        "zeroFillBatches": zero_fill,
        "perBatch": per_batch,
        "totals": {
            "fills": fills_total,
            "gaps": gaps_total,
            "agentGaps": sum(pb.get("agentGaps", 0) for pb in per_batch),
            "orchestratorGaps": sum(pb.get("orchestratorGaps", 0) for pb in per_batch),
            "na": na_total,
            "wallclockSecMax": round(wc_max, 2),
            "wallclockSecP95": round(wc_p95, 2),
            "toolCallSum": tool_sum,
        },
    }


def write_cycle_telemetry(cycle_date: str, telemetry: dict) -> Path:
    """Write `data/_telemetry/<cycle_date>.json`. Idempotent on rerun
    (overwrites existing file for the same date). Returns the path."""
    out_dir = PROJECT / "data" / "_telemetry"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{cycle_date}.json"
    out_path.write_text(
        json.dumps(telemetry, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out_path


def record_write_skip(batch_id: str, cycle_date: str) -> Path:
    """FAZ 8.A (2026-05-18): track agents that returned status without Write.

    Appends to `data/_telemetry/<cycle_date>.json` under `writeSkips: [...]`.
    Each entry is a dict: {batchId, recordedAt}. Idempotent — duplicate
    (batch_id, cycle_date) tuples are deduplicated in-place.

    The orchestrator's Step 5 write-skip guard calls this BEFORE dispatching
    a recovery sonnet, so the telemetry reflects EVERY contract violation
    (including ones successfully recovered). Cycle-over-cycle trend
    indicates whether the agent's HARD RULE 11 is being internalized.
    """
    out_dir = PROJECT / "data" / "_telemetry"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{cycle_date}.json"
    if out_path.is_file():
        try:
            existing = json.loads(out_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = {}
    else:
        existing = {}
    if not isinstance(existing, dict):
        existing = {}
    skips = existing.setdefault("writeSkips", [])
    if not isinstance(skips, list):
        skips = []
        existing["writeSkips"] = skips
    # Idempotent: skip duplicates.
    if not any(isinstance(e, dict) and e.get("batchId") == batch_id for e in skips):
        skips.append({"batchId": batch_id, "recordedAt": _utc_iso()})
    out_path.write_text(
        json.dumps(existing, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return out_path


def metadata_changelog_row(meta: dict) -> str:
    """Compact one-line metadata for the CHANGELOG entry header."""
    fr = meta.get("fillRatio", 0.0) or 0.0
    elapsed = meta.get("lastCycleElapsedMs") or 0
    elapsed_min = round(elapsed / 60000.0, 1) if isinstance(elapsed, int) else "?"
    parts = [
        f"fillRatio:{fr:.2f}",
        f"cells:{meta.get('filledCells', '?')}/{meta.get('totalCells', '?')}",
        f"contradictions:{meta.get('contradictionsResolved', '?')}",
        f"fetch:{elapsed_min}min",
        f"tools:{meta.get('lastCycleToolCallCount', '?')}",
        f"batches:{meta.get('lastCycleBatchCount', '?')}",
        f"build:{meta.get('buildSha', '?')}",
    ]
    return "[" + " ".join(parts) + "]"
