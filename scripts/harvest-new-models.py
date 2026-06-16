#!/usr/bin/env python3
"""Systematic new-model detection — harvest EVERY new-model signal from EVERY
artifact and union them into .aicodermap-lineup.json's newModels[].

Two signal channels, both source-agnostic:
  1. `lineupHints[event='new']`  — incidental sightings a gather agent emits
     while researching its model slice.
  2. `lineupChanges.new[]`       — the dedicated Phase-0 WebSearch new-release
     net (agent.md step 3b) + vendor-lineup diff.

Root cause this fixes:
  - 2026-06-06: detection depended SOLELY on the lineup agent's vendor-page fetch.
    When that page is SPA/403/dead and the WebSearch fallback misses the release,
    a genuinely-new model is silently dropped even though a gather agent SAW it
    (channel 1, e.g. minimax-m3).
  - 2026-06-16: channel 2 (`lineupChanges.new`) had NO path to newModels[] at all.
    local-synth.py drops it, gen_unified_artifact.py copies synth verbatim, and
    this harvest only read `lineupHints`. So a model surfaced ONLY by the WebSearch
    new-release net (the safety net for broken vendor pages) never became a stub.
    Now BOTH channels are unioned from gather + synth + agent-out artifacts.

`lineupChanges.new` entries carry richer evidence (suggestedId, vendor,
evidenceUrl, evidenceConfidence) which the stub-add evidence gate uses to admit
officially-announced models on a single source. Idempotent. Non-fatal. Run after
gather, before stub-add. Stdlib only.
"""

import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _artifact_paths() -> list[str]:
    """Every artifact that may carry a new-model signal — gather batches plus the
    synth + final unified outputs (source-agnostic: any single source failing
    must not suppress detection)."""
    paths = glob.glob(str(ROOT / ".aicodermap-agent-out-*.gather.json"))
    for extra in (".aicodermap-agent-out-synth.json", ".aicodermap-agent-out.json"):
        p = ROOT / extra
        if p.exists():
            paths.append(str(p))
    return paths


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
    for f in _artifact_paths():
        try:
            d = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            continue

        # Channel 1 — incidental gather sightings.
        for h in d.get("lineupHints", []) or []:
            if h.get("event") != "new":
                continue
            mid = h.get("modelId")
            if not mid or mid in already:
                continue
            already.add(mid)
            new_models.append(
                {
                    "id": mid,
                    "name": mid,  # display name resolved at stub-add time
                    "provider": None,
                    "released": None,
                    "evidenceUrl": h.get("evidence"),
                    "evidenceConfidence": "gather-hint",
                    "notes": h.get("details", ""),
                    "source": "gatherLineupHint",
                }
            )
            harvested.append((mid, "lineupHint", h.get("evidence")))

        # Channel 2 — dedicated WebSearch new-release net / lineup diff.
        lc = d.get("lineupChanges") or {}
        for n in lc.get("new", []) or []:
            mid = n.get("suggestedId") or n.get("id")
            if not mid or mid in already:
                continue
            already.add(mid)
            new_models.append(
                {
                    "id": mid,
                    "name": n.get("name") or mid,
                    "provider": n.get("vendor") or n.get("provider"),
                    "released": n.get("released"),
                    "evidenceUrl": n.get("evidenceUrl") or n.get("evidence"),
                    "evidenceConfidence": n.get("evidenceConfidence")
                    or "newReleaseProbe",
                    "notes": n.get("notes") or n.get("observedVersion") or "",
                    "source": n.get("source") or "lineupChanges.new",
                }
            )
            harvested.append((mid, "lineupChanges.new", n.get("evidenceUrl")))

    if harvested:
        lineup_path.write_text(
            json.dumps(lineup, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        for mid, channel, ev in harvested:
            print(f"  + harvested new model [{channel}]: {mid}  ({ev})")
    print(f"=== HARVEST === new models added: {len(harvested)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
