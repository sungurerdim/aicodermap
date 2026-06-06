"""Observation clustering helpers (FAZ 6.B/6.D, extracted 2026-06-06).

Greedy value-clustering + low-confidence trust penalty for the consensus
winner path. Used by merge.py (forward path) and reconcile-bench-consensus.py
(historical backlog). Kept separate from lib.winner because
`_cluster_observations` carries the FAZ 6.D recency-tiebreak that
winner._cluster lacks — replacing one with the other would change behavior.

Stdlib-only.
"""

from __future__ import annotations

from typing import Any


def _cluster_observations(
    scored: list[dict[str, Any]], agreement_pp: float
) -> list[dict[str, Any]]:
    """Group same-value observations into clusters. Two observations land in
    the same cluster when |valueA - valueB| <= agreement_pp. Centroid is the
    trustScore-weighted mean of cluster members. Returns clusters sorted by
    summed trustScore (descending) so [0] is the consensus cluster.

    Greedy single-pass clustering. Sorted by trustScore desc so highest-trust
    obs seeds the cluster centroid before lower-trust outliers join — keeps
    the cluster representative stable when one source has a typo near the
    agreement boundary.
    """
    clusters: list[dict[str, Any]] = []
    for s in sorted(scored, key=lambda x: -x["trustScore"]):
        placed = False
        for cl in clusters:
            if abs(s["value"] - cl["centroid"]) <= agreement_pp:
                cl["members"].append(s)
                tot = sum(m["trustScore"] for m in cl["members"]) or 1e-6
                cl["centroid"] = (
                    sum(m["value"] * m["trustScore"] for m in cl["members"]) / tot
                )
                cl["sum_trust"] = round(tot, 4)
                cl["distinct_sources"] = len(
                    {(m.get("sourceUrl") or "").lower() for m in cl["members"]}
                )
                # FAZ 6.D: track latest fetched date per cluster for the
                # recency tiebreaker.
                cl["latest_fetched"] = max(
                    cl.get("latest_fetched") or "", s.get("fetched") or ""
                )
                placed = True
                break
        if not placed:
            clusters.append(
                {
                    "centroid": s["value"],
                    "members": [s],
                    "sum_trust": round(s["trustScore"], 4),
                    "distinct_sources": 1,
                    "latest_fetched": s.get("fetched") or "",
                }
            )
    # FAZ 6.D — recency tiebreaker. When two clusters' sum_trust differ by
    # less than RECENCY_TIEBREAK_BAND (0.5), the one with the more recent
    # latest_fetched date wins. Only fires AFTER strict gate (the override
    # threshold in reconcile/synth still must pass), so it never promotes
    # a freshly-fabricated single source over an old multi-source consensus
    # — it only re-orders within the same evidence band.
    RECENCY_TIEBREAK_BAND = 0.5

    def _rank_key(c: dict[str, Any]) -> tuple[Any, ...]:
        # Primary: bucket the trust into bands so close clusters compare equal
        # at this stage; recency then breaks the tie. Bucket size matches the
        # tiebreak band so two clusters within the band share a primary key.
        bucket = round(c["sum_trust"] / RECENCY_TIEBREAK_BAND)
        return (
            bucket,
            c["distinct_sources"],
            c.get("latest_fetched") or "",
            len(c["members"]),
        )

    clusters.sort(key=_rank_key, reverse=True)
    return clusters


def _apply_low_confidence_penalty(
    scored: list[dict[str, Any]],
    low_conf_urls: set[str],
    multiplier: float,
) -> list[dict[str, Any]]:
    """FAZ 6.C: multiply trustScore by `multiplier` for any obs whose URL
    matches `low_conf_urls`. Mutates list in place; returns the same list
    for chaining."""
    if not low_conf_urls or multiplier == 1.0:
        return scored
    for s in scored:
        url = (s.get("sourceUrl") or "").strip().rstrip("/").lower()
        if url and url in low_conf_urls:
            s["trustScore"] = round(s["trustScore"] * multiplier, 4)
            s["_lowConfidence"] = True
    return scored
