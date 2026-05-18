#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rename artifact files whose batchId contains filename-unsafe characters.

Cycle 2026-05-18 dispatch produced batchIds like `batch10-z.ai_(zhipu_`
(parens, dots) — the orchestrator's per-batch artifact files then carry the
same unsafe characters, which broke `Path(out_path).exists()` checks and
caused shell-glob resolution failures on Windows.

FAZ 8.A renamed dispatch.py's `family_hint` regex to `[a-z0-9_-]`. This
script back-fills any existing files on disk to the same form, so a
post-fix `refresh-all` can locate prior artifacts.

Idempotent. `--dry-run` previews without writing.

Usage:
    python scripts/migrate-batchid-filenames.py [--dry-run]

Targets:
    .aicodermap-agent-out-*.json
    .aicodermap-agent-out-*.gather.json
    .aicodermap-agent-out-*.synth.json
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]

# Match the unsafe characters dispatch.py's old code allowed (`. (`).
# Old regex: .lower().replace(" ", "_") — left ., (, ), /, : intact.
# New regex: [^a-z0-9_-] → "_".
UNSAFE_RE = re.compile(r"[^a-z0-9_-]")

# Glob patterns for orchestrator artifacts that embed batchId in filename.
GLOBS = (
    ".aicodermap-agent-out-*.json",
    ".aicodermap-agent-out-*.gather.json",
    ".aicodermap-agent-out-*.synth.json",
)


def sanitize(name: str) -> str:
    """Apply the FAZ 8.A regex to the batchId slice of a filename.

    Example:
      .aicodermap-agent-out-batch10-z.ai_(zhipu_.json
      → .aicodermap-agent-out-batch10-z_ai__zhipu_.json
    """
    prefix = ".aicodermap-agent-out-"
    if not name.startswith(prefix):
        return name
    # Split off the trailing `.json` (or `.gather.json` / `.synth.json`).
    # Anything between prefix and the FIRST `.json` token is the batchId.
    body = name[len(prefix) :]
    # Find suffix: longest matching ".synth.json" / ".gather.json" / ".json"
    for suf in (".gather.json", ".synth.json", ".json"):
        if body.endswith(suf):
            batch_id = body[: -len(suf)]
            new_batch = UNSAFE_RE.sub("_", batch_id.lower())
            return f"{prefix}{new_batch}{suf}"
    return name


def collect_targets(root: Path) -> list[tuple[Path, Path]]:
    seen: set[Path] = set()
    pairs: list[tuple[Path, Path]] = []
    for pattern in GLOBS:
        for p in root.glob(pattern):
            if p in seen:
                continue
            seen.add(p)
            new_name = sanitize(p.name)
            if new_name == p.name:
                continue
            pairs.append((p, p.with_name(new_name)))
    return pairs


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    pairs = collect_targets(PROJECT)
    if not pairs:
        print("no unsafe batchId filenames found — nothing to do")
        return 0

    for src, dst in pairs:
        verb = "would rename" if dry_run else "renamed"
        action = "->"
        print(f"{verb}: {src.name} {action} {dst.name}")
        if dry_run:
            continue
        if dst.exists():
            print(f"  WARN: target exists, skipping ({dst.name})", file=sys.stderr)
            continue
        src.rename(dst)

    summary = (
        f"{'dry-run: ' if dry_run else ''}{len(pairs)} file(s) "
        f"{'would be' if dry_run else ''} renamed"
    )
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
