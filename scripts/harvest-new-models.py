#!/usr/bin/env python3
"""Systematic new-model detection — harvest `lineupHints[event='new']` from EVERY
gather artifact and union them into .aicodermap-lineup.json's newModels[].

Root cause this fixes (2026-06-06): new-model detection depended SOLELY on the
dedicated lineup agent's vendor-page fetch. When that page is SPA/403/dead and the
WebSearch fallback misses the release, a genuinely-new model is silently dropped —
even though a gather agent researching that vendor's slice SAW it and emitted a
lineupHint. Example: minimax-m3 (released 2026-06-01, SWE-Pro 59.0) was flagged by
batch04-minimax's gather but never reached newModels[] because the orchestrator
only read the lineup file. Now ANY agent that spots a new model on any page surfaces
it, and this harvest reconciles all sources against currentIds.

Idempotent. Non-fatal. Run after gather, before stub-add. Stdlib only.
"""

import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    models = json.loads((ROOT / "data" / "models.json").read_text(encoding="utf-8"))
    ms = models["models"] if isinstance(models, dict) else models
    current = {m["id"] for m in ms}

    lineup_path = ROOT / ".aicodermap-lineup.json"
    lineup = (
        json.loads(lineup_path.read_text(encoding="utf-8"))
        if lineup_path.exists()
        else {"lineup": {}, "newModels": [], "gaps": []}
    )
    new_models = lineup.setdefault("newModels", [])
    already = {n.get("id") for n in new_models} | current

    harvested = []
    for f in glob.glob(str(ROOT / ".aicodermap-agent-out-batch*.gather.json")):
        try:
            d = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            continue
        for h in d.get("lineupHints", []) or []:
            if h.get("event") != "new":
                continue
            mid = h.get("modelId")
            if not mid or mid in already:
                continue
            already.add(mid)
            entry = {
                "id": mid,
                "name": mid,  # display name resolved at stub-add time
                "provider": None,
                "released": None,
                "evidenceUrl": h.get("evidence"),
                "evidenceConfidence": "gather-hint",
                "notes": h.get("details", ""),
                "source": "gatherLineupHint",
            }
            new_models.append(entry)
            harvested.append((mid, h.get("evidence")))

    if harvested:
        lineup_path.write_text(
            json.dumps(lineup, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        for mid, ev in harvested:
            print(f"  + harvested new model from gather hint: {mid}  ({ev})")
    print(f"=== HARVEST === gather-discovered new models added: {len(harvested)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
