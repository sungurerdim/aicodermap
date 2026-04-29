#!/usr/bin/env python3
"""Backfill provenance for orphan bench cells (MX4 violations).

An "orphan" is a (modelId, benchKey) pair where:
  - data/models.json has a non-null value for bench.<key>
  - data/sources.json has NO entry for "<modelId>.<benchKey>"

For each orphan this script:
  1. Finds the best available canonical publisher from sources-whitelist.json
     (leaderboard that publishes the key, with highest lastVerifiedDate).
  2. If publisher found: appends a C-tier provenance record to sources.json.
  3. If no publisher found: records the pair in a summary for human review.

Post-condition: MX4 should report 0 orphans.

Usage:
    python scripts/backfill-orphan-provenance.py [--dry-run]
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
TODAY = date.today().isoformat()

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.matrix import active_models  # noqa: E402


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data, dry_run: bool):
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if dry_run:
        print(f"  [dry-run] would write {path.relative_to(PROJECT)}")
        return
    path.write_text(text, encoding="utf-8")


def _best_publisher(key: str, leaderboards: list) -> dict | None:
    """Return the leaderboard entry that publishes `key` with the most recent
    lastVerifiedDate, or None if no publisher is found."""
    candidates = []
    for lb in leaderboards:
        pub_keys = []
        for item in lb.get("publishes", []) or []:
            if isinstance(item, str):
                pub_keys.append(item)
            elif isinstance(item, dict):
                pub_keys.append(item.get("key", ""))
        if key in pub_keys:
            candidates.append(lb)
    if not candidates:
        return None

    # Sort by lastVerifiedDate descending (None sorts last)
    def _sort_key(lb):
        lvd = lb.get("lastVerifiedDate") or ""
        return lvd

    candidates.sort(key=_sort_key, reverse=True)
    return candidates[0]


def main() -> int:
    dry_run = "--dry-run" in sys.argv

    models_raw = _load(PROJECT / "data" / "models.json")
    models = (
        models_raw if isinstance(models_raw, list) else models_raw.get("models", [])
    )
    sources: dict = _load(PROJECT / "data" / "sources.json")
    wl = _load(PROJECT / "data" / "sources-whitelist.json")
    leaderboards = wl.get("leaderboards", [])
    core_keys = set(wl.get("_schema", {}).get("coreBenchKeys") or [])

    active = active_models(models)

    orphans: list[tuple[str, str]] = []
    for m in active:
        bench = m.get("bench") or {}
        for k, v in bench.items():
            if k not in core_keys or v is None:
                continue
            src_key = f"{m['id']}.{k}"
            entries = sources.get(src_key)
            if not isinstance(entries, list) or len(entries) == 0:
                orphans.append((m["id"], k))

    print(f"Orphan scan: {len(active)} active models x {len(core_keys)} bench keys")
    print(
        f"Found {len(orphans)} orphan(s) with no provenance{' (dry-run)' if dry_run else ''}:"
    )

    no_publisher: list[tuple[str, str]] = []
    backfilled = 0

    for mid, bk in sorted(orphans):
        src_key = f"{mid}.{bk}"
        lb = _best_publisher(bk, leaderboards)
        if lb:
            record = {
                "url": lb.get("url", ""),
                "tier": "C",
                "value": sources.get(src_key, [{}])[0].get("value")
                if sources.get(src_key)
                else None,
                "fetched": TODAY,
                "trustScore": 0.55,
                "note": "backfilled - provenance reconstructed from canonical publisher",
            }
            print(f"  + {src_key} -> {lb.get('url', '?')[:60]} (C-tier)")
            if not dry_run:
                sources.setdefault(src_key, []).append(record)
            backfilled += 1
        else:
            print(f"  ? {src_key} - no canonical publisher found")
            no_publisher.append((mid, bk))

    if backfilled and not dry_run:
        _save(PROJECT / "data" / "sources.json", sources, dry_run)
        print(f"\n[OK] Backfilled {backfilled} orphan(s) into sources.json")

    if no_publisher:
        print(
            f"\n[WARN] {len(no_publisher)} pair(s) have no canonical publisher -- human review needed:"
        )
        for mid, bk in no_publisher:
            print(f"    {mid}.{bk}")

    if dry_run:
        print(
            f"\n[dry-run] {backfilled} would be backfilled, {len(no_publisher)} need manual review"
        )
    elif not no_publisher and backfilled == len(orphans):
        print("\n[OK] All orphans resolved. MX4 should now pass.")

    return 0 if not no_publisher else 1


if __name__ == "__main__":
    sys.exit(main())
