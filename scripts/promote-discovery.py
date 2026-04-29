#!/usr/bin/env python3
"""Promote accepted discovery candidates into sources-whitelist.json.

Reads data/discoveries.json, shows pending items interactively, and writes
accepted entries to the appropriate whitelist section.

Usage:
    python scripts/promote-discovery.py [--type vendors|benchmarks|leaderboards]
    python scripts/promote-discovery.py --accept <id> [--type vendors]
    python scripts/promote-discovery.py --reject <id> [--type vendors]
    python scripts/promote-discovery.py --list
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
DISCOVERIES_PATH = PROJECT / "data" / "discoveries.json"
WHITELIST_PATH = PROJECT / "data" / "sources-whitelist.json"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data):
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _list_pending(discoveries: dict):
    total = 0
    for kind in ("vendors", "benchmarks", "leaderboards"):
        pending = [e for e in discoveries.get(kind, []) if e.get("status") == "pending"]
        if pending:
            print(f"\n{kind.upper()} ({len(pending)} pending):")
            for e in pending:
                eid = e.get("id") or e.get("key") or e.get("url") or "?"
                print(
                    f"  [{eid}]  {json.dumps({k: v for k, v in e.items() if k != 'status'})}"
                )
            total += len(pending)
    if not total:
        print("No pending discovery candidates.")


def _set_status(discoveries: dict, kind: str, eid: str, status: str) -> bool:
    for e in discoveries.get(kind, []):
        cand_id = e.get("id") or e.get("key") or e.get("url") or ""
        if cand_id == eid:
            e["status"] = status
            return True
    return False


def _promote_vendor(entry: dict, whitelist: dict):
    vendors = whitelist.get("vendors", {})
    vid = entry.get("id", "")
    if vid and vid not in vendors:
        vendors[vid] = {
            "tier": entry.get("suggestedTier", "S"),
            "urls": {},
            "_note": f"promoted from discovery queue {entry.get('observedAt', '?')}",
        }
        whitelist["vendors"] = vendors
        print(f"  + Added vendor '{vid}' to whitelist (tier={vendors[vid]['tier']})")


def _promote_leaderboard(entry: dict, whitelist: dict):
    url = entry.get("url") or ""
    if not url:
        print("  ✗ leaderboard entry has no url — skipping")
        return
    lbs = whitelist.get("leaderboards", [])
    if any(lb.get("url") == url for lb in lbs):
        print(f"  ~ leaderboard {url} already in whitelist")
        return
    lbs.append(
        {
            "url": url,
            "tier": "I",
            "publishes": entry.get("suggestedKeys", []),
            "lastVerifiedDate": None,
            "_note": f"promoted from discovery queue",
        }
    )
    whitelist["leaderboards"] = lbs
    print(f"  + Added leaderboard {url}")


def main() -> int:
    args = sys.argv[1:]

    if not DISCOVERIES_PATH.exists():
        print("discoveries.json not found — nothing to promote.")
        return 0

    discoveries = _load(DISCOVERIES_PATH)

    if "--list" in args or not args:
        _list_pending(discoveries)
        return 0

    kind_arg = None
    if "--type" in args:
        idx = args.index("--type")
        kind_arg = args[idx + 1] if idx + 1 < len(args) else None

    if "--accept" in args:
        idx = args.index("--accept")
        eid = args[idx + 1] if idx + 1 < len(args) else None
        if not eid:
            print("--accept requires an id", file=sys.stderr)
            return 2
        kind = kind_arg or "vendors"
        if not _set_status(discoveries, kind, eid, "accepted"):
            print(f"  ✗ '{eid}' not found in {kind}", file=sys.stderr)
            return 1
        _save(DISCOVERIES_PATH, discoveries)

        # Write to whitelist
        whitelist = _load(WHITELIST_PATH)
        entry = next(
            (
                e
                for e in discoveries.get(kind, [])
                if (e.get("id") or e.get("key") or e.get("url")) == eid
            ),
            {},
        )
        if kind == "vendors":
            _promote_vendor(entry, whitelist)
        elif kind == "leaderboards":
            _promote_leaderboard(entry, whitelist)
        else:
            print(
                f"  ⚠ '{kind}' promotion not yet automated — update whitelist manually"
            )
        _save(WHITELIST_PATH, whitelist)
        print(f"✓ Accepted '{eid}' from {kind}.")
        return 0

    if "--reject" in args:
        idx = args.index("--reject")
        eid = args[idx + 1] if idx + 1 < len(args) else None
        if not eid:
            print("--reject requires an id", file=sys.stderr)
            return 2
        kind = kind_arg or "vendors"
        if not _set_status(discoveries, kind, eid, "rejected"):
            print(f"  ✗ '{eid}' not found in {kind}", file=sys.stderr)
            return 1
        _save(DISCOVERIES_PATH, discoveries)
        print(f"✓ Rejected '{eid}' from {kind}.")
        return 0

    _list_pending(discoveries)
    return 0


if __name__ == "__main__":
    sys.exit(main())
