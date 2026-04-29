#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bench-key ↔ leaderboard mapping audit (P2 reform).

Three checks:
  AC6 (BLOCK): every coreBenchKey ∈ ⋃ leaderboards[].publishes[]
               i.e., every bench we track is published by at least one
               whitelisted leaderboard. A bench with no publisher has
               no sourcing path — coverage will be 0 forever.
  AC7 (BLOCK): ⋃ leaderboards[].publishes[] ⊆ coreBenchKeys ∪ deprecatedBenchKeys
               i.e., a leaderboard cannot advertise a bench key that the
               canonical universe does not recognize. Catches reverse drift.
  AC8 (WARN):  per-bench publisher count >= 2.
               Single-publisher benches are flagged for human awareness so
               the fallback chain (aggregator mirrors / WebSearch) can be
               beefed up before the publisher goes down.

Used as a CI-style gate by:
  - scripts/merge.py post-write step (advisory log; HARD BLOCK after W2 activation)
  - scripts/hooks/pre-commit (HARD BLOCK after W2 activation)
  - manual `python scripts/audit-bench-source-mapping.py`

Exit code:
  0  every check passed
  1  AC6 or AC7 drift
  (AC8 is WARN-only — never returns non-zero)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow `from lib.whitelist import ...` when invoked from any cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.whitelist import (  # noqa: E402
    bench_universe,
    core_bench_keys,
    deprecated_bench_keys,
    leaderboard_index_by_bench,
    load_whitelist,
)

for _stream in (sys.stdout, sys.stderr):
    _reconf = getattr(_stream, "reconfigure", None)
    if callable(_reconf):
        try:
            _reconf(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


def main() -> int:
    wl = load_whitelist()
    core = set(core_bench_keys(wl))
    deprecated = set(deprecated_bench_keys(wl))
    universe = bench_universe(wl)
    by_bench = leaderboard_index_by_bench(wl)

    failures: list[str] = []
    warnings: list[str] = []

    # AC6 — every coreBenchKey has at least one publishing leaderboard
    missing_publisher = sorted(k for k in core if k not in by_bench)
    if missing_publisher:
        failures.append(
            f"AC6 — {len(missing_publisher)} coreBenchKey(s) have no whitelisted "
            f"publisher (no leaderboards[].publishes[] mention them): "
            f"{missing_publisher}"
        )

    # AC7 — leaderboard-advertised keys ⊆ core ∪ deprecated
    advertised = set(by_bench.keys())
    rogue = sorted(advertised - (core | deprecated))
    if rogue:
        failures.append(
            f"AC7 — {len(rogue)} bench key(s) appear in leaderboards[].publishes[] "
            f"but are NOT in coreBenchKeys nor deprecatedBenchKeys: {rogue}"
        )

    # AC8 — single-publisher benches (WARN)
    single = sorted(k for k, lbs in by_bench.items() if len(lbs) == 1 and k in core)
    if single:
        warnings.append(
            f"AC8 — {len(single)} core bench key(s) have only ONE publishing "
            f"leaderboard (single point of failure): {single}"
        )

    # Report
    print(f"Bench-source mapping audit  (universe={len(universe)} keys)")
    print(f"  core:        {len(core)}")
    print(f"  deprecated:  {len(deprecated)}")
    print(f"  advertised:  {len(advertised)}")
    if not failures and not warnings:
        print("  ✓ FULL MAPPING — every coreBenchKey has ≥2 publishers")
        return 0
    if failures:
        print(f"\n  ✗ FAIL ({len(failures)} drift signal(s)):")
        for f in failures:
            print(f"    - {f}", file=sys.stderr)
    if warnings:
        print(f"\n  ⚠ WARN ({len(warnings)}):")
        for w in warnings:
            print(f"    - {w}")

    # WARN-only mode for migration phase
    warn_only = os.environ.get("AICODERMAP_BENCH_SOURCE_WARN_ONLY") == "1"
    if warn_only and failures:
        print(
            "\n  (warn-only: AICODERMAP_BENCH_SOURCE_WARN_ONLY=1 set — "
            "exit 0 despite failures; W2 activation will remove this flag)",
            file=sys.stderr,
        )
        return 0
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
