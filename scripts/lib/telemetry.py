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
