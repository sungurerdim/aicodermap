"""Shared whitelist + contract loaders.

Single source for every script that walks data/sources-whitelist.json. The
reform doctrine (P9) routes contract sabitleri (eşikler, retry sayıları, vb)
through `_schema.contracts` so SKILL.md/agent.md/scripts mirror tutmak
yerine tek noktadan okur.

Stdlib-only. Importable from scripts/* and scripts/lib/*.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

PROJECT = Path(__file__).resolve().parents[2]
WHITELIST_PATH = PROJECT / "data" / "sources-whitelist.json"

# Migration safety net (W3 sonunda kaldırılacak — Faz 0/1/2 sırasında
# `_schema.contracts` bloğu yoksa script panik etmesin).
SAFE_DEFAULTS: dict[str, Any] = {
    "ABSOLUTE_COVERAGE_FLOOR": 0.30,
    "MIN_SOURCES_PER_FILLED_CELL": 2,
    "COMPLETENESS_RETRY_LIMIT": 1,
    "VERIFICATION_AGREEMENT_THRESHOLD": 3,
    "VERIFICATION_AGREEMENT_PP": 1.5,
    "CONTRADICTION_WARN_PP": 3.0,
    "CONTRADICTION_BLOCK_PP": 5.0,
    "COVERAGE_TARGET": 0.85,
    "COVERAGE_HARD_BLOCK": 0.50,
    "STALE_DAYS": 14,
    "DEPRECATION_GRACE_DAYS": 60,
    "FAMILY_BASELINE_MIN": 30,
    "FETCH_TIMEOUT_SEC": 10,
    "FETCH_RETRY_COUNT": 1,
    "PARALLEL_FETCH_BATCH": 5,
    "HEALTH_CHECK_TTL_DAYS": 7,
}


def load_whitelist(path: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    p = Path(path) if path else WHITELIST_PATH
    with open(p, encoding="utf-8") as fp:
        return json.load(fp)


def schema(whitelist: dict[str, Any]) -> dict[str, Any]:
    return whitelist.get("_schema") or {}


def contracts(whitelist: dict[str, Any]) -> dict[str, Any]:
    """Return merged contract dict: SAFE_DEFAULTS overlaid by `_schema.contracts`."""
    merged = dict(SAFE_DEFAULTS)
    block = schema(whitelist).get("contracts") or {}
    for k, v in block.items():
        merged[k] = v
    return merged


def core_bench_keys(whitelist: dict[str, Any]) -> list[str]:
    return list(schema(whitelist).get("coreBenchKeys") or [])


def deprecated_bench_keys(whitelist: dict[str, Any]) -> list[str]:
    return list(schema(whitelist).get("deprecatedBenchKeys") or [])


def _publishes_keys(entry: dict[str, Any]) -> list[str]:
    """publishes[] shape may be ["key", ...] (legacy) or [{key, priority}, ...]
    (P10.4 reform). This helper normalizes both into a flat list of keys."""
    out: list[str] = []
    for item in entry.get("publishes", []) or []:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict) and "key" in item:
            out.append(item["key"])
    return out


def bench_universe(whitelist: dict[str, Any]) -> set[str]:
    """coreBenchKeys ∪ leaderboards[].publishes[] (excluding deprecated)."""
    universe: set[str] = set(core_bench_keys(whitelist))
    for lb in whitelist.get("leaderboards", []) or []:
        for k in _publishes_keys(lb):
            universe.add(k)
    deprecated = set(deprecated_bench_keys(whitelist))
    return universe - deprecated


def leaderboard_index_by_bench(
    whitelist: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    """benchKey → [leaderboard entry, …] mapping.

    Each leaderboard entry includes its `priority` resolution: legacy string
    publishes default to "primary"; new {key, priority} dicts carry their
    declared priority through.
    """
    idx: dict[str, list[dict[str, Any]]] = {}
    for lb in whitelist.get("leaderboards", []) or []:
        for item in lb.get("publishes", []) or []:
            key: str | None = None
            priority = "primary"
            if isinstance(item, str):
                key = item
            elif isinstance(item, dict):
                key = item.get("key")
                priority = item.get("priority") or "primary"
            if not key:
                continue
            idx.setdefault(key, []).append({"leaderboard": lb, "priority": priority})
    return idx


def vendor_index(whitelist: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return whitelist.get("vendors", {}) or {}


def hostname_index(
    whitelist: dict[str, Any],
) -> dict[str, tuple[str | None, str | None]]:
    """host → (format, tier) lookup across every entry that carries a URL."""
    idx: dict[str, tuple[str | None, str | None]] = {}
    for cat in ("leaderboards", "aggregators", "community", "local", "registries"):
        for e in whitelist.get(cat, []) or []:
            url = e.get("url")
            if not url:
                continue
            try:
                host = (urlparse(url).hostname or "").lower().lstrip("www.")
            except Exception:
                continue
            if host and host not in idx:
                idx[host] = (e.get("format"), e.get("tier"))
    return idx


def not_applicable_rules(whitelist: dict[str, Any]) -> dict[str, Any]:
    """Tier-based N/A rules. Hardcoded model id YASAK — kural-bazlı."""
    return schema(whitelist).get("notApplicableRules") or {}


def bench_aliases(whitelist: dict[str, Any]) -> dict[str, list[str]]:
    """Bench alias table: canonicalKey → [human aliases]."""
    return schema(whitelist).get("benchAliases") or {}
