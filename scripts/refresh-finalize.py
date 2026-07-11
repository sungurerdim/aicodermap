"""Refresh-cycle finalizer (FAZ 7.E, 2026-05-10).

Combines three previously-separate process spawns into ONE pass:
  1. gen_unified_artifact — picks best source (synth artifact preferred,
     gather union as fallback) and writes `.aicodermap-agent-out.json`.
  2. scripts/gap_gen.py — supplements unfilled cells with auto-gap entries
     so merge.py's MX1 invariant (filled+gaps+na == totalCells) holds.
  3. merge.py — atomic write to data/{models,sources}.json + audit.

Token impact: 3 process spawns + 3 file load+writes → 1 + 1 + 1. The
underlying scripts are already idempotent; this wrapper just chains them
without spawning a separate Python interpreter for each.

Quality preserved: each step's logic is unchanged. The only behavior
difference is "merge fails → return non-zero" (same as today's pipeline,
but surfaced through a single exit code).

Stdlib + sys.path-resolved imports.
"""

from __future__ import annotations

import argparse
import runpy
import subprocess
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
SCRIPTS = PROJECT / "scripts"
sys.path.insert(0, str(SCRIPTS))
from lib.constants import SINGLE_ARTIFACT_PATH  # noqa: E402
from lib.util import configure_utf8_output  # noqa: E402


def _run_script(path: Path, *, name: str) -> int:
    """Execute a Python script in-process via runpy. Captures sys.exit() codes."""
    print(f"\n=== {name} ===", flush=True)
    started = time.time()
    try:
        runpy.run_path(str(path), run_name="__main__")
        rc = 0
    except SystemExit as e:
        rc = int(e.code) if isinstance(e.code, int) else (1 if e.code else 0)
    except Exception as exc:  # noqa: BLE001
        print(f"  ! {name} raised: {exc}", flush=True)
        rc = 1
    elapsed = time.time() - started
    print(f"  {name} exit={rc} elapsed={elapsed:.1f}s", flush=True)
    return rc


def _run_subprocess(cmd: list[str], *, name: str) -> int:
    """Fallback: spawn a subprocess (used when the underlying script can't
    be safely re-imported in-process — e.g., merge.py mutates global state)."""
    print(f"\n=== {name} ===", flush=True)
    started = time.time()
    rc = subprocess.run(cmd, cwd=PROJECT).returncode
    elapsed = time.time() - started
    print(f"  {name} exit={rc} elapsed={elapsed:.1f}s", flush=True)
    return rc


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh-cycle finalizer.")
    parser.add_argument(
        "--skip-gen-unified",
        action="store_true",
        help="Skip gen_unified_artifact step (use when artifact already current).",
    )
    parser.add_argument(
        "--skip-gap-gen",
        action="store_true",
        help="Skip gap-gen supplement (rare; merge will fail MX1 invariant).",
    )
    parser.add_argument(
        "--skip-merge",
        action="store_true",
        help="Skip merge.py (dry-run mode — preview artifact without writing).",
    )
    parser.add_argument(
        "--in-process",
        action="store_true",
        help="Run scripts in-process via runpy (faster but shares globals; "
        "default is subprocess for isolation).",
    )
    args = parser.parse_args()

    runner = (
        _run_script
        if args.in_process
        else (lambda p, *, name: _run_subprocess([sys.executable, str(p)], name=name))
    )

    rc_total = 0

    # 1. gen_unified_artifact.py
    if not args.skip_gen_unified:
        rc = runner(SCRIPTS / "gen_unified_artifact.py", name="gen_unified_artifact")
        if rc != 0:
            print("  ✗ gen_unified failed; aborting finalize", flush=True)
            return rc
        rc_total |= rc

    # 1b. validate-artifact-keys.py — pre-merge guard: reject non-canonical
    # bench keys in the unified artifact BEFORE merge.py's MX4 audit would
    # roll back the entire write (cycle 2026-05-18 data-loss mode).
    if not args.skip_gen_unified:
        rc = _run_subprocess(
            [
                sys.executable,
                str(SCRIPTS / "validate-artifact-keys.py"),
                str(PROJECT / SINGLE_ARTIFACT_PATH),
            ],
            name="validate-artifact-keys",
        )
        if rc != 0:
            print("  ✗ validate-artifact-keys failed; aborting finalize", flush=True)
            return rc
        rc_total |= rc

    # 2. scripts/gap_gen.py (F1.3: moved from project root to scripts/)
    if not args.skip_gap_gen:
        gapgen = SCRIPTS / "gap_gen.py"
        if gapgen.is_file():
            rc = runner(gapgen, name="gap-gen")
            if rc != 0:
                print(
                    "  ⚠ gap-gen exit non-zero — continuing to merge "
                    "(merge.py will fail MX1 if cells unaccounted)",
                    flush=True,
                )
            rc_total |= rc
        else:
            print("\n=== gap-gen ===", flush=True)
            print("  ! gap-gen script missing at scripts/gap_gen.py; skipping", flush=True)

    # 3. merge.py
    if not args.skip_merge:
        rc = runner(SCRIPTS / "merge.py", name="merge")
        if rc != 0:
            print("  ✗ merge failed", flush=True)
            return rc
        rc_total |= rc

        # 4. add-new-lineup-stubs.py — SAFETY-NET pass of the new-model admission
        # step (c930089, 2026-06-27 lineup-first ordering). The PRIMARY admission
        # already ran PRE-GATHER in Step 0, so a model discovered there is already
        # in data/models.json and had its benches filled by Stage A this run. This
        # post-merge call only catches a model first sighted mid-gather (idempotent
        # — ids already admitted pre-gather are skipped); such a model's bench
        # cells start null and fill next refresh. Non-fatal — a stub-add failure
        # must never undo a good merge.
        rc_stub = runner(SCRIPTS / "add-new-lineup-stubs.py", name="add-new-stubs")
        if rc_stub != 0:
            print(
                "  ⚠ add-new-stubs exit non-zero — continuing (merge already wrote "
                "data; new-model admission retries next cycle)",
                flush=True,
            )

        # 5. reconcile-stored-winners.py — enforce the SSOT invariant
        # `stored == pick_winner(full sources.json provenance)` for every cell.
        # merge only recomputes a cell's winner when THIS cycle produced fresh
        # observations; a confirmed/skip cell is otherwise frozen and can hold a
        # stale single-source minority value even as a multi-source consensus
        # accumulates (deepseek-v4-pro.lcb 85.9 vs 22 sources @ 93.5, 2026-07-02).
        # This deterministic no-fetch pass re-derives every stored scalar from the
        # ALWAYS-RETAINED provenance pool each run — records are kept forever, the
        # computation is dynamic over all data. AA-definitional indices are skipped
        # (apply-aa-authoritative owns them). Non-fatal — a reconcile failure must
        # never undo a good merge; its own coherence guard rolls back on drift.
        rc_rec = _run_subprocess(
            [sys.executable, str(SCRIPTS / "reconcile-stored-winners.py"), "--apply"],
            name="reconcile-winners",
        )
        if rc_rec != 0:
            print(
                "  ⚠ reconcile-winners exit non-zero — continuing (merge already "
                "wrote coherent data; invariant re-enforced next cycle)",
                flush=True,
            )

        # 6. check-new-model-coverage.py (Fable-5 R5, 2026-07-11) — loud warning
        # when a model admitted THIS cycle (either admission pass, step 4 above
        # or the pre-gather primary pass) still sits below the coverage floor
        # after Stage A/B + merge. New models are the likeliest 0-fills
        # (leaderboards/AA lag a launch); this distinguishes "expected, still
        # early" from a silent pipeline miss. Non-fatal, advisory-only.
        rc_cov = _run_subprocess(
            [sys.executable, str(SCRIPTS / "check-new-model-coverage.py")],
            name="new-model-coverage",
        )
        if rc_cov != 0:
            print(
                "  ⚠ new-model-coverage-check exit non-zero — continuing "
                "(advisory only, does not affect written data)",
                flush=True,
            )

    print(f"\n=== FINALIZE OK === total exit={rc_total}", flush=True)
    return rc_total


if __name__ == "__main__":
    configure_utf8_output()
    raise SystemExit(main())
