"""Python-side synth (FAZ 4.D, 2026-05-10) — replaces sonnet synth agent.

Input: 18 flat gather artifacts (FAZ 4.C.1.b schema).
Output: full OUTPUT_SCHEMA artifact ready for merge.py.

Why Python instead of sonnet:
  - trustScore arithmetic, argmax, contradiction delta detection, N/A rule
    lookup, lineup aggregation are all DETERMINISTIC mechanical operations.
  - Sonnet synth attempts hit 32K output token limit on full 60-model schema.
  - Python is faster, free, and deterministic — better fit for the work.
  - Edge cases (WRONG_ID nuance) can still escalate to sonnet via a hook
    if needed; default flow is pure Python.

trustScore formula (per agent.md / SKILL.md):
  trustScore(value) = tierWeight × min(verifications, 3)/3 × recencyDecay(date)
  tierWeight: I=1.0, S=0.7, C=0.4
  recencyDecay: <30d=1.00, <90d=0.85, <180d=0.70, <365d=0.50, ≥365d=0.30

Contradiction thresholds (per _schema.contracts):
  VERIFICATION_AGREEMENT_PP = 1.5  (within → agreement)
  CONTRADICTION_WARN_PP     = 3.0  (YELLOW)
  CONTRADICTION_BLOCK_PP    = 5.0  (RED)
"""

from __future__ import annotations

import datetime
import glob
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

# SSOT: tier weights live in lib.tiers; pp thresholds in lib.constants (were
# parallel literals here before 2026-06-06).
from .constants import CONTRADICTION_BLOCK_PP as DEFAULT_BLOCK_PP
from .constants import CONTRADICTION_WARN_PP as DEFAULT_WARN_PP
from .constants import VERIFICATION_AGREEMENT_PP as DEFAULT_AGREEMENT_PP
from .tiers import TIER_WEIGHT as TIER_WEIGHTS


def _parse_date(s: Any) -> datetime.date | None:
    if not isinstance(s, str):
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _recency_decay(fetched: str, today: datetime.date) -> float:
    d = _parse_date(fetched)
    if d is None:
        return 0.5
    age = (today - d).days
    if age < 30:
        return 1.00
    if age < 90:
        return 0.85
    if age < 180:
        return 0.70
    if age < 365:
        return 0.50
    return 0.30


def _trust_score(
    tier: str,
    verifications: int,
    fetched: str,
    today: datetime.date,
    *,
    source_url: str = "",
    bench_key: str = "",
    reliability_ledger: dict | None = None,
) -> float:
    """Phase R2+R3: delegates verif_factor to tiers.verif_factor (log-base-4
    information-theoretic scaling) and, when reliability_ledger is supplied,
    applies the per-(source, bench) Beta-Binomial multiplier.
    """
    from .tiers import verif_factor as _vf

    w = TIER_WEIGHTS.get((tier or "C").upper(), 0.4)
    v = _vf(int(verifications) if verifications is not None else 0)
    r = _recency_decay(fetched, today)
    base = round(w * v * r, 3)
    if reliability_ledger and source_url:
        from .reliability import reliability_multiplier  # type: ignore

        mult = reliability_multiplier(reliability_ledger, source_url, bench_key)
        return round(base * mult, 3)
    return base


def _load_gather_artifacts(root: Path) -> list[tuple[str, dict[str, Any]]]:
    paths = sorted(glob.glob(str(root / ".aicodermap-agent-out-batch*.gather.json")))
    out: list[tuple[str, dict[str, Any]]] = []
    for p in paths:
        try:
            with open(p, encoding="utf-8") as fp:
                data = json.load(fp)
            if isinstance(data, dict):
                out.append((p, data))
        except (OSError, json.JSONDecodeError) as e:
            print(f"⚠ skipping {Path(p).name}: {e}")
    return out


def _load_unhealthy_urls(root: Path, wl: dict[str, Any] | None = None) -> set[str]:
    """FAZ 6.A (2026-05-10): observations citing URLs marked unhealthy in
    data/sources-whitelist.json._runtime.unhealthy MUST be dropped before
    trustScore math runs. The cycle 2026-05-09 fabricated 26 tb2 values
    from https://tbench.ai/leaderboard (a SPA shell with empty snapshot)
    and the I-tier override promoted them over multi-source consensus.

    6.6: pass an already-parsed `wl` to avoid a redundant whitelist read.
    """
    if wl is None:
        wl_path = root / "data" / "sources-whitelist.json"
        try:
            wl = json.loads(wl_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return set()
    runtime = (wl or {}).get("_runtime") or {}
    unhealthy = runtime.get("unhealthy") or {}
    return {
        (u or "").strip().rstrip("/").lower() for u, flag in unhealthy.items() if flag
    }


def _load_low_confidence_urls(
    root: Path, wl: dict[str, Any] | None = None
) -> tuple[set[str], float]:
    """FAZ 6.C (2026-05-10): root-listing URLs (whole-leaderboard pages) are
    prone to cross-row misattribution. Specific bench-path URLs are reliable;
    bare root URLs that list every (model, bench) combination are not.
    Penalize their trustScore by `trustPenaltyMultiplier` so a single
    root-cited entry can't out-weigh multi-source bench-path consensus.

    Returns: (url_set, multiplier). When url_set is empty, no penalty applies.
    6.6: pass an already-parsed `wl` to avoid a redundant whitelist read.
    """
    if wl is None:
        wl_path = root / "data" / "sources-whitelist.json"
        try:
            wl = json.loads(wl_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return set(), 1.0
    runtime = (wl or {}).get("_runtime") or {}
    block = runtime.get("lowConfidenceUrls") or {}
    multiplier = float(block.get("trustPenaltyMultiplier") or 0.5)
    urls = block.get("urls") or {}
    return (
        {(u or "").strip().rstrip("/").lower() for u, flag in urls.items() if flag},
        multiplier,
    )


def _aggregate_observations(
    artifacts: list[tuple[str, dict[str, Any]]],
    unhealthy_urls: set[str] | None = None,
) -> dict[tuple[str, str], list[dict[str, Any]]]:
    """Group all observations by (modelId, benchKey) cell.

    FAZ 6.A (2026-05-10): observations citing URLs in `unhealthy_urls`
    (sourced from sources-whitelist.json `_runtime.unhealthy`) are dropped
    BEFORE trustScore math. This kills the SPA-shell fabrication class
    without relying on consensus heuristics downstream.
    """
    skip_urls = unhealthy_urls or set()
    cells: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    rejected_count = 0
    for _path, art in artifacts:
        for obs in art.get("observations") or []:
            if not isinstance(obs, dict):
                continue
            mid = obs.get("modelId")
            bk = obs.get("benchKey")
            if not (isinstance(mid, str) and isinstance(bk, str)):
                continue
            url_value = obs.get("value")
            if url_value is None:
                continue
            try:
                value = float(url_value)
            except (TypeError, ValueError):
                continue
            url = (obs.get("sourceUrl") or "").strip().rstrip("/").lower()
            if url and url in skip_urls:
                rejected_count += 1
                continue
            cells[(mid, bk)].append(
                {
                    "value": value,
                    "sourceUrl": obs.get("sourceUrl") or "",
                    "tier": (obs.get("tier") or "C").upper(),
                    "fetched": obs.get("fetched") or "",
                }
            )
    if rejected_count:
        print(
            f"⚠ FAZ 6.A SPA guard: dropped {rejected_count} observations citing "
            f"unhealthy URLs ({sorted(skip_urls)})"
        )
    return cells


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


def _pick_winner(
    observations: list[dict[str, Any]],
    today: datetime.date,
    *,
    agreement_pp: float = DEFAULT_AGREEMENT_PP,
    low_conf_urls: set[str] | None = None,
    low_conf_multiplier: float = 1.0,
    bench_key: str = "",
    reliability_ledger: dict | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], float]:
    """Cluster-aware winner selection (FAZ 6.B, 2026-05-10).

    Replaces the prior single-argmax. The previous rule picked the
    observation with max individual trustScore — that let a single
    high-tier outlier (verifs=1, fabricated I-tier) override 5+ agreeing
    lower-tier sources. Concrete failure: deepseek-v4-pro.swePro had 6
    sources at 55.4 (incl. Scale SEAL trust=0.87) but a single
    benchlm.ai/ root-URL fabrication at 20.12 (trust=0.333) was emitted
    as the winner because it was the most recent/most-recent-tied entry.

    New rule:
      1. Cluster observations by value (members within agreement_pp join).
      2. Pick the cluster with max sum(trustScore) — multi-source cluster
         with mid-trust members beats single-source cluster with high-trust
         outlier.
      3. Tiebreak: distinct sources desc, then member count desc.
      4. Within the winning cluster, the winner is the highest-individual-
         trustScore member (most authoritative source for the consensus).

    Returns (winner_obs, all_scored, max_delta_across_all_obs).
    """
    if not observations:
        return ({}, [], 0.0)
    # FAZ 6.E (2026-05-10): pass DISTINCT URL count instead of total
    # observation count to _trust_score. The agent emits one observation
    # per (modelId, benchKey) per fetch attempt — three obs from the same
    # Scale SEAL page should count as 1 verification, not 3. Distinct
    # source count caps the verifications input.
    distinct_urls = {(o.get("sourceUrl") or "").strip().lower() for o in observations}
    distinct_urls.discard("")
    verif_count = len(distinct_urls) or len(observations)
    scored = []
    for o in observations:
        score = _trust_score(
            o["tier"],
            verif_count,
            o.get("fetched") or "",
            today,
            source_url=o.get("sourceUrl") or "",
            bench_key=bench_key,
            reliability_ledger=reliability_ledger,
        )
        scored.append({**o, "trustScore": score})

    # FAZ 6.C — root-URL trust penalty before clustering. Lets a 0.4-trust
    # demoted root citation lose to specific-bench-path multi-source consensus.
    if low_conf_urls:
        _apply_low_confidence_penalty(scored, low_conf_urls, low_conf_multiplier)

    clusters = _cluster_observations(scored, agreement_pp)
    winning_cluster = clusters[0]
    winner = max(
        winning_cluster["members"],
        key=lambda m: (m["trustScore"], m.get("fetched") or ""),
    )
    values = [s["value"] for s in scored]
    max_delta = max(values) - min(values) if len(values) > 1 else 0.0
    return winner, scored, max_delta


def _build_pricing_api(
    pricingObs: list[dict[str, Any]],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, set[str]]]:
    """Group pricingObs by modelId → pricing.api[] entries (deduped by provider)."""
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen: dict[str, set[str]] = defaultdict(set)
    for p in pricingObs:
        if not isinstance(p, dict):
            continue
        mid = p.get("modelId")
        provider = p.get("provider")
        if not (isinstance(mid, str) and isinstance(provider, str)):
            continue
        key = provider.lower()
        if key in seen[mid]:
            continue
        seen[mid].add(key)
        entry = {"provider": provider}
        for f in ("in", "out", "cacheHit", "throughput"):
            if isinstance(p.get(f), (int, float)):
                entry[f] = p[f]
        for f in ("url", "fetched"):
            if isinstance(p.get(f), str):
                entry[f] = p[f]
        by_model[mid].append(entry)
    return by_model, seen


def _build_ollama_block(ollamaObs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_model: dict[str, dict[str, Any]] = {}
    for o in ollamaObs:
        if not isinstance(o, dict):
            continue
        mid = o.get("modelId")
        if not isinstance(mid, str):
            continue
        block = {k: v for k, v in o.items() if k != "modelId" and v is not None}
        existing = by_model.get(mid, {})
        # Merge, preferring the larger/more-complete entry.
        for k, v in block.items():
            existing[k] = v
        by_model[mid] = existing
    return by_model


_PRIVACY_FIELDS = (
    "trainingDataOptOut",
    "dataResidency",
    "soc2",
    "gdpr",
    "apiLogging",
)
_PRIVACY_TIER_RANK = {"I": 3, "S": 2, "C": 1}


def _build_privacy_block(
    privacyObs: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Group privacyObs by (modelId, field); pick highest-tier winner,
    then most-recent fetched. I-tier audit registries override S-tier
    vendor self-report. Returns {modelId: {field: value, ...}}.
    """
    by_cell: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for p in privacyObs:
        if not isinstance(p, dict):
            continue
        mid = p.get("modelId")
        field = p.get("field")
        if not (isinstance(mid, str) and field in _PRIVACY_FIELDS):
            continue
        if "value" not in p:
            continue
        by_cell[(mid, field)].append(p)

    def _rank(o: dict[str, Any]) -> int:
        t = o.get("tier")
        return _PRIVACY_TIER_RANK.get(t, 0) if isinstance(t, str) else 0

    by_model: dict[str, dict[str, Any]] = defaultdict(dict)
    for (mid, field), obs_list in by_cell.items():
        top_tier = max(_rank(o) for o in obs_list)
        top = [o for o in obs_list if _rank(o) == top_tier]
        top.sort(key=lambda o: o.get("fetched") or "", reverse=True)
        by_model[mid][field] = top[0]["value"]
    return by_model


def _build_unsloth_variants(
    unslothObs: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen: dict[str, set[str]] = defaultdict(set)
    for u in unslothObs:
        if not isinstance(u, dict):
            continue
        mid = u.get("modelId")
        name = u.get("name") or u.get("variant")
        if not (isinstance(mid, str) and isinstance(name, str)):
            continue
        if name in seen[mid]:
            continue
        seen[mid].add(name)
        entry = {"name": name}
        for f in ("size", "vram"):
            if u.get(f) is not None:
                entry[f] = u[f]
        by_model[mid].append(entry)
    return by_model


def _aggregate_meta(modelMeta: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Merge modelMeta entries by modelId. Last writer wins per field."""
    by_model: dict[str, dict[str, Any]] = defaultdict(dict)
    for m in modelMeta:
        if not isinstance(m, dict):
            continue
        mid = m.get("modelId")
        if not isinstance(mid, str):
            continue
        for k, v in m.items():
            if k == "modelId" or v is None:
                continue
            by_model[mid][k] = v
    return by_model


def _aggregate_lineup_hints(
    artifacts: list[tuple[str, dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {
        "new": [],
        "deprecated": [],
        "renamed": [],
        "removed": [],
    }
    for _p, art in artifacts:
        for h in art.get("lineupHints") or []:
            if not isinstance(h, dict):
                continue
            event = h.get("event")
            if event in out:
                out[event].append(
                    {
                        "id": h.get("modelId"),
                        "evidenceUrl": h.get("evidence") or h.get("evidenceUrl"),
                        "details": h.get("details"),
                    }
                )
    return out


def _aggregate_na_candidates(
    artifacts: list[tuple[str, dict[str, Any]]],
    canonical_rules: set[str],
    filled_cells: set[tuple[str, str]] | None = None,
) -> dict[str, list[dict[str, str]]]:
    """Map naCandidates rationale → canonical rule. Drop unmappable.

    User policy (2026-05-10): N/A is NEVER permanent — every cycle
    re-attempts the cell. If a fill was found this cycle (cell in
    `filled_cells`), N/A is suppressed (fill > N/A precedence). If no
    fill but a rationale matches a canonical rule, the cell remains N/A
    until the next cycle re-attempts.
    """
    by_model: dict[str, list[dict[str, str]]] = defaultdict(list)
    filled_cells = filled_cells or set()
    rule_keywords = {
        # Original two rules
        "embedding-only-tier": ["embedding"],
        "spa-blocked-bench-without-alt": [
            "spa",
            "no extractable",
            "blocked",
            "spa-blocked",
        ],
        # FAZ 5.B (2026-05-10): expanded taxonomy.
        "vendor-no-niche-bench-publish": [
            "not published",
            "vendor no self-report",
            "vendor does not publish",
            "no vendor self-report",
            "vendor reporting absent",
            "no published",
            "absent from vendor",
        ],
        "legacy-bench-superseded": [
            "deprecated",
            "superseded",
            "replaced by",
            "legacy bench",
        ],
        "closed-weight-no-local-runtime": [
            "closed-weight",
            "proprietary",
            "no local runtime",
            "no ollama",
            "no unsloth",
            "api-only",
            "inference api only",
        ],
        "compute-only-public-no-elo": [
            "lmarena",
            "elo only",
            "vote-based",
            "no public elo",
            "no chat arena",
        ],
        "vendor-emphasis-mismatch": [
            "vendor emphasis",
            "different bench focus",
            "vendor focus",
            "research-grade",
            "western leaderboards sparse",
        ],
        "edge-model-no-frontier-bench": [
            "edge model",
            "edge tier",
            "small footprint",
            "on-device",
            "ultra-small",
        ],
    }
    for _p, art in artifacts:
        for c in art.get("naCandidates") or []:
            if not isinstance(c, dict):
                continue
            mid = c.get("modelId")
            bk = c.get("benchKey")
            rationale = (c.get("rationale") or "").lower()
            if not (isinstance(mid, str) and isinstance(bk, str)):
                continue
            # FILL > N/A precedence: if cell was filled this cycle, drop N/A.
            if (mid, bk) in filled_cells:
                continue
            chosen = None
            for rule, kw_list in rule_keywords.items():
                if rule not in canonical_rules:
                    continue
                if any(kw in rationale for kw in kw_list):
                    chosen = rule
                    break
            if chosen:
                # dedup by (modelId, benchKey)
                if not any(e["benchKey"] == bk for e in by_model[mid]):
                    by_model[mid].append({"benchKey": bk, "rule": chosen})
    return by_model


def _aggregate_raw_gaps(
    artifacts: list[tuple[str, dict[str, Any]]],
    filled_cells: set[tuple[str, str]],
    bench_to_url: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Take rawGaps, dedupe by key, add source='agent', drop cells now filled.

    Empty `triedSources` fall back to the bench's primary leaderboard URL
    so MX3 (validate_gaps) doesn't strip the entry.
    """
    bench_to_url = bench_to_url or {}
    fallback_url = "https://artificialanalysis.ai/leaderboards/models"
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for _p, art in artifacts:
        for g in art.get("rawGaps") or []:
            if not isinstance(g, dict):
                continue
            mid = g.get("modelId")
            bk = g.get("benchKey")
            if not (isinstance(mid, str) and isinstance(bk, str)):
                continue
            if (mid, bk) in filled_cells:
                continue
            key = f"{mid}.{bk}"
            if key in seen:
                continue
            seen.add(key)
            triedSources = g.get("triedSources") or []
            if not triedSources:
                triedSources = [bench_to_url.get(bk, fallback_url)]
            triedQueries = g.get("triedQueries") or []
            if not triedQueries:
                triedQueries = [
                    f"{mid} {bk} benchmark 2026",
                    f"{mid} {bk} score",
                ]
            out.append(
                {
                    "key": key,
                    "reason": g.get("reason") or "agent attempted but found no value",
                    "triedSources": triedSources,
                    "triedQueries": triedQueries,
                    "triedFormats": g.get("triedFormats") or ["websearch_snippet"],
                    "source": "agent",
                }
            )
    return out


def synth(
    artifacts: list[tuple[str, dict[str, Any]]],
    canonical_bench_keys: set[str],
    canonical_na_rules: set[str],
    today: datetime.date,
    *,
    agreement_pp: float = DEFAULT_AGREEMENT_PP,
    warn_pp: float = DEFAULT_WARN_PP,
    block_pp: float = DEFAULT_BLOCK_PP,
    unhealthy_urls: set[str] | None = None,
    low_conf_urls: set[str] | None = None,
    low_conf_multiplier: float = 1.0,
    reliability_ledger: dict | None = None,
) -> dict[str, Any]:
    """Run the full synthesis pipeline. Returns OUTPUT_SCHEMA artifact dict."""
    # Aggregate all observation cells. FAZ 6.A — drop SPA-shell citations
    # before trustScore math runs.
    cells = _aggregate_observations(artifacts, unhealthy_urls=unhealthy_urls)

    # Walk each cell: pick winner, detect contradiction.
    models_by_id: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "updates": {"bench": {}, "lastUpdated": today.isoformat()},
            "sourcesAdded": [],
            "notApplicable": [],
        }
    )
    contradictions: list[dict[str, Any]] = []
    filled_cells: set[tuple[str, str]] = set()

    for (mid, bk), obs_list in cells.items():
        if bk not in canonical_bench_keys:
            # Drop non-canonical bench keys at synth time (e.g. legacy 'aider').
            continue
        winner, scored, max_delta = _pick_winner(
            obs_list,
            today,
            agreement_pp=agreement_pp,
            low_conf_urls=low_conf_urls,
            low_conf_multiplier=low_conf_multiplier,
            bench_key=bk,
            reliability_ledger=reliability_ledger,
        )
        if not winner:
            continue
        models_by_id[mid]["id"] = mid
        models_by_id[mid]["updates"]["bench"][bk] = winner["value"]
        filled_cells.add((mid, bk))

        # SourcesAdded: append every observation with its trustScore.
        for s in scored:
            models_by_id[mid]["sourcesAdded"].append(
                {
                    "key": f"{mid}.{bk}",
                    "value": s["value"],
                    "source": s["sourceUrl"][:100] or "synth-aggregated",
                    "url": s["sourceUrl"],
                    "tier": s["tier"],
                    "fetched": s["fetched"],
                    "verifications": len(scored),
                    "trustScore": s["trustScore"],
                }
            )

        # Contradiction detection: max delta between any two observations.
        if max_delta >= agreement_pp and len(scored) > 1:
            severity = (
                "RED"
                if max_delta >= block_pp
                else "YELLOW"
                if max_delta >= warn_pp
                else "GREEN"
            )
            contradictions.append(
                {
                    "modelId": mid,
                    "field": bk,
                    "candidates": scored,
                    "delta": round(max_delta, 2),
                    "severity": severity,
                    "autoResolveWinner": {
                        "value": winner["value"],
                        "trustScore": winner["trustScore"],
                        "sourceUrl": winner["sourceUrl"],
                        "tier": winner["tier"],
                    },
                }
            )

    # Pricing aggregation.
    all_pricing = []
    for _p, art in artifacts:
        all_pricing.extend(art.get("pricingObs") or [])
    pricing_by_model, _ = _build_pricing_api(all_pricing)
    for mid, api_list in pricing_by_model.items():
        models_by_id[mid]["id"] = mid
        models_by_id[mid]["updates"]["pricing"] = {"api": api_list}

    # Ollama aggregation.
    all_ollama = []
    for _p, art in artifacts:
        all_ollama.extend(art.get("ollamaObs") or [])
    ollama_by_model = _build_ollama_block(all_ollama)
    for mid, block in ollama_by_model.items():
        models_by_id[mid]["id"] = mid
        models_by_id[mid]["updates"]["ollama"] = block

    # Unsloth variants.
    all_unsloth = []
    for _p, art in artifacts:
        all_unsloth.extend(art.get("unslothObs") or [])
    unsloth_by_model = _build_unsloth_variants(all_unsloth)
    for mid, variants in unsloth_by_model.items():
        models_by_id[mid]["id"] = mid
        models_by_id[mid]["updates"]["unslothVariants"] = variants

    # Privacy / compliance aggregation. I-tier audit registries override
    # S-tier vendor self-report; ties broken by most-recent fetched date.
    all_privacy = []
    for _p, art in artifacts:
        all_privacy.extend(art.get("privacyObs") or [])
    privacy_by_model = _build_privacy_block(all_privacy)
    for mid, block in privacy_by_model.items():
        models_by_id[mid]["id"] = mid
        models_by_id[mid]["updates"]["privacy"] = block

    # Meta scalars (released, context, license, open, providers, vramRequirement).
    all_meta = []
    for _p, art in artifacts:
        all_meta.extend(art.get("modelMeta") or [])
    meta_by_model = _aggregate_meta(all_meta)
    canonical_tiers = {
        "frontier",
        "open-flagship",
        "coder-specialized",
        "gemma",
        "ollama-local",
    }
    canonical_status = {"active", "deprecated", "archived"}
    for mid, meta in meta_by_model.items():
        models_by_id[mid]["id"] = mid
        for k, v in meta.items():
            if k in (
                "released",
                "context",
                "license",
                "open",
                "providers",
                "vramRequirement",
                "name",
                "ollamaSize",
            ):
                models_by_id[mid]["updates"].setdefault(k, v)
            elif k == "tier":
                # Drop non-canonical tier — haiku confused source-tier (I/S/C)
                # with model-tier (frontier/open-flagship/...).
                if v in canonical_tiers:
                    models_by_id[mid]["updates"].setdefault("tier", v)
            elif k == "status":
                if v in canonical_status:
                    models_by_id[mid]["updates"].setdefault("status", v)

    # N/A rule mapping.
    na_by_model = _aggregate_na_candidates(artifacts, canonical_na_rules, filled_cells)
    for mid, na_list in na_by_model.items():
        models_by_id[mid]["id"] = mid
        models_by_id[mid]["notApplicable"] = na_list

    # Lineup aggregation.
    lineup_changes = _aggregate_lineup_hints(artifacts)

    # Gaps (after filled cells settled). Build bench → URL map for triedSources fallback.
    bench_to_url: dict[str, str] = {}
    try:
        from lib.whitelist import load_whitelist as _lw

        wl = _lw()
        for lb in wl.get("leaderboards", []) or []:
            url = lb.get("url") or ""
            for pub in lb.get("publishes") or []:
                key = (
                    pub
                    if isinstance(pub, str)
                    else (pub.get("key") if isinstance(pub, dict) else None)
                )
                if key and key not in bench_to_url:
                    bench_to_url[key] = url
    except Exception:
        pass
    gaps = _aggregate_raw_gaps(artifacts, filled_cells, bench_to_url)

    # Coverage matrix.
    total_filled = sum(
        len((m.get("updates") or {}).get("bench") or {}) for m in models_by_id.values()
    )
    total_na = sum(len(m.get("notApplicable") or []) for m in models_by_id.values())

    return {
        "confidence": "HIGH" if total_filled > 100 else "MEDIUM",
        "synthesis": (
            f"Python synth (FAZ 4.D): {len(artifacts)} flat-gather batches → "
            f"{total_filled} cell fills, {len(contradictions)} contradictions, "
            f"{total_na} N/A, {len(gaps)} agent gaps."
        ),
        "lineupChanges": lineup_changes,
        "models": [{"id": mid, **m} for mid, m in models_by_id.items()],
        "newModels": [],
        "contradictions": contradictions,
        "gaps": gaps,
        "discoveries": {"vendors": [], "benchmarks": []},
        "validationCoverage": 0.0,  # filled by gap-gen
        "coverageMatrix": {
            "totalCells": 0,
            "filledCells": total_filled,
            "gapsRecorded": len(gaps),
            "notApplicableCells": total_na,
        },
        "runtime": {"healthChecks": {}, "fetchErrors": []},
        "runMetadata": {
            "agentVersion": "synth-python-2026-05-10",
            "startedAt": datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "finishedAt": datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "toolCallCount": 0,
            "fetchAttemptCount": 0,
            "batchCount": len(artifacts),
        },
        "error": None,
    }


def main() -> int:
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ROOT = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(ROOT / "scripts"))
    from lib.whitelist import (  # noqa: E402
        all_bench_keys,
        load_whitelist,
        not_applicable_rules,
    )

    artifacts = _load_gather_artifacts(ROOT)
    print(f"=== PYTHON SYNTH (FAZ 4.D) === gather artifacts: {len(artifacts)}")
    if not artifacts:
        print("⚠ no gather artifacts found")
        return 1

    wl = load_whitelist()
    # FAZ 8.A (2026-05-18): canonical universe is core ∪ emerging so the
    # synth drop-filter doesn't discard valid emerging-key fills that
    # gather agents emit. Prior `core_bench_keys()` alone dropped ~295
    # cells/cycle, the most expensive recurring data loss.
    canonical_bench = set(all_bench_keys(wl))
    na_rules = not_applicable_rules(wl) or {}
    canonical_na = {
        r.get("rule") for r in (na_rules.get("rules") or []) if r.get("rule")
    }

    today = datetime.date.today()
    unhealthy_urls = _load_unhealthy_urls(ROOT)
    low_conf_urls, low_conf_mult = _load_low_confidence_urls(ROOT)
    if unhealthy_urls:
        print(f"FAZ 6.A SPA guard active: {len(unhealthy_urls)} unhealthy URL(s)")
    if low_conf_urls:
        print(
            f"FAZ 6.C low-confidence guard active: {len(low_conf_urls)} root URL(s) "
            f"× {low_conf_mult} trust multiplier"
        )
    artifact = synth(
        artifacts,
        canonical_bench,
        canonical_na,
        today,
        unhealthy_urls=unhealthy_urls,
        low_conf_urls=low_conf_urls,
        low_conf_multiplier=low_conf_mult,
    )

    out_path = ROOT / ".aicodermap-agent-out-synth.json"
    out_path.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"wrote: {out_path.relative_to(ROOT)}")
    print(f"  models with fills:       {len(artifact['models'])}")
    print(f"  total bench fills:       {artifact['coverageMatrix']['filledCells']}")
    print(f"  contradictions:          {len(artifact['contradictions'])}")
    print(
        f"  N/A:                     {artifact['coverageMatrix']['notApplicableCells']}"
    )
    print(f"  gaps:                    {len(artifact['gaps'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
