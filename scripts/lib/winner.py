"""SSOT contradiction/winner resolver (F2.1).

Single canonical implementation of the pick_winner logic. Previously
duplicated across:
  - scripts/local-synth.py      (cluster ranking by distinct_sources + sum_trust)
  - scripts/merge.py            (_consensus_winner, FAZ 6.B re-clustering)
  - scripts/reconcile-bench-consensus.py

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
from .util import VERIFYING_TIERS, distinct_publishers, publisher_id

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

# Stricter twin of the thresholds above, for S-tier (official vendor
# self-report) singletons. Self-reports carry real inflation/cherry-picking
# risk that independent leaderboards don't, so the bar is materially
# higher: double the sample size, a tighter accuracy floor, and a shorter
# freshness window (forces re-verification against an independent source
# sooner). This is what lets a brand-new model's only-source-at-launch
# (the vendor's own announcement) avoid the confidence-floor quarantine
# without opening the door to unverified self-reports in general.
EXCEPTIONAL_S_TIER_RELIABILITY_THRESHOLD: float = 0.97
EXCEPTIONAL_S_TIER_SAMPLE_MIN: int = 40
EXCEPTIONAL_S_TIER_RECENCY_MIN: float = 0.90

# Earned-trust provisional admission (2026-07-24). The override thresholds
# above are expressed in the ledger's DECAYED-WEIGHT units, where the highest
# vendor figure in the whole ledger is anthropic.com×tb2 = 8.37 — so the
# S-tier escape hatch could never fire for any vendor on any bench, and every
# launch-day official number fell into the confidence<0.2 quarantine. That is
# blanket caution, not earned caution: the ledger's own record says
# anthropic.com is 97/97 agree and deepmind.google 228/228, while the real
# misses are bench-specific (openai.com×cfElo 0/6, openai.com×hle 3/3).
#
# This gate therefore judges a vendor PER BENCH on its RAW track record:
# raw counts are the honest measure of "has this source ever been wrong here",
# whereas the decayed weights measure current influence and collapse the
# posterior for small-but-perfect records (swePro 23/0 → 0.886 weighted vs
# 0.960 raw). Clearing it does not make a cell verified — it makes it
# PROVISIONAL: it counts toward the composite (with the single-source
# confidence haircut it already earns) and carries a "vendor-reported,
# awaiting independent verification" badge until an I-tier source lands.
PROVISIONAL_S_TIER_BENCH_SAMPLE_MIN: int = 20
PROVISIONAL_S_TIER_GLOBAL_SAMPLE_MIN: int = 40
PROVISIONAL_S_TIER_POSTERIOR_MIN: float = 0.90
PROVISIONAL_S_TIER_RECENCY_MIN: float = 0.85

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
                # Publisher identity, not URL: three pages of one leaderboard
                # are one source of evidence, however many URLs they occupy.
                pubs = distinct_publishers(cl["members"])
                cl["distinct_sources"] = len(pubs) if pubs else len(cl["members"])
                cl["latest_fetched"] = max(
                    cl.get("latest_fetched") or "",
                    s.get("fetched") or "",
                )
                placed = True
                break
        if not placed:
            pid = publisher_id(s.get("sourceUrl"), s.get("source"))
            clusters.append(
                {
                    "centroid": s["value"],
                    "members": [s],
                    "sum_trust": round(s["trustScore"], 4),
                    "distinct_sources": 1 if pid else 0,
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
        # Condition: ≥2 distinct I-tier PUBLISHERS OR average I-tier trust ≥
        # threshold. Counted per publisher so one leaderboard's several pages
        # cannot clear the "two independent sources" bar by itself.
        i_pubs = distinct_publishers(i_members)
        n_distinct_i = len(i_pubs) if i_pubs else len(i_members)
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


def s_tier_earned_trust(
    winner_obs: dict[str, Any] | None,
    reliability_ledger: dict[str, Any] | None,
    bench_key: str,
) -> bool:
    """True when an official (S-tier) singleton has EARNED provisional trust.

    Per-(vendor, bench) first: >= PROVISIONAL_S_TIER_BENCH_SAMPLE_MIN raw prior
    observations and a raw Beta(1,1) posterior >= PROVISIONAL_S_TIER_POSTERIOR_MIN
    (n=20 with zero misses → 0.955; a single miss still clears, two do not).
    When that bench is too thin, fall back to the vendor's global record
    (reliability.py's hierarchical doctrine) — but ONLY if the bench itself has
    no disagreement history of its own, so a vendor with a clean overall record
    still cannot borrow it to cover a bench it has been caught wrong on
    (openai.com is 69/69 globally yet 0/6 on cfElo → refused).

    Counts are RAW, not decay-weighted, deliberately: see the constants above.
    Observation freshness is still required (recency_decay >= 0.85) so a stale
    vendor page cannot ride a good track record.
    """
    if str((winner_obs or {}).get("tier") or "").upper() != "S":
        return False
    if not reliability_ledger:
        return False
    from .reliability import posterior_accuracy, source_identity  # type: ignore

    sid = source_identity(
        (winner_obs or {}).get("sourceUrl") or "",
        (winner_obs or {}).get("source") or "",
    )
    if not sid:
        return False
    entry = ((reliability_ledger or {}).get("sources") or {}).get(sid) or {}
    bench = (entry.get("byBench") or {}).get(bench_key) or {}
    bench_agree = int(bench.get("rawAgree") or 0)
    bench_disagree = int(bench.get("rawDisagree") or 0)
    agree, disagree = bench_agree, bench_disagree
    if agree + disagree < PROVISIONAL_S_TIER_BENCH_SAMPLE_MIN:
        if bench_disagree > 0:
            return False
        glob = entry.get("global") or {}
        agree = int(glob.get("rawAgree") or 0)
        disagree = int(glob.get("rawDisagree") or 0)
        if agree + disagree < PROVISIONAL_S_TIER_GLOBAL_SAMPLE_MIN:
            return False
    if posterior_accuracy(agree, disagree) < PROVISIONAL_S_TIER_POSTERIOR_MIN:
        return False
    return recency_decay((winner_obs or {}).get("fetched")) >= (
        PROVISIONAL_S_TIER_RECENCY_MIN
    )


def should_quarantine(
    result: dict[str, Any],
    primary_obs: list[dict[str, Any]] | None = None,
) -> bool:
    """Quarantine = "this value is UNTRUSTED, exclude it from the composite."
    Triggers, in order:
    - distinct value CLUSTERS > 5  → extreme dispersion (no agreed value)
    - any scaffold-variant obs     → different eval contexts must not share a cell
    - confidence < 0.2             → low-confidence floor, EXCEPT a clean I-tier
      winner, or an S-tier winner that cleared the stricter
      exceptional-source-override-s-tier bar (see below)

    DISPERSION COUNTS CLUSTERS, NOT RAW VALUES (2026-06-06): the trigger groups
    observations within agreement_pp first, so a strong consensus reported with
    trivial rounding spread (sweV 87.5 / 87.51 / 87.6 / 86.4 = ONE ~87.5 cluster)
    counts once. Counting raw rounded values conflated that with genuine
    dispersion and quarantined clean multi-source cells — opus-4-7.sweV had 6
    raw values but only 3 clusters (≈87.5 consensus from 20+ I-tier sources, plus
    an AA no-tools 72.5 and an lmcouncil 82.0, both legitimate harness variance,
    not misfiles — see the AA tooled-vs-no-tools note). A fabrication that
    disagrees still forms its own cluster, and a truly dispersed cell (>5
    non-agreeing clusters) still quarantines, so fabrication defense is intact.

    I-TIER EXEMPTION (2026-06-06): a single observation from a canonical
    independent leaderboard (tier I) that is NOT contradicted (severity ≠ RED)
    and NOT dispersed is the project's MOST-trusted evidence — Artificial
    Analysis for aaCoding/aaAgentic, Scale SEAL for swePro, etc. Quarantining it
    merely for confidence < 0.2 double-penalizes verification scarcity that
    trustScore ALREADY discounts (v=1 → 0.5) on top of the composite's
    coverage^(1/expo) shrinkage, and it self-contradicts apply-aa-authoritative
    (AA's own definitional indices were being excluded). Empirically this floor
    quarantined 153 such clean I-tier cells (48% of all quarantines, 2026-06-06),
    systematically sinking brand-new frontier models whose best benchmarks come
    from 1-2 independent leaderboards. The confidence floor is RETAINED for
    low-tier (C/S-only) or RED-contradicted single-source cells — the cases it
    was actually meant to catch (hype-blog inflation, conflicting numbers)."""
    scored = result.get("scored") or []
    clusters = result.get("all_clusters") or []
    if len(clusters) > 5:
        return True
    pool = list(primary_obs or scored)
    for o in pool:
        if not isinstance(o, dict):
            continue
        ctx = o.get("evaluationContext") or {}
        if isinstance(ctx, dict) and ctx.get("scaffold"):
            return True
    conf = float(result.get("confidence") or 0.0)
    if conf < 0.2:
        winner_tier = str((result.get("winner_obs") or {}).get("tier") or "").upper()
        severity = result.get("severity", "GREEN")
        override_mode = result.get("override_mode")
        # Clean canonical-leaderboard evidence is trusted, not quarantined.
        if winner_tier == "I" and severity != "RED":
            return False
        # A single official (S-tier) source is trusted ONLY when it has
        # earned the stricter S-tier reliability bar (see
        # _exceptional_source_override) — this is what unblocks brand-new
        # models whose sole source at launch is the vendor's own
        # announcement, without opening the door to unverified self-reports
        # in general (the hype-blog/inflation case this floor exists for).
        if (
            winner_tier == "S"
            and override_mode == "exceptional-source-override-s-tier"
            and severity != "RED"
        ):
            return False
        # Earned-trust provisional admission (2026-07-24): the vendor cleared
        # the per-bench raw track-record bar in s_tier_earned_trust, so the
        # cell is admitted as PROVISIONAL (badged in the UI) rather than
        # dropped. A vendor with a miss record on this bench never gets here.
        if winner_tier == "S" and result.get("provisional") and severity != "RED":
            return False
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
    """Phase R4 (+ S-tier extension): bypass _single_outlier_guard for highly
    trusted singletons.

    Returns (cluster, override_mode) when a single-source cluster meets every
    gate for its tier:
      I-tier: ≥20 prior samples, Beta-Binomial posterior ≥0.90 on this bench,
              recency_decay ≥0.85 (roughly: < 90 days old)
      S-tier: ≥40 prior samples, posterior ≥0.97, recency_decay ≥0.90 —
              stricter because official self-reports carry inflation risk
              independent leaderboards don't.
    Otherwise returns (None, None). Every threshold is data-derived; no
    source allowlist.
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
        tier = (member.get("tier") or "C").upper()
        if tier == "I":
            sample_min = EXCEPTIONAL_SAMPLE_MIN
            reliability_threshold = EXCEPTIONAL_RELIABILITY_THRESHOLD
            recency_min = EXCEPTIONAL_RECENCY_MIN
            mode = "exceptional-source-override"
        elif tier == "S":
            sample_min = EXCEPTIONAL_S_TIER_SAMPLE_MIN
            reliability_threshold = EXCEPTIONAL_S_TIER_RELIABILITY_THRESHOLD
            recency_min = EXCEPTIONAL_S_TIER_RECENCY_MIN
            mode = "exceptional-source-override-s-tier"
        else:
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
        if n < sample_min:
            continue
        accuracy = posterior_accuracy(agree, disagree)
        if accuracy < reliability_threshold:
            continue
        if recency_decay(member.get("fetched")) < recency_min:
            continue
        return cl, mode
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
            "provisional": False,
            "bayesianPoint": None,
        }

    # FAZ 8.A.3b: separate pseudo entries — they survive into the returned
    # payload (for audit) but do NOT participate in clustering.
    primary, pseudo = filter_pseudo_sources(raw_valid)
    valid = primary or raw_valid  # fallback to pseudo-only when nothing else

    # Tag evaluation context (scaffold / tool condition / lcb-version) so
    # downstream consumers can split clusters when needed.
    valid = tag_evaluation_context(valid)

    # Distinct URL count for verifications cap (FAZ 6.E). Count PRIMARY
    # (non-pseudo) sources only — a backfill / snapshot-extraction stub is
    # excluded from clustering, so counting it as a verification would be
    # inconsistent and would inflate the trust of a cell that has no real
    # source yet. A pseudo-only cell (primary empty) correctly yields
    # verif_count=0 → verif_factor 0 → low trust until a real source arrives.
    # Equals the prior value whenever any primary source exists (valid==primary
    # in that case); only the pseudo-only fallback changes (1→0).
    # 2026-07-25: counted per PUBLISHER, and only tiers that may confirm a
    # value independently (I/S). Community reruns still contribute tier weight
    # and still show in the provenance trail, but five blogs republishing one
    # leaderboard no longer read as five verifications. A cell backed solely by
    # community sources floors at 1 rather than 0 — corroboration, not proof,
    # and not an automatic wipe of the only evidence we have.
    verifying_pubs = distinct_publishers(primary, tiers=VERIFYING_TIERS)
    any_pubs = distinct_publishers(primary)
    verif_count = len(verifying_pubs) or (1 if (any_pubs or primary) else 0)

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
    # Earned-trust provisional flag — computed BEFORE should_quarantine, which
    # consumes it. Only single-source official cells can be provisional: a
    # multi-source cell is either verified or contradicted, never "pending
    # independent verification".
    result["provisional"] = bool(
        (winning_cluster.get("distinct_sources") or 0) <= 1
        and severity != "RED"
        and s_tier_earned_trust(winner_obs, reliability_ledger, bench_key)
    )
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
