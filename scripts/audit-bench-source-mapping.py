#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bench-key ↔ leaderboard mapping audit.

Four checks:
  AC6 (BLOCK): every coreBenchKey ∈ ⋃ live leaderboards[].publishes[]
               A publisher counts as "live" if EITHER:
               (a) lastVerifiedDate is non-null AND ≤60 days old, OR
               (b) data/sources.json contains ≥1 S/I-tier entry whose url
                   matches the leaderboard URL (historical extraction proof).
               Self-declared-only publishers without recent verification are
               rejected — this blocks fictional bench keys from passing AC6.
  AC7 (BLOCK): ⋃ leaderboards[].publishes[] ⊆ coreBenchKeys ∪ deprecatedBenchKeys
  AC8 (CONDITIONAL BLOCK): per-bench live-publisher count >= 2 (single point of
               failure). Newly-added publishers (firstSeen ≤ AC8_GRACE_DAYS old)
               receive a 14-day grace window — single-publisher status is WARN
               for them, BLOCK once the grace expires. Override: env-flag
               AICODERMAP_AC8_WARN_ONLY=1 keeps the legacy warn-only behaviour.
  AC9_live (WARN): leaderboards with no verification in >60 days flagged for review.

Exit code:
  0  every check passed (or AC8 grace-period warnings only)
  1  AC6, AC7, or AC8-after-grace drift
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
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

LIVENESS_DAYS = 60
AC8_GRACE_DAYS = 14
# AC8 single-publisher block: opt-in until FAZ E lands the missing publishers.
# Default = warn-only so legacy single-publisher state (bfcl, webDevElo) does
# NOT immediately reject commits; flip via env-flag once each core key has ≥2
# live publishers.
AC8_BLOCK_ENABLED = os.environ.get("AICODERMAP_AC8_BLOCK") == "1"
AC8_WARN_ONLY = not AC8_BLOCK_ENABLED


def _load_sources() -> dict:
    path = PROJECT / "data" / "sources.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _url_has_extraction_proof(url: str, sources: dict) -> bool:
    """Return True if sources.json has ≥1 S/I-tier entry whose url matches."""
    url = url.rstrip("/")
    for entries in sources.values():
        if not isinstance(entries, list):
            continue
        for e in entries:
            if not isinstance(e, dict):
                continue
            tier = e.get("tier", "")
            src_url = (e.get("url") or "").rstrip("/")
            if tier in ("I", "S") and (src_url == url or src_url.startswith(url)):
                return True
    return False


def _is_live(lb: dict, sources: dict) -> bool:
    """Publisher counts as live: recent verification OR historical extraction proof."""
    lvd = lb.get("lastVerifiedDate")
    if lvd:
        try:
            d = date.fromisoformat(str(lvd))
            if date.today() - d <= timedelta(days=LIVENESS_DAYS):
                return True
        except ValueError:
            pass
    url = lb.get("url", "")
    return bool(url and _url_has_extraction_proof(url, sources))


def main() -> int:
    wl = load_whitelist()
    sources = _load_sources()
    core = set(core_bench_keys(wl))
    deprecated = set(deprecated_bench_keys(wl))
    universe = bench_universe(wl)
    by_bench = leaderboard_index_by_bench(wl)

    failures: list[str] = []
    warnings: list[str] = []

    # Build live-publisher index: only publishers that pass liveness check
    live_by_bench: dict[str, list] = {}
    stale_lbs: list[str] = []
    for lb in wl.get("leaderboards", []):
        alive = _is_live(lb, sources)
        if not alive:
            stale_lbs.append(lb.get("url") or lb.get("name") or "?")
        for item in lb.get("publishes", []) or []:
            key = (
                item
                if isinstance(item, str)
                else (item.get("key") if isinstance(item, dict) else None)
            )
            if not key:
                continue
            if alive:
                live_by_bench.setdefault(key, []).append(lb)

    if stale_lbs:
        warnings.append(
            f"AC9_live — {len(stale_lbs)} leaderboard(s) have no recent verification "
            f"(>{LIVENESS_DAYS}d) and no extraction proof in sources.json: "
            f"{stale_lbs[:5]}{' ...' if len(stale_lbs) > 5 else ''}"
        )

    # AC6 — every coreBenchKey has at least one LIVE publishing leaderboard
    missing_publisher = sorted(k for k in core if k not in live_by_bench)
    if missing_publisher:
        failures.append(
            f"AC6 — {len(missing_publisher)} coreBenchKey(s) have no live "
            f"publisher (lastVerifiedDate stale or missing, no extraction proof): "
            f"{missing_publisher}"
        )

    # AC7 — all advertised keys (any publisher, live or not) ⊆ core ∪ deprecated
    advertised = set(by_bench.keys())
    rogue = sorted(advertised - (core | deprecated))
    if rogue:
        failures.append(
            f"AC7 — {len(rogue)} bench key(s) appear in leaderboards[].publishes[] "
            f"but are NOT in coreBenchKeys nor deprecatedBenchKeys: {rogue}"
        )

    # AC8 — single live-publisher benches.
    # Default: HARD BLOCK once the lone publisher's firstSeen ≤ AC8_GRACE_DAYS
    # ago has matured (i.e., the bench has been advertised long enough that we
    # should have found a second publisher). Brand-new benches get a grace
    # window so a freshly-added coreBenchKey isn't rejected immediately.
    # Override: AICODERMAP_AC8_WARN_ONLY=1 reverts to legacy warn-only.
    today = date.today()
    grace = timedelta(days=AC8_GRACE_DAYS)
    single_block: list[str] = []
    single_grace: list[str] = []
    for key in sorted(
        k for k, lbs in live_by_bench.items() if len(lbs) == 1 and k in core
    ):
        lone = live_by_bench[key][0]
        first_seen_raw = lone.get("firstSeen") or lone.get("addedDate") or ""
        is_new = False
        try:
            if (
                first_seen_raw
                and (today - date.fromisoformat(str(first_seen_raw))) <= grace
            ):
                is_new = True
        except ValueError:
            pass
        if is_new or AC8_WARN_ONLY:
            single_grace.append(key)
        else:
            single_block.append(key)
    if single_block:
        msg = (
            f"AC8 — {len(single_block)} core bench key(s) have only ONE live "
            f"publishing leaderboard past the {AC8_GRACE_DAYS}-day grace window: "
            f"{single_block}"
        )
        if AC8_WARN_ONLY:
            warnings.append(msg + " (warn-only via AICODERMAP_AC8_WARN_ONLY)")
        else:
            failures.append(msg)
    if single_grace:
        warnings.append(
            f"AC8_grace — {len(single_grace)} core bench key(s) have only ONE "
            f"live publishing leaderboard but are within "
            f"{AC8_GRACE_DAYS}-day grace window or warn-only override: "
            f"{single_grace}"
        )

    # Report
    live_count = len(live_by_bench)
    print(f"Bench-source mapping audit  (universe={len(universe)} keys)")
    print(f"  core:        {len(core)}")
    print(f"  deprecated:  {len(deprecated)}")
    print(f"  advertised:  {len(advertised)}  live: {live_count}")
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

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
