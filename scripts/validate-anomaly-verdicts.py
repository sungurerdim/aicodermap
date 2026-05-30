#!/usr/bin/env python3
"""Gate: every anomaly-verify verdict must be traceable before it mutates data.

Sibling of validate-synth-traceability.py, for the Layer-3 anomaly-verify loop.
apply-anomaly-verdicts.py mechanically applies confirm/reclassify/clear verdicts
to data/{models,sources}.json. A `reclassify` MOVES a value into a different
bench cell; a `confirm` UN-QUARANTINES a value so it counts in the composite.
Both are data-corrupting if the verdict is wrong — e.g. reclassifying a raw
Codeforces Elo (110-3500 scale) into a 0-100 percentage bench, or confirming a
value that lies outside every shred of evidence for its cell.

This gate classifies each verdict against the TARGET cell's evidence envelope:

  band      — _schema.benchRanges hard bounds for the target bench. A value
              outside is wrong-scale garbage (scale-corruption guard) → REJECT.
  envelope  — fresh gather obs ∪ historical data/sources.json values for the
              TARGET cell. If any evidence exists and the value lies outside
              [min - TOL, max + TOL] → REJECT (the value does not belong there).

Verdict-shape requirements (also enforced):
  reclassify → needs non-empty `toBench` AND `evidence`; value validated vs toBench.
  confirm    → needs `evidence`; current value validated vs its own (modelId,benchKey).
  clear      → needs a `reason`; removal is non-corrupting, so a missing reason
               is a WARNING, not a rejection.

Exit 0 = all verdicts pass (or rejected ones filtered out via --filter).
Exit 2 = at least one verdict rejected and NOT filtered. Stdlib-only. Idempotent.

Usage:
  python scripts/validate-anomaly-verdicts.py [--filter] [--quiet]
    --filter : rewrite .aicodermap-anomaly-verdicts.json keeping only the
               passing verdicts (rejected ones quarantined in the report), exit 0.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

VERDICTS_PATH = ROOT / ".aicodermap-anomaly-verdicts.json"
MODELS_PATH = ROOT / "data" / "models.json"
SOURCES_PATH = ROOT / "data" / "sources.json"
WHITELIST_PATH = ROOT / "data" / "sources-whitelist.json"
REPORT_PATH = ROOT / "data" / "_anomaly-verdict-traceability.json"

TOL = 0.5  # rounding tolerance at envelope edges (pp / Elo points).


def _to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _band(schema_block: dict, key: str) -> tuple[float, float]:
    """Hard plausibility band [hardMin, hardMax] for a bench key (SSOT: benchRanges)."""
    ranges = schema_block.get("benchRanges") or {}
    default = ranges.get("_default") or {"hardMin": 0, "hardMax": 100}
    r = ranges.get(key) or default
    return float(r.get("hardMin", 0)), float(r.get("hardMax", 100))


def _gather_observations() -> dict[tuple[str, str], list[float]]:
    """Fresh observations from this cycle's gather artifacts (stale excluded by glob)."""
    obs: dict[tuple[str, str], list[float]] = defaultdict(list)
    for p in sorted(ROOT.glob(".aicodermap-agent-out-batch*.gather.json")):
        try:
            art = json.load(open(p, encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for o in art.get("observations") or []:
            v = _to_float(o.get("value"))
            mid, bk = o.get("modelId"), o.get("benchKey")
            if v is not None and mid and bk:
                obs[(mid, bk)].append(v)
    return obs


def _historical_values() -> dict[tuple[str, str], list[float]]:
    """Every prior provenance value, keyed by cell."""
    hist: dict[tuple[str, str], list[float]] = defaultdict(list)
    if not SOURCES_PATH.is_file():
        return hist
    data = json.load(open(SOURCES_PATH, encoding="utf-8"))
    for full_key, entries in data.items():
        if "." not in full_key or not isinstance(entries, list):
            continue
        mid, bk = full_key.split(".", 1)
        for e in entries:
            v = _to_float(e.get("value"))
            if v is not None:
                hist[(mid, bk)].append(v)
    return hist


def _check_value(
    value: float,
    target_mid: str,
    target_bk: str,
    schema_block: dict,
    fresh: dict[tuple[str, str], list[float]],
    hist: dict[tuple[str, str], list[float]],
) -> str | None:
    """Return a rejection reason string, or None if the value is traceable to
    the target cell (band + evidence envelope)."""
    lo, hi = _band(schema_block, target_bk)
    if value < lo or value > hi:
        return f"outside-band[{target_bk}:{lo:g}-{hi:g}]"
    cands = list(fresh.get((target_mid, target_bk), [])) + list(
        hist.get((target_mid, target_bk), [])
    )
    if cands:
        clo, chi = min(cands), max(cands)
        if value < clo - TOL or value > chi + TOL:
            return f"outside-envelope[{round(clo, 2)}-{round(chi, 2)}]"
    return None


def classify(
    verdicts: list[dict],
    models: list[dict],
    schema_block: dict,
    fresh: dict[tuple[str, str], list[float]],
    hist: dict[tuple[str, str], list[float]],
) -> dict:
    by_id = {m.get("id"): m for m in models}
    passing: list[dict] = []
    rejected: list[dict] = []
    warnings: list[dict] = []
    checked = 0

    for v in verdicts:
        mid = v.get("modelId")
        bk = v.get("benchKey")
        action = v.get("action")
        m = by_id.get(mid)
        cell = f"{mid}.{bk}"

        if not m or not bk or action not in ("confirm", "reclassify", "clear"):
            # Malformed verdict: apply-anomaly-verdicts.py would skip it anyway.
            warnings.append(
                {"cell": cell, "action": action, "reason": "malformed-or-unknown-model"}
            )
            passing.append(v)
            continue

        bench = m.get("bench") or {}

        if action == "clear":
            # Removal is non-corrupting; only require a reason for audit trail.
            if not (v.get("reason") or "").strip():
                warnings.append(
                    {"cell": cell, "action": "clear", "reason": "missing-reason"}
                )
            passing.append(v)
            continue

        if action == "confirm":
            checked += 1
            if not (v.get("evidence") or "").strip():
                rejected.append(
                    {"cell": cell, "action": "confirm", "reason": "missing-evidence"}
                )
                continue
            val = _to_float(bench.get(bk))
            if val is None:
                warnings.append(
                    {"cell": cell, "action": "confirm", "reason": "cell-empty-noop"}
                )
                passing.append(v)
                continue
            why = _check_value(val, mid, bk, schema_block, fresh, hist)
            if why:
                rejected.append(
                    {"cell": cell, "action": "confirm", "value": val, "reason": why}
                )
            else:
                passing.append(v)
            continue

        # reclassify
        checked += 1
        to = (v.get("toBench") or "").strip()
        if not to or not (v.get("evidence") or "").strip():
            rejected.append(
                {
                    "cell": cell,
                    "action": "reclassify",
                    "reason": "missing-toBench-or-evidence",
                }
            )
            continue
        val = _to_float(bench.get(bk))
        if val is None:
            warnings.append(
                {
                    "cell": cell,
                    "action": "reclassify",
                    "reason": "source-cell-empty-noop",
                }
            )
            passing.append(v)
            continue
        why = _check_value(val, mid, to, schema_block, fresh, hist)
        if why:
            rejected.append(
                {
                    "cell": cell,
                    "action": "reclassify",
                    "toBench": to,
                    "value": val,
                    "reason": why,
                }
            )
        else:
            passing.append(v)

    return {
        "checked": checked,
        "passing": passing,
        "rejected": rejected,
        "warnings": warnings,
        "ok": len(rejected) == 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Anomaly-verify verdict traceability gate."
    )
    ap.add_argument(
        "--filter",
        action="store_true",
        help="Rewrite the verdicts file keeping only passing verdicts (rejected "
        "ones quarantined in the report), then exit 0.",
    )
    ap.add_argument(
        "--quiet", action="store_true", help="Suppress per-verdict listing."
    )
    args = ap.parse_args()

    if not VERDICTS_PATH.is_file():
        print("no verdicts file; nothing to validate")
        return 0
    verdicts = (json.loads(VERDICTS_PATH.read_text(encoding="utf-8")) or {}).get(
        "verdicts"
    ) or []
    if not verdicts:
        print("verdicts file empty; nothing to validate")
        return 0

    models = json.loads(MODELS_PATH.read_text(encoding="utf-8"))
    try:
        schema_block = json.loads(WHITELIST_PATH.read_text(encoding="utf-8")).get(
            "_schema", {}
        )
    except (OSError, json.JSONDecodeError):
        schema_block = {}

    rep = classify(
        verdicts, models, schema_block, _gather_observations(), _historical_values()
    )

    REPORT_PATH.write_text(
        json.dumps(
            {
                "checked": rep["checked"],
                "rejected": rep["rejected"],
                "warnings": rep["warnings"],
                "ok": rep["ok"],
                "filtered": bool(args.filter and rep["rejected"]),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    rej, warn = rep["rejected"], rep["warnings"]
    print(
        f"=== ANOMALY VERDICT TRACEABILITY === checked={rep['checked']} "
        f"rejected={len(rej)} warnings={len(warn)} ok={rep['ok']}"
    )
    if rej and not args.quiet:
        print("  REJECTED (would corrupt live data — not applied):")
        for r in rej[:40]:
            to = f" -> {r['toBench']}" if r.get("toBench") else ""
            val = f" = {r['value']}" if "value" in r else ""
            print(f"    {r['cell']}{to}{val}  [{r['action']}: {r['reason']}]")
    if warn and not args.quiet:
        print("  WARNINGS (applied as-is, audit only):")
        for w in warn[:40]:
            print(f"    {w['cell']}  [{w['action']}: {w['reason']}]")
    print(f"  report: {REPORT_PATH}")

    if args.filter and rej:
        VERDICTS_PATH.write_text(
            json.dumps({"verdicts": rep["passing"]}, indent=2, ensure_ascii=False)
            + "\n",
            encoding="utf-8",
        )
        print(f"  --filter: kept {len(rep['passing'])} verdict(s), dropped {len(rej)}")
        return 0

    return 0 if rep["ok"] else 2


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    raise SystemExit(main())
