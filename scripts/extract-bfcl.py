"""Berkeley BFCL extractor — reads the live overall-results CSV directly.

Why this exists: gorilla.cs.berkeley.edu/leaderboard.html is a SPA shell (0
model names in raw HTML, confirmed live) — the whitelist correctly marks it
`spa_full`. But the same site checks in the exact CSV its SPA fetches
client-side at a plain, non-SPA URL (`data_overall.csv`) — same "read the
artifact the SPA itself reads" approach as extract-livebench.py, applied to
Berkeley's own dashboard instead of LiveBench's.

BFCL's CSV lists each model once per invocation harness — "(FC)" (native
function-calling), "(Prompt)", "(FC thinking)", "(Prompt + Thinking)" — and
these can diverge sharply for the same underlying model (e.g. Claude Opus
4.5: 77.47% FC vs 33.47% Prompt). This is the same "scaffold variance"
phenomenon already documented on the SWE-bench experiments repo whitelist
entry ("Treat the current best demonstrated result as the observation") —
applied the same way here: when multiple harness variants resolve to the
same one of our model ids, take the MAX (the model's best demonstrated
BFCL capability), not an arbitrary pick.

Stdlib only. Usage:
  python scripts/extract-bfcl.py            # write _bfcl-rows.json + gather artifact
  python scripts/extract-bfcl.py --verbose  # print observation + unmatched counts
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

CSV_URL = "https://gorilla.cs.berkeley.edu/data_overall.csv"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
OUT_PATH = REPO / "data" / ".leaderboard-snapshots" / "_bfcl-rows.json"
# batch93 sorts after LiveBench's batch91 and vals.ai's batch92 in the
# `.aicodermap-agent-out-batch*.gather.json` glob local-synth.py reads.
GATHER_PATH = REPO / ".aicodermap-agent-out-batch93-bfcl.gather.json"
BENCH_KEY = "bfcl"

_MODE_SUFFIX_RE = re.compile(r"\s*\([^)]*\)\s*$")
_DATE_SUFFIX_RE = re.compile(r"-\d{4}-\d{2}-\d{2}$|-\d{8}$")


def fetch(url: str, timeout: int = 40) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return (
        urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
    )


def base_model_name(raw: str) -> str:
    """Strip the trailing harness-mode tag ("(FC)", "(Prompt + Thinking)", ...)
    and a trailing ISO-date suffix (vendor snapshot dates our shorter ids omit)."""
    name = _MODE_SUFFIX_RE.sub("", raw).strip()
    name = _DATE_SUFFIX_RE.sub("", name).strip()
    return name


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract Berkeley BFCL's Overall Acc into bfcl."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="print observation + unmatched counts"
    )
    args = parser.parse_args()

    text = fetch(CSV_URL)
    rows = list(csv.DictReader(io.StringIO(text)))

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

    # Group by our resolved id first (best-of-harness-variants), THEN emit —
    # so a (FC)/(Prompt) split for the same model yields exactly one observation.
    best: dict[str, tuple[float, str]] = {}  # modelId -> (value, raw name of the winner)
    unmatched: list[str] = []
    for row in rows:
        raw_acc = (row.get("Overall Acc") or "").strip()
        raw_name = (row.get("Model") or "").strip()
        if not raw_acc or not raw_name:
            continue
        try:
            val = float(raw_acc.rstrip("%"))
        except ValueError:
            continue
        base = base_model_name(raw_name)
        mid = by_norm.get(_norm(base))
        if not mid:
            unmatched.append(raw_name)
            continue
        cur = best.get(mid)
        if cur is None or val > cur[0]:
            best[mid] = (val, raw_name)

    today = today_iso()
    observations: list[dict] = []
    for mid, (val, raw_name) in best.items():
        rounded = round(val, 2)
        if not (0 <= rounded <= 100):
            continue  # sanity band: bfcl is a 0-100 metric
        observations.append(
            {
                "modelId": mid,
                "benchKey": BENCH_KEY,
                "value": rounded,
                "sourceUrl": CSV_URL,
                "tier": "I",
                "fetched": today,
                "_bfclRow": raw_name,
            }
        )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(
            {
                "source": CSV_URL,
                "fetched": today,
                "modelsParsed": len(rows),
                "ourModelsMatched": sorted(best.keys()),
                "observations": observations,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    GATHER_PATH.write_text(
        json.dumps(
            {
                "batchId": "batch93-bfcl",
                "mode": "gather",
                "observations": observations,
                "runtime": {
                    "startedAt": int(time.time()),
                    "source": "berkeley-bfcl-csv-deterministic",
                    "fills": len(observations),
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(
        f"=== BFCL === parsed={len(rows)} "
        f"matched_our={len(best)}/{len(our)} observations={len(observations)} "
        f"-> {OUT_PATH.name}"
    )
    if args.verbose:
        print(f"  data-bearing BFCL rows with NO match to our set: {len(unmatched)}")
        if unmatched:
            print(f"  unmatched sample: {unmatched[:10]}")
    return 0


if __name__ == "__main__":
    configure_utf8_output()
    raise SystemExit(main())
