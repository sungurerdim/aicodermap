"""Apply Berkeley BFCL's `bfcl` observations directly to data/*.json — fill-only.

`bfcl` is a `coreBenchKeys` entry; scripts/merge.py's MX1 invariant expects a
full active×core-bench matrix artifact per cycle, which a handful-of-cells
patch can't satisfy without gap_gen.py stamping hundreds of unrelated core
cells as synthetic "surveyed" gaps never actually surveyed this run (same
reasoning as apply-livebench.py / apply-vals-lcb.py).

Applies directly, and ONLY fills cells that are currently empty — never
overrides an existing value (an existing bfcl cell may carry a
multi-source consensus; adjudicating a disagreement is the normal
verification/contradiction pipeline's job, not a single-source patch script's).

Report-only by default; pass --apply to write. Rotates .bak. Stdlib-only.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from lib.tiers import trust_score  # noqa: E402  (SSOT)
from lib.util import configure_utf8_output, today_iso  # noqa: E402

ROWS_PATH = REPO / "data" / ".leaderboard-snapshots" / "_bfcl-rows.json"
MODELS = REPO / "data" / "models.json"
SOURCES = REPO / "data" / "sources.json"
BENCH_KEY = "bfcl"
SOURCE_NAME = "gorilla.cs.berkeley.edu"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply Berkeley BFCL observations to data/*.json (fill-only)."
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="write fills to data/*.json (default: dry-run report)",
    )
    args = parser.parse_args()
    apply = args.apply
    today = today_iso()
    if not ROWS_PATH.is_file():
        print("no _bfcl-rows.json; run extract-bfcl.py first")
        return 1
    data = json.loads(ROWS_PATH.read_text(encoding="utf-8"))
    obs = [o for o in data.get("observations", []) if o.get("benchKey") == BENCH_KEY]

    models = json.loads(MODELS.read_text(encoding="utf-8"))
    by_id = {m["id"]: m for m in models}
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))

    fills, skipped_filled = [], []
    for o in obs:
        mid, val = o["modelId"], o["value"]
        mdl = by_id.get(mid)
        if mdl is None:
            continue
        bench = mdl.setdefault("bench", {})
        if bench.get(BENCH_KEY) is not None:
            skipped_filled.append(mid)
            continue
        fills.append({"modelId": mid, "value": val})
        if apply:
            bench[BENCH_KEY] = val
            key = f"{mid}.{BENCH_KEY}"
            sources.setdefault(key, []).append(
                {
                    "date": today,
                    "source": SOURCE_NAME,
                    "tier": o.get("tier", "I"),
                    "trustScore": trust_score(o.get("tier", "I"), 1, today),
                    "url": o["sourceUrl"],
                    "value": val,
                    "verifications": 1,
                }
            )
            mdl["lastUpdated"] = today

    print(
        f"=== BFCL-APPLY === fills={len(fills)} "
        f"already-filled-skipped={len(skipped_filled)} apply={apply}"
    )
    for f in fills:
        print(f"  FILL {f['modelId']}.{BENCH_KEY} = {f['value']}")
    if skipped_filled:
        print(f"  skipped (already has {BENCH_KEY}): {skipped_filled}")

    if apply and fills:
        shutil.copy(MODELS, str(MODELS) + ".bak")
        shutil.copy(SOURCES, str(SOURCES) + ".bak")
        MODELS.write_text(
            json.dumps(models, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        SOURCES.write_text(
            json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print("  wrote models.json + sources.json (.bak rotated)")
    elif not apply:
        print("  (report-only; pass --apply to write)")
    return 0


if __name__ == "__main__":
    configure_utf8_output()
    raise SystemExit(main())
