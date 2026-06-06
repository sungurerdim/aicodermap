"""Apply Artificial Analysis as the AUTHORITATIVE source for AA-composite benches.

aaIdx / aaCoding / aaAgentic are AA's OWN proprietary composite indices — no
other entity computes them. Therefore any stored value that disagrees with AA's
current value is, by definition, a misfile (an agent misread AA, or filed a
different metric). Confirmed empirically: AA's observed aaIdx ceiling across all
our models is ~61, yet agents had stored 71-79 (physically impossible).

This corrector deterministically sets each AA-composite cell to AA's RSC value
(from extract-aa-rsc.py) and REPLACES its provenance with a single AA I-tier
entry — purging the misfiled history (these are invalid, not legitimate
alternates). gpqa/hle/tau2/tbHard are NOT touched here: AA only *measures* those
external benchmarks, so a vendor/other source can legitimately differ — those go
through normal verification, not authoritative override.

Report-only by default; pass --apply to write. Rotates .bak. Stdlib-only.
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from lib.constants import AA_COMPOSITE_KEYS, AA_MEASURED_KEYS  # noqa: E402

AA_ROWS = REPO / "data" / ".leaderboard-snapshots" / "_aa-rows.json"
MODELS = REPO / "data" / "models.json"
SOURCES = REPO / "data" / "sources.json"
AA_URL = "https://artificialanalysis.ai/leaderboards/models"
AA_COMPOSITE = AA_COMPOSITE_KEYS  # SSOT: lib.constants (AA-definitional → adopt AA)
AA_MEASURED = (
    AA_MEASURED_KEYS  # SSOT: lib.constants (external → adopt only if impossible)
)
MISFILE_TOL = (
    2.0  # composite Δ at-or-below this is precision, not a misfile → leave existing
)
# AA-measured: a stored value outside [min*FLOOR, max*CEIL] of AA's observed
# distribution for that bench is physically impossible (e.g. hle=79 when AA's
# ceiling across all models is 45.7) → agent misfile → adopt AA's value. Margins
# are generous so legitimate tooled-vs-untooled variance (e.g. HLE ~50) is kept.
ENV_CEIL = 1.25
ENV_FLOOR = 0.6
I_TIER_TRUST = 0.5  # I-tier, 1 verification, fresh (tierWeight 1.0 × verif 0.5 × 1 × 1)


def main() -> int:
    apply = "--apply" in sys.argv
    today = date.today().isoformat()
    if not AA_ROWS.is_file():
        print("no _aa-rows.json; run extract-aa-rsc.py first")
        return 1
    obs = json.loads(AA_ROWS.read_text(encoding="utf-8")).get("observations", [])
    aa = {(o["modelId"], o["benchKey"]): o["value"] for o in obs}
    env: dict[str, tuple[float, float]] = {}
    for bk in AA_MEASURED:
        vals = [o["value"] for o in obs if o["benchKey"] == bk]
        if vals:
            env[bk] = (min(vals) * ENV_FLOOR, max(vals) * ENV_CEIL)

    models = json.loads(MODELS.read_text(encoding="utf-8"))
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))

    overrides, fills, impossible, touched = [], [], [], set()

    def _set(mid, bk, aav):
        touched.add(mid)
        if apply:
            mdl["bench"][bk] = aav
            sources[f"{mid}.{bk}"] = [
                {
                    "date": today,
                    "source": "artificialanalysis.ai",
                    "tier": "I",
                    "trustScore": I_TIER_TRUST,
                    "url": AA_URL,
                    "value": aav,
                    "verifications": 1,
                }
            ]

    for mdl in models:
        mid = mdl["id"]
        bench = mdl.setdefault("bench", {})
        # AA-COMPOSITE: AA is definitional → always adopt AA
        for bk in AA_COMPOSITE:
            aav = aa.get((mid, bk))
            if aav is None:
                continue
            cur = bench.get(bk)
            # Skip cells already AA-correct within MISFILE_TOL: a sub-2pp gap is
            # precision/rounding, not a misfile — leave the existing (possibly
            # multi-source-corroborated) value rather than downgrade it to a
            # single AA entry. Only real misfiles (Δ>2) and empties get rewritten.
            if cur is not None and abs(cur - aav) <= MISFILE_TOL:
                continue
            (overrides if cur is not None else fills).append(
                {"modelId": mid, "benchKey": bk, "from": cur, "to": aav}
            )
            _set(mid, bk, aav)
        # AA-MEASURED: adopt AA ONLY when current is outside AA's observed envelope
        # (physically impossible → misfile). Plausible disagreements are left alone.
        for bk in AA_MEASURED:
            aav = aa.get((mid, bk))
            cur = bench.get(bk)
            if aav is None or cur is None or bk not in env:
                continue
            lo, hi = env[bk]
            if cur < lo or cur > hi:
                impossible.append(
                    {
                        "modelId": mid,
                        "benchKey": bk,
                        "from": cur,
                        "to": aav,
                        "env": [round(lo, 1), round(hi, 1)],
                    }
                )
                _set(mid, bk, aav)
        if apply and mid in touched:
            mdl["lastUpdated"] = today

    print(
        f"=== AA-AUTHORITATIVE === composite: overrides={len(overrides)} fills={len(fills)} "
        f"| measured-impossible-fixes={len(impossible)} | models touched={len(touched)} apply={apply}"
    )
    if "--verbose" in sys.argv or not apply:
        big = [r for r in overrides if abs((r["from"] or 0) - r["to"]) > 2]
        print(
            f"  -- composite misfile fixes (Δ>2): {len(big)} (rest are precision updates) --"
        )
        for r in sorted(big, key=lambda x: -abs((x["from"] or 0) - x["to"])):
            print(f"  FIX  {r['modelId']}.{r['benchKey']}: {r['from']} -> {r['to']}")
        print(f"  -- AA-measured impossible-value fixes: {len(impossible)} --")
        for r in sorted(impossible, key=lambda x: -abs((x["from"] or 0) - x["to"])):
            print(
                f"  IMPOSSIBLE {r['modelId']}.{r['benchKey']}: {r['from']} outside AA env {r['env']} -> {r['to']}"
            )

    if apply:
        shutil.copy(MODELS, str(MODELS) + ".bak")
        shutil.copy(SOURCES, str(SOURCES) + ".bak")
        MODELS.write_text(
            json.dumps(models, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        SOURCES.write_text(
            json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print("  wrote models.json + sources.json (.bak rotated)")
    else:
        print("  (report-only; pass --apply to write)")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    raise SystemExit(main())
