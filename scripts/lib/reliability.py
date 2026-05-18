"""Source reliability ledger (Phase R1 — behavior-neutral foundation).

Beta-Binomial conjugate prior for per-(source, bench) accuracy posterior.
Stdlib only (math + statistics + urllib).

Doctrine (per Source Reliability v2 plan):
  - Cold-start: n < COLD_START_N → neutral 1.0 multiplier
  - Half-life: 3 cycles (decay factor 0.7937 per cycle, ~7 days/cycle)
  - Hierarchical fallback: per-(source, bench) → per-source global → 1.0
  - Bounds: clamp multiplier to [MIN_MULTIPLIER, MAX_MULTIPLIER]

Phase R1 only POPULATES the ledger. reliability_multiplier() is callable
but not yet wired into trust_score — that happens in Phase R3.
"""

from __future__ import annotations

import datetime
import json
import math
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

SCHEMA_VERSION = "v1"
HALF_LIFE_CYCLES = 3
CYCLE_DAYS = 7
HALF_LIFE_DAYS = HALF_LIFE_CYCLES * CYCLE_DAYS  # 21 days
DECAY_FACTOR = 0.5 ** (1.0 / HALF_LIFE_CYCLES)  # ≈ 0.7937 per cycle
COLD_START_N = 10
PRIOR_ALPHA = 1.0  # Beta(1, 1) uniform prior
PRIOR_BETA = 1.0
MIN_MULTIPLIER = 0.3
MAX_MULTIPLIER = 1.0


def source_identity(url: str, source_label: str = "") -> str:
    """Canonical hostname from URL, lowercased, www-stripped.

    Falls back to source_label (lowercased) when url is empty/unparseable.
    Returns empty string when both are unusable — callers should skip.
    """
    if url:
        try:
            host = (urlparse(str(url).strip()).hostname or "").lower().strip()
            if host.startswith("www."):
                host = host[4:]
            if host:
                return host
        except Exception:
            pass
    return (source_label or "").strip().lower()


def _parse_date(stamp: Any) -> datetime.date | None:
    if not stamp:
        return None
    try:
        return datetime.date.fromisoformat(str(stamp)[:10])
    except Exception:
        return None


def _cycles_elapsed(prev_cycle: Any, current_cycle: Any) -> float:
    """Fractional cycle count between two YYYY-MM-DD stamps.

    1 cycle = CYCLE_DAYS (7) days. Returns 0.0 when either stamp is missing,
    when current ≤ prev (no time advance), or when parsing fails.
    """
    if not prev_cycle or prev_cycle == current_cycle:
        return 0.0
    p = _parse_date(prev_cycle)
    c = _parse_date(current_cycle)
    if not p or not c:
        return 0.0
    days = (c - p).days
    if days <= 0:
        return 0.0
    return days / CYCLE_DAYS


def decay_counters(ledger: dict, current_cycle: str) -> None:
    """Apply exponential decay to every (source, bench).agree/disagree counter.

    Idempotent within the same cycle (lastCycle stamp guard). Raw lifetime
    counts (rawAgree / rawDisagree) are audit-only and never decayed.
    """
    last = ledger.get("lastCycle")
    elapsed = _cycles_elapsed(last, current_cycle)
    if elapsed <= 0:
        ledger["lastCycle"] = current_cycle
        return
    factor = DECAY_FACTOR**elapsed
    for src in (ledger.get("sources") or {}).values():
        g = src.setdefault(
            "global",
            {"agree": 0.0, "disagree": 0.0, "rawAgree": 0, "rawDisagree": 0},
        )
        g["agree"] = round(float(g.get("agree", 0.0)) * factor, 6)
        g["disagree"] = round(float(g.get("disagree", 0.0)) * factor, 6)
        for bench in (src.get("byBench") or {}).values():
            bench["agree"] = round(float(bench.get("agree", 0.0)) * factor, 6)
            bench["disagree"] = round(float(bench.get("disagree", 0.0)) * factor, 6)
    ledger["lastCycle"] = current_cycle


def _ensure_source(ledger: dict, sid: str, cycle_id: str) -> dict:
    sources = ledger.setdefault("sources", {})
    src = sources.get(sid)
    if src is None:
        src = {
            "firstSeen": cycle_id,
            "lastSeen": cycle_id,
            "global": {
                "agree": 0.0,
                "disagree": 0.0,
                "rawAgree": 0,
                "rawDisagree": 0,
            },
            "byBench": {},
        }
        sources[sid] = src
    src["lastSeen"] = cycle_id
    return src


def update_reliability(
    ledger: dict,
    source_url: str,
    bench_key: str,
    agreed: bool,
    cycle_id: str,
    *,
    source_label: str = "",
) -> None:
    """Increment agree/disagree by 1.0 in both byBench[bench_key] and global.

    Raw lifetime counters track integer counts for audit visibility.
    Silently no-ops when source_identity() yields empty (no url, no label).
    """
    sid = source_identity(source_url, source_label)
    if not sid:
        return
    src = _ensure_source(ledger, sid, cycle_id)
    g = src["global"]
    if agreed:
        g["agree"] = float(g.get("agree", 0.0)) + 1.0
        g["rawAgree"] = int(g.get("rawAgree", 0)) + 1
    else:
        g["disagree"] = float(g.get("disagree", 0.0)) + 1.0
        g["rawDisagree"] = int(g.get("rawDisagree", 0)) + 1
    if bench_key:
        bench = src["byBench"].setdefault(
            bench_key,
            {"agree": 0.0, "disagree": 0.0, "rawAgree": 0, "rawDisagree": 0},
        )
        if agreed:
            bench["agree"] = float(bench.get("agree", 0.0)) + 1.0
            bench["rawAgree"] = int(bench.get("rawAgree", 0)) + 1
        else:
            bench["disagree"] = float(bench.get("disagree", 0.0)) + 1.0
            bench["rawDisagree"] = int(bench.get("rawDisagree", 0)) + 1


def posterior_accuracy(agree: float, disagree: float) -> float:
    """Beta(α + agree, β + disagree) posterior mean.

    Uniform prior Beta(1,1) → (1+a) / (2+a+d). When both counts are zero,
    returns 0.5 (the prior mean).
    """
    a = PRIOR_ALPHA + float(agree or 0.0)
    b = PRIOR_BETA + float(disagree or 0.0)
    denom = a + b
    return a / denom if denom > 0 else 0.5


def accuracy_ci(agree: float, disagree: float) -> tuple[float, float]:
    """95% normal-approximation CI on the Beta posterior mean.

    Wald approximation — caller should check n >= ~30 for tight validity.
    Returns (0.0, 1.0) when n < 1.
    """
    n = float(agree or 0.0) + float(disagree or 0.0)
    if n < 1.0:
        return (0.0, 1.0)
    p = posterior_accuracy(agree, disagree)
    se = math.sqrt(max(p * (1.0 - p) / n, 0.0))
    z = 1.96
    lo = max(0.0, p - z * se)
    hi = min(1.0, p + z * se)
    return (round(lo, 4), round(hi, 4))


def reliability_multiplier(
    ledger: dict,
    source_url: str,
    bench_key: str,
    *,
    source_label: str = "",
) -> float:
    """Hierarchical posterior lookup.

    1. Per-(source, bench): if effective n >= COLD_START_N → posterior mean
    2. Per-source global:   if global n  >= COLD_START_N → global posterior
    3. Cold-start fallback: 1.0 (neutral — new sources are not penalized)

    Output clamped to [MIN_MULTIPLIER, MAX_MULTIPLIER].
    """
    sid = source_identity(source_url, source_label)
    if not sid:
        return 1.0
    src = ((ledger or {}).get("sources") or {}).get(sid)
    if not src:
        return 1.0
    if bench_key:
        bench = (src.get("byBench") or {}).get(bench_key)
        if bench:
            n = float(bench.get("agree", 0.0)) + float(bench.get("disagree", 0.0))
            if n >= COLD_START_N:
                p = posterior_accuracy(bench["agree"], bench["disagree"])
                return max(MIN_MULTIPLIER, min(MAX_MULTIPLIER, round(p, 4)))
    g = src.get("global") or {}
    gn = float(g.get("agree", 0.0)) + float(g.get("disagree", 0.0))
    if gn >= COLD_START_N:
        p = posterior_accuracy(g["agree"], g["disagree"])
        return max(MIN_MULTIPLIER, min(MAX_MULTIPLIER, round(p, 4)))
    return 1.0


def _empty_ledger() -> dict:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "halfLifeCycles": HALF_LIFE_CYCLES,
        "coldStartN": COLD_START_N,
        "lastCycle": None,
        "sources": {},
    }


def load_ledger(path: Path | str) -> dict:
    """Read the ledger JSON. Returns a fresh scaffold when the file is
    missing or unreadable. Never raises."""
    p = Path(path)
    if not p.exists():
        return _empty_ledger()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return _empty_ledger()
        data.setdefault("schemaVersion", SCHEMA_VERSION)
        data.setdefault("halfLifeCycles", HALF_LIFE_CYCLES)
        data.setdefault("coldStartN", COLD_START_N)
        data.setdefault("lastCycle", None)
        data.setdefault("sources", {})
        return data
    except Exception:
        return _empty_ledger()


def save_ledger(path: Path | str, ledger: dict) -> None:
    """Atomic-ish write: serialize to string, then write once."""
    p = Path(path)
    payload = json.dumps(ledger, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    p.write_text(payload, encoding="utf-8")
