#!/usr/bin/env python3
"""Convert flat gather artifacts (.gather.json) to OUTPUT_SCHEMA format.

Reads all .aicodermap-agent-out-batch*.gather.json files, applies
tier-based winner selection (I > S > C), detects contradictions,
and writes .aicodermap-agent-out-synth.json ready for gen_unified_artifact.py.

FAZ 4.C fallback: used when the synth agent exceeds output-token limits.
"""

from __future__ import annotations

import datetime
import glob
import json
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
GATHER_GLOB = str(ROOT / ".aicodermap-agent-out-batch*.gather.json")
OUT_PATH = ROOT / ".aicodermap-agent-out-synth.json"
TODAY = datetime.date.today().isoformat()
NOW_ISO = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

TIER_WEIGHT: dict[str, float] = {"I": 1.0, "S": 0.7, "C": 0.4}
CORE_BENCH_KEYS = frozenset(
    {
        "sweV",
        "gpqa",
        "lcb",
        "aaIdx",
        "tb2",
        "hle",
        "swePro",
        "mmluPro",
        "tau2",
        "aime26",
    }
)

# Model ID corrections: gather agents emitted wrong IDs for some models.
ID_FIXES: dict[str, str | None] = {
    "kimi-k2": "kimi-k2-6",
    "step-3-5": "step-3-5-flash",
    "grok-3-5": None,  # model does not exist; observations discarded
}


def _fix_id(mid: str) -> str | None:
    return ID_FIXES.get(mid, mid)


def _tier_w(obs: dict) -> float:
    return TIER_WEIGHT.get(obs.get("tier", "C"), 0.4)


def _pick_winner(obs_list: list[dict]) -> tuple[float | None, list[dict]]:
    valid = [o for o in obs_list if o.get("value") is not None]
    if not valid:
        return None, []
    # Group by value to count verifications per candidate value.
    val_sources: dict[float, list[dict]] = defaultdict(list)
    for o in valid:
        val_sources[o["value"]].append(o)
    best_val: float | None = None
    best_score = -1.0
    for val, srcs in val_sources.items():
        top_tw = max(_tier_w(s) for s in srcs)
        score = top_tw * min(len(srcs), 3) / 3
        if score > best_score:
            best_score = score
            best_val = val
    return best_val, valid


def _detect_contradiction(obs_list: list[dict]) -> tuple[float, str] | None:
    valid_vals = [o["value"] for o in obs_list if o.get("value") is not None]
    if len(valid_vals) < 2:
        return None
    delta = max(valid_vals) - min(valid_vals)
    if delta < 3:
        return None
    severity = "RED" if delta >= 5 else "YELLOW"
    return delta, severity


def main() -> int:
    paths = sorted(glob.glob(GATHER_GLOB))
    artifacts: list[tuple[str, dict]] = []
    for p in paths:
        try:
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
            if data.get("mode") == "gather":
                artifacts.append((p, data))
                print(
                    f"  loaded {Path(p).name} ({len(data.get('observations') or [])} obs)"
                )
        except Exception as e:
            print(f"  ⚠ skipping {p}: {e}")

    if not artifacts:
        print("⚠ no gather artifacts found — nothing to synthesize")
        return 1

    print(f"\nLoaded {len(artifacts)} gather artifacts")

    # ── Pool all data ──────────────────────────────────────────────────────────
    all_obs: dict[tuple[str, str], list[dict]] = defaultdict(list)
    model_meta: dict[str, dict] = {}
    pricing_obs: dict[str, list[dict]] = defaultdict(list)
    ollama_obs: dict[str, dict] = {}
    unsloth_obs: dict[str, list[dict]] = defaultdict(list)
    lineup_new_raw: list[dict] = []
    lineup_deprecated_raw: list[dict] = []
    na_candidates: dict[str, list[tuple[str, str]]] = defaultdict(list)
    raw_gaps: list[dict] = []

    for _path, data in artifacts:
        for obs in data.get("observations") or []:
            mid = _fix_id(obs.get("modelId") or "")
            bk = obs.get("benchKey") or ""
            if not mid or not bk or bk not in CORE_BENCH_KEYS:
                continue
            if obs.get("value") is not None:
                all_obs[(mid, bk)].append({**obs, "modelId": mid})

        for mm in data.get("modelMeta") or []:
            mid = _fix_id(mm.get("modelId") or "")
            if not mid:
                continue
            existing = model_meta.setdefault(mid, {})
            for k, v in mm.items():
                if k != "modelId" and v is not None:
                    existing.setdefault(k, v)

        for po in data.get("pricingObs") or []:
            mid = _fix_id(po.get("modelId") or "")
            if mid and po.get("in") is not None and po.get("out") is not None:
                pricing_obs[mid].append({**po, "modelId": mid})

        for oo in data.get("ollamaObs") or []:
            mid = _fix_id(oo.get("modelId") or "")
            if mid and mid not in ollama_obs:
                ollama_obs[mid] = oo

        for uo in data.get("unslothObs") or []:
            mid = _fix_id(uo.get("modelId") or "")
            if mid:
                unsloth_obs[mid].append(uo)

        for lh in data.get("lineupHints") or []:
            event = lh.get("event")
            mid = _fix_id(lh.get("modelId") or "")
            if not mid:
                continue
            if event == "new":
                lineup_new_raw.append(
                    {
                        "id": mid,
                        "vendor": "unknown",
                        "evidenceUrl": lh.get("evidence", ""),
                    }
                )
            elif event == "deprecated":
                lineup_deprecated_raw.append(
                    {
                        "id": mid,
                        "deprecationDate": TODAY,
                        "evidenceUrl": lh.get("evidence", ""),
                    }
                )

        for nc in data.get("naCandidates") or []:
            mid = _fix_id(nc.get("modelId") or "")
            bk = nc.get("benchKey") or ""
            if mid and bk:
                na_candidates[mid].append((bk, nc.get("rationale", "")))

        for rg in data.get("rawGaps") or []:
            mid = _fix_id(rg.get("modelId") or "")
            bk = rg.get("benchKey") or ""
            if mid and bk:
                raw_gaps.append(
                    {
                        "key": f"{mid}.{bk}",
                        "reason": "Not found after exhaustive search",
                        "triedSources": rg.get("triedSources") or [],
                        "triedQueries": rg.get("triedQueries") or [],
                        "triedFormats": ["static_html_table", "spa_full"],
                        "source": "agent",
                    }
                )

    # ── Load tracked model IDs ────────────────────────────────────────────────
    models_json_path = ROOT / "data" / "models.json"
    with open(models_json_path, encoding="utf-8") as f:
        models_json = json.load(f)
    tracked_ids: set[str] = {m["id"] for m in models_json if isinstance(m, dict)}

    all_seen_ids = tracked_ids | set(model_meta) | {mid for (mid, _) in all_obs}
    # models[] only contains tracked IDs; untracked IDs go to newModels[]
    tracked_seen_ids = tracked_ids & all_seen_ids
    untracked_seen_ids = all_seen_ids - tracked_ids

    # ── Build models[] (tracked only) ────────────────────────────────────────
    contradictions: list[dict] = []
    models_out: list[dict] = []

    for mid in sorted(tracked_seen_ids):
        bench: dict[str, float] = {}
        sources_added: list[dict] = []
        na_list: list[dict] = []

        for bk in CORE_BENCH_KEYS:
            obs_list = all_obs.get((mid, bk), [])
            # Contradiction check
            contra = _detect_contradiction(obs_list)
            if contra:
                delta, severity = contra
                best_obs = max(obs_list, key=_tier_w)
                contradictions.append(
                    {
                        "modelId": mid,
                        "field": bk,
                        "candidates": [
                            {
                                "value": o["value"],
                                "source": o.get("sourceUrl", ""),
                                "url": o.get("sourceUrl", ""),
                                "tier": o.get("tier", "C"),
                                "fetched": o.get("fetched", TODAY),
                                "verifications": 1,
                                "trustScore": _tier_w(o),
                            }
                            for o in obs_list
                            if o.get("value") is not None
                        ],
                        "delta": round(delta, 2),
                        "severity": severity,
                        "autoResolveWinner": {
                            "value": best_obs["value"],
                            "trustScore": _tier_w(best_obs),
                            "sourceUrl": best_obs.get("sourceUrl", ""),
                            "tier": best_obs.get("tier", "C"),
                        },
                    }
                )

            winner_val, valid_obs = _pick_winner(obs_list)
            if winner_val is not None:
                bench[bk] = winner_val
                best_obs = max(valid_obs, key=_tier_w)
                sources_added.append(
                    {
                        "key": f"{mid}.{bk}",
                        "value": winner_val,
                        "source": best_obs.get("sourceUrl", ""),
                        "url": best_obs.get("sourceUrl", ""),
                        "tier": best_obs.get("tier", "C"),
                        "fetched": best_obs.get("fetched", TODAY),
                        "verifications": len(valid_obs),
                        "trustScore": round(
                            _tier_w(best_obs) * min(len(valid_obs), 3) / 3, 4
                        ),
                    }
                )

        # NA entries
        seen_na_keys: set[str] = set()
        for bk, rationale in na_candidates.get(mid, []):
            if bk not in bench and bk not in seen_na_keys:
                na_list.append({"benchKey": bk, "rule": rationale[:120]})
                seen_na_keys.add(bk)

        # Pricing
        pricing_api = [
            {
                "provider": po.get("provider", "unknown"),
                "in": po["in"],
                "out": po["out"],
                "cacheHit": po.get("cacheHit"),
                "throughput": po.get("throughput"),
                "url": po.get("url", ""),
                "fetched": po.get("fetched", TODAY),
            }
            for po in pricing_obs.get(mid, [])
        ]

        # Ollama
        ollama = None
        if mid in ollama_obs:
            oo = ollama_obs[mid]
            ollama = {
                "pullCmd": oo.get("pullCmd", ""),
                "tags": oo.get("tags") or [],
                "pullCount": oo.get("pullCount"),
                "architecture": None,
                "parameters": None,
                "license": None,
                "releasedISO": None,
                "ollamaUrl": oo.get("ollamaUrl", ""),
            }

        # Unsloth
        unsloth = [
            {"name": uo.get("name"), "size": uo.get("size"), "vram": uo.get("vram")}
            for uo in unsloth_obs.get(mid, [])
        ]

        if not bench and not pricing_api and mid not in model_meta:
            continue  # nothing to update for this model

        mm = model_meta.get(mid, {})
        updates: dict = {"lastUpdated": TODAY}
        if bench:
            updates["bench"] = bench
        if pricing_api:
            updates["pricing"] = {"api": pricing_api}
        if ollama:
            updates["ollama"] = ollama
        if unsloth:
            updates["unslothVariants"] = unsloth
        for field in (
            "context",
            "license",
            "open",
            "released",
            "providers",
            "vramRequirement",
        ):
            if mm.get(field) is not None:
                updates[field] = mm[field]

        models_out.append(
            {
                "id": mid,
                "updates": updates,
                "notApplicable": na_list,
                "sourcesAdded": sources_added,
            }
        )

    # ── newModels[] — IDs found in gather but NOT in models.json ─────────────
    new_model_ids = sorted(
        mid
        for mid in untracked_seen_ids
        if any(all_obs.get((mid, bk)) for bk in CORE_BENCH_KEYS)
        or model_meta.get(mid)
        or pricing_obs.get(mid)
    )
    new_models_out: list[dict] = []
    for mid in new_model_ids:
        bench = {}
        sources_added = []
        for bk in CORE_BENCH_KEYS:
            winner_val, valid_obs = _pick_winner(all_obs.get((mid, bk), []))
            if winner_val is not None:
                bench[bk] = winner_val
                best_obs = max(valid_obs, key=_tier_w)
                sources_added.append(
                    {
                        "key": f"{mid}.{bk}",
                        "value": winner_val,
                        "source": best_obs.get("sourceUrl", ""),
                        "url": best_obs.get("sourceUrl", ""),
                        "tier": best_obs.get("tier", "C"),
                        "fetched": best_obs.get("fetched", TODAY),
                        "verifications": len(valid_obs),
                        "trustScore": round(_tier_w(best_obs), 4),
                    }
                )
        pricing_api = [
            {
                "provider": po.get("provider", "unknown"),
                "in": po["in"],
                "out": po["out"],
                "cacheHit": po.get("cacheHit"),
                "throughput": po.get("throughput"),
                "url": po.get("url", ""),
                "fetched": po.get("fetched", TODAY),
            }
            for po in pricing_obs.get(mid, [])
        ]
        mm = model_meta.get(mid, {})
        if bench or pricing_api:
            updates = {"lastUpdated": TODAY}
            if bench:
                updates["bench"] = bench
            if pricing_api:
                updates["pricing"] = {"api": pricing_api}
            for field in ("context", "license", "open", "released"):
                if mm.get(field) is not None:
                    updates[field] = mm[field]
            new_models_out.append(
                {
                    "id": mid,
                    "updates": updates,
                    "notApplicable": [],
                    "sourcesAdded": sources_added,
                }
            )

    # ── Lineup dedup ──────────────────────────────────────────────────────────
    seen_new: set[str] = set()
    lineup_new_deduped: list[dict] = []
    for e in lineup_new_raw:
        eid = e.get("id")
        if eid and eid not in tracked_ids and eid not in seen_new:
            seen_new.add(eid)
            lineup_new_deduped.append(e)

    seen_dep: set[str] = set()
    lineup_dep_deduped: list[dict] = []
    for e in lineup_deprecated_raw:
        eid = e.get("id")
        if eid and eid not in seen_dep:
            seen_dep.add(eid)
            lineup_dep_deduped.append(e)

    # ── Gaps dedup ────────────────────────────────────────────────────────────
    gap_keys_seen: set[str] = set()
    gaps_deduped: list[dict] = []
    for g in raw_gaps:
        k = g.get("key")
        if k and k not in gap_keys_seen:
            gap_keys_seen.add(k)
            gaps_deduped.append(g)

    # ── Coverage counts ───────────────────────────────────────────────────────
    filled_cells = sum(
        len((m.get("updates") or {}).get("bench") or {}) for m in models_out
    )
    na_cells = sum(len(m.get("notApplicable") or []) for m in models_out)
    total_cells = len(tracked_ids) * len(CORE_BENCH_KEYS)

    # ── Emit ──────────────────────────────────────────────────────────────────
    output = {
        "confidence": "MEDIUM",
        "synthesis": (
            f"Gather-union from {len(artifacts)} batch artifacts. "
            f"{len(models_out)} models updated, {filled_cells} bench cells filled, "
            f"{len(contradictions)} contradictions, {len(new_models_out)} new models."
        ),
        "lineupChanges": {
            "new": lineup_new_deduped,
            "deprecated": lineup_dep_deduped,
            "renamed": [],
            "removed": [],
        },
        "models": models_out,
        "newModels": new_models_out,
        "contradictions": contradictions,
        "gaps": gaps_deduped,
        "coverageMatrix": {
            "totalCells": total_cells,
            "filledCells": filled_cells,
            "filledThisCycle": filled_cells,
            "gapsRecorded": len(gaps_deduped),
            "notApplicableCells": na_cells,
            "byBench": {},
            "byModel": {},
        },
        "validationCoverage": round(filled_cells / total_cells, 4)
        if total_cells
        else 0.0,
        "runMetadata": {
            "agentVersion": "gather-union-2026-05-13",
            "startedAt": NOW_ISO,
            "finishedAt": NOW_ISO,
            "elapsedMs": 0,
            "toolCallCount": 0,
            "fetchAttemptCount": 0,
            "batchCount": len(artifacts),
        },
        "error": None,
    }

    OUT_PATH.write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\nWritten: {OUT_PATH}")
    print(f"Models updated: {len(models_out)}")
    print(f"New models: {len(new_models_out)}")
    print(f"Contradictions: {len(contradictions)}")
    print(f"Gaps (agent-tried): {len(gaps_deduped)}")
    print(f"Bench fills: {filled_cells} / {total_cells} cells")
    print(
        f"Lineup new: {len(lineup_new_deduped)}, deprecated: {len(lineup_dep_deduped)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
