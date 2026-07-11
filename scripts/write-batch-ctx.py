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

from lib.dispatch import compute_dispatch_plan, slow_families_from_telemetry  # noqa: E402
from lib.freshness import compute_skip_cells  # noqa: E402
from lib.idea_context import build_per_batch_ctx  # noqa: E402
from lib.matrix import active_models, matrix_snapshot, priority_cells  # noqa: E402
from lib.constants import VERIFICATION_MAP_PATH  # noqa: E402
from lib.util import safe_json_load as _read_json  # noqa: E402
from lib.whitelist import (  # noqa: E402
    banned_fetch_patterns,
    contracts,
    core_bench_keys,
    required_bench_keys,
)


def main() -> int:
    models = _read_json(REPO / "data" / "models.json", [])
    wl = _read_json(REPO / "data" / "sources-whitelist.json", {})
    vmap = _read_json(REPO / VERIFICATION_MAP_PATH, {"cells": {}})
    snap_index = _read_json(REPO / "data" / ".leaderboard-snapshots" / "_index.json", {})
    # Index is written by prefetch-leaderboards.py under "snapshots" (NOT
    # "byUrl"). Reading the wrong key silently produced an EMPTY snapshot map in
    # every batch ctx, so agents WebFetched leaderboards they could have Read
    # from disk — defeating the entire PRELIM-B prefetch optimization.
    snapshots = snap_index.get("snapshots") or {}
    # Layer-3 anomaly verification queue (PRELIM-F). Sliced per batch below so
    # each agent resolves its flagged cells FIRST (agent.md OUTLIERS->INVESTIGATE).
    anomalies = (_read_json(REPO / "data" / "_anomalies.json", {}) or {}).get("anomalies") or []

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
        required_keys=required_bench_keys(wl),
    )
    sk = compute_skip_cells(vmap, today, [m["id"] for m in active], keys)
    bp = banned_fetch_patterns(wl)

    # #1 (2026-06-07) — shrink families that overran wallclock LAST cycle into
    # smaller, vendor-pure batches so the slowest batch no longer sets the whole
    # wave's wall-clock. Derived from telemetry (advisory; empty set = no change).
    slow_families = slow_families_from_telemetry(
        REPO / "data" / "_telemetry",
        batch_wallclock_sec=int(ctr.get("BATCH_WALLCLOCK_SEC", 600)),
    )
    if slow_families:
        print(f"  [dense-shrink] slow families from last cycle: {sorted(slow_families)}")
    plan = compute_dispatch_plan(active, keys, dense_families=slow_families)
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
        _bm = set(batch["modelIds"])
        ctx["anomalies"] = [a for a in anomalies if a.get("modelId") in _bm]
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
