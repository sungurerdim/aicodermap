#!/usr/bin/env python3
"""Apply anomaly-verify research verdicts (Layer 3 auto-resolution, 2026-05-27).

Closes the loop: an anomaly-verify research agent (agent.md scope=anomaly-verify)
investigates the cells in data/_anomalies.json and writes verdicts to
`.aicodermap-anomaly-verdicts.json`; this script applies the SAFE, MECHANICAL
ones to data/{models,sources}.json. It is the generic, verdict-driven form of
the one-off migrate-cfelo-metric.py.

Verdict shape (one per resolved cell):
  {"modelId","benchKey","action": <confirm|reclassify|clear>, ...}
  - confirm    : value is a real, correctly-classified result → clear any
                 benchQuarantine flag on the cell so it counts. (evidence req.)
  - reclassify : value belongs to a different cell (metric/scale misfile) →
                 {"toBench": "<key>"}: move the value + its provenance there,
                 remove the original cell + quarantine flag.
  - clear      : value is wrong/unverifiable/wrong-model → remove cell + sources
                 + quarantine flag.
VALUE-ACCURACY corrections (a cell whose value is simply wrong) are NOT applied
here — they route through the normal gather→merge path so trustScore + provenance
are computed correctly. This script only does classification/quarantine fixes
(no provenance fabrication).

Stdlib-only. Idempotent. Rotates .bak. Run after the anomaly-verify agent,
before merge.py re-runs its audit.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "data" / "models.json"
SOURCES = ROOT / "data" / "sources.json"
VERDICTS = ROOT / ".aicodermap-anomaly-verdicts.json"


def main() -> int:
    if not VERDICTS.exists():
        print("no verdicts file; nothing to apply")
        return 0
    verdicts = (json.loads(VERDICTS.read_text(encoding="utf-8")) or {}).get(
        "verdicts"
    ) or []
    models = json.loads(MODELS.read_text(encoding="utf-8"))
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))
    by_id = {m.get("id"): m for m in models}
    applied = {"confirm": 0, "reclassify": 0, "clear": 0, "skipped": 0}

    for v in verdicts:
        mid, bk, action = v.get("modelId"), v.get("benchKey"), v.get("action")
        m = by_id.get(mid)
        if not m or not bk or action not in ("confirm", "reclassify", "clear"):
            applied["skipped"] += 1
            continue
        bench = m.setdefault("bench", {})
        bq = m.get("benchQuarantine") or {}

        if action == "confirm":
            bq.pop(bk, None)  # verified → un-quarantine
            applied["confirm"] += 1
        elif action == "clear":
            bench.pop(bk, None)
            bq.pop(bk, None)
            sources.pop(f"{mid}.{bk}", None)
            applied["clear"] += 1
        elif action == "reclassify":
            to = v.get("toBench")
            if not to:
                applied["skipped"] += 1
                continue
            val = bench.get(bk)
            # SAFETY: only move into an EMPTY destination — never overwrite an
            # already-populated (correctly-sourced) cell. If the destination is
            # filled, the misfiled value is simply dropped (the correct value stays).
            if val is not None and bench.get(to) is None:
                bench[to] = val
                ent = sources.pop(f"{mid}.{bk}", None)
                if ent is not None:
                    sources.setdefault(f"{mid}.{to}", [])
                    sources[f"{mid}.{to}"].extend(ent)
            else:
                sources.pop(f"{mid}.{bk}", None)
            bench.pop(bk, None)
            bq.pop(bk, None)
            applied["reclassify"] += 1

        if "benchQuarantine" in m:
            m["benchQuarantine"] = bq

    shutil.copy2(MODELS, MODELS.with_suffix(".json.bak"))
    shutil.copy2(SOURCES, SOURCES.with_suffix(".json.bak"))
    MODELS.write_text(
        json.dumps(models, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    SOURCES.write_text(
        json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"=== APPLY VERDICTS === {applied}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
