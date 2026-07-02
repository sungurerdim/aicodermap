#!/usr/bin/env python3
"""Gate: every synth bench value must trace to real evidence.

Defect guarded (cycle 2026-05-28): the FAZ 4.C Stage-B sonnet synth FABRICATED
bench values — numbers present in NO gather observation, attributed to real
URLs, contradicting the gathered evidence (e.g. opus-4-7.hle=11.6 when the only
observation was 54.7; grok-4-20.sweV=90.1 with no observation at all). The LLM
synth must pick a trust-winner FROM the gathered candidates, never invent one.

This gate classifies every non-null `models[].updates.bench[k]` in the synth
artifact against the evidence envelope for its (modelId, benchKey) cell:

  candidates = this cycle's fresh gather observations
             ∪ historical data/sources.json values for the cell

  FABRICATION  — candidates non-empty but value lies OUTSIDE
                 [min(candidates) - TOL, max(candidates) + TOL]; or candidates
                 empty while value is non-null (a value with zero evidence).
                 The in-envelope allowance covers a legitimate trust-weighted
                 point estimate between candidates (local-synth's bayesianPoint).
  DIVERGENCE   — grounded (in-envelope) yet disagrees with THIS cycle's fresh
                 observation consensus by > CONTRADICTION_WARN_PP. Advisory:
                 surfaced for the Step 7.7 anomaly->research loop, never blocks.

Scale-agnostic: the envelope is the cell's own candidate range, so cfElo /
webDevElo / 0-100 benches all validate without special-casing.

Exit 0 = clean (or recovered via --auto-fallback). Exit 2 = fabrication present
and not recovered. Stdlib + sys.path-resolved imports. Idempotent.

Usage:
  python scripts/validate-synth-traceability.py [--auto-fallback] [--quiet]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from lib.tiers import is_pseudo_source  # type: ignore  # noqa: E402
from lib.whitelist import contracts  # type: ignore  # noqa: E402
from lib.constants import GATHER_BATCH_GLOB  # noqa: E402
from lib.util import configure_utf8_output  # noqa: E402

SYNTH_PATH = ROOT / ".aicodermap-agent-out-synth.json"
SOURCES_PATH = ROOT / "data" / "sources.json"
WHITELIST_PATH = ROOT / "data" / "sources-whitelist.json"
REPORT_PATH = ROOT / "data" / "_synth-traceability.json"
LOCAL_SYNTH = ROOT / "scripts" / "local-synth.py"

TOL = 0.5  # rounding tolerance at envelope edges (pp / Elo points).


def _to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _gather_observations() -> dict[tuple[str, str], list[float]]:
    """Fresh observations from this cycle's gather artifacts (stale excluded by glob)."""
    obs: dict[tuple[str, str], list[float]] = defaultdict(list)
    for p in sorted(ROOT.glob(GATHER_BATCH_GLOB)):
        try:
            with open(p, encoding="utf-8") as _f:
                art = json.load(_f)
        except (OSError, json.JSONDecodeError):
            continue
        for o in art.get("observations") or []:
            v = _to_float(o.get("value"))
            mid, bk = o.get("modelId"), o.get("benchKey")
            if v is not None and mid and bk:
                obs[(mid, bk)].append(v)
    return obs


def _prior_fabricated_cells() -> set[str]:
    """Cells the PRIOR cycle's report flagged as fabricated. Reading the report
    BEFORE this run overwrites it gives last cycle's verdict — a value that was
    fabricated once must not anchor this cycle's envelope (5.2 contamination)."""
    flagged: set[str] = set()
    if not REPORT_PATH.is_file():
        return flagged
    try:
        rep = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return flagged
    for key in ("fabricated", "fabricatedBeforeFallback"):
        for f in rep.get(key) or []:
            cell = f.get("cell") if isinstance(f, dict) else None
            if cell:
                flagged.add(cell)
    return flagged


def _historical_values() -> dict[tuple[str, str], list[float]]:
    """Prior provenance values per cell, with the contamination sources EXCLUDED
    (5.2): pseudo-source entries (snapshot-extraction / synth-backfill / auto-
    resolution candidate) and any cell the prior cycle flagged as fabricated do
    NOT widen the envelope — otherwise a once-fabricated value re-validates itself
    forever (historical contamination bypass). This makes the gate stricter."""
    hist: dict[tuple[str, str], list[float]] = defaultdict(list)
    if not SOURCES_PATH.is_file():
        return hist
    fabricated = _prior_fabricated_cells()
    with open(SOURCES_PATH, encoding="utf-8") as _f:
        data = json.load(_f)
    for full_key, entries in data.items():
        if "." not in full_key or not isinstance(entries, list):
            continue
        if full_key in fabricated:
            continue  # cell was fabricated last cycle — its history is suspect
        mid, bk = full_key.split(".", 1)
        for e in entries:
            if not isinstance(e, dict) or is_pseudo_source(e):
                continue  # pseudo-source: never anchors the envelope
            v = _to_float(e.get("value"))
            if v is not None:
                hist[(mid, bk)].append(v)
    return hist


def _consensus(values: list[float]) -> float:
    s = sorted(values)
    return s[len(s) // 2]  # median-ish (lower median for even n)


def classify(
    synth: dict,
    fresh: dict[tuple[str, str], list[float]],
    hist: dict[tuple[str, str], list[float]],
    warn_pp: float,
) -> dict:
    """Return {fabricated[], divergences[], checked, ok}."""
    fabricated: list[dict] = []
    divergences: list[dict] = []
    checked = 0
    for m in synth.get("models") or []:
        mid = m.get("id")
        bench = (m.get("updates") or {}).get("bench") or {}
        for bk, raw in bench.items():
            val = _to_float(raw)
            if val is None:
                continue
            checked += 1
            key = (mid, bk)
            cands = list(fresh.get(key, [])) + list(hist.get(key, []))
            if not cands:
                fabricated.append(
                    {"cell": f"{mid}.{bk}", "value": val, "reason": "no-evidence"}
                )
                continue
            lo, hi = min(cands), max(cands)
            if val < lo - TOL or val > hi + TOL:
                fabricated.append(
                    {
                        "cell": f"{mid}.{bk}",
                        "value": val,
                        "reason": "outside-envelope",
                        "envelope": [round(lo, 2), round(hi, 2)],
                    }
                )
                continue
            # Grounded — check divergence from THIS cycle's fresh consensus.
            fv = fresh.get(key)
            if fv:
                fc = _consensus(fv)
                if abs(val - fc) > warn_pp:
                    divergences.append(
                        {
                            "cell": f"{mid}.{bk}",
                            "value": val,
                            "freshConsensus": round(fc, 2),
                            "freshObs": sorted(set(round(x, 2) for x in fv)),
                            "deltaPp": round(abs(val - fc), 2),
                        }
                    )
    return {
        "checked": checked,
        "fabricated": fabricated,
        "divergences": divergences,
        "ok": len(fabricated) == 0,
    }


def _validate_once(warn_pp: float) -> dict:
    with open(SYNTH_PATH, encoding="utf-8") as _f:
        synth = json.load(_f)
    return classify(synth, _gather_observations(), _historical_values(), warn_pp)


def main() -> int:
    ap = argparse.ArgumentParser(description="Synth bench-value traceability gate.")
    ap.add_argument(
        "--auto-fallback",
        action="store_true",
        help="On fabrication, regenerate the synth artifact via local-synth.py "
        "(deterministic, cannot hallucinate) and re-validate.",
    )
    ap.add_argument("--quiet", action="store_true", help="Suppress per-cell listing.")
    args = ap.parse_args()

    if not SYNTH_PATH.is_file():
        print(f"✗ synth artifact missing: {SYNTH_PATH.name}", file=sys.stderr)
        return 2

    try:
        with open(WHITELIST_PATH, encoding="utf-8") as _f:
            warn_pp = float(contracts(json.load(_f)).get("CONTRADICTION_WARN_PP", 3.0))
    except Exception:
        warn_pp = 3.0

    rep = _validate_once(warn_pp)
    recovered = False

    if not rep["ok"] and args.auto_fallback:
        print(
            f"⚠ FABRICATION GATE: {len(rep['fabricated'])} ungrounded synth value(s) "
            f"— regenerating via local-synth.py (deterministic fallback)",
            file=sys.stderr,
        )
        rc = subprocess.run([sys.executable, str(LOCAL_SYNTH)], cwd=ROOT).returncode
        if rc != 0:
            print(f"✗ local-synth fallback failed (exit {rc})", file=sys.stderr)
        else:
            rep_after = _validate_once(warn_pp)
            rep = {
                **rep_after,
                "fallbackApplied": True,
                "fabricatedBeforeFallback": rep["fabricated"],
            }
            recovered = rep_after["ok"]

    REPORT_PATH.write_text(
        json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    fab = rep["fabricated"]
    div = rep["divergences"]
    print(
        f"=== SYNTH TRACEABILITY === checked={rep['checked']} "
        f"fabricated={len(fab)} divergences={len(div)} "
        f"ok={rep['ok']}{' (recovered)' if recovered else ''}"
    )
    if fab and not args.quiet:
        print("  FABRICATED (ungrounded — would corrupt live data):")
        for f in fab[:40]:
            env = f.get("envelope")
            env_s = f" envelope={env}" if env else ""
            print(f"    {f['cell']} = {f['value']}  [{f['reason']}{env_s}]")
    if div and not args.quiet:
        print("  DIVERGENCES (grounded but disagree with fresh obs — advisory):")
        for d in div[:40]:
            print(
                f"    {d['cell']} = {d['value']}  fresh={d['freshConsensus']} "
                f"(Δ{d['deltaPp']}pp) obs={d['freshObs']}"
            )
    print(f"  report: {REPORT_PATH}")

    return 0 if rep["ok"] else 2


if __name__ == "__main__":
    configure_utf8_output()
    raise SystemExit(main())
