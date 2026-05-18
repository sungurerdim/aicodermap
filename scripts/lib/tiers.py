"""Tier weight + trust constants — single source of truth.

Previously duplicated across:
  - scripts/local-synth.py   TIER_WEIGHT = {I:1.0, S:0.7, C:0.4, U:0.1}
  - scripts/gather-union.py  TIER_WEIGHT: dict[str, float]
  - scripts/lib/synth.py     TIER_WEIGHTS = {I:1.0, S:0.7, C:0.4, U:0.1}

All callers import from here. No magic numbers in individual scripts.
"""

from __future__ import annotations

import datetime
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


def recency_decay(date_str: Any) -> float:
    """Compute recency decay multiplier from an ISO date string.

    age <  30d → 1.00
    age <  90d → 0.85
    age < 180d → 0.70
    age < 365d → 0.50
    age ≥ 365d → 0.30
    """
    if not date_str:
        return 0.50
    try:
        s = str(date_str).strip()
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z"):
            try:
                dt = datetime.datetime.strptime(s[: len(fmt.replace("%", "XX"))], fmt)
                age = (
                    datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                    - dt
                ).days
                break
            except ValueError:
                continue
        else:
            # ISO-8601 slice fallback
            age = (datetime.date.today() - datetime.date.fromisoformat(s[:10])).days
    except Exception:
        return 0.50
    if age < 30:
        return 1.00
    if age < 90:
        return 0.85
    if age < 180:
        return 0.70
    if age < 365:
        return 0.50
    return 0.30


def trust_score(tier: str, verifications: int, date_str: Any) -> float:
    """Canonical trust score formula.

    trustScore = tierWeight × min(verifications, 3)/3 × recencyDecay(date)
    """
    tw = tier_weight(tier)
    v = min(max(int(verifications), 1), 3) / 3.0
    r = recency_decay(date_str)
    return round(tw * v * r, 4)


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
    is_pseudo: bool = False,
) -> float:
    """Trust score with pseudo-source dampening.

    Pseudo entries (FAZ 8.A.3b) get a 0.2 multiplier — signal only, never
    anchor. Used when pseudo entries SURVIVE into clustering (rescue mode)
    so they don't dominate composite calculations.
    """
    base = trust_score(tier, verifications, date_str)
    if is_pseudo:
        return round(base * 0.2, 4)
    return base
