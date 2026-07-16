"""LiveBench "Coding" category extractor — dated-CSV-snapshot aware.

Why this exists: livebench.ai is a SPA whose live page ships no data in the
raw HTML (confirmed `spa_full`, agent WebFetch returns the shell only). But
the site's OWN GitHub Pages repo checks in the exact dated CSV/JSON snapshot
files the SPA fetches client-side (`public/table_<date>.csv` +
`public/categories_<date>.json`) — a real, non-SPA, directly fetchable data
source. This mirrors the AA-RSC extractor's approach (read the artifact the
SPA itself reads, skip the JS rendering layer entirely) for a different site.

LiveBench and LiveCodeBench are two DIFFERENT benchmarks with confusingly
similar names. This extractor writes ONLY `lbCoding` (LiveBench's own
"Coding" category average) — never `lcb` (LiveCodeBench). See
`_schema.benchAliases.lbCoding` / `CONFUSABLE_FAMILIES` in
scripts/lib/whitelist.py for the mechanical guard against that misfile class.

Stdlib only. Usage:
  python scripts/extract-livebench.py            # write _livebench-rows.json + gather artifact
  python scripts/extract-livebench.py --verbose  # print observation + unmatched counts
"""

from __future__ import annotations

import argparse
import csv
import io
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

CONTENTS_API_URL = (
    "https://api.github.com/repos/LiveBench/livebench.github.io/contents/public"
)
RAW_BASE = (
    "https://raw.githubusercontent.com/LiveBench/livebench.github.io/master/public/"
)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
OUT_PATH = REPO / "data" / ".leaderboard-snapshots" / "_livebench-rows.json"
# batch91 sorts after AA's batch90 in the `.aicodermap-agent-out-batch*.gather.json`
# glob (GATHER_BATCH_GLOB in scripts/lib/constants.py) that local-synth.py reads.
GATHER_PATH = REPO / ".aicodermap-agent-out-batch91-livebench.gather.json"

_DATE_RE = re.compile(r"^table_(\d{4}_\d{2}_\d{2})\.csv$")
# LiveBench's own category name for the "Coding" score — read the task-column
# mapping from categories_<date>.json fresh every run (never hardcode the
# column list) so a future LiveBench category redefinition doesn't silently
# go stale.
CODING_CATEGORY = "Coding"


def fetch(url: str, timeout: int = 40) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return (
        urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
    )


def discover_latest_date() -> str:
    """Max `table_<date>.csv` date present in the repo's public/ dir, via the
    GitHub Contents API — robust to any single SPA build's embedded date list
    going stale (it's read from the live directory listing every run)."""
    listing = json.loads(fetch(CONTENTS_API_URL))
    dates = set()
    names = {e.get("name") for e in listing if isinstance(e, dict)}
    for name in names:
        m = _DATE_RE.match(name or "")
        if m and f"categories_{m.group(1)}.json" in names:
            dates.add(m.group(1))
    if not dates:
        raise RuntimeError("no table_<date>.csv + categories_<date>.json pair found")
    return max(dates)  # zero-padded YYYY_MM_DD sorts chronologically as a string


def load_coding_columns(date: str) -> list[str]:
    categories = json.loads(fetch(RAW_BASE + f"categories_{date}.json"))
    cols = categories.get(CODING_CATEGORY) or []
    if not cols:
        raise RuntimeError(f"categories_{date}.json has no '{CODING_CATEGORY}' entry")
    return list(cols)


def load_table_rows(date: str) -> list[dict[str, str]]:
    text = fetch(RAW_BASE + f"table_{date}.csv")
    return list(csv.DictReader(io.StringIO(text)))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract LiveBench's own 'Coding' category average into lbCoding."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="print observation + unmatched counts"
    )
    args = parser.parse_args()

    date = discover_latest_date()
    coding_cols = load_coding_columns(date)
    rows = load_table_rows(date)
    table_url = RAW_BASE + f"table_{date}.csv"

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
    for row in rows:
        name = (row.get("model") or "").strip()
        if not name:
            continue
        vals: list[float] = []
        for col in coding_cols:
            raw = (row.get(col) or "").strip()
            if not raw:
                continue
            try:
                vals.append(float(raw))
            except ValueError:
                continue
        if not vals:
            continue
        mid = by_norm.get(_norm(name))
        if not mid:
            unmatched.append(name)
            continue
        matched_ids.add(mid)
        val = round(sum(vals) / len(vals), 2)
        if not (0 <= val <= 100):
            continue  # sanity band: lbCoding is a 0-100 metric
        observations.append(
            {
                "modelId": mid,
                "benchKey": "lbCoding",
                "value": val,
                "sourceUrl": table_url,
                "tier": "I",
                "fetched": today,
                "_lbSlug": name,
                "_lbDate": date,
            }
        )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(
            {
                "source": table_url,
                "fetched": today,
                "snapshotDate": date,
                "codingColumns": coding_cols,
                "modelsParsed": len(rows),
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
                "batchId": "batch91-livebench",
                "mode": "gather",
                "observations": observations,
                "runtime": {
                    "startedAt": int(time.time()),
                    "source": "livebench-csv-deterministic",
                    "fills": len(observations),
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(
        f"=== LiveBench === date={date} parsed={len(rows)} "
        f"matched_our={len(matched_ids)}/{len(our)} observations={len(observations)} "
        f"-> {OUT_PATH.name}"
    )
    if args.verbose:
        print(f"  coding columns: {coding_cols}")
        print(f"  data-bearing LiveBench rows with NO match to our set: {len(unmatched)}")
        if unmatched:
            print(f"  unmatched sample: {unmatched[:10]}")
    return 0


if __name__ == "__main__":
    configure_utf8_output()
    raise SystemExit(main())
