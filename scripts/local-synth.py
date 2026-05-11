#!/usr/bin/env python3
"""Deterministic synth fallback for when sonnet synth agent fails.

Groups flat gather observations into per-model unified artifact shape.
Applies trustScore formula and contradiction detection without LLM reasoning.
"""

from __future__ import annotations
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from lib.whitelist import contracts  # type: ignore
from lib.matrix import active_models  # type: ignore

TIER_WEIGHT = {"I": 1.0, "S": 0.7, "C": 0.4, "U": 0.1}


def recency_decay(d: str) -> float:
    try:
        dt = datetime.fromisoformat(d.replace("Z", ""))
        age = (datetime.utcnow() - dt).days
    except Exception:
        age = 999
    if age < 30:
        return 1.00
    if age < 90:
        return 0.85
    if age < 180:
        return 0.70
    if age < 365:
        return 0.50
    return 0.30


def trust_score(tier: str, verifications: int, dtstr: str) -> float:
    tw = TIER_WEIGHT.get(tier, 0.1)
    v = min(max(verifications, 1), 3) / 3.0
    return round(tw * v * recency_decay(dtstr), 4)


def find_batch_artifacts() -> list[Path]:
    return sorted(ROOT.glob(".aicodermap-agent-out-batch*.gather.json"))


def main() -> int:
    os.chdir(ROOT)
    with open("data/models.json", encoding="utf-8") as f:
        md = json.load(f)
    models = md if isinstance(md, list) else md.get("models", [])
    with open("data/sources-whitelist.json", encoding="utf-8") as f:
        wl = json.load(f)
    core_keys = wl["_schema"]["coreBenchKeys"]
    ctr = contracts(wl)
    agreement_pp = float(ctr.get("VERIFICATION_AGREEMENT_PP", 1.5))

    active = active_models(models)
    active_ids = {m["id"] for m in active}

    artifacts = find_batch_artifacts()
    print(f"Reading {len(artifacts)} gather artifacts")

    cells: dict[tuple, list] = defaultdict(list)
    all_pricing: dict[str, list] = defaultdict(list)
    all_ollama: dict[str, list] = defaultdict(list)
    all_unsloth: dict[str, list] = defaultdict(list)
    all_na_candidates: list = []
    all_raw_gaps: list = []
    all_lineup_hints: list = []
    runtime_total = {
        "batchesMerged": 0,
        "observationsTotal": 0,
        "pricingObsTotal": 0,
        "ollamaObsTotal": 0,
        "unslothObsTotal": 0,
        "naCandidatesTotal": 0,
        "rawGapsTotal": 0,
    }

    for p in artifacts:
        try:
            art = json.load(open(p, encoding="utf-8"))
        except Exception as e:
            print(f"  ! skip {p.name}: {e}")
            continue
        runtime_total["batchesMerged"] += 1
        for obs in art.get("observations") or []:
            mid = obs.get("modelId")
            bk = obs.get("benchKey")
            val = obs.get("value")
            if mid not in active_ids or bk not in core_keys or val is None:
                continue
            try:
                val = float(val)
            except Exception:
                continue
            cells[(mid, bk)].append(
                {
                    "value": val,
                    "sourceUrl": obs.get("sourceUrl") or "",
                    "tier": obs.get("tier") or "C",
                    "fetched": obs.get("fetched") or date.today().isoformat(),
                    "source": obs.get("source") or "",
                }
            )
            runtime_total["observationsTotal"] += 1
        for po in art.get("pricingObs") or []:
            mid = po.get("modelId")
            if mid in active_ids:
                all_pricing[mid].append(po)
                runtime_total["pricingObsTotal"] += 1
        for oo in art.get("ollamaObs") or []:
            mid = oo.get("modelId")
            if mid in active_ids:
                all_ollama[mid].append(oo)
                runtime_total["ollamaObsTotal"] += 1
        for uo in art.get("unslothObs") or []:
            mid = uo.get("modelId")
            if mid in active_ids:
                all_unsloth[mid].append(uo)
                runtime_total["unslothObsTotal"] += 1
        for nc in art.get("naCandidates") or []:
            all_na_candidates.append(nc)
            runtime_total["naCandidatesTotal"] += 1
        for rg in art.get("rawGaps") or []:
            all_raw_gaps.append(rg)
            runtime_total["rawGapsTotal"] += 1
        for lh in art.get("lineupHints") or []:
            all_lineup_hints.append(lh)

    print(
        f"Aggregated: {len(cells)} cells, "
        f"{runtime_total['observationsTotal']} obs, "
        f"{runtime_total['pricingObsTotal']} pricing, "
        f"{runtime_total['ollamaObsTotal']} ollama, "
        f"{runtime_total['unslothObsTotal']} unsloth"
    )

    # Group by model
    per_model: dict[str, dict] = {}
    for mid in active_ids:
        per_model[mid] = {
            "id": mid,
            "updates": {"bench": {}},
            "sourcesAdded": [],
        }

    contradictions: list = []
    fills_count = 0

    for (mid, bk), entries in cells.items():
        # Dedupe by (sourceUrl, value), aggregate verifications, use max recency
        by_value: dict[float, dict] = {}
        for e in entries:
            val = e["value"]
            if val not in by_value:
                by_value[val] = {
                    "value": val,
                    "sources": [],
                    "tier": e["tier"],
                    "latestDate": e["fetched"],
                    "verifications": 0,
                }
            bv = by_value[val]
            url = e["sourceUrl"]
            existing_urls = {s["url"] for s in bv["sources"]}
            if url and url not in existing_urls:
                bv["sources"].append(
                    {
                        "url": url,
                        "tier": e["tier"],
                        "fetched": e["fetched"],
                        "source": e["source"],
                    }
                )
                bv["verifications"] += 1
            # Pick highest-tier among same-value cluster
            if TIER_WEIGHT.get(e["tier"], 0) > TIER_WEIGHT.get(bv["tier"], 0):
                bv["tier"] = e["tier"]
            if e["fetched"] > bv["latestDate"]:
                bv["latestDate"] = e["fetched"]
            if bv["verifications"] == 0:
                bv["verifications"] = 1

        # Compute trustScore per value cluster
        ranked = []
        for val, bv in by_value.items():
            ts = trust_score(bv["tier"], bv["verifications"], bv["latestDate"])
            ranked.append((ts, val, bv))
        ranked.sort(key=lambda x: (-x[0], -x[2]["verifications"], -x[1]))

        # Contradiction check: distinct values that differ by > VERIFICATION_AGREEMENT_PP
        distinct_vals = [v for _, v, _ in ranked]
        is_contradiction = False
        if len(distinct_vals) >= 2:
            spread = max(distinct_vals) - min(distinct_vals)
            if spread > agreement_pp:
                is_contradiction = True

        winner_ts, winner_val, winner_bv = ranked[0]
        per_model[mid]["updates"]["bench"][bk] = winner_val
        fills_count += 1

        # Build sourcesAdded entry (wrapped Provenance shape, one per winner)
        for s in winner_bv["sources"][:5]:
            per_model[mid]["sourcesAdded"].append(
                {
                    "key": f"{mid}.{bk}",
                    "value": winner_val,
                    "source": s.get("source") or s["url"].split("/")[2]
                    if "://" in s["url"]
                    else "",
                    "url": s["url"],
                    "tier": s["tier"],
                    "date": s["fetched"],
                    "verifications": winner_bv["verifications"],
                    "trustScore": winner_ts,
                }
            )

        if is_contradiction:
            contradictions.append(
                {
                    "modelId": mid,
                    "field": bk,
                    "candidates": [
                        {
                            "value": v,
                            "trustScore": ts,
                            "tier": bv["tier"],
                            "verifications": bv["verifications"],
                            "latestDate": bv["latestDate"],
                            "sourceCount": len(bv["sources"]),
                        }
                        for ts, v, bv in ranked
                    ],
                    "autoResolveWinner": {
                        "value": winner_val,
                        "trustScore": winner_ts,
                        "tier": winner_bv["tier"],
                        "verifications": winner_bv["verifications"],
                        "latestDate": winner_bv["latestDate"],
                    },
                    "spread": max(distinct_vals) - min(distinct_vals),
                    "severity": "yellow"
                    if (max(distinct_vals) - min(distinct_vals)) < 5
                    else "red",
                }
            )

    # Attach pricing/ollama/unsloth observations to model entries
    for mid, plist in all_pricing.items():
        if mid in per_model:
            per_model[mid]["pricingObservations"] = plist
    for mid, olist in all_ollama.items():
        if mid in per_model:
            per_model[mid]["ollamaObservations"] = olist
    for mid, ulist in all_unsloth.items():
        if mid in per_model:
            per_model[mid]["unslothObservations"] = ulist

    # Filter out empty model entries (no fills, no observations)
    final_models = [
        m
        for m in per_model.values()
        if m["updates"]["bench"]
        or m["sourcesAdded"]
        or m.get("pricingObservations")
        or m.get("ollamaObservations")
        or m.get("unslothObservations")
    ]

    # Compute notApplicable promotion: only those with a matching rule
    not_applicable: list = []
    na_rules = wl.get("_schema", {}).get("notApplicableRules", {})
    valid_rule_keys = set()
    if isinstance(na_rules, dict):
        # Common shapes: {ruleId: {description, ...}} OR {benchKey: [ruleIds]}
        valid_rule_keys = set(na_rules.keys())
    for nc in all_na_candidates:
        rule_id = nc.get("ruleId") or nc.get("rule") or nc.get("reason")
        if rule_id and (not valid_rule_keys or rule_id in valid_rule_keys):
            not_applicable.append(nc)

    # Coverage computation
    total_cells = len(active) * len(core_keys)
    covered = fills_count
    validation_coverage = (
        round(covered / max(total_cells, 1), 4) if total_cells else 0.0
    )

    artifact = {
        "scope": "full",
        "mode": "synth-local",
        "confidence": "medium" if fills_count > 100 else "low",
        "models": final_models,
        "newModels": [],
        "contradictions": contradictions,
        "lineupChanges": {
            "new": [],
            "deprecated": [],
            "renamed": [],
            "removed": [],
            "hints": all_lineup_hints,
        },
        "gaps": all_raw_gaps,
        "notApplicable": not_applicable,
        "i18nUpdates": {},
        "validationCoverage": validation_coverage,
        "runtime": {
            **runtime_total,
            "cellsFilled": fills_count,
            "contradictionsDetected": len(contradictions),
            "naPromoted": len(not_applicable),
            "modelsTouched": len(final_models),
            "totalCellsExpected": total_cells,
            "synthMethod": "local-deterministic",
        },
        "whitelistAdditions": [],
    }

    out_path = ROOT / ".aicodermap-agent-out-synth.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(artifact, f, ensure_ascii=False, indent=2)

    size_kb = out_path.stat().st_size / 1024
    print(f"\nWROTE: {out_path}  ({size_kb:.1f} KB)")
    print(f"  modelsTouched: {len(final_models)}")
    print(f"  fills (cellsFilled): {fills_count}")
    print(f"  contradictions: {len(contradictions)}")
    print(f"  naPromoted: {len(not_applicable)}")
    print(f"  gapsCarried: {len(all_raw_gaps)}")
    print(f"  validationCoverage: {validation_coverage * 100:.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
