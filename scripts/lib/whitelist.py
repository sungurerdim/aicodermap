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

from .util import extract_domain

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


def bench_band(whitelist: dict[str, Any], key: str) -> tuple[float, float]:
    """SSOT (hardMin, hardMax) for a bench value, from `_schema.benchRanges[key]`
    with `_default` fallback. Was hand-rolled as `_band()` in audit-agent-misfiles,
    validate-anomaly-verdicts, and audit-data-coherence independently.

    Accepts EITHER the full whitelist (has a `_schema` key) OR an
    already-extracted `_schema` block (has `benchRanges` directly). Callers
    historically passed both; before this guard, passing a `_schema` block made
    `schema()` double-extract (look for `_schema._schema`), silently fall back to
    the (0, 100) default, and reject every Elo-scale verdict (cfElo 3206 → wrongly
    "outside-band[0-100]"). Disambiguating on the `_schema` key makes the helper
    miscall-proof for any current or future caller."""
    block = whitelist.get("_schema") if "_schema" in whitelist else whitelist
    ranges = (block or {}).get("benchRanges") or {}
    entry = ranges.get(key) or ranges.get("_default") or {"hardMin": 0, "hardMax": 100}
    return float(entry.get("hardMin", 0)), float(entry.get("hardMax", 100))


def bench_hard_max(whitelist: dict[str, Any], key: str, default: float = 100.0) -> float:
    """SSOT upper bound for a bench value, from `_schema.benchRanges[key].hardMax`.
    Used to drop mis-scaled observations (e.g. an Elo 1753 filed as a 0-100 index).
    benchRanges is the single source — local-synth/merge/audit must not hardcode
    per-bench caps (cfElo 3800, webDevElo 2000, else 100) independently."""
    hi = bench_band(whitelist, key)[1]
    return hi if hi else default


# SSOT for the whitelist source categories — was repeated verbatim as an inline
# tuple in 6+ scripts and drifted (some omit "local", some add others).
ALL_WHITELIST_CATEGORIES = (
    "leaderboards",
    "aggregators",
    "local",
    "community",
    "registries",
)


def deprecated_bench_keys(whitelist: dict[str, Any]) -> list[str]:
    return list(schema(whitelist).get("deprecatedBenchKeys") or [])


def emerging_bench_keys(whitelist: dict[str, Any]) -> list[str]:
    """FAZ 5.C (2026-05-10): bench keys with <30% fill rate, not counted in
    main coverage formula. Still surveyed every cycle (vendor may publish);
    if a fill is found, the cell appears alongside core fills.
    """
    return list(schema(whitelist).get("emergingBenchKeys") or [])


def all_bench_keys(whitelist: dict[str, Any]) -> list[str]:
    """coreBenchKeys ∪ emergingBenchKeys — full universe agents are
    expected to attempt. Coverage formulas use coreBenchKeys only."""
    return core_bench_keys(whitelist) + emerging_bench_keys(whitelist)


def required_bench_keys(whitelist: dict[str, Any]) -> set[str]:
    """Union of every preset's `requiredBenches` (`_schema.presets.*`).

    A cell in this set gates a model out of the "Limited Coverage" band for
    at least one ranking preset (assets/js/scoring.js `rankGateStatus`) when
    missing — see `_schema.presets.<name>.requiredBenches`. Used to boost a
    cell's research priority when filling it would flip a model from gated
    to ranked, which raw starvation ordering (fewest total filled hits)
    otherwise buries under high-coverage models missing only 1-2 cells."""
    presets = schema(whitelist).get("presets") or {}
    out: set[str] = set()
    for preset in presets.values():
        if isinstance(preset, dict):
            out.update(preset.get("requiredBenches") or [])
    return out


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
            host = extract_domain(url)
            if host and host not in idx:
                idx[host] = (e.get("format"), e.get("tier"))
    return idx


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
    return {(u or "").strip().rstrip("/").lower() for u, flag in unhealthy.items() if flag}


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


def not_applicable_rules(whitelist: dict[str, Any]) -> dict[str, Any]:
    """Tier-based N/A rules. Hardcoded model id YASAK — kural-bazlı."""
    return schema(whitelist).get("notApplicableRules") or {}


def bench_aliases(whitelist: dict[str, Any]) -> dict[str, list[str]]:
    """Bench alias table: canonicalKey → [human aliases]."""
    return schema(whitelist).get("benchAliases") or {}


def banned_fetch_patterns(whitelist: dict[str, Any]) -> list[str]:
    """FAZ 1.4 (2026-05-07): URLs the agent must NEVER WebFetch.

    Three sources of bans, all whitelist-derived (no hardcoded URLs):
      1. Every URL whose declared `format` has skipWebFetch=true in
         _schema.formatTaxonomy (currently spa_full, image_embedded,
         bot_blocked).
      2. Every URL whose entry-level `_runtime.unhealthy=true` (≥3
         consecutive failures).
      3. Every URL whose entry-level `skipWebFetch=true` override.

    Returns: list of regex strings (anchored on URL prefix). Agent's
    matches_any() iterates these against entry.url BEFORE issuing
    WebFetch. Repeated WebFetch on a banned URL is a contract violation
    (logged to runtime.bannedFetchHits[]).
    """
    import re

    from urllib.parse import urlparse

    ft = schema(whitelist).get("formatTaxonomy") or {}
    banned_formats = {
        k for k, v in ft.items() if isinstance(v, dict) and v.get("skipWebFetch") is True
    }

    # D (2026-06-07): immediate dead-URL ban. A host the source-health-probe
    # marked dead/unreachable/bot-blocked THIS cycle burns the full per-fetch
    # timeout budget (404, DNS-fail, 403) on the slowest (CN/data-sparse)
    # batches BEFORE the agent falls back to WebSearch. The pre-existing ban
    # only fired on `_runtime.unhealthy=true` (>=3 consecutive cycles) — too
    # slow to react. Here we ban any entry whose `_runtime.healthChecks[key]`
    # status is a reachability failure right now. `ssl-env-unverified` is the
    # local cert-bundle artifact (per SKILL.md PRELIM-B) — NOT a dead source —
    # so it is explicitly excluded.
    dead_statuses = {"dead", "unreachable", "bot_blocked", "403_blocked"}

    def _is_dead_status(s: object) -> bool:
        if not isinstance(s, str):
            return False
        if s == "ssl-env-unverified":
            return False
        return s in dead_statuses or "404" in s

    health_checks = (whitelist.get("_runtime") or {}).get("healthChecks") or {}
    dead_keys = {
        k
        for k, v in health_checks.items()
        if isinstance(v, dict) and _is_dead_status(v.get("status"))
    }

    def _domain_key(url: str | None) -> str:
        # Mirror source-health-probe._domain_key: host (www-stripped) + first
        # path segment. Keys must match the probe's exactly or the ban misses.
        if not isinstance(url, str) or not url:
            return ""
        p = urlparse(url)
        host = (p.hostname or "").lower()
        if host.startswith("www."):
            host = host[4:]
        seg = [s for s in (p.path or "").split("/") if s]
        return f"{host}/{seg[0]}" if seg else host

    def _dead_now(url: str | None) -> bool:
        return bool(dead_keys) and _domain_key(url) in dead_keys

    patterns: list[str] = []
    seen: set[str] = set()

    def _add(url: str | None) -> None:
        if not isinstance(url, str) or not url:
            return
        # Anchor on full URL prefix; agent's matches_any does
        # `re.match(pattern, entry.url)`. Escape the URL so any regex
        # metacharacters in the URL itself are treated as literals.
        pat = re.escape(url)
        if pat in seen:
            return
        seen.add(pat)
        patterns.append(pat)

    for cat in ("leaderboards", "aggregators", "community", "local", "registries"):
        for e in whitelist.get(cat, []) or []:
            fmt = e.get("format")
            unhealthy = (e.get("_runtime") or {}).get("unhealthy") is True
            override = e.get("skipWebFetch") is True
            if fmt in banned_formats or unhealthy or override or _dead_now(e.get("url")):
                _add(e.get("url"))

    # Vendor URL bundles — every per-vendor URL whose format mirrors one
    # of the banned format keys gets banned too. Vendors carry a
    # per-URL `format` map under vendors.<v>.urlFormats (when present).
    for v in (whitelist.get("vendors") or {}).values():
        urls = (v or {}).get("urls") or {}
        formats_map = (v or {}).get("urlFormats") or {}
        for url_key, url in urls.items():
            fmt = formats_map.get(url_key)
            if fmt in banned_formats or _dead_now(url):
                _add(url)

    return patterns


# Frontend/merge-only `_schema` blocks — never read by the gather agent
# (0-hit in agent.md, 2026-06-06). Pruned from per-batch ctx; the canonical
# values still live in data/sources-whitelist.json for the frontend + merge.py.
_SCHEMA_GATHER_DROP = frozenset(
    {"presets", "composite", "vendorComposites", "perModelExpansion", "uncertainty"}
)


def filter_for_batch(
    whitelist: dict[str, Any],
    providers: set[str] | list[str],
    *,
    keep_categories: tuple[str, ...] = ("leaderboards", "aggregators", "local"),
    bench_keys: set[str] | list[str] | None = None,
) -> dict[str, Any]:
    """FAZ 7.B (2026-05-10) — return a slimmed whitelist for per-batch ctx.

    Cuts the per-batch idea_context payload from ~106 KB (full whitelist) to
    ~25-30 KB by:
      • Keeping `_schema` in full (bench keys, format taxonomy, contracts,
        notApplicableRules — all of which the agent reads in every batch).
      • Filtering `vendors` to only entries matching `providers` (case-
        insensitive substring + token match against vendor key).
      • Keeping `keep_categories` (leaderboards/aggregators/local by default)
        but filtering each entry's `publishes[]` to only bench_keys when
        provided. `community` and `registries` are dropped by default —
        agents that need them can fall back to direct file Read.

    Quality is preserved: the agent still sees the universe of bench keys
    via `_schema.coreBenchKeys`, the format taxonomy via `_schema.formatTaxonomy`,
    notApplicableRules, and every leaderboard/aggregator URL relevant to the
    bench keys it surveys. The only thing pruned is unrelated vendor entries
    and rarely-used `community`/`registries` lists.

    Returns a NEW dict; does not mutate the input.
    """
    pset_lower = {str(p).lower() for p in providers}

    def vendor_matches(vendor_key: str) -> bool:
        kn = vendor_key.lower()
        for p in pset_lower:
            if not p:
                continue
            if p in kn or kn in p:
                return True
            # Drop '.' (fuse "z.ai" -> "zai") and turn '(', ')' into separators
            # before tokenizing, so display names like "Z.ai (Zhipu AI)" yield
            # "zai"/"zhipu"/"ai" tokens instead of "z.ai"/"(zhipu"/"ai)" — the
            # latter never substring-matched vendor key "zai_glm", silently
            # emptying that vendor's whitelist bundle for every zai_glm batch
            # (found 2026-07-11).
            cleaned = p.replace(".", "").replace("(", " ").replace(")", " ")
            for token in cleaned.replace("_", " ").replace("-", " ").split():
                if token and len(token) > 2 and token in kn:
                    return True
        return False

    out: dict[str, Any] = {}
    for k, v in whitelist.items():
        if k == "vendors":
            continue
        if k in ("community", "registries") and k not in keep_categories:
            continue
        if k == "_schema" and isinstance(v, dict):
            # Gather agents never read the frontend/merge-only schema blocks
            # (verified 0-hit in agent.md). Pruning them cuts ~12 KB/ctx with
            # zero quality impact. Keep everything the agent DOES read:
            # coreBenchKeys, benchAliases, formatTaxonomy, regexLibrary,
            # newReleaseProbe, benchVerificationStrict, privacyFieldNormalize, …
            out[k] = {sk: sv for sk, sv in v.items() if sk not in _SCHEMA_GATHER_DROP}
            continue
        if k == "_runtime" and isinstance(v, dict):
            # The agent reads `_runtime.unhealthy` (skip list) + lowConfidenceUrls
            # but WRITES its own runtime.healthChecks — the injected 142-domain
            # healthChecks map (~22 KB) is pure orchestrator state, useless to the
            # agent. Collapse to the fields it actually consults.
            out[k] = {
                sk: v[sk]
                for sk in (
                    "unhealthy",
                    "lowConfidenceUrls",
                    "lastFullCycle",
                    "schemaVersion",
                )
                if sk in v
            }
            continue
        out[k] = v

    # Filter vendors to matching providers only.
    vendors = whitelist.get("vendors") or {}
    out["vendors"] = {k: v for k, v in vendors.items() if vendor_matches(k)}

    # Optional: filter publishes[] inside kept categories to bench_keys universe.
    if bench_keys:
        bk_set = {str(k) for k in bench_keys}
        for cat in keep_categories:
            entries = whitelist.get(cat) or []
            filtered: list[dict[str, Any]] = []
            for e in entries:
                if not isinstance(e, dict):
                    continue
                pubs = e.get("publishes") or []
                kept_pubs: list[Any] = []
                for item in pubs:
                    if isinstance(item, str):
                        if item in bk_set:
                            kept_pubs.append(item)
                    elif isinstance(item, dict):
                        if item.get("key") in bk_set:
                            kept_pubs.append(item)
                # Keep entries with at least one matched key, OR entries
                # with no `publishes` field (treated as universal).
                if kept_pubs or not pubs:
                    new_e = dict(e)
                    if pubs:
                        new_e["publishes"] = kept_pubs
                    filtered.append(new_e)
            out[cat] = filtered

    return out


# ── Elo/SWE-variant sibling-metric misfile guard (SSOT — 2026-06-07) ───────────
# Shared by audit-data-coherence.py (merge GATE) and local-synth.py (Stage B) so
# the synth drops EXACTLY the cells the merge audit would hard-block — eliminating
# the merge-rollback + manual-fix + full-Stage-B-re-run round-trip the cfElo
# misfile (gemma-4-26b-moe, 2026-06-07) cost. One definition, two callers.
CONFUSABLE_FAMILIES: list[set[str]] = [
    {"cfElo", "lmArenaElo", "webDevElo"},  # Elo (distinct scales)
    {"sweV", "swePro", "sweMulti"},  # SWE-bench variants
    {"tb2", "tbHard"},  # Terminal-Bench
    {"tau2", "tau3"},  # tau-bench
    {"aaIdx", "aaCoding", "aaAgentic", "aaOmni"},  # AA composites
]
# The two families whose misfile most corrupts the composite (distinct scales /
# difficulty) → a cell supported ONLY by sibling-publishers is merge-BLOCKING.
HARD_CONFUSABLE: set[str] = {
    "cfElo",
    "lmArenaElo",
    "webDevElo",
    "sweV",
    "swePro",
    "sweMulti",
}
# Arena-family Elo publishers seeded even when a whitelist entry's scope is
# incomplete (chat/webdev Elo, never Codeforces cfElo).
_ARENA_DOMAINS = ("lmarena.ai", "arena.ai", "lmsys.org", "chatbot-arena.com")


def confusable_family(bk: str) -> set[str]:
    """Return the confusable family set containing bench key `bk`, else empty."""
    for fam in CONFUSABLE_FAMILIES:
        if bk in fam:
            return fam
    return set()


def build_domain_publishes(whitelist: dict[str, Any]) -> dict[str, set]:
    """host → set(benchKeys published), from the scoped whitelist categories +
    Arena Elo seeds. SSOT input for the Elo/SWE sibling-metric misfile guard."""
    dp: dict[str, set] = {}
    for cat in ("leaderboards", "aggregators", "local", "community", "registries"):
        for e in whitelist.get(cat) or []:
            if not isinstance(e, dict):
                continue
            pub = e.get("publishes") or []
            d = extract_domain(e.get("url") or "")
            if pub and d:
                dp.setdefault(d, set()).update(pub)
    for ad in _ARENA_DOMAINS:
        dp.setdefault(ad, set()).update({"lmArenaElo", "webDevElo"})
    return dp


def elo_swe_misfile(
    bk: str, source_urls, domain_publishes: dict[str, set]
) -> tuple[str | None, bool]:
    """Decide whether a filled confusable cell is a sibling-metric misfile.

    Returns (sibling_hit, is_hard):
      - sibling_hit: a "<-<domain>(has [<siblings>])" suffix when some source is a
        KNOWN, scoped publisher of a SIBLING metric but NOT `bk` itself; else None.
        (The caller prepends "<modelId>.<benchKey>".)
      - is_hard: True iff `bk` is in HARD_CONFUSABLE AND no source publishes `bk`
        by name — the merge-BLOCKING condition. Else False (advisory only).

    Mirrors audit-data-coherence §6b exactly so local-synth can pre-drop hard
    misfiles before they reach (and roll back) the merge.
    """
    fam = confusable_family(bk)
    if not fam:
        return None, False
    has_valid = False
    sibling_hit: str | None = None
    for u in source_urls:
        d = extract_domain(u or "")
        pub = domain_publishes.get(d)
        if not pub:
            continue
        if bk in pub:
            has_valid = True
        elif (pub & fam) and sibling_hit is None:
            sibling_hit = f"<-{d}(has {sorted(pub & fam)})"
    if sibling_hit is None:
        return None, False
    return sibling_hit, (bk in HARD_CONFUSABLE and not has_valid)
