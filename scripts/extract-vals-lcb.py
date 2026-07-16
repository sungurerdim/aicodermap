"""Vals.ai LiveCodeBench (`lcb`) extractor — Astro-island-JSON aware.

Why this exists: vals.ai/benchmarks/lcb is server-rendered by Astro, so live
WebFetch previously got classified `static_html_table` and mined with a
plain HTML-table extractor — but the actual per-model data isn't in visible
<table> markup at all. It lives in a <astro-island component-url="/_astro/
BenchmarkView..."> element's `props` attribute: an HTML-entity-encoded JSON
blob using a `[typeTag, value]` tuple wrapper on every node (Astro's
client-hydration serialization). This extractor decodes that attribute
directly — same "read the embedded JSON, skip the JS render" approach as
extract-aa-rsc.py, applied to a different site's different serialization
format.

`lcb` here is the genuine LiveCodeBench (vals.ai's own metadata literally
says `benchmark: "LiveCodeBench", slug: "lcb"`) — unlike the LiveBench
situation (see extract-livebench.py), there is no confusable-name risk on
this source; it feeds the EXISTING `lcb` key, not a new one.

vals.ai's `tasks.overall` view already carries exactly ONE score per model
(their own harness already picked a single reasoning-effort setting per
model) — no effort-variant disambiguation needed on our side.

Stdlib only. Usage:
  python scripts/extract-vals-lcb.py            # write _vals-lcb-rows.json + gather artifact
  python scripts/extract-vals-lcb.py --verbose  # print observation + unmatched counts
"""

from __future__ import annotations

import argparse
import html as htmllib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from lib.util import slug_norm as _norm  # noqa: E402  (SSOT)
from lib.util import configure_utf8_output, today_iso  # noqa: E402

VALS_URL = "https://www.vals.ai/benchmarks/lcb"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
OUT_PATH = REPO / "data" / ".leaderboard-snapshots" / "_vals-lcb-rows.json"
# batch92 sorts after AA's batch90 and LiveBench's batch91 in the
# `.aicodermap-agent-out-batch*.gather.json` glob local-synth.py reads.
GATHER_PATH = REPO / ".aicodermap-agent-out-batch92-vals-lcb.gather.json"
BENCH_KEY = "lcb"


def fetch(url: str, timeout: int = 40) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return (
        urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
    )


def _unwrap(o):
    """Recursively strip Astro's `[typeTag:int, value]` tuple wrapper that
    wraps every scalar/dict/list node in an island's `props` JSON."""
    if isinstance(o, list) and len(o) == 2 and isinstance(o[0], int):
        return _unwrap(o[1])
    if isinstance(o, dict):
        return {k: _unwrap(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_unwrap(x) for x in o]
    return o


def parse_overall_scores(html_text: str) -> dict[str, dict]:
    """Extract `tasks.overall` — {'<org>/<slug>': {accuracy, ...}} — from the
    BenchmarkView astro-island's props attribute."""
    m = re.search(
        r'<astro-island[^>]*component-url="/_astro/BenchmarkView[^"]*"[^>]*>',
        html_text,
    )
    if not m:
        raise RuntimeError("BenchmarkView astro-island not found (format may have changed)")
    pm = re.search(r'\bprops="([^"]*)"', m.group(0))
    if not pm:
        raise RuntimeError("astro-island has no props attribute")
    props_raw = htmllib.unescape(pm.group(1))
    data = _unwrap(json.loads(props_raw))
    default = data["benchmarkView"]["default"]
    return default["tasks"]["overall"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract vals.ai's LiveCodeBench (lcb) scores."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="print observation + unmatched counts"
    )
    args = parser.parse_args()

    html_text = fetch(VALS_URL)
    overall = parse_overall_scores(html_text)

    our = json.loads((REPO / "data" / "models.json").read_text(encoding="utf-8"))
    by_norm: dict[str, str] = {}
    collisions: set[str] = set()
    for m in our:
        for cand in (m.get("id"), m.get("name")):
            n = _norm(cand)
            if not n:
                continue
            if n in by_norm and by_norm[n] != m["id"]:
                collisions.add(n)  # ambiguous normalized key -> never auto-match
            by_norm.setdefault(n, m["id"])
    for n in collisions:
        by_norm.pop(n, None)

    today = today_iso()
    observations: list[dict] = []
    matched_ids: set[str] = set()
    unmatched: list[str] = []
    for org_slug, row in overall.items():
        val = row.get("accuracy")
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            continue
        # "<org>/<slug>" or, for a few nested-provider entries, "<org>/.../<slug>"
        # — the model-identifying part is always the LAST path segment.
        slug = org_slug.rsplit("/", 1)[-1]
        mid = by_norm.get(_norm(slug))
        if not mid:
            unmatched.append(org_slug)
            continue
        matched_ids.add(mid)
        rounded = round(float(val), 2)
        if not (0 <= rounded <= 100):
            continue  # sanity band: lcb is a 0-100 metric
        observations.append(
            {
                "modelId": mid,
                "benchKey": BENCH_KEY,
                "value": rounded,
                "sourceUrl": VALS_URL,
                "tier": "I",
                "fetched": today,
                "_valsSlug": org_slug,
                "_valsReasoningEffort": row.get("reasoning_effort"),
            }
        )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(
            {
                "source": VALS_URL,
                "fetched": today,
                "modelsParsed": len(overall),
                "ourModelsMatched": sorted(matched_ids),
                "observations": observations,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    GATHER_PATH.write_text(
        json.dumps(
            {
                "batchId": "batch92-vals-lcb",
                "mode": "gather",
                "observations": observations,
                "runtime": {
                    "startedAt": int(time.time()),
                    "source": "vals-ai-astro-island-deterministic",
                    "fills": len(observations),
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(
        f"=== VALS-LCB === parsed={len(overall)} "
        f"matched_our={len(matched_ids)}/{len(our)} observations={len(observations)} "
        f"-> {OUT_PATH.name}"
    )
    if args.verbose:
        print(f"  data-bearing vals.ai rows with NO match to our set: {len(unmatched)}")
        if unmatched:
            print(f"  unmatched sample: {unmatched[:10]}")
    return 0


if __name__ == "__main__":
    configure_utf8_output()
    raise SystemExit(main())
