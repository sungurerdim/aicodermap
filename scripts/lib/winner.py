"""SSOT contradiction/winner resolver (F2.1).

Single canonical implementation of the pick_winner logic. Previously
duplicated across:
  - scripts/local-synth.py      (cluster ranking by distinct_sources + sum_trust)
  - scripts/merge.py            (_consensus_winner, FAZ 6.B re-clustering)
  - scripts/reconcile-bench-consensus.py
  - scripts/lib/synth.py        (_pick_winner — cluster-aware)

All callers import pick_winner() from here.

Decision tree (SKILL.md "I-tier always overrides S-tier" memory directive):
  1. If ≥1 I-tier observation exists AND (distinct_sources ≥ 2 OR
     source_reliability ≥ 0.6 among I-tier cluster members) →
     I-tier cluster wins regardless of sum_trust ordering.
     UI flag: contradictionMode="independent-override"
  2. Otherwise → cluster with max sum_trust wins.
  3. Single-observation outlier (verifications=1) NEVER beats a cluster
     with ≥3 distinct sources.
  4. Within the winning cluster the individual winner is the member with
     the highest individual trustScore (most authoritative source).

Bench-type-aware delta thresholds:
  Loaded from sources-whitelist.json _schema.benchTypes (via contracts.py).
  Falls back to global CONTRADICTION_WARN_PP / CONTRADICTION_BLOCK_PP.

Stdlib-only.
"""

from __future__ import annotations

import datetime
from typing import Any

from .tiers import tier_rank, trust_score

# Global fallback thresholds (overridden per-bench via benchTypes)
DEFAULT_AGREEMENT_PP: float = 1.5
DEFAULT_WARN_PP: float = 3.0
DEFAULT_BLOCK_PP: float = 5.0

# Minimum I-tier cluster reliability to trigger independent-override
I_TIER_MIN_SOURCES: int = 2
I_TIER_MIN_RELIABILITY: float = 0.6


def _cluster(
    scored: list[dict[str, Any]],
    agreement_pp: float,
) -> list[dict[str, Any]]:
    """Greedy cluster by value proximity within agreement_pp.

    Seeds clusters from highest-trustScore observations first (stable centroid).
    Returns clusters sorted by (sum_trust DESC, distinct_sources DESC).
    """
    clusters: list[dict[str, Any]] = []
    for s in sorted(scored, key=lambda x: -x["trustScore"]):
        placed = False
        for cl in clusters:
            if abs(s["value"] - cl["centroid"]) <= agreement_pp:
                cl["members"].append(s)
                total_ts = sum(m["trustScore"] for m in cl["members"]) or 1e-9
                cl["centroid"] = (
                    sum(m["value"] * m["trustScore"] for m in cl["members"]) / total_ts
                )
                cl["sum_trust"] = round(total_ts, 4)
                urls = {(m.get("sourceUrl") or "").lower() for m in cl["members"]}
                urls.discard("")
                cl["distinct_sources"] = len(urls) if urls else len(cl["members"])
                cl["latest_fetched"] = max(
                    cl.get("latest_fetched") or "",
                    s.get("fetched") or "",
                )
                placed = True
                break
        if not placed:
            url = (s.get("sourceUrl") or "").lower()
            clusters.append(
                {
                    "centroid": s["value"],
                    "members": [s],
                    "sum_trust": round(s["trustScore"], 4),
                    "distinct_sources": 1 if url else 0,
                    "latest_fetched": s.get("fetched") or "",
                }
            )
    clusters.sort(key=lambda c: (-c["sum_trust"], -c["distinct_sources"]))
    return clusters


def _i_tier_cluster(
    clusters: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Return the first cluster that satisfies the I-tier override rule, or None."""
    for cl in clusters:
        i_members = [m for m in cl["members"] if tier_rank(m.get("tier", "C")) == 3]
        if not i_members:
            continue
        # Condition: ≥2 distinct I-tier sources OR average trust of I-tier ≥ threshold
        i_urls = {(m.get("sourceUrl") or "").lower() for m in i_members}
        i_urls.discard("")
        n_distinct_i = len(i_urls) if i_urls else len(i_members)
        avg_trust = sum(m["trustScore"] for m in i_members) / len(i_members)
        if n_distinct_i >= I_TIER_MIN_SOURCES or avg_trust >= I_TIER_MIN_RELIABILITY:
            return cl
    return None


def _single_outlier_guard(
    clusters: list[dict[str, Any]],
) -> dict[str, Any]:
    """Rule 3: single-observation outlier cannot beat ≥3-distinct-source cluster.

    If the top cluster has 1 observation but a later cluster has ≥3 distinct
    sources, demote the outlier and pick the multi-source cluster.
    """
    if not clusters:
        return {}
    top = clusters[0]
    if top["distinct_sources"] <= 1 and len(clusters) > 1:
        for cl in clusters[1:]:
            if cl["distinct_sources"] >= 3:
                return cl
    return top


def pick_winner(
    observations: list[dict[str, Any]],
    *,
    bench_key: str = "",
    agreement_pp: float = DEFAULT_AGREEMENT_PP,
    warn_pp: float = DEFAULT_WARN_PP,
    block_pp: float = DEFAULT_BLOCK_PP,
    today: datetime.date | None = None,
) -> dict[str, Any]:
    """Select the winning observation and detect contradictions.

    Parameters
    ----------
    observations:
        List of raw observation dicts, each with at minimum:
          {value (float), tier (str), sourceUrl (str), fetched (str)}
    bench_key:
        Canonical bench key — used for per-bench delta thresholds when
        bench_types are loaded externally. Not required; pass for logging.
    agreement_pp / warn_pp / block_pp:
        Delta thresholds. Callers should pass bench-type-specific values
        from contracts.bench_delta_thresholds(bench_key) when available.
    today:
        Reference date for recency decay. Defaults to today().

    Returns
    -------
    dict with keys:
      winner_value    float | None   — the value to commit
      winner_obs      dict           — the winning observation (with trustScore)
      winning_cluster dict           — the cluster that won
      all_clusters    list[dict]     — all clusters (for contradiction reporting)
      scored          list[dict]     — all observations with trustScore attached
      is_contradiction bool
      severity        str            — "GREEN" | "YELLOW" | "RED"
      max_delta       float
      override_mode   str | None     — "independent-override" when rule 1 fired
    """
    _ = bench_key  # reserved for per-bench logging; consumed by caller
    _today = today or datetime.date.today()
    del _today  # recency decay uses wall-clock inside tiers.trust_score

    valid = [o for o in (observations or []) if o.get("value") is not None]
    if not valid:
        return {
            "winner_value": None,
            "winner_obs": {},
            "winning_cluster": {},
            "all_clusters": [],
            "scored": [],
            "is_contradiction": False,
            "severity": "GREEN",
            "max_delta": 0.0,
            "override_mode": None,
        }

    # Distinct URL count for verifications cap (FAZ 6.E)
    distinct_urls = {(o.get("sourceUrl") or "").strip().lower() for o in valid}
    distinct_urls.discard("")
    verif_count = len(distinct_urls) or len(valid)

    scored: list[dict[str, Any]] = []
    for o in valid:
        ts = trust_score(o.get("tier", "C"), verif_count, o.get("fetched") or "")
        scored.append({**o, "trustScore": ts, "value": float(o["value"])})

    clusters = _cluster(scored, agreement_pp)

    # Rule 1 — I-tier override
    override_mode: str | None = None
    i_cluster = _i_tier_cluster(clusters)
    if i_cluster and clusters[0] is not i_cluster:
        # I-tier cluster is not already on top — promote it
        clusters.remove(i_cluster)
        clusters.insert(0, i_cluster)
        override_mode = "independent-override"
    elif i_cluster and clusters[0] is i_cluster:
        override_mode = "independent-override"

    # Rule 3 — single-outlier guard (applied to post-override cluster order)
    winning_cluster = _single_outlier_guard(clusters)

    # Rule 4 — best individual within winning cluster
    winner_obs = max(
        winning_cluster.get("members", []) or scored[:1],
        key=lambda m: (m["trustScore"], m.get("fetched") or ""),
    )
    winner_value = winner_obs["value"]

    # Contradiction detection — max delta across ALL observations
    all_values = [s["value"] for s in scored]
    max_delta = max(all_values) - min(all_values) if len(all_values) > 1 else 0.0
    is_contradiction = max_delta >= agreement_pp and len(clusters) > 1
    if max_delta >= block_pp:
        severity = "RED"
    elif max_delta >= warn_pp:
        severity = "YELLOW"
    else:
        severity = "GREEN"

    return {
        "winner_value": winner_value,
        "winner_obs": winner_obs,
        "winning_cluster": winning_cluster,
        "all_clusters": clusters,
        "scored": scored,
        "is_contradiction": is_contradiction,
        "severity": severity,
        "max_delta": round(max_delta, 2),
        "override_mode": override_mode,
    }


def build_contradiction_entry(
    model_id: str,
    bench_key: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    """Build the contradictions[] entry from a pick_winner result."""
    scored = result.get("scored") or []
    winner_obs = result.get("winner_obs") or {}
    return {
        "modelId": model_id,
        "field": bench_key,
        "candidates": [
            {
                "value": s["value"],
                "trustScore": s["trustScore"],
                "tier": s.get("tier", "C"),
                "sourceUrl": s.get("sourceUrl", ""),
                "fetched": s.get("fetched", ""),
                "verifications": 1,
            }
            for s in scored
        ],
        "autoResolveWinner": {
            "value": winner_obs.get("value"),
            "trustScore": winner_obs.get("trustScore"),
            "tier": winner_obs.get("tier", "C"),
            "sourceUrl": winner_obs.get("sourceUrl", ""),
        },
        "delta": result.get("max_delta", 0.0),
        "severity": result.get("severity", "GREEN"),
        "overrideMode": result.get("override_mode"),
    }
