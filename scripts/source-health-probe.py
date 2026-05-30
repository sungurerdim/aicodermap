#!/usr/bin/env python3
"""One-pass source health probe across EVERY whitelist category (Phase 2.6).

prefetch-leaderboards.py only caches leaderboard/aggregator bodies. This probe
goes wider and diagnoses: it fetches vendors (lineup + news), leaderboards,
aggregators, local, registries, complianceAggregators and community in ONE pass,
classifies each URL's OBSERVED format, and refreshes `_runtime.healthChecks`.

It reports four reachability problems the cycle must know about before dispatch:
  format-drift — declared static_html_table/article but now SPA or bot-walled
                 (or declared spa_full but now static → re-promotable).
  redirect     — final URL host differs from requested (cross-host 30x).
  spa          — 200 but no extractable rows (client-rendered shell).
  bot-block    — 403/429 or a login/robot interstitial body.

Stdlib-only (urllib). Concurrent. Writes _runtime.healthChecks + lastFullCycle
back into data/sources-whitelist.json unless --report-only. Idempotent.

Usage:
  python scripts/source-health-probe.py [--report-only] [--limit N]
                                        [--timeout SEC] [--max-workers N] [--quiet]
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

PROJECT = Path(__file__).resolve().parents[1]
WHITELIST = PROJECT / "data" / "sources-whitelist.json"
REPORT = PROJECT / "data" / "_runtime-health-report.json"

USER_AGENT = "AICoderMap-HealthProbe/1.0 (+https://sungurerdim.github.io/aicodermap/)"
FETCH_TIMEOUT_SEC = 15
DEFAULT_MAX_WORKERS = 8

ALL_CATEGORIES = (
    "leaderboards",
    "aggregators",
    "local",
    "registries",
    "community",
    "complianceAggregators",
)
# Static formats that should still server-render rows; drift to SPA/bot is bad.
STATIC_FORMATS = {"static_html_table", "static_html_article"}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _host(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def _domain_key(url: str) -> str:
    """Stable healthCheck key: host + first path segment (matches existing keys
    like 'artificialanalysis.ai/leaderboards', 'openai.com/index')."""
    p = urlparse(url)
    host = (p.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    seg = [s for s in (p.path or "").split("/") if s]
    return f"{host}/{seg[0]}" if seg else host


def _gather_targets(wl: dict, vendors: bool = True) -> list[dict]:
    targets: list[dict] = []
    seen: set[str] = set()

    def add(url, fmt, cat, label):
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            return
        if url in seen:
            return
        seen.add(url)
        targets.append(
            {"url": url, "declaredFormat": fmt, "category": cat, "label": label}
        )

    for cat in ALL_CATEGORIES:
        for e in wl.get(cat, []) or []:
            add(e.get("url"), e.get("format"), cat, e.get("name") or e.get("id"))
    if vendors:
        for vid, v in (wl.get("vendors") or {}).items():
            urls = v.get("urls") or {}
            add(urls.get("lineup"), "lineup", "vendors.lineup", vid)
            add(urls.get("news"), v.get("postFormat"), "vendors.news", vid)
    return targets


def _classify(
    status: int, body: bytes, declared: str | None, requested: str, final: str
) -> dict:
    """Return {observedFormat, problems[]}."""
    problems: list[str] = []
    text = body.decode("utf-8", errors="replace") if body else ""
    low = text.lower()

    redirected = _host(requested) != _host(final) and _host(final) != ""
    if redirected:
        problems.append("redirect")

    # bot-block / interstitial heuristics.
    bot_markers = (
        "are you a robot",
        "enable javascript and cookies",
        "log in to continue",
        "verify you are human",
        "access denied",
        "blocked",
        "captcha",
    )
    if status in (401, 403, 429):
        observed = "bot_blocked"
        problems.append("bot-block")
    elif status == 404 or status >= 500:
        observed = "dead"
        problems.append(f"http-{status}")
    elif len(text) < 9000 and any(m in low for m in bot_markers):
        observed = "bot_blocked"
        problems.append("bot-block")
    else:
        has_table = "<table" in low or low.count("<tr") >= 5
        spa_markers = (
            "__next_data__",
            '<div id="root"',
            '<div id="__next"',
            "no models found",
            "you need to enable javascript",
        )
        is_spa_shell = (not has_table) and (
            any(m in low for m in spa_markers) or len(text) < 4000
        )
        if has_table:
            observed = "static_html_table"
        elif is_spa_shell:
            observed = "spa_full"
            problems.append("spa")
        else:
            observed = "static_html_article"

    # format-drift: declared static but now SPA/bot/dead.
    if declared in STATIC_FORMATS and observed in ("spa_full", "bot_blocked", "dead"):
        problems.append("format-drift")
    # re-promotable: declared spa_full but now static (informational).
    if declared == "spa_full" and observed in ("static_html_table",):
        problems.append("repromotable")

    return {
        "observedFormat": observed,
        "problems": sorted(set(problems)),
        "finalUrl": final,
    }


def _probe_one(t: dict, timeout: int) -> dict:
    url = t["url"]
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", 200) or 200
            final = resp.geturl()
            body = resp.read(200_000)  # cap: enough to classify, bounded memory
        cls = _classify(status, body, t["declaredFormat"], url, final)
        return {**t, "status": status, **cls, "ok": "dead" not in cls["observedFormat"]}
    except HTTPError as e:
        cls = _classify(e.code, b"", t["declaredFormat"], url, url)
        return {
            **t,
            "status": e.code,
            **cls,
            "ok": False,
            "error": f"HTTP {e.code} {e.reason}",
        }
    except (URLError, TimeoutError, OSError) as e:
        msg = f"{type(e).__name__}: {e}"
        # An SSL-trust failure from THIS host's cert bundle is an environment
        # artifact, not the source being down. Tag it separately so it neither
        # counts as a reachability failure nor bumps consecutiveFailures.
        if "CERTIFICATE_VERIFY_FAILED" in str(e) or "SSL" in str(e):
            return {
                **t,
                "status": 0,
                "observedFormat": "ssl-env-unverified",
                "problems": ["ssl-env"],
                "finalUrl": url,
                "ok": True,
                "error": msg,
            }
        return {
            **t,
            "status": 0,
            "observedFormat": "unreachable",
            "problems": ["unreachable"],
            "finalUrl": url,
            "ok": False,
            "error": msg,
        }


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe all whitelist source categories.")
    ap.add_argument(
        "--report-only",
        action="store_true",
        help="Do not write _runtime.healthChecks back; only emit the report.",
    )
    ap.add_argument(
        "--limit", type=int, default=0, help="Probe only the first N targets (debug)."
    )
    ap.add_argument("--timeout", type=int, default=FETCH_TIMEOUT_SEC)
    ap.add_argument("--max-workers", type=int, default=DEFAULT_MAX_WORKERS)
    ap.add_argument("--no-vendors", action="store_true", help="Skip vendor URLs.")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    wl = json.loads(WHITELIST.read_text(encoding="utf-8"))
    targets = _gather_targets(wl, vendors=not args.no_vendors)
    if args.limit:
        targets = targets[: args.limit]

    with ThreadPoolExecutor(max_workers=args.max_workers) as ex:
        results = list(ex.map(lambda t: _probe_one(t, args.timeout), targets))

    # Aggregate problems.
    drift = [r for r in results if "format-drift" in r["problems"]]
    redirects = [r for r in results if "redirect" in r["problems"]]
    spas = [r for r in results if "spa" in r["problems"]]
    bots = [r for r in results if "bot-block" in r["problems"]]
    dead = [r for r in results if not r["ok"]]

    # Refresh _runtime.healthChecks (merge, bump consecutiveFailures).
    rt = wl.setdefault("_runtime", {})
    hc = rt.setdefault("healthChecks", {})
    for r in results:
        key = _domain_key(r["url"])
        prev = hc.get(key) or {}
        fails = int(prev.get("consecutiveFailures", 0) or 0)
        fails = fails + 1 if not r["ok"] else 0
        entry = {
            "status": r["observedFormat"],
            "observedFormat": r["observedFormat"],
            "lastProbedAt": _today(),
            "consecutiveFailures": fails,
        }
        if r["problems"]:
            entry["problems"] = r["problems"]
        if "redirect" in r["problems"]:
            entry["redirectedTo"] = r["finalUrl"]
        hc[key] = entry
    rt["lastFullCycle"] = _today()

    report = {
        "probedAt": _utc_now_iso(),
        "total": len(results),
        "counts": {
            "format-drift": len(drift),
            "redirect": len(redirects),
            "spa": len(spas),
            "bot-block": len(bots),
            "dead": len(dead),
        },
        "formatDrift": [
            {
                "url": r["url"],
                "declared": r["declaredFormat"],
                "observed": r["observedFormat"],
            }
            for r in drift
        ],
        "redirects": [{"url": r["url"], "to": r["finalUrl"]} for r in redirects],
        "spa": [r["url"] for r in spas],
        "botBlocked": [r["url"] for r in bots],
        "dead": [{"url": r["url"], "error": r.get("error")} for r in dead],
    }
    REPORT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    if not args.report_only:
        WHITELIST.write_text(
            json.dumps(wl, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    print(
        f"=== SOURCE HEALTH PROBE === probed={len(results)} "
        f"format-drift={len(drift)} redirect={len(redirects)} spa={len(spas)} "
        f"bot-block={len(bots)} dead={len(dead)}"
        f"{' (report-only)' if args.report_only else ' (healthChecks updated)'}"
    )
    if not args.quiet:
        for label, items in (("FORMAT-DRIFT", drift), ("DEAD", dead)):
            for r in items[:30]:
                print(
                    f"  {label}: {r['url']} -> {r.get('observedFormat')} {r.get('error', '')}"
                )
    print(f"  report: {REPORT}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    raise SystemExit(main())
