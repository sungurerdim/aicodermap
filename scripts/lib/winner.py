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

from .tiers import (
    I_TIER_MIN_VERIFICATIONS,
    effective_trust_score,
    is_pseudo_source,
    recency_decay,
    tier_rank,
    vendor_update_interval,
)

# Phase R4 thresholds for the exceptional-source override. When a single
# I-tier observation has enough Bayesian evidence (n >= 20, accuracy >= 0.90)
# and is fresh (recency_decay >= 0.85, i.e. < ~90 days old), it bypasses the
# single-outlier guard so it can survive against larger but less reliable
# clusters. Every override fires only on (source, bench) pairs that have
# *earned* the override via accumulated track record — no hardcoded source
# allowlists.
EXCEPTIONAL_RELIABILITY_THRESHOLD: float = 0.90
EXCEPTIONAL_SAMPLE_MIN: int = 20
EXCEPTIONAL_RECENCY_MIN: float = 0.85

# Global fallback thresholds (overridden per-bench via benchTypes)
DEFAULT_AGREEMENT_PP: float = 1.5
DEFAULT_WARN_PP: float = 3.0
DEFAULT_BLOCK_PP: float = 5.0

# Minimum I-tier cluster reliability to trigger independent-override
I_TIER_MIN_SOURCES: int = 2
I_TIER_MIN_RELIABILITY: float = 0.6

# Confidence severity penalties (FAZ 8.A.3b)
_SEVERITY_PENALTY = {"GREEN": 0.0, "YELLOW": 0.15, "RED": 0.4}


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
    *,
    require_min_verifications: bool = True,
) -> dict[str, Any] | None:
    """Return the first cluster that satisfies the I-tier override rule, or None.

    FAZ 8.A.3b: when `require_min_verifications` is True, a single I-tier
    observation with `verifications < I_TIER_MIN_VERIFICATIONS` cannot
    trigger the override — it stays in the cluster sort but won't promote
    above a multi-source S-tier consensus.
    """
    for cl in clusters:
        i_members = [m for m in cl["members"] if tier_rank(m.get("tier", "C")) == 3]
        if not i_members:
            continue
        # Condition: ≥2 distinct I-tier sources OR average trust of I-tier ≥ threshold
        i_urls = {(m.get("sourceUrl") or "").lower() for m in i_members}
        i_urls.discard("")
        n_distinct_i = len(i_urls) if i_urls else len(i_members)
        avg_trust = sum(m["trustScore"] for m in i_members) / len(i_members)
        # FAZ 8.A.3b: single-shot I-tier dampening
        if require_min_verifications:
            i_verifs = max(
                (int(m.get("verifications") or 0) for m in i_members),
                default=0,
            )
            if (
                n_distinct_i < I_TIER_MIN_SOURCES
                and i_verifs < I_TIER_MIN_VERIFICATIONS
            ):
                continue
        if n_distinct_i >= I_TIER_MIN_SOURCES or avg_trust >= I_TIER_MIN_RELIABILITY:
            return cl
    return None


def filter_pseudo_sources(
    observations: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split observations into (primary, pseudo).

    Pseudo entries (snapshot-extraction / auto-resolution candidate /
    synth-backfill) lack verifiable URLs — exclude from clustering so
    they don't anchor consensus. Returned pseudo list is preserved for
    audit/telemetry surfacing.
    """
    primary: list[dict[str, Any]] = []
    pseudo: list[dict[str, Any]] = []
    for o in observations or []:
        if is_pseudo_source(o):
            pseudo.append(o)
        else:
            primary.append(o)
    return primary, pseudo


def tag_evaluation_context(
    observations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Annotate observations with an `evaluationContext` field when source
    hints reveal scaffold / tool-condition / benchmark-version splits.

    Detects three signals from notes/sourceUrl heuristically:
      - 'scaffold=<name>' or '/scaffold/' path segments -> scaffold variant
      - 'tools=on|off' or '/agentic/' path segments    -> tool condition split
      - 'lcb-v6' / 'v6' suffixes on lcb-family URLs    -> benchmark version

    The signal lives only on the observation; downstream clustering can
    use it to split clusters by context (caller decision).
    """
    out: list[dict[str, Any]] = []
    for o in observations or []:
        if not isinstance(o, dict):
            out.append(o)
            continue
        url = (o.get("sourceUrl") or "").lower()
        notes = (o.get("notes") or "").lower()
        ctx: dict[str, Any] = {}
        # Scaffold variants (e.g. "agentless", "swe-agent", "aider")
        for sf in ("agentless", "swe-agent", "aider", "openhands", "moatless"):
            if sf in notes or sf in url:
                ctx["scaffold"] = sf
                break
        # Tool conditions
        if "tools=on" in notes or "/tools-on/" in url:
            ctx["condition"] = "tools-on"
        elif "tools=off" in notes or "/tools-off/" in url:
            ctx["condition"] = "tools-off"
        # Benchmark version on lcb family
        if "lcb-v6" in url or "lcb_v6" in url or "lcb-v6" in notes:
            ctx["lcbVersion"] = "v6"
        elif "lcb-v5" in url or "lcb_v5" in url:
            ctx["lcbVersion"] = "v5"
        if ctx:
            o = {**o, "evaluationContext": ctx}
        out.append(o)
    return out


def detect_category_bleed(
    observations: list[dict[str, Any]],
    bench_key: str,
    *,
    all_cell_obs: dict[tuple[str, str], list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    """Flag observations whose URL also feeds another bench cell with the
    same value — symptom of an extractor mis-routing a row across bench
    columns (e.g. deepseek-v3-2.sweV pulling 83.3 from an LCB row).

    Returns a new list with `_categoryBleed: True` set on flagged entries.
    When `all_cell_obs` is None, returns input untouched (no cross-cell
    visibility; callers like local-synth pass the full cell map).
    """
    if not all_cell_obs:
        return list(observations or [])
    out: list[dict[str, Any]] = []
    for o in observations or []:
        if not isinstance(o, dict):
            out.append(o)
            continue
        url = (o.get("sourceUrl") or "").strip().lower()
        val = o.get("value")
        if not url or val is None:
            out.append(o)
            continue
        flagged = False
        for (mid, bk), other_obs in all_cell_obs.items():
            if bk == bench_key:
                continue
            for other in other_obs or []:
                if not isinstance(other, dict):
                    continue
                if (other.get("sourceUrl") or "").strip().lower() != url:
                    continue
                if other.get("value") == val:
                    flagged = True
                    break
            if flagged:
                break
        if flagged:
            o = {**o, "_categoryBleed": True}
        out.append(o)
    return out


def compute_cell_confidence(result: dict[str, Any]) -> float:
    """Confidence score in [0, 1] for a pick_winner result.

    Formula:
        verifications_factor = min(N_primary / 3, 1)
        trust_factor         = winner_trust / I_weight (=1.0 cap)
        severity_penalty     = {GREEN: 0, YELLOW: 0.15, RED: 0.4}
        confidence = verifications_factor × trust_factor × (1 - severity_penalty)
    """
    scored = result.get("scored") or []
    primary = [s for s in scored if not is_pseudo_source(s)]
    n_primary = len(primary)
    verif_factor = min(n_primary / 3.0, 1.0)
    winner_obs = result.get("winner_obs") or {}
    winner_trust = float(winner_obs.get("trustScore") or 0.0)
    trust_factor = min(winner_trust / 1.0, 1.0)
    severity = result.get("severity", "GREEN")
    penalty = _SEVERITY_PENALTY.get(severity, 0.0)
    conf = verif_factor * trust_factor * (1.0 - penalty)
    return round(max(0.0, min(1.0, conf)), 4)


def should_quarantine(
    result: dict[str, Any],
    primary_obs: list[dict[str, Any]] | None = None,
) -> bool:
    """FAZ 8.A.3b quarantine triggers:
    - confidence < 0.2
    - distinct primary values > 5 (extreme dispersion)
    - any observation flagged as scaffold-variant (different evaluation
      contexts shouldn't share a single composite cell)
    """
    conf = float(result.get("confidence") or 0.0)
    if conf < 0.2:
        return True
    scored = result.get("scored") or []
    distinct_values = {
        round(float(s["value"]), 2) for s in scored if s.get("value") is not None
    }
    if len(distinct_values) > 5:
        return True
    pool = list(primary_obs or scored)
    for o in pool:
        if not isinstance(o, dict):
            continue
        ctx = o.get("evaluationContext") or {}
        if isinstance(ctx, dict) and ctx.get("scaffold"):
            return True
    return False


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


def _exceptional_source_override(
    clusters: list[dict[str, Any]],
    reliability_ledger: dict[str, Any] | None,
    bench_key: str,
) -> tuple[dict[str, Any] | None, str | None]:
    """Phase R4: bypass _single_outlier_guard for highly trusted singletons.

    Returns (cluster, override_mode) when a single-source I-tier cluster meets
    every gate: ≥20 prior samples, Beta-Binomial posterior ≥0.90 on this
    bench, and recency_decay ≥0.85 (roughly: < 90 days old). Otherwise
    returns (None, None). Every threshold is data-derived; no source allowlist.
    """
    if not reliability_ledger or not clusters:
        return None, None
    from .reliability import posterior_accuracy, source_identity  # type: ignore

    sources_idx = (reliability_ledger or {}).get("sources") or {}
    for cl in clusters:
        if cl.get("distinct_sources") != 1:
            continue
        members = cl.get("members") or []
        if not members:
            continue
        member = members[0]
        if (member.get("tier") or "C").upper() != "I":
            continue
        url = member.get("sourceUrl") or ""
        if not url:
            continue
        sid = source_identity(url, "")
        if not sid:
            continue
        bench_data = (sources_idx.get(sid) or {}).get("byBench", {}).get(
            bench_key
        ) or {}
        agree = float(bench_data.get("agree", 0.0))
        disagree = float(bench_data.get("disagree", 0.0))
        n = agree + disagree
        if n < EXCEPTIONAL_SAMPLE_MIN:
            continue
        accuracy = posterior_accuracy(agree, disagree)
        if accuracy < EXCEPTIONAL_RELIABILITY_THRESHOLD:
            continue
        if recency_decay(member.get("fetched")) < EXCEPTIONAL_RECENCY_MIN:
            continue
        return cl, "exceptional-source-override"
    return None, None


def pick_winner(
    observations: list[dict[str, Any]],
    *,
    bench_key: str = "",
    agreement_pp: float = DEFAULT_AGREEMENT_PP,
    warn_pp: float = DEFAULT_WARN_PP,
    block_pp: float = DEFAULT_BLOCK_PP,
    today: datetime.date | None = None,
    reliability_ledger: dict[str, Any] | None = None,
    vendor_whitelist: dict[str, Any] | None = None,
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

    raw_valid = [o for o in (observations or []) if o.get("value") is not None]
    if not raw_valid:
        return {
            "winner_value": None,
            "winner_obs": {},
            "winning_cluster": {},
            "all_clusters": [],
            "scored": [],
            "pseudo_observations": [],
            "is_contradiction": False,
            "severity": "GREEN",
            "max_delta": 0.0,
            "override_mode": None,
            "confidence": 0.0,
            "quarantine": False,
            "bayesianPoint": None,
        }

    # FAZ 8.A.3b: separate pseudo entries — they survive into the returned
    # payload (for audit) but do NOT participate in clustering.
    primary, pseudo = filter_pseudo_sources(raw_valid)
    valid = primary or raw_valid  # fallback to pseudo-only when nothing else

    # Tag evaluation context (scaffold / tool condition / lcb-version) so
    # downstream consumers can split clusters when needed.
    valid = tag_evaluation_context(valid)

    # Distinct URL count for verifications cap (FAZ 6.E)
    distinct_urls = {(o.get("sourceUrl") or "").strip().lower() for o in valid}
    distinct_urls.discard("")
    verif_count = len(distinct_urls) or len(valid)

    scored: list[dict[str, Any]] = []
    # Phase R5: resolve per-source recency curve when a whitelist is supplied.
    # vendor_whitelist is the full whitelist dict; we only need its `vendors`
    # subtree for the lookup. None => every obs gets the "default" curve.
    _vendor_idx = (vendor_whitelist or {}).get("vendors") if vendor_whitelist else None
    for o in valid:
        url = o.get("sourceUrl") or ""
        source_type = (
            vendor_update_interval(url, _vendor_idx) if _vendor_idx else "default"
        )
        # Phase R3: effective_trust_score applies the Beta-Binomial
        # reliability multiplier when a ledger is supplied; Phase R5 lets
        # vendor-cadence sources age more slowly via `source_type`.
        ts = effective_trust_score(
            o.get("tier", "C"),
            verif_count,
            o.get("fetched") or "",
            source_url=url,
            bench_key=bench_key,
            source_type=source_type,
            reliability_ledger=reliability_ledger,
            is_pseudo=False,
        )
        scored.append({**o, "trustScore": ts, "value": float(o["value"])})

    clusters = _cluster(scored, agreement_pp)

    # Rule 1 — I-tier override (with FAZ 8.A.3b single-shot dampening)
    override_mode: str | None = None
    i_cluster = _i_tier_cluster(clusters, require_min_verifications=True)
    if i_cluster and clusters[0] is not i_cluster:
        # I-tier cluster is not already on top — promote it
        clusters.remove(i_cluster)
        clusters.insert(0, i_cluster)
        override_mode = "independent-override"
    elif i_cluster and clusters[0] is i_cluster:
        override_mode = "independent-override"

    # Phase R4 — exceptional single-source override. When a single I-tier
    # observation has earned enough Bayesian track record (n>=20, posterior
    # accuracy >= 0.90, fresh < ~90d) on this bench, it bypasses the
    # single-outlier guard and wins directly. Every gate is data-derived;
    # no source allowlist.
    ex_cluster, ex_mode = _exceptional_source_override(
        clusters, reliability_ledger, bench_key
    )
    if ex_cluster is not None:
        if clusters[0] is not ex_cluster:
            clusters.remove(ex_cluster)
            clusters.insert(0, ex_cluster)
        winning_cluster = ex_cluster
        override_mode = ex_mode
    else:
        # Rule 3 — single-outlier guard (applied to post-override cluster order)
        winning_cluster = _single_outlier_guard(clusters)

    # Rule 4 — best individual within winning cluster
    winner_obs = max(
        winning_cluster.get("members", []) or scored[:1],
        key=lambda m: (m["trustScore"], m.get("fetched") or ""),
    )
    winner_value = winner_obs["value"]

    # Contradiction detection — max delta across primary observations only
    all_values = [s["value"] for s in scored]
    max_delta = max(all_values) - min(all_values) if len(all_values) > 1 else 0.0
    is_contradiction = max_delta >= agreement_pp and len(clusters) > 1
    if max_delta >= block_pp:
        severity = "RED"
    elif max_delta >= warn_pp:
        severity = "YELLOW"
    else:
        severity = "GREEN"

    result = {
        "winner_value": winner_value,
        "winner_obs": winner_obs,
        "winning_cluster": winning_cluster,
        "all_clusters": clusters,
        "scored": scored,
        "pseudo_observations": pseudo,
        "is_contradiction": is_contradiction,
        "severity": severity,
        "max_delta": round(max_delta, 2),
        "override_mode": override_mode,
        "bayesianPoint": None,  # populated by synth_core when historical pool ≥3
    }
    result["confidence"] = compute_cell_confidence(result)
    # Pass the tagged scored list so evaluationContext flags propagate.
    result["quarantine"] = should_quarantine(result, scored)
    return result


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
