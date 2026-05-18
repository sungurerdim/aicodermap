"""Write per-batch idea_context JSON files for skill orchestrator dispatch.

Reads dispatch plan, builds slim per-batch ctx via lib.idea_context.build_per_batch_ctx,
writes one .aicodermap-ctx-<batchId>.json per batch.

Stdlib-only. Idempotent. Run once per cycle just before Stage A dispatch.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.dispatch import compute_dispatch_plan
from lib.freshness import compute_skip_cells
from lib.idea_context import build_per_batch_ctx
from lib.matrix import active_models, matrix_snapshot, priority_cells
from lib.whitelist import (
    banned_fetch_patterns,
    contracts,
    core_bench_keys,
)


def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def main() -> int:
    models = _read_json(REPO / "data" / "models.json", [])
    wl = _read_json(REPO / "data" / "sources-whitelist.json", {})
    vmap = _read_json(REPO / ".aicodermap-verification-map.json", {"cells": {}})
    snap_index = _read_json(
        REPO / "data" / ".leaderboard-snapshots" / "_index.json", {}
    )
    snapshots = snap_index.get("byUrl") or {}

    ctr = contracts(wl)
    keys = core_bench_keys(wl)
    active = active_models(models)
    today = date.today()

    ms = matrix_snapshot(active, keys)
    pc = priority_cells(
        active,
        keys,
        limit=200,
        verification_map=vmap,
        skip_confirmed_within_days=ctr.get("FRESHNESS_TTL_DAYS", 7),
    )
    sk = compute_skip_cells(
        vmap,
        today,
        [m["id"] for m in active],
        keys,
        ttl_days=ctr.get("FRESHNESS_TTL_DAYS", 7),
        min_verifs=ctr.get("MIN_VERIFICATIONS_FOR_SKIP", 3),
    )
    bp = banned_fetch_patterns(wl)

    plan = compute_dispatch_plan(active, keys)
    cycle_started = time.time()

    last_refresh = ""
    for m in models:
        lu = m.get("lastUpdated", "")
        if lu and lu > last_refresh:
            last_refresh = lu

    current_ids = [m["id"] for m in models]
    written = 0
    for batch in plan["batches"]:
        ctx = build_per_batch_ctx(
            batch_spec=batch,
            full_whitelist=wl,
            matrix_state=ms,
            priority_cells=pc,
            skip_cells=sk,
            verification_map=vmap,
            leaderboard_snapshots=snapshots,
            contracts=ctr,
            banned_fetch_patterns=bp,
            cycle_started_unix=cycle_started,
            total_models=len(models),
            last_refresh=last_refresh,
            current_ids=current_ids,
            bench_keys=keys,
        )
        out_path = REPO / f".aicodermap-ctx-{batch['batchId']}.json"
        out_path.write_text(json.dumps(ctx, ensure_ascii=False), encoding="utf-8")
        size_kb = out_path.stat().st_size / 1024
        print(
            f"  [ok] {batch['batchId']:40s} wave={batch['waveIndex']} "
            f"models={len(batch['modelIds'])} ctx={size_kb:.1f}KB"
        )
        written += 1

    print(f"=== CTX === written: {written}  cycleStartedUnix: {cycle_started:.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
