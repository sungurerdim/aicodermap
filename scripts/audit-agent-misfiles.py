"""Comprehensive agent-caused misfile sweep.

Surfaces the misfile classes that LLM gather agents have historically produced,
using deterministic ground-truth where it exists:

  1. AA cross-check — Artificial Analysis ships authoritative per-model values
     (data/.leaderboard-snapshots/_aa-rows.json, from extract-aa-rsc.py).
     - AA-COMPOSITE benches (aaIdx/aaCoding/aaAgentic) are AA's OWN definitional
       indices: nobody else computes them, so a stored value that disagrees with
       AA is a misfile (agent misread AA, or filed a different metric). AUTHORITATIVE.
     - AA-MEASURED external benches (gpqa/hle/tau2/tbHard): AA is one strong I-tier
       voice; a large disagreement is a CANDIDATE misfile (advisory — another
       source can legitimately differ; verify before changing).
  2. Band/scale violations — value outside its benchRanges hard band (e.g. an Elo
     stored as a 0-100 %, a negative, a >100). Impossible → misfile.
  3. Cross-bench duplication — the same non-null value under >=2 different core
     benches for one model (the snapshot-extraction duplicate-attribution artifact).

Report-only by default (writes data/_misfile-audit.json + prints a summary).
Stdlib-only. No mutation here — corrections are applied by dedicated scripts so
each stage stays independently verifiable.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from lib.constants import AA_COMPOSITE_KEYS, AA_MEASURED_KEYS  # noqa: E402
from lib.whitelist import bench_band as _band  # noqa: E402  (SSOT)

AA_ROWS = REPO / "data" / ".leaderboard-snapshots" / "_aa-rows.json"

AA_COMPOSITE = (
    AA_COMPOSITE_KEYS  # SSOT: lib.constants (AA-definitional → authoritative)
)
AA_MEASURED = (
    AA_MEASURED_KEYS  # SSOT: lib.constants (AA measures; advisory cross-check)
)
COMPOSITE_TOL = 6.0  # pp disagreement that flags an AA-composite misfile
MEASURED_TOL = 8.0  # pp disagreement that flags an AA-measured candidate


def main() -> int:
    models = json.loads((REPO / "data" / "models.json").read_text(encoding="utf-8"))
    schema = json.loads(
        (REPO / "data" / "sources-whitelist.json").read_text(encoding="utf-8")
    )["_schema"]
    core = list(schema.get("coreBenchKeys") or [])

    aa_obs: dict[tuple[str, str], float] = {}
    if AA_ROWS.is_file():
        for o in json.loads(AA_ROWS.read_text(encoding="utf-8")).get(
            "observations", []
        ):
            aa_obs[(o["modelId"], o["benchKey"])] = o["value"]

    composite_misfiles = []
    measured_candidates = []
    band_violations = []
    crossbench_dups = []

    for m in models:
        mid = m["id"]
        bench = m.get("bench") or {}
        # 1. AA cross-check
        for bk, cur in bench.items():
            if cur is None:
                continue
            aav = aa_obs.get((mid, bk))
            if aav is None:
                continue
            delta = round(abs(cur - aav), 2)
            if bk in AA_COMPOSITE and delta > COMPOSITE_TOL:
                composite_misfiles.append(
                    {
                        "modelId": mid,
                        "benchKey": bk,
                        "current": cur,
                        "aa": aav,
                        "delta": delta,
                    }
                )
            elif bk in AA_MEASURED and delta > MEASURED_TOL:
                measured_candidates.append(
                    {
                        "modelId": mid,
                        "benchKey": bk,
                        "current": cur,
                        "aa": aav,
                        "delta": delta,
                    }
                )
        # 2. band/scale violations
        for bk, cur in bench.items():
            if cur is None:
                continue
            lo, hi = _band(schema, bk)
            if not (lo <= cur <= hi):
                band_violations.append(
                    {"modelId": mid, "benchKey": bk, "value": cur, "band": [lo, hi]}
                )
        # 3. cross-bench duplicate values (core benches only, ignore 0)
        seen: dict[float, list[str]] = {}
        for bk in core:
            v = bench.get(bk)
            if v is None or v == 0:
                continue
            seen.setdefault(v, []).append(bk)
        for v, keys in seen.items():
            if len(keys) >= 2:
                crossbench_dups.append(
                    {"modelId": mid, "value": v, "benchKeys": sorted(keys)}
                )

    report = {
        "_summary": {
            "compositeMisfiles": len(composite_misfiles),
            "measuredCandidates": len(measured_candidates),
            "bandViolations": len(band_violations),
            "crossBenchDups": len(crossbench_dups),
            "aaRowsLoaded": len(aa_obs),
        },
        "compositeMisfiles": sorted(composite_misfiles, key=lambda x: -x["delta"]),
        "measuredCandidates": sorted(measured_candidates, key=lambda x: -x["delta"]),
        "bandViolations": band_violations,
        "crossBenchDups": crossbench_dups,
    }
    out = REPO / "data" / "_misfile-audit.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    s = report["_summary"]
    print(
        f"=== MISFILE AUDIT === composite-misfiles={s['compositeMisfiles']} "
        f"measured-candidates={s['measuredCandidates']} band-violations={s['bandViolations']} "
        f"cross-bench-dups={s['crossBenchDups']} (aa_rows={s['aaRowsLoaded']})"
    )
    if "--verbose" in sys.argv:
        print("\n-- AA-COMPOSITE MISFILES (AA authoritative; will be corrected) --")
        for r in report["compositeMisfiles"]:
            print(
                f"  {r['modelId']}.{r['benchKey']}: current={r['current']} -> AA={r['aa']} (Δ{r['delta']})"
            )
        print("\n-- AA-MEASURED CANDIDATES (advisory; verify before change) --")
        for r in report["measuredCandidates"]:
            print(
                f"  {r['modelId']}.{r['benchKey']}: current={r['current']} vs AA={r['aa']} (Δ{r['delta']})"
            )
        print("\n-- BAND VIOLATIONS --")
        for r in report["bandViolations"]:
            print(f"  {r['modelId']}.{r['benchKey']}={r['value']} outside {r['band']}")
        print("\n-- CROSS-BENCH DUPLICATES --")
        for r in report["crossBenchDups"]:
            print(f"  {r['modelId']}: {r['value']} under {r['benchKeys']}")
    print(f"report: {out}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    raise SystemExit(main())
