"""Stale-artifact prune (PRELIM-C, F1.2 refactor).

Runs at the start of every refresh-all cycle. Renames prior-cycle gather
artifacts and the synth output to `.stale-<epoch>` so dispatched agents
cannot reuse them as cached output. Defends against the
"agent reused prior cycle's gather output without writing" failure mode
observed 2026-05-10 (synth file mtime predated cycle start by 4h).

Canonical artifact pattern (F1.2 — single pattern, no hyphen variant):
  .aicodermap-agent-out-<batchId>.gather.json
  .aicodermap-agent-out-synth.json
  .aicodermap-agent-out.json

Old hyphen-variant (.aicodermap-agent-out-batch*-gather.json) is still
matched for backwards compat with artifacts from pre-F1.2 cycles, but new
agents emit only the dot-extension form.

--gc-archive-older-than=N:
  Stale files older than N days are moved to .aicodermap-stale-archive/
  instead of staying in the project root (prevents unbounded root clutter).

Renamed (not deleted) so previous cycle's data remains recoverable.
Renames are gitignored.

Usage:
  python scripts/prune-stale-artifacts.py                        # rename anything older than now
  python scripts/prune-stale-artifacts.py --dry-run              # report only
  python scripts/prune-stale-artifacts.py --max-age 300          # rename older than 300s
  python scripts/prune-stale-artifacts.py --gc-archive-older-than 14  # archive >14d old stale

Exit 0 always (non-fatal). Prints summary to stdout.
"""

from __future__ import annotations

import argparse
import glob
import sys
import time
from pathlib import Path

# Canonical pattern first; hyphen variant kept for backwards-compat with pre-F1.2 artifacts.
PATTERNS = [
    ".aicodermap-agent-out-batch*.gather.json",
    ".aicodermap-agent-out-batch*-gather.json",  # pre-F1.2 compat only
    ".aicodermap-agent-out-synth.json",
    ".aicodermap-agent-out.json",
    # Per-batch idea_context files. The dispatch plan can split providers into a
    # DIFFERENT set of batchIds cycle-to-cycle (e.g. mistral 1×6 → 2×{6,2}); a
    # prior-cycle ctx whose batchId no longer exists in the fresh plan is never
    # overwritten and pollutes the fresh ctx glob with stale/duplicate model
    # assignments (observed 2026-06-06: 9 orphan ctx files collided with 16
    # fresh, duplicating deprecated-model slices). Prune them with the rest.
    ".aicodermap-ctx-batch*.json",
]

ARCHIVE_DIR_NAME = ".aicodermap-stale-archive"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--max-age",
        type=int,
        default=0,
        help="Only rename files older than this many seconds (default 0 = always).",
    )
    parser.add_argument(
        "--gc-archive-older-than",
        type=int,
        default=0,
        metavar="DAYS",
        help="Move stale files older than DAYS days to archive subdir (default 0 = disabled).",
    )
    args = parser.parse_args()

    project = Path(__file__).resolve().parent.parent
    now = time.time()
    epoch_tag = int(now)
    cutoff = now - args.max_age

    matches: list[Path] = []
    for pat in PATTERNS:
        matches.extend(Path(p) for p in glob.glob(str(project / pat)))

    seen = set()
    deduped: list[Path] = []
    for p in matches:
        if p in seen or not p.is_file():
            continue
        seen.add(p)
        deduped.append(p)

    archive_cutoff_sec = (
        args.gc_archive_older_than * 86400 if args.gc_archive_older_than > 0 else 0
    )
    archive_dir = project / ARCHIVE_DIR_NAME

    renamed = 0
    archived = 0
    skipped = 0
    for p in sorted(deduped):
        try:
            mtime = p.stat().st_mtime
        except OSError:
            continue
        if mtime > cutoff:
            skipped += 1
            print(f"  - keep   {p.name} (mtime within cutoff)")
            continue

        # Determine destination: archive subdir for very old stale files
        age_sec = now - mtime
        if archive_cutoff_sec > 0 and age_sec > archive_cutoff_sec:
            if not args.dry_run:
                archive_dir.mkdir(exist_ok=True)
            target = archive_dir / f"{p.name}.stale-{epoch_tag}"
            action = "archive"
        else:
            target = p.with_name(f"{p.name}.stale-{epoch_tag}")
            action = "rename"

        if args.dry_run:
            print(f"  - {action} {p.name} -> {target.name}")
        else:
            try:
                p.rename(target)
                print(f"  - {action} {p.name} -> {target.name}")
            except OSError as e:
                print(f"  ! failed {p.name}: {e}")
                continue
        if action == "archive":
            archived += 1
        else:
            renamed += 1

    print(
        f"=== PRUNE === renamed: {renamed}  archived: {archived}  "
        f"kept: {skipped}  dry_run: {args.dry_run}"
    )
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    raise SystemExit(main())
