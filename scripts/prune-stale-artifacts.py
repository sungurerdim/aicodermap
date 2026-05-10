"""Stale-artifact prune (PRELIM-C, 2026-05-10).

Runs at the start of every refresh-all cycle. Renames prior-cycle gather
artifacts and the synth output to `.stale-<epoch>` so dispatched agents
cannot reuse them as cached output. Defends against the
"agent reused prior cycle's gather output without writing" failure mode
observed 2026-05-10 (synth file mtime predated cycle start by 4h).

Files matched (project root):
  .aicodermap-agent-out-batch*.gather.json
  .aicodermap-agent-out-batch*-gather.json   (hyphen variant agents emit)
  .aicodermap-agent-out-synth.json
  .aicodermap-agent-out.json                  (FROM SYNTH — gen_unified_artifact rebuilds)

Renamed (not deleted) so previous cycle's data remains recoverable for
audit/forensics within the same working tree. Renames are gitignored.

Usage:
  python scripts/prune-stale-artifacts.py                # rename anything older than now
  python scripts/prune-stale-artifacts.py --dry-run      # report only
  python scripts/prune-stale-artifacts.py --max-age 300  # rename older than 300s

Exit 0 always (non-fatal). Prints summary to stdout.
"""

from __future__ import annotations

import argparse
import glob
import sys
import time
from pathlib import Path

PATTERNS = [
    ".aicodermap-agent-out-batch*.gather.json",
    ".aicodermap-agent-out-batch*-gather.json",
    ".aicodermap-agent-out-synth.json",
    ".aicodermap-agent-out.json",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--max-age",
        type=int,
        default=0,
        help="Only rename files older than this many seconds (default 0 = always).",
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

    renamed = 0
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
        target = p.with_name(f"{p.name}.stale-{epoch_tag}")
        if args.dry_run:
            print(f"  - rename {p.name} -> {target.name}")
        else:
            try:
                p.rename(target)
                print(f"  - rename {p.name} -> {target.name}")
            except OSError as e:
                print(f"  ! failed {p.name}: {e}")
                continue
        renamed += 1

    print(f"=== PRUNE === renamed: {renamed}  kept: {skipped}  dry_run: {args.dry_run}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    raise SystemExit(main())
