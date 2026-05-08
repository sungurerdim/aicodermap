#!/usr/bin/env python3
"""Prefetch leaderboard snapshots — orchestrator-side single-pass HTTP.

FAZ 2.1 (2026-05-07): each refresh-all cycle previously had 18 sub-agents
each doing their own Phase 1 leaderboard sweep, fetching ~37 leaderboards
× 18 batches = ~666 duplicated WebFetches per cycle. This script collapses
that into ONE prefetch pass: every healthy whitelist URL is fetched once
via stdlib `urllib`, written to `data/.leaderboard-snapshots/`, and an
index file maps URL → relative snapshot path. Each batch agent then reads
the snapshot from disk (1 Read per leaderboard) instead of WebFetching
(1 WebFetch + retries + SPA cascade per leaderboard).

Skip rules (no fetch issued):
  - format has _schema.formatTaxonomy[<f>].skipWebFetch=true
    (spa_full / image_embedded / bot_blocked)
  - entry-level _runtime.unhealthy=true
  - entry-level skipWebFetch=true override

Output:
  data/.leaderboard-snapshots/<host>__<sha8>.{html,json}
  data/.leaderboard-snapshots/_index.json

  _index.json shape:
    {
      "_meta": {"writtenAt": "<iso>", "totalAttempted": N, "totalSucceeded": M},
      "snapshots": {
        "<url>": {
          "path": "<relative path under data/.leaderboard-snapshots/>",
          "fetchedAt": "<iso>",
          "etag": "<etag-or-null>",
          "contentLength": <int>,
          "contentType": "<mime>",
          "format": "<whitelist format key>",
          "category": "<leaderboards|aggregators|community|registries>"
        }
      }
    }

CLI:
  python scripts/prefetch-leaderboards.py            # respect freshness TTL
  python scripts/prefetch-leaderboards.py --force    # ignore TTL, fetch all
  python scripts/prefetch-leaderboards.py --max 12   # cap parallel workers

Stdlib-only. No npm, no pip deps. Usable from skill orchestrator + CLI.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

PROJECT = Path(__file__).resolve().parents[1]
SNAPSHOTS_DIR = PROJECT / "data" / ".leaderboard-snapshots"
INDEX_PATH = SNAPSHOTS_DIR / "_index.json"
USER_AGENT = "AICoderMap-Prefetch/1.0 (+https://sungurerdim.github.io/aicodermap/)"

# Cycles run on a 14-day cadence (M5 STALE_DAYS); within-cycle snapshots
# are valid for 24h. Older than that → re-fetch.
DEFAULT_TTL_HOURS = 24
DEFAULT_MAX_WORKERS = 8
FETCH_TIMEOUT_SEC = 15

PREFETCH_CATEGORIES = ("leaderboards", "aggregators", "community", "registries")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stable_filename(url: str, content_type: str) -> str:
    host = (urlparse(url).hostname or "unknown").replace(".", "_")
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:8]
    if "json" in content_type.lower():
        ext = "json"
    elif "html" in content_type.lower() or "xml" in content_type.lower():
        ext = "html"
    else:
        ext = "bin"
    return f"{host}__{digest}.{ext}"


def _load_index() -> dict[str, Any]:
    if not INDEX_PATH.exists():
        return {"_meta": {}, "snapshots": {}}
    try:
        with INDEX_PATH.open(encoding="utf-8") as fp:
            data = json.load(fp)
            if "snapshots" not in data:
                data["snapshots"] = {}
            return data
    except (json.JSONDecodeError, OSError):
        return {"_meta": {}, "snapshots": {}}


def _is_stale(entry: dict[str, Any], ttl_hours: int) -> bool:
    ts = entry.get("fetchedAt")
    if not ts:
        return True
    try:
        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return True
    age_sec = (datetime.now(timezone.utc) - dt).total_seconds()
    return age_sec > ttl_hours * 3600


def _gather_targets(whitelist: dict[str, Any]) -> list[dict[str, Any]]:
    """Walk PREFETCH_CATEGORIES, filter out banned-format / unhealthy / override."""
    ft = (whitelist.get("_schema") or {}).get("formatTaxonomy") or {}
    banned_formats = {
        k
        for k, v in ft.items()
        if isinstance(v, dict) and v.get("skipWebFetch") is True
    }
    targets: list[dict[str, Any]] = []
    for cat in PREFETCH_CATEGORIES:
        for e in whitelist.get(cat, []) or []:
            url = e.get("url")
            if not isinstance(url, str) or not url.startswith(("http://", "https://")):
                continue
            fmt = e.get("format")
            if fmt in banned_formats:
                continue
            if (e.get("_runtime") or {}).get("unhealthy") is True:
                continue
            if e.get("skipWebFetch") is True:
                continue
            targets.append(
                {
                    "url": url,
                    "format": fmt,
                    "category": cat,
                }
            )
    return targets


def _fetch_one(target: dict[str, Any]) -> dict[str, Any]:
    """HTTP GET with stdlib urllib. Returns either {ok:True, ...} or {ok:False, error:...}."""
    url = target["url"]
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        with urlopen(req, timeout=FETCH_TIMEOUT_SEC) as resp:
            status = getattr(resp, "status", 200)
            body = resp.read()
            content_type = (
                resp.headers.get("Content-Type", "text/html").split(";")[0].strip()
            )
            etag = resp.headers.get("ETag")
            return {
                "ok": True,
                "url": url,
                "status": status,
                "body": body,
                "contentType": content_type,
                "etag": etag,
                "format": target.get("format"),
                "category": target.get("category"),
            }
    except HTTPError as e:
        return {
            "ok": False,
            "url": url,
            "error": f"HTTP {e.code} {e.reason}",
            "format": target.get("format"),
            "category": target.get("category"),
        }
    except (URLError, TimeoutError, OSError) as e:
        return {
            "ok": False,
            "url": url,
            "error": f"{type(e).__name__}: {e}",
            "format": target.get("format"),
            "category": target.get("category"),
        }


def _persist_snapshot(result: dict[str, Any]) -> dict[str, Any]:
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    fname = _stable_filename(result["url"], result["contentType"])
    fpath = SNAPSHOTS_DIR / fname
    with fpath.open("wb") as fp:
        fp.write(result["body"])
    return {
        "path": str(fpath.relative_to(PROJECT)).replace("\\", "/"),
        "fetchedAt": _utc_now_iso(),
        "etag": result.get("etag"),
        "contentLength": len(result["body"]),
        "contentType": result["contentType"],
        "format": result.get("format"),
        "category": result.get("category"),
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Prefetch whitelist leaderboards")
    parser.add_argument(
        "--force",
        action="store_true",
        help="ignore TTL; re-fetch every target",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=DEFAULT_MAX_WORKERS,
        help="max parallel HTTP workers (default 8)",
    )
    parser.add_argument(
        "--ttl-hours",
        type=int,
        default=DEFAULT_TTL_HOURS,
        help="snapshot freshness window in hours (default 24)",
    )
    args = parser.parse_args()

    sys.path.insert(0, str(PROJECT / "scripts"))
    from lib.whitelist import load_whitelist  # noqa: E402 — runtime path injection

    for stream in (sys.stdout, sys.stderr):
        reconf = getattr(stream, "reconfigure", None)
        if callable(reconf):
            try:
                reconf(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass

    wl = load_whitelist()
    targets = _gather_targets(wl)
    index = _load_index()
    snapshots = index.get("snapshots") or {}

    fresh: list[dict[str, Any]] = []
    stale: list[dict[str, Any]] = []
    for t in targets:
        existing = snapshots.get(t["url"])
        if not args.force and existing and not _is_stale(existing, args.ttl_hours):
            fresh.append(t)
        else:
            stale.append(t)

    print("=== PREFETCH ===")
    print(
        f"targets: {len(targets)}  fresh: {len(fresh)}  to-fetch: {len(stale)}  "
        f"workers: {args.max}  ttl: {args.ttl_hours}h"
    )

    if not stale:
        print("All snapshots within TTL; no work.")
        return 0

    succeeded = 0
    failed: list[dict[str, Any]] = []
    started = time.monotonic()

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max) as pool:
        future_map = {pool.submit(_fetch_one, t): t for t in stale}
        for fut in concurrent.futures.as_completed(future_map):
            result = fut.result()
            if not result["ok"]:
                failed.append(result)
                print(f"  ✗ {result['url']}  {result['error']}")
                continue
            entry = _persist_snapshot(result)
            snapshots[result["url"]] = entry
            succeeded += 1
            print(
                f"  ✓ {result['url']}  ({entry['contentLength']}B {entry['contentType']})"
            )

    elapsed = time.monotonic() - started
    index["snapshots"] = snapshots
    index["_meta"] = {
        "writtenAt": _utc_now_iso(),
        "totalAttempted": len(stale),
        "totalSucceeded": succeeded,
        "totalFailed": len(failed),
        "elapsedSec": round(elapsed, 2),
    }
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    with INDEX_PATH.open("w", encoding="utf-8") as fp:
        json.dump(index, fp, indent=2, sort_keys=True)
    print(
        f"\n=== DONE ===  fetched: {succeeded}/{len(stale)}  "
        f"failed: {len(failed)}  elapsed: {elapsed:.1f}s"
    )
    print(f"index: {INDEX_PATH.relative_to(PROJECT)}")
    return 0 if not failed else 0  # non-fatal — partial prefetch is OK


if __name__ == "__main__":
    raise SystemExit(_main())
