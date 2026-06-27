"""Refresh-cycle finalizer (FAZ 7.E, 2026-05-10).

Combines three previously-separate process spawns into ONE pass:
  1. gen_unified_artifact — picks best source (synth artifact preferred,
     gather union as fallback) and writes `.aicodermap-agent-out.json`.
  2. .aicodermap-gap-gen — supplements unfilled cells with auto-gap entries
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

    # 2. scripts/gap_gen.py (F1.3: moved from project root to scripts/)
    if not args.skip_gap_gen:
        # Canonical path (F1.3); backwards-compat fallback to old root location.
        gapgen = SCRIPTS / "gap_gen.py"
        if not gapgen.is_file():
            gapgen = PROJECT / ".aicodermap-gap-gen.py"
            if gapgen.is_file():
                print(
                    "\n=== gap-gen === ⚠ using legacy root path (.aicodermap-gap-gen.py); "
                    "update to scripts/gap_gen.py",
                    flush=True,
                )
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
            print(
                "  ! gap-gen script missing at scripts/gap_gen.py; skipping", flush=True
            )

    # 3. merge.py
    if not args.skip_merge:
        rc = runner(SCRIPTS / "merge.py", name="merge")
        if rc != 0:
            print("  ✗ merge failed", flush=True)
            return rc
        rc_total |= rc

        # 4. add-new-lineup-stubs.py — the SINGLE SSOT new-model admission step.
        # Runs AFTER merge (this is the only place it runs every full cycle): it
        # scans THIS cycle's gather/synth/agent-out artifacts in-memory, gates
        # each candidate, and writes schema-complete stubs into data/models.json
        # + i18n. Bench cells start null and fill next refresh. Non-fatal — a
        # stub-add failure must never undo a good merge.
        rc_stub = runner(SCRIPTS / "add-new-lineup-stubs.py", name="add-new-stubs")
        if rc_stub != 0:
            print(
                "  ⚠ add-new-stubs exit non-zero — continuing (merge already wrote "
                "data; new-model admission retries next cycle)",
                flush=True,
            )

    print(f"\n=== FINALIZE OK === total exit={rc_total}", flush=True)
    return rc_total


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    raise SystemExit(main())
