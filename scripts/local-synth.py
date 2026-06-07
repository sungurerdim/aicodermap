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

from lib.whitelist import all_bench_keys, bench_hard_max, contracts  # type: ignore  # noqa: E402
from lib.matrix import active_models  # type: ignore  # noqa: E402
from lib import reliability as _reliability  # type: ignore  # noqa: E402
from lib.tiers import TIER_WEIGHT  # type: ignore  # noqa: E402  (SSOT)
from lib.tiers import verif_factor as _verif_factor  # type: ignore  # noqa: E402
from lib.constants import ELO_BENCH_KEYS  # type: ignore  # noqa: E402  (SSOT)
from lib.util import extract_domain  # type: ignore  # noqa: E402  (SSOT)

LEDGER_PATH = ROOT / "data" / "source-reliability.json"


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


def trust_score(
    tier: str,
    verifications: int,
    dtstr: str,
    *,
    source_url: str = "",
    bench_key: str = "",
    reliability_ledger: dict | None = None,
) -> float:
    """Phase R2+R3: log-base-4 verif_factor + optional Beta-Binomial multiplier.

    Stays behaviourally identical to the pre-R2 formula when verifications
    equals 3 and no ledger is supplied; otherwise applies the canonical
    `tiers.verif_factor` and (when ledger present) the per-(source, bench)
    reliability posterior.
    """
    tw = TIER_WEIGHT.get(tier, 0.1)
    v = _verif_factor(int(verifications) if verifications is not None else 0)
    base = round(tw * v * recency_decay(dtstr), 4)
    if reliability_ledger and source_url:
        mult = _reliability.reliability_multiplier(
            reliability_ledger, source_url, bench_key
        )
        return round(base * mult, 4)
    return base


def find_batch_artifacts() -> list[Path]:
    return sorted(ROOT.glob(".aicodermap-agent-out-batch*.gather.json"))


_ELO_SIBLINGS = ELO_BENCH_KEYS  # SSOT: lib.constants.ELO_BENCH_KEYS


def build_host_publishes(wl: dict) -> dict:
    """host -> set(benchKeys it publishes), from every whitelist category. Used by
    the Elo-trap filter to spot a cfElo value scraped off a webDevElo-only page."""
    out: dict[str, set] = {}
    for cat in (wl.get(k) for k in wl if isinstance(wl.get(k), list)):
        for e in cat or []:
            if not isinstance(e, dict):
                continue
            url = e.get("url") or ""
            pub = e.get("publishes") or []
            if not url or not pub:
                continue
            host = extract_domain(url)
            if host:
                out.setdefault(host, set()).update(pub)
    return out


def is_elo_sibling_misfile(
    bk: str, val: float, source_url: str, host_pub: dict
) -> bool:
    """C1 (2026-05-31): drop an Elo observation that is almost certainly a
    sibling-metric misfile — the source host publishes a DIFFERENT Elo
    (cfElo/webDevElo/lmArenaElo) but not this one, AND the value itself sits in
    the arena range (1000-1600) rather than the Codeforces range (>1600). This
    keeps genuine cross-sourced values (e.g. cfElo=3206 read off a page that also
    lists webDevElo) while stopping a webDevElo=1300 filed as cfElo from entering
    the cluster pool (the class that recurrently hard-blocks merge)."""
    if bk not in _ELO_SIBLINGS:
        return False
    host = extract_domain(source_url)
    pub = host_pub.get(host)
    if not pub or bk in pub or not (pub & _ELO_SIBLINGS):
        return False  # host can't be judged / legitimately publishes bk / no sibling
    # Host publishes a sibling Elo but NOT bk. Only drop if the value also looks
    # like the sibling metric (arena-range), confirming the misfile.
    if bk == "cfElo" and val >= 1600:
        return False  # genuine Codeforces-range rating, not a webDevElo misfile
    return True


def main() -> int:
    os.chdir(ROOT)
    with open("data/models.json", encoding="utf-8") as f:
        md = json.load(f)
    models = md if isinstance(md, list) else md.get("models", [])
    with open("data/sources-whitelist.json", encoding="utf-8") as f:
        wl = json.load(f)
    # SoC: two distinct bench-key concerns, each with ONE SSOT accessor.
    #   • core_keys (coreBenchKeys, 17) → COVERAGE/matrix denominator only.
    #   • value_keys (all_bench_keys = core ∪ emerging, 29) → which observed
    #     values may be INGESTED/scored. Mirrors frontend BENCH_KEYS exactly.
    # Filtering ingestion to core_keys alone silently DROPPED every fresh
    # emerging observation (2026-06-06: 45 obs / 33 cells — e.g. opus-4-8
    # mcpA=82.2 + sweMulti=84.4 lost, sinking it in swe-focused despite top
    # swePro/sweV). Emerging cells are optional (never gap-demanded), but their
    # observed values MUST flow through so PRESETS that weight them see them.
    core_keys = wl["_schema"]["coreBenchKeys"]
    value_keys = set(all_bench_keys(wl))
    ctr = contracts(wl)
    agreement_pp = float(ctr.get("VERIFICATION_AGREEMENT_PP", 1.5))
    host_pub = build_host_publishes(wl)  # C1 Elo-trap filter input
    elo_dropped = 0

    active = active_models(models)
    active_ids = {m["id"] for m in active}

    artifacts = find_batch_artifacts()
    print(f"Reading {len(artifacts)} gather artifacts")

    # CRITICAL — preload HISTORICAL sources.json entries into cluster pool.
    # Without this, single new low-tier observations override strong historical
    # consensus (cycle 2026-05-11 wrote 80.6 to deepseek-v4-pro.swePro from a
    # blog post, overriding 6 prior sources clustered at 55.4 including Scale SEAL).
    historical_path = ROOT / "data" / "sources.json"
    historical: dict[tuple, list] = defaultdict(list)
    if historical_path.exists():
        hist = json.load(open(historical_path, encoding="utf-8"))
        for full_key, entries in hist.items():
            if "." not in full_key:
                continue
            mid, bk = full_key.split(".", 1)
            if bk not in value_keys:
                continue
            for e in entries:
                v = e.get("value")
                if v is None:
                    continue
                try:
                    v = float(v)
                except Exception:
                    continue
                historical[(mid, bk)].append(
                    {
                        "value": v,
                        "sourceUrl": e.get("url") or "",
                        "tier": (e.get("tier") or "C").upper(),
                        "fetched": e.get("date") or "2026-01-01",
                        "source": e.get("source") or "",
                        "_historical": True,
                    }
                )

    cells: dict[tuple, list] = defaultdict(list)
    all_pricing: dict[str, list] = defaultdict(list)
    all_ollama: dict[str, list] = defaultdict(list)
    all_unsloth: dict[str, list] = defaultdict(list)
    all_raw_gaps: list = []
    all_lineup_hints: list = []
    runtime_total = {
        "batchesMerged": 0,
        "observationsTotal": 0,
        "pricingObsTotal": 0,
        "ollamaObsTotal": 0,
        "unslothObsTotal": 0,
        "rawGapsTotal": 0,
    }

    # 6.1 — parse each batch artifact ONCE; the observations pass and the
    # pricing pass below both iterate this cached list instead of re-reading
    # every .gather.json from disk a second time.
    parsed_artifacts: list[tuple[Path, dict]] = []
    for p in artifacts:
        try:
            parsed_artifacts.append((p, json.load(open(p, encoding="utf-8"))))
        except Exception as e:
            print(f"  ! skip {p.name}: {e}")

    for p, art in parsed_artifacts:
        runtime_total["batchesMerged"] += 1
        for obs in art.get("observations") or []:
            mid = obs.get("modelId")
            bk = obs.get("benchKey")
            val = obs.get("value")
            if mid not in active_ids or bk not in value_keys or val is None:
                continue
            try:
                val = float(val)
            except Exception:
                continue
            # Drop out-of-range bench values. A mis-scaled obs — e.g. aaAgentic
            # recorded as a raw LMArena Elo (1753) instead of the 0-100 index —
            # must never enter the cluster pool. Caps come from the benchRanges
            # SSOT (was hardcoded 3500/2000/100 here, diverging from the schema).
            if val < 0 or val > bench_hard_max(wl, bk):
                continue
            # C1 (2026-05-31): drop Elo values that are sibling-metric misfiles
            # (e.g. a webDevElo scraped off its page and filed as cfElo) before
            # they can win a cell + recurrently hard-block merge.
            if is_elo_sibling_misfile(bk, val, obs.get("sourceUrl") or "", host_pub):
                elo_dropped += 1
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

    # Merge historical observations into the cluster pool for any cell touched
    # by this cycle. We do NOT inject historical for cells with zero new obs —
    # those should remain as they are in data/models.json (untouched).
    historical_injected = 0
    for (mid, bk), new_obs in list(cells.items()):
        for h in historical.get((mid, bk), []):
            # Skip exact-URL dupes already in new_obs
            already = any(
                no["sourceUrl"] == h["sourceUrl"] and no["value"] == h["value"]
                for no in new_obs
            )
            if not already:
                cells[(mid, bk)].append(h)
                historical_injected += 1
    runtime_total["historicalObsInjected"] = historical_injected

    for p, art in parsed_artifacts:
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
        # N/A fully retired 2026-05-25: naCandidates are neither produced nor
        # counted — every (model, bench) cell is FILLED or GAP.
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

    # Phase R3: load the source-reliability ledger once for the whole run.
    # When the ledger is empty or the source is below the cold-start threshold,
    # trust_score behaves exactly as before (multiplier = 1.0).
    reliability_ledger = _reliability.load_ledger(LEDGER_PATH)

    for (mid, bk), entries in cells.items():
        # Build per-observation list with trustScore for sum-based cluster ranking.
        obs_list = []
        for e in entries:
            ts = trust_score(
                e["tier"],
                1,
                e["fetched"],
                source_url=e.get("sourceUrl") or "",
                bench_key=bk,
                reliability_ledger=reliability_ledger,
            )
            obs_list.append(
                {
                    "value": e["value"],
                    "url": e["sourceUrl"],
                    "tier": e["tier"],
                    "fetched": e["fetched"],
                    "source": e["source"],
                    "trustScore": ts,
                    "_historical": e.get("_historical", False),
                }
            )

        # Cluster observations within AGREEMENT_PP. Greedy single-pass: sort
        # by value, group consecutive within tolerance, centroid = median.
        obs_list.sort(key=lambda o: o["value"])
        clusters: list[list[dict]] = []
        for o in obs_list:
            placed = False
            for cl in clusters:
                centroid = sum(x["value"] for x in cl) / len(cl)
                if abs(o["value"] - centroid) <= agreement_pp:
                    cl.append(o)
                    placed = True
                    break
            if not placed:
                clusters.append([o])

        # Rank clusters by: distinct_sources DESC, sum_trust DESC, latest DESC.
        cluster_meta = []
        for cl in clusters:
            distinct_urls = {x["url"] for x in cl if x["url"]}
            n_dist = len(distinct_urls) if distinct_urls else len(cl)
            sum_trust = sum(x["trustScore"] for x in cl)
            latest = max(x["fetched"] for x in cl)
            centroid = sum(x["value"] for x in cl) / len(cl)
            # Winner inside cluster = highest individual trustScore
            cluster_winner = max(cl, key=lambda x: (x["trustScore"], x["fetched"]))
            cluster_meta.append(
                {
                    "centroid": round(centroid, 2),
                    "members": cl,
                    "n_distinct": n_dist,
                    "sum_trust": round(sum_trust, 4),
                    "latest": latest,
                    "winner": cluster_winner,
                }
            )
        cluster_meta.sort(
            key=lambda c: (-c["n_distinct"], -c["sum_trust"], c["latest"]),
            reverse=False,
        )
        cluster_meta = sorted(
            cluster_meta,
            key=lambda c: (-c["n_distinct"], -c["sum_trust"]),
        )

        best_cluster = cluster_meta[0]
        winner_obs = best_cluster["winner"]
        winner_val = winner_obs["value"]
        winner_ts = winner_obs["trustScore"]

        # Build a winner_bv-equivalent dict for downstream sourcesAdded
        winner_bv = {
            "value": winner_val,
            "sources": [
                {
                    "url": x["url"],
                    "tier": x["tier"],
                    "fetched": x["fetched"],
                    "source": x["source"],
                }
                for x in best_cluster["members"]
                if x["url"]
            ][:5],
            "tier": winner_obs["tier"],
            "latestDate": best_cluster["latest"],
            "verifications": best_cluster["n_distinct"],
        }

        # Contradiction = any rival cluster outside agreement_pp with ≥1 source
        is_contradiction = len(cluster_meta) >= 2

        # Build by_value-equivalent for contradictions[] reporting
        by_value = {}
        for cm in cluster_meta:
            v = cm["centroid"]
            by_value[v] = {
                "value": v,
                "sources": [
                    {"url": x["url"], "tier": x["tier"], "fetched": x["fetched"]}
                    for x in cm["members"]
                    if x["url"]
                ],
                "tier": cm["winner"]["tier"],
                "latestDate": cm["latest"],
                "verifications": cm["n_distinct"],
            }
        ranked = [
            (cm["winner"]["trustScore"], cm["centroid"], by_value[cm["centroid"]])
            for cm in cluster_meta
        ]
        distinct_vals = [r[1] for r in ranked]
        per_model[mid]["updates"]["bench"][bk] = winner_val
        fills_count += 1

        # Build sourcesAdded entry (wrapped Provenance shape, one per winner).
        # ALL winner-cluster sources are carried — no truncation — so 6+ sourced
        # cells keep their full provenance trail in sources.json. The field name
        # is `fetched` (NOT `date`) to match merge.py's reader (s.get("fetched"))
        # + the agent's sourcesAdded contract; a `date` key would be dropped and
        # the original fetch date silently replaced by TODAY.
        for s in winner_bv["sources"]:
            per_model[mid]["sourcesAdded"].append(
                {
                    "key": f"{mid}.{bk}",
                    "value": winner_val,
                    "source": s.get("source") or s["url"].split("/")[2]
                    if "://" in s["url"]
                    else "",
                    "url": s["url"],
                    "tier": s["tier"],
                    "fetched": s["fetched"],
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

    # N/A retired 2026-05-25: naCandidates are never promoted. Every
    # (model, bench) cell is FILLED or GAP — an unmeasured cell stays a gap
    # and is re-researched every cycle (freshness-skip only).

    # Coverage computation
    total_cells = len(active) * len(core_keys)
    covered = fills_count
    validation_coverage = (
        round(covered / max(total_cells, 1), 4) if total_cells else 0.0
    )

    # Canonicalize raw gather gaps to the schema-valid `key` shape
    # ("<modelId>.<benchKey>", Branch A of agent-out.schema.json gaps[]).
    # Gather emits {modelId, benchKey, ...}; merge.py's validator and gap_gen
    # both key on `key`/`field`, not `benchKey` — so a passthrough produced
    # schema-invalid gaps AND double-counting in gap_gen. Dedup by cell and
    # restrict to active × core so the filled+gaps invariant holds.
    _gap_seen: set[tuple[str, str]] = set()
    gap_entries: list = []
    for rg in all_raw_gaps:
        mid = rg.get("modelId")
        bk = rg.get("benchKey")
        if not mid or not bk or mid not in active_ids or bk not in core_keys:
            continue
        if (mid, bk) in _gap_seen:
            continue
        _gap_seen.add((mid, bk))
        gap_entries.append(
            {
                "key": f"{mid}.{bk}",
                "reason": rg.get("reason") or "agent surveyed; value unavailable",
                "triedSources": rg.get("triedSources") or [],
                "triedQueries": rg.get("triedQueries") or [],
                "triedFormats": rg.get("triedFormats")
                or ["static_html_table", "websearch_snippet"],
                "source": "agent",
            }
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
        "gaps": gap_entries,
        "i18nUpdates": {},
        "validationCoverage": validation_coverage,
        "runtime": {
            **runtime_total,
            "cellsFilled": fills_count,
            "contradictionsDetected": len(contradictions),
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
    print(f"  gapsCarried: {len(gap_entries)} (deduped from {len(all_raw_gaps)} raw)")
    print(f"  validationCoverage: {validation_coverage * 100:.1f}%")
    if elo_dropped:
        print(f"  eloSiblingMisfilesDropped (C1): {elo_dropped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
