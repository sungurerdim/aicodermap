#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Idempotent seed: ensure newly-promoted bench keys exist on every model.

FAZ 8.A (2026-05-18): 6 emerging keys (tbHard, cfElo, nl2Repo, aaCoding,
aaAgentic, arcAgi2) were promoted to coreBenchKeys. Frontend BENCH_KEYS
universe (26) already includes them, but `data/models.json` rows may not
carry the field yet — the render pass would then print N/A even when
gather artifacts have valid fills queued. This script walks every active
model and ensures `bench[<promoted_key>]` exists as `null` (when missing).

Hard contract: NEVER overwrite a non-null value. `setdefault` only.

Run once after Phase 2 commit. Re-runs are no-ops.

Usage:
    python scripts/seed-promoted-keys.py [--dry-run]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
MODELS_PATH = PROJECT / "data" / "models.json"

PROMOTED_KEYS = (
    "tbHard",
    "cfElo",
    "nl2Repo",
    "aaCoding",
    "aaAgentic",
    "arcAgi2",
)


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    text = MODELS_PATH.read_text(encoding="utf-8")
    obj = json.loads(text)
    models = obj.get("MODELS") if isinstance(obj, dict) else obj
    if not isinstance(models, list):
        print(
            f"ERROR: unexpected models.json shape: {type(models).__name__}",
            file=sys.stderr,
        )
        return 1

    seeded = 0
    touched_models = 0

    for m in models:
        if not isinstance(m, dict):
            continue
        bench = m.setdefault("bench", {})
        if not isinstance(bench, dict):
            continue
        added_here = 0
        for k in PROMOTED_KEYS:
            if k not in bench:
                bench[k] = None
                added_here += 1
        if added_here:
            seeded += added_here
            touched_models += 1

    if seeded == 0:
        print(
            f"no-op: all {len(models)} models already carry {len(PROMOTED_KEYS)} promoted keys"
        )
        return 0

    if dry_run:
        print(
            f"dry-run: would seed {seeded} null fields across {touched_models} models"
        )
        return 0

    # Preserve top-level structure (dict-wrap or bare list)
    if isinstance(obj, dict):
        obj["MODELS"] = models
        out = obj
    else:
        out = models
    MODELS_PATH.write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"seeded {seeded} null fields across {touched_models} models (promoted keys: {list(PROMOTED_KEYS)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
