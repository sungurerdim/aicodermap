#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Post-push GitHub Pages deploy verification.

Skill workflow Step 14 (added 2026-05-06): the cycle is not "complete"
until this script exits 0. Catches the failure mode where `git push`
succeeds but GitHub Pages doesn't actually serve the new build (CDN
propagation hiccup, GitHub status incident, branch-protection delay).

Checks (in order; first failure aborts):
  1. Local HEAD short SHA matches the deployed commit on origin/main
     via the GitHub commits API.
  2. https://sungurerdim.github.io/aicodermap/data/models.json ETag
     differs from `pre_push_etag` (recorded by merge.py before push).
  3. The served data/models.json's modelCount + benchKeyCount match the
     local data/_meta.json.

Retry policy: 60s delay before first probe (GitHub Pages CDN warm-up),
then 3 retries spaced 30s apart. Total budget: ~2.5 min.

Exit codes:
  0  every check passed
  1  one or more checks failed (cycle should be flagged DEPLOY_VERIFY_FAILED)
  2  no network / tooling error (can't determine — should not block local dev)
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
GH_REPO = "sungurerdim/aicodermap"
PAGES_BASE = f"https://{GH_REPO.split('/')[0]}.github.io/{GH_REPO.split('/')[1]}"

INITIAL_DELAY_SEC = 60
RETRY_INTERVAL_SEC = 30
MAX_RETRIES = 3
HTTP_TIMEOUT = 12


def _say(msg: str) -> None:
    print(msg, flush=True)


def _say_err(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def local_head_sha() -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT,
            capture_output=True,
            text=True,
            check=True,
        )
        return (out.stdout or "").strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def gh_remote_sha() -> str | None:
    """Last commit on origin/main per GitHub API."""
    url = f"https://api.github.com/repos/{GH_REPO}/commits/main"
    try:
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "aicodermap-verify-deploy",
            },
        )
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            data = json.loads(resp.read())
            return data.get("sha")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError):
        return None


def served_etag() -> str | None:
    """ETag of the live data/models.json served by GitHub Pages."""
    url = f"{PAGES_BASE}/data/models.json"
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            return resp.headers.get("ETag") or resp.headers.get("etag")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        return None


def served_meta() -> dict | None:
    """Live data/_meta.json content (None if absent)."""
    url = f"{PAGES_BASE}/data/_meta.json"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            return json.loads(resp.read())
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError):
        return None


def local_meta() -> dict | None:
    p = PROJECT / "data" / "_meta.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def local_pre_push_etag() -> str | None:
    """ETag merge.py stored before the push (data/_meta.json.prev_etag)."""
    meta = local_meta() or {}
    return meta.get("prevPushEtag")


def main() -> int:
    head = local_head_sha()
    if head is None:
        _say_err("verify-deploy: cannot read local HEAD SHA — is this a git repo?")
        return 2
    head_short = head[:7]
    _say(f"verify-deploy: local HEAD = {head_short}")

    _say(f"verify-deploy: waiting {INITIAL_DELAY_SEC}s for GitHub Pages CDN warm-up…")
    time.sleep(INITIAL_DELAY_SEC)

    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        _say(f"verify-deploy: attempt {attempt}/{MAX_RETRIES}")
        # Check 1 — origin/main SHA matches local HEAD.
        remote = gh_remote_sha()
        if remote is None:
            last_err = "GitHub commits API unreachable"
        elif remote.startswith(head):
            _say(f"  ✓ origin/main {remote[:7]} matches local HEAD")
            # Check 2 — Pages ETag differs from pre-push ETag.
            etag_now = served_etag()
            etag_pre = local_pre_push_etag()
            if etag_now is None:
                last_err = "Pages /data/models.json HEAD failed"
            elif etag_pre and etag_now == etag_pre:
                last_err = (
                    f"Pages still serving pre-push ETag {etag_pre} — "
                    f"deploy not propagated"
                )
            else:
                _say(f"  ✓ Pages ETag rotated ({etag_pre or '<none>'} → {etag_now})")
                # Check 3 — served meta matches local meta (if both exist).
                lmeta = local_meta()
                rmeta = served_meta()
                if lmeta and rmeta:
                    same_count = lmeta.get("modelCount") == rmeta.get(
                        "modelCount"
                    ) and lmeta.get("benchKeyCount") == rmeta.get("benchKeyCount")
                    if same_count:
                        _say(
                            f"  ✓ served _meta.json matches local "
                            f"({lmeta.get('modelCount')} models × "
                            f"{lmeta.get('benchKeyCount')} bench keys)"
                        )
                        _say("verify-deploy: ✓ DEPLOY VERIFIED")
                        return 0
                    last_err = (
                        f"served _meta.json drift: served="
                        f"{rmeta.get('modelCount')}m/{rmeta.get('benchKeyCount')}b, "
                        f"local={lmeta.get('modelCount')}m/{lmeta.get('benchKeyCount')}b"
                    )
                else:
                    # _meta.json absent yet — that's OK if FAZ D not landed.
                    _say("verify-deploy: ✓ DEPLOY VERIFIED (no _meta.json available)")
                    return 0
        else:
            last_err = f"origin/main {remote[:7]} != local HEAD {head_short}"

        if attempt < MAX_RETRIES:
            _say(f"  ✗ {last_err} — retrying in {RETRY_INTERVAL_SEC}s")
            time.sleep(RETRY_INTERVAL_SEC)

    _say_err("\n" + "=" * 72)
    _say_err("✗ DEPLOY VERIFICATION FAILED")
    _say_err("=" * 72)
    _say_err(f"  last error: {last_err}")
    _say_err(f"  local HEAD: {head_short}")
    _say_err(f"  Pages URL:  {PAGES_BASE}/")
    _say_err("  next step:  check https://www.githubstatus.com/, then")
    _say_err("              `git push origin main` again or wait a cycle.")
    _say_err("=" * 72)
    return 1


if __name__ == "__main__":
    sys.exit(main())
