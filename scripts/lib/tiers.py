"""Tier weight + trust constants — single source of truth.

Previously duplicated across:
  - scripts/local-synth.py   TIER_WEIGHT = {I:1.0, S:0.7, C:0.4, U:0.1}
  - scripts/gather-union.py  TIER_WEIGHT: dict[str, float]
  - scripts/lib/synth.py     TIER_WEIGHTS = {I:1.0, S:0.7, C:0.4, U:0.1}

All callers import from here. No magic numbers in individual scripts.
"""

from __future__ import annotations

import datetime
import math
from typing import Any

# Canonical tier weights (SKILL.md TRUST_SCORE_FORMULA)
TIER_WEIGHT: dict[str, float] = {
    "I": 1.0,  # independent leaderboard
    "S": 0.7,  # vendor self-report
    "C": 0.4,  # community / 3rd-party
    "U": 0.1,  # forum / social (signal only, never committed)
}

TIER_LABELS: dict[str, str] = {
    "I": "independent",
    "S": "vendor",
    "C": "community",
    "U": "forum",
}

# Tier hierarchy for comparison (higher = more authoritative)
TIER_RANK: dict[str, int] = {"I": 3, "S": 2, "C": 1, "U": 0}


def tier_weight(tier: str) -> float:
    """Return the trust weight for a tier string. Unknown tiers → C weight."""
    return TIER_WEIGHT.get((tier or "C").upper(), TIER_WEIGHT["C"])


def tier_rank(tier: str) -> int:
    """Return the ordinal rank for tier comparison. Higher = more authoritative."""
    return TIER_RANK.get((tier or "C").upper(), TIER_RANK["C"])


def tier_label(tier: str) -> str:
    """Return human-readable tier label."""
    return TIER_LABELS.get((tier or "C").upper(), "community")


def is_independent(tier: str) -> bool:
    return (tier or "").upper() == "I"


# Phase R5: per-source-type recency decay curves. Each entry is a list of
# (max_age_days, weight) tuples in strictly ascending age. The first tuple
# whose threshold exceeds the observation age supplies the multiplier.
# `default` matches the pre-R5 piecewise; longer-cadence sources (vendor
# quarterly/annual releases) age more slowly, weekly community blogs age
# faster. Choosing the right curve depends on the publisher's update
# rhythm — derived from the whitelist via vendor_update_interval().
INTERVAL_DECAY_CURVES: dict[str, list[tuple[int, float]]] = {
    "default": [
        (30, 1.00),
        (90, 0.85),
        (180, 0.70),
        (365, 0.50),
        (10**9, 0.30),
    ],
    "weekly": [
        (30, 0.80),
        (90, 0.40),
        (180, 0.10),
        (10**9, 0.00),
    ],
    "monthly": [
        (30, 0.95),
        (90, 0.75),
        (180, 0.50),
        (365, 0.20),
        (10**9, 0.05),
    ],
    "quarterly": [
        (30, 1.00),
        (90, 0.95),
        (180, 0.85),
        (365, 0.60),
        (10**9, 0.30),
    ],
    "annual": [
        (30, 1.00),
        (90, 1.00),
        (180, 0.95),
        (365, 0.85),
        (10**9, 0.60),
    ],
}


def _age_days(date_str: Any) -> int | None:
    """Parse an ISO date and return its age in days from today. Returns
    None when the input is missing or unparseable."""
    if not date_str:
        return None
    try:
        s = str(date_str).strip()
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z"):
            try:
                dt = datetime.datetime.strptime(s[: len(fmt.replace("%", "XX"))], fmt)
                return (
                    datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                    - dt
                ).days
            except ValueError:
                continue
        return (datetime.date.today() - datetime.date.fromisoformat(s[:10])).days
    except Exception:
        return None


def recency_decay(date_str: Any, *, source_type: str = "default") -> float:
    """Recency-decay multiplier for an ISO date.

    Phase R5: `source_type` selects the curve from `INTERVAL_DECAY_CURVES`.
    Unknown source_types fall back to the `default` curve so any caller
    written before R5 keeps the pre-R5 behaviour exactly.

    Missing/unparseable dates return 0.50 (legacy contract).
    """
    age = _age_days(date_str)
    if age is None:
        return 0.50
    curve = INTERVAL_DECAY_CURVES.get(
        source_type or "default", INTERVAL_DECAY_CURVES["default"]
    )
    for threshold, weight in curve:
        if age < threshold:
            return weight
    return curve[-1][1]


def vendor_update_interval(url: str, whitelist_vendors: dict | None) -> str:
    """Return the vendorUpdateInterval ('weekly' | 'monthly' | 'quarterly'
    | 'annual') for a URL by matching its hostname against the whitelist's
    vendor entries. Returns 'default' when no match.

    Walks every vendor.urls list (the whitelist tags vendors with multiple
    canonical hostnames). Case-insensitive, www-stripped.
    """
    if not url or not whitelist_vendors:
        return "default"
    try:
        from urllib.parse import urlparse

        host = (urlparse(str(url)).hostname or "").lower().strip()
    except Exception:
        return "default"
    if host.startswith("www."):
        host = host[4:]
    if not host:
        return "default"
    for vendor in whitelist_vendors.values():
        if not isinstance(vendor, dict):
            continue
        interval = vendor.get("vendorUpdateInterval")
        if not interval:
            continue
        # urls may be either a list of URL strings or a dict mapping role -> URL.
        urls_field = vendor.get("urls") or []
        if isinstance(urls_field, dict):
            url_values = list(urls_field.values())
        elif isinstance(urls_field, list):
            url_values = urls_field
        else:
            url_values = []
        for u in url_values:
            try:
                from urllib.parse import urlparse

                vh = (urlparse(str(u)).hostname or "").lower().strip()
                if vh.startswith("www."):
                    vh = vh[4:]
                if vh and vh == host:
                    return str(interval)
            except Exception:
                continue
    return "default"


VERIF_FACTOR_CAP: float = 1.5


def verif_factor(verifications: int) -> float:
    """Information-theoretic verification factor (Phase R2).

    Replaces the prior linear `min(v, 3) / 3` with a log-scale curve that
    rewards additional independent measurements beyond the 3-source anchor.

    Calibration (anchored at log base 4):
        v=0   -> 0.00   (no signal)
        v=1   -> 0.50   (log 2 / log 4)
        v=3   -> 1.00   (log 4 / log 4 — anchor matches prior formula)
        v=5   -> 1.29   (log 6 / log 4)
        v=10  -> 1.66   -> capped at 1.5
        v=100 -> 3.33   -> capped at 1.5

    Rationale (Shannon information accumulation): each independent
    measurement contributes ~1 bit of information when the consensus is
    unanimous; per Bayesian information theory, posterior precision grows
    logarithmically with the sample count. The log-base-4 calibration
    preserves the 3-source = 1.0 anchor of the prior linear formula while
    granting diminishing-but-positive returns for v > 3.
    """
    if verifications is None or verifications <= 0:
        return 0.0
    return min(math.log(1.0 + float(verifications)) / math.log(4.0), VERIF_FACTOR_CAP)


def trust_score(
    tier: str,
    verifications: int,
    date_str: Any,
    *,
    source_type: str = "default",
) -> float:
    """Canonical trust score formula (Phase R2+R5).

    trustScore = tierWeight × verif_factor(verifications)
                 × recencyDecay(date, source_type)

    `verif_factor` (R2) is the information-theoretic scaling; `source_type`
    (R5) picks the recency curve so vendor-release sources age slower than
    weekly community blogs. Default falls back to the pre-R5 piecewise.
    """
    tw = tier_weight(tier)
    vf = verif_factor(int(verifications) if verifications is not None else 0)
    rd = recency_decay(date_str, source_type=source_type)
    return round(tw * vf * rd, 4)


# FAZ 8.A.3b (2026-05-18): pseudo-source tags — observations that pretend
# to be canonical provenance but lack verifiable URLs. The Phase 3a purge
# removed all such entries from sources.json, but research-agent fresh
# emits may still inject them. winner.py.filter_pseudo_sources() walks
# this set before clustering.
PSEUDO_SOURCE_TAGS = frozenset(
    {"snapshot-extraction", "auto-resolution candidate", "synth-backfill"}
)

# Minimum verifications a single I-tier observation needs before it can
# override an existing multi-source S-tier consensus. Without this gate,
# one fresh fetch from an independent leaderboard outranks 3-source vendor
# data — the FAZ 8.A.3b doctrine treats single-shot I-tier as suggestive
# evidence, not authoritative override.
I_TIER_MIN_VERIFICATIONS = 2


def is_pseudo_source(obs: dict) -> bool:
    """Return True if observation carries a pseudo-source tag (FAZ 8.A.3b)."""
    if not isinstance(obs, dict):
        return False
    return obs.get("source") in PSEUDO_SOURCE_TAGS


def effective_trust_score(
    tier: str,
    verifications: int,
    date_str: Any,
    *,
    source_url: str = "",
    bench_key: str = "",
    source_type: str = "default",
    reliability_ledger: dict | None = None,
    is_pseudo: bool = False,
) -> float:
    """Trust score with pseudo-source dampening + Beta-Binomial reliability.

    Pseudo entries (FAZ 8.A.3b) get a 0.2 multiplier — signal only, never
    anchor. They are short-circuited before the reliability lookup so they
    don't pollute the ledger statistics.

    Phase R3 adds the reliability multiplier: when a ledger is supplied and
    the source has accumulated enough samples to escape the cold-start
    threshold, the score is multiplied by the Beta posterior accuracy of
    that source on this bench (or its global accuracy as fallback). Below
    the cold-start threshold the multiplier is 1.0, leaving trust_score
    unchanged — new sources are not penalized.
    """
    base = trust_score(tier, verifications, date_str, source_type=source_type)
    if is_pseudo:
        return round(base * 0.2, 4)
    if reliability_ledger and source_url:
        from .reliability import reliability_multiplier  # type: ignore

        mult = reliability_multiplier(reliability_ledger, source_url, bench_key)
        return round(base * mult, 4)
    return base
