#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSOT coherence audit. Walks every surface that touches bench keys + model
IDs, computes the cross-surface diff, and reports it. Designed to be loud
on drift — silent failure is the bug we're guarding against.

Surfaces audited:
  Canonical (source of truth):
    A. data/sources-whitelist.json `_schema.coreBenchKeys`
    B. data/models.json — model IDs + bench cells

  Mirrors that MUST agree with canonical:
    1. assets/js/core.js — BENCH_KEYS array
    2. assets/js/core.js — DEFAULT_WEIGHTS keys (subset of BENCH_KEYS)
    3. assets/js/core.js — PRESETS[*] keys (subset of BENCH_KEYS)
    4. i18n/en.json `benchmarks.*`
    5. i18n/tr.json `benchmarks.*`
    6. data/sources.json keys (bench suffix) → must be in canonical
    7. data/sources.json keys (model prefix) → must reference live models

Exit code:
  0  every check passed
  1  one or more drift signals — details printed to stderr

Used as a CI-style gate by:
  - scripts/merge.py post-write step (advisory log; never blocks commit)
  - manual `python scripts/audit-data-coherence.py` for human review
  - skill workflow before git commit (loud warning if dirty)
"""

import functools
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.matrix import active_models as _active_models  # noqa: E402
from lib.util import canonical_display_name as _canonical_name  # noqa: E402
from lib.util import extract_domain  # noqa: E402

for _stream in (sys.stdout, sys.stderr):
    _reconf = getattr(_stream, "reconfigure", None)
    if callable(_reconf):
        try:
            _reconf(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass

PROJECT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def load_json(path):
    with open(path, encoding="utf-8") as fp:
        return json.load(fp)


def parse_bench_keys_from_core(core_src):
    """Extract the BENCH_KEYS array literal from core.js."""
    m = re.search(r"BENCH_KEYS\s*=\s*\[([^\]]+)\]", core_src, re.S)
    if not m:
        return []
    return re.findall(r"'([\w]+)'", m.group(1))


def parse_default_weights_from_core(core_src):
    m = re.search(r"DEFAULT_WEIGHTS\s*=\s*\{([^}]+)\}", core_src, re.S)
    if not m:
        return []
    return re.findall(r"(\w+):\s*\d+", m.group(1))


def parse_presets_from_core(core_src):
    m = re.search(r"PRESETS\s*=\s*\{(.*?)\n\};", core_src, re.S)
    if not m:
        return {}
    block = m.group(1)
    out = {}
    for pname in re.findall(r"'([\w-]+)':\s*\{", block):
        pmatch = re.search(rf"'{pname}':\s*\{{([^}}]+)\}}", block, re.S)
        if pmatch:
            out[pname] = re.findall(r"(\w+):\s*\d+", pmatch.group(1))
    return out


def parse_sources_key(key):
    """Sources key shapes:
       <modelId>.<benchKey>          → ('bench', modelId, benchKey)
       <modelId>.pricing.api         → ('field', modelId, 'pricing.api')
       <modelId>.<otherField>        → ('field', modelId, otherField)
    Returns (kind, modelId, suffix)."""
    parts = key.split(".", 1)
    if len(parts) != 2:
        return ("malformed", key, None)
    return ("split", parts[0], parts[1])


def fmt_set_diff(a, b, label_a, label_b):
    only_a = sorted(a - b)
    only_b = sorted(b - a)
    return only_a, only_b


def main():
    failures = []
    warnings = []

    whitelist = load_json(f"{PROJECT}/data/sources-whitelist.json")
    models = load_json(f"{PROJECT}/data/models.json")
    sources = load_json(f"{PROJECT}/data/sources.json")
    en = load_json(f"{PROJECT}/i18n/en.json")
    tr = load_json(f"{PROJECT}/i18n/tr.json")
    with open(f"{PROJECT}/assets/js/core.js", encoding="utf-8") as fp:
        core_src = fp.read()

    # === Canonical sets ===
    # FAZ 5.C (2026-05-10): bench universe = coreBenchKeys ∪ emergingBenchKeys.
    # Coverage formula uses core only; surfaces (core.js, i18n, models.json
    # cells, sources.json suffixes) may reference either set freely.
    schema_block = whitelist.get("_schema") or {}
    core_bench_set = set(schema_block.get("coreBenchKeys") or [])
    emerging_bench_set = set(schema_block.get("emergingBenchKeys") or [])
    canonical_bench = core_bench_set | emerging_bench_set
    canonical_ids = {m["id"] for m in models}
    active_ids = {m["id"] for m in _active_models(models)}

    # === 1. core.js BENCH_KEYS ===
    core_bench = set(parse_bench_keys_from_core(core_src))
    only_core, only_canon = fmt_set_diff(
        core_bench, canonical_bench, "core.js", "whitelist"
    )
    if only_core:
        failures.append(
            f"core.js BENCH_KEYS has keys NOT in whitelist coreBenchKeys: {only_core}"
        )
    if only_canon:
        failures.append(
            f"whitelist coreBenchKeys has keys NOT in core.js BENCH_KEYS: {only_canon}"
        )

    # === 2. DEFAULT_WEIGHTS subset ===
    dw_keys = set(parse_default_weights_from_core(core_src))
    extra_dw = dw_keys - canonical_bench
    if extra_dw:
        failures.append(
            f"DEFAULT_WEIGHTS has keys NOT in canonical: {sorted(extra_dw)}"
        )

    # === 3. PRESETS subset ===
    presets = parse_presets_from_core(core_src)
    for pname, pkeys in presets.items():
        extra = set(pkeys) - canonical_bench
        if extra:
            failures.append(
                f"PRESET '{pname}' has keys NOT in canonical: {sorted(extra)}"
            )

    # === 3b. PRESET weights sum to 100 (schema = runtime SSOT via getPresets) ===
    # Every atomicComposite preset's atomicWeights MUST sum to exactly 100, else
    # the composite score is silently mis-normalized per preset. vendorConsensus
    # presets carry no atomic weights (sum 0) and are exempt. Keys must also be
    # canonical. (Schema diverged from core.js on 2026-05-28 — balanced/agentic/
    # reasoning/benchmark summed 90-92 after AA benches were dropped.)
    for pname, pdef in (schema_block.get("presets") or {}).items():
        if pname.startswith("_") or not isinstance(pdef, dict):
            continue
        if pdef.get("kind") == "vendorConsensus":
            continue
        aw = pdef.get("atomicWeights") or {}
        bad_keys = set(aw) - canonical_bench
        if bad_keys:
            failures.append(
                f"schema preset '{pname}' atomicWeights has non-canonical keys: {sorted(bad_keys)}"
            )
        total = round(sum(v for v in aw.values() if isinstance(v, (int, float))), 4)
        if total != 100:
            failures.append(
                f"schema preset '{pname}' atomicWeights sum={total}, must be 100"
            )

    # === 4-5. i18n benchmarks keys ===
    en_bench = set((en.get("benchmarks") or {}).keys())
    tr_bench = set((tr.get("benchmarks") or {}).keys())
    if en_bench != canonical_bench:
        only_en, only_canon = fmt_set_diff(en_bench, canonical_bench, "en", "canonical")
        if only_en:
            failures.append(
                f"i18n/en.json benchmarks has keys NOT in canonical: {only_en}"
            )
        if only_canon:
            failures.append(
                f"canonical has keys NOT in i18n/en.json benchmarks: {only_canon}"
            )
    if tr_bench != canonical_bench:
        only_tr, only_canon = fmt_set_diff(tr_bench, canonical_bench, "tr", "canonical")
        if only_tr:
            failures.append(
                f"i18n/tr.json benchmarks has keys NOT in canonical: {only_tr}"
            )
        if only_canon:
            failures.append(
                f"canonical has keys NOT in i18n/tr.json benchmarks: {only_canon}"
            )
    # i18n EN ↔ TR drift (label sets must be identical)
    en_tr_diff = en_bench ^ tr_bench
    if en_tr_diff:
        failures.append(f"i18n EN/TR benchmarks key drift: {sorted(en_tr_diff)}")

    # Per-bench label completeness — every entry MUST have short + name in both locales.
    for k in canonical_bench:
        for locale_label, locale in (("en", en), ("tr", tr)):
            entry = (locale.get("benchmarks") or {}).get(k) or {}
            for sub in ("short", "name"):
                v = entry.get(sub)
                if not isinstance(v, str) or not v.strip():
                    failures.append(
                        f"i18n/{locale_label}.json benchmarks.{k}.{sub} missing/empty"
                    )

    # === 6. data/models.json bench cells ===
    # Plausibility bands are data-driven from _schema.benchRanges (SSOT). hard
    # bounds = scale-corruption guard (wrong-scale value that would distort the
    # 0-100 composite) → HARD BLOCK. soft bounds = plausibility band: in-hard but
    # out-of-soft = unusual-but-possible → advisory WARN (re-verify, never reject —
    # a genuine outlier/breakthrough stays). Unlisted benches default to a 0-100
    # percentage. Most cells are percentages; cfElo/webDevElo/lmArenaElo are raw
    # Elo (see benchRanges + _benchKeyNotes).
    _ranges = schema_block.get("benchRanges") or {}
    _range_default = _ranges.get("_default") or {"hardMin": 0, "hardMax": 100}

    def _band(key):
        r = _ranges.get(key) or _range_default
        return (
            r.get("hardMin", 0),
            r.get("hardMax", 100),
            r.get("softMin"),
            r.get("softMax"),
        )

    data_bench_cells = set()
    bad_cells = []
    soft_suspects = []
    for m in models:
        for k, v in (m.get("bench") or {}).items():
            data_bench_cells.add(k)
            if v is None:
                continue
            if not isinstance(v, (int, float)):
                bad_cells.append(f"{m['id']}.{k}={v!r} (non-numeric)")
                continue
            lo, hi, slo, shi = _band(k)
            if v < lo or v > hi:
                bad_cells.append(f"{m['id']}.{k}={v} (out of [{lo},{hi}])")
            elif (slo is not None and v < slo) or (shi is not None and v > shi):
                soft_suspects.append(f"{m['id']}.{k}={v} (soft [{slo},{shi}])")
    rogue = data_bench_cells - canonical_bench
    if rogue:
        failures.append(
            f"data/models.json has bench cells with NON-canonical keys: {sorted(rogue)}"
        )
    if bad_cells:
        failures.append(
            f"data/models.json has {len(bad_cells)} bench cell(s) with bad values: {bad_cells[:5]}"
            f"{' ...' if len(bad_cells) > 5 else ''}"
        )
    if soft_suspects:
        warnings.append(
            f"{len(soft_suspects)} bench cell(s) outside the plausibility band "
            f"(unusual value — re-verify, not rejected): {soft_suspects[:5]}"
            f"{' ...' if len(soft_suspects) > 5 else ''}"
        )

    # === 6b. Source-authorization guard (advisory) — general metric-
    # misclassification detection. Build domain → published-benches from the
    # whitelist (entries with a NON-EMPTY publishes[]) + the known Arena-family
    # Elo publishers. A FILLED bench cell is flagged when one of its sources is a
    # KNOWN, scoped publisher whose publishes[] does NOT include this bench (e.g.
    # an LMArena Elo filed into cfElo, or any leaderboard contributing a bench it
    # doesn't actually report). Vendor / arxiv / uncategorized sources never
    # trigger (they can report anything about a model) → low false-positive.
    # Advisory: surfaces the cell for re-verification, never blocks. Pairs with
    # the agent.md "BENCH METRIC INTEGRITY" rule (gather-time prevention).
    @functools.lru_cache(maxsize=8192)
    def _dom(u):
        # 6.2 — memoized: source URLs recur across many cells; cache the parse.
        return extract_domain(u or "")

    domain_publishes: dict[str, set] = {}
    for _cat in ("leaderboards", "aggregators", "local", "community", "registries"):
        for e in whitelist.get(_cat) or []:
            pub = e.get("publishes") or []
            d = _dom(e.get("url"))
            if pub and d:
                domain_publishes.setdefault(d, set()).update(pub)
    # Known Arena-family Elo publishers (chat/webdev Elo, never Codeforces cfElo)
    # — ensure coverage even if a whitelist entry's scope is incomplete.
    for _ad in ("lmarena.ai", "arena.ai", "lmsys.org", "chatbot-arena.com"):
        domain_publishes.setdefault(_ad, set()).update({"lmArenaElo", "webDevElo"})

    # Confusable bench families — members are easy to misfile into one another
    # (the Elo family especially: same "Elo" name token, different scales). Flag a
    # filled cell ONLY when a source publishes a SIBLING in the same family but NOT
    # this bench — the source reports a confusable metric, so the value likely
    # belongs to the sibling. Now covers ALL families: scripts/derive-publishes.py
    # completes whitelist publishes[] from observed provenance, so a source that
    # legitimately reports both members (e.g. AA → sweV AND swePro) is no longer a
    # false positive. Advisory only.
    confusable_families = [
        {"cfElo", "lmArenaElo", "webDevElo"},  # Elo (distinct scales)
        {"sweV", "swePro", "sweMulti"},  # SWE-bench variants
        {"tb2", "tbHard"},  # Terminal-Bench
        {"tau2", "tau3"},  # tau-bench
        {"aaIdx", "aaCoding", "aaAgentic", "aaOmni"},  # AA composites
    ]

    def _family(bk):
        for fam in confusable_families:
            if bk in fam:
                return fam
        return set()

    # 4.3 — the Elo family (distinct scales 0-3500 vs ~1000-1700) and the
    # SWE-bench variant family (different difficulty) are the two confusables
    # whose misfile most corrupts the composite. A cell in these families whose
    # value is supported ONLY by sibling-publishers (NO source publishes the
    # actual bench) is a genuine misfile → HARD FAILURE (merge-blocking). The
    # other families, or a hard-family cell that ALSO has a valid publisher,
    # stay advisory WARN.
    hard_confusable = {"cfElo", "lmArenaElo", "webDevElo", "sweV", "swePro", "sweMulti"}
    src_mismatch = []  # soft / advisory
    src_misfile_hard = []  # merge-blocking
    for m in models:
        for bk, bv in (m.get("bench") or {}).items():
            if bv is None or bk not in canonical_bench:
                continue
            fam = _family(bk)
            if not fam:
                continue
            has_valid_publisher = False
            sibling_hit = None
            for e in sources.get(f"{m['id']}.{bk}") or []:
                pub = domain_publishes.get(_dom(e.get("url")))
                if not pub:
                    continue
                if bk in pub:
                    has_valid_publisher = True
                elif (pub & fam) and sibling_hit is None:
                    sibling_hit = (
                        f"{m['id']}.{bk}<-{_dom(e.get('url'))}(has {sorted(pub & fam)})"
                    )
            if sibling_hit is None:
                continue
            if bk in hard_confusable and not has_valid_publisher:
                src_misfile_hard.append(sibling_hit)
            else:
                src_mismatch.append(sibling_hit)
    if src_misfile_hard:
        failures.append(
            f"{len(src_misfile_hard)} Elo/SWE-variant bench cell(s) supported ONLY "
            f"by a sibling-metric publisher (no source publishes the actual bench) "
            f"— genuine misfile, MERGE-BLOCKING: {src_misfile_hard[:8]}"
            f"{' ...' if len(src_misfile_hard) > 8 else ''}"
        )
    if src_mismatch:
        warnings.append(
            f"{len(src_mismatch)} bench cell(s) sourced from a publisher of a "
            f"confusable SIBLING metric but not this bench (likely misfiled, "
            f"re-verify): {src_mismatch[:5]}{' ...' if len(src_mismatch) > 5 else ''}"
        )

    # === 7. data/sources.json keys ===
    src_unknown_models = []
    src_rogue_bench = []
    for key in sources.keys():
        kind, mid, suffix = parse_sources_key(key)
        if kind == "malformed":
            warnings.append(f"data/sources.json malformed key: {key!r}")
            continue
        if mid not in canonical_ids:
            src_unknown_models.append(key)
        # Bench-suffix keys (single-segment suffix) must be in canonical
        if (
            suffix
            and "." not in suffix
            and suffix in (canonical_bench | data_bench_cells)
        ):
            if suffix not in canonical_bench:
                src_rogue_bench.append(key)
    if src_unknown_models:
        failures.append(
            f"data/sources.json references {len(src_unknown_models)} unknown model id(s): "
            f"{src_unknown_models[:5]}{' ...' if len(src_unknown_models) > 5 else ''}"
        )
    if src_rogue_bench:
        failures.append(
            f"data/sources.json has bench-suffix keys NOT in canonical: {src_rogue_bench[:5]}"
        )

    # === Required model fields ===
    required = [
        "id",
        "name",
        "provider",
        "license",
        "tier",
        "status",
        "open",
        "context",
        "lastUpdated",
    ]
    missing_fields = []
    for m in models:
        for f in required:
            if f not in m or m[f] in (None, "", {}, []):
                missing_fields.append(f"{m.get('id', '?')}.{f}")
    if missing_fields:
        warnings.append(
            f"{len(missing_fields)} required field(s) missing across models — first 10: "
            f"{missing_fields[:10]}"
        )

    # === Tier values must use the canonical taxonomy ===
    canonical_tiers = {
        "frontier",
        "open-flagship",
        "coder-specialized",
        "gemma",
        "ollama-local",
    }
    bad_tiers = [
        f"{m['id']}={m.get('tier')!r}"
        for m in models
        if m.get("tier") and m["tier"] not in canonical_tiers
    ]
    if bad_tiers:
        failures.append(f"models with non-canonical tier: {bad_tiers}")

    # === Status values ===
    canonical_status = {"active", "deprecated", "archived"}
    bad_status = [
        f"{m['id']}={m.get('status')!r}"
        for m in models
        if m.get("status") and m["status"] not in canonical_status
    ]
    if bad_status:
        failures.append(f"models with non-canonical status: {bad_status}")

    # === AC9 — N/A retired (no notApplicableBenchKeys / notApplicable /
    #           naCandidates) ===
    # The N/A permanent-skip was retired 2026-05-26: every (model, bench) cell
    # is FILLED or GAP — unmeasured cells become gaps and are re-researched each
    # cycle (freshness-skip only). A reappearing notApplicableBenchKeys /
    # notApplicable / naCandidates field means a stale data path or reverted
    # agent contract. (naCandidates added to the guard 2026-06-07 — it had
    # leaked into every model in data/models.json unnoticed because the prior
    # guard only checked the other two field names.)
    _NA_FIELDS = ("notApplicableBenchKeys", "notApplicable", "naCandidates")
    has_na = [m["id"] for m in models if any(m.get(f) for f in _NA_FIELDS)]
    if has_na:
        failures.append(
            f"AC9 — N/A is retired but {len(has_na)} model(s) still carry "
            f"{'/'.join(_NA_FIELDS)}: {has_na[:5]}"
            f"{' ...' if len(has_na) > 5 else ''}"
        )

    # === AC12 — display name version-format canonical (model-agnostic) ===
    # Every model name must already be in canonical form: a bare minor-version
    # number uses a dot, not a space ("Qwen3.7 Max", never "Qwen3 7 Max").
    # Reuses lib.util.canonical_display_name (SSOT with merge.py's auto-fix) so
    # the gate and the fixer never diverge. Param sizes ("Gemma 3 27B") and
    # already-dotted versions ("Qwen 3.5 9B") are intentionally left untouched.
    bad_names: list[str] = []
    for m in models:
        nm = m.get("name")
        if isinstance(nm, str):
            canon = _canonical_name(nm)
            if canon != nm:
                bad_names.append(f"{m['id']}: {nm!r} -> {canon!r}")
    if bad_names:
        failures.append(
            f"AC12 — {len(bad_names)} model name(s) not version-format canonical: "
            f"{bad_names[:5]}{' ...' if len(bad_names) > 5 else ''}"
        )

    # === AC11 — privacy block shape (BLOCK) ===
    # model.privacy is optional; if present it MUST be a dict with only
    # canonical keys and canonical values per
    # sources-whitelist._schema.privacyFieldNormalize.
    privacy_canonical_keys = {
        "trainingDataOptOut",
        "dataResidency",
        "soc2",
        "gdpr",
        "apiLogging",
    }
    optout_values = {"available", "none", "unknown"}
    residency_codes = {
        "US",
        "EU",
        "JP",
        "SG",
        "AU",
        "CA",
        "UK",
        "IN",
        "BR",
        "MX",
        "DE",
        "FR",
        "KR",
        "CN",
        "global",
    }
    logging_values = {
        "not_logged",
        "opt_out",
        "default_off",
        "default_on",
        "unknown",
    }
    bad_privacy: list[str] = []
    for m in models:
        p = m.get("privacy")
        if p is None:
            continue
        if not isinstance(p, dict):
            bad_privacy.append(
                f"{m['id']}.privacy: not a dict (got {type(p).__name__})"
            )
            continue
        for pk, pv in p.items():
            if pk not in privacy_canonical_keys:
                bad_privacy.append(f"{m['id']}.privacy.{pk}: unknown field")
                continue
            if pk == "trainingDataOptOut":
                if pv is not None and pv not in optout_values:
                    bad_privacy.append(
                        f"{m['id']}.privacy.trainingDataOptOut={pv!r}: not in {sorted(optout_values)}"
                    )
            elif pk == "dataResidency":
                if pv is not None and not (
                    isinstance(pv, list)
                    and all(isinstance(c, str) and c in residency_codes for c in pv)
                ):
                    bad_privacy.append(
                        f"{m['id']}.privacy.dataResidency={pv!r}: must be list of codes from {sorted(residency_codes)}"
                    )
            elif pk in ("soc2", "gdpr"):
                if pv is not None and not isinstance(pv, bool):
                    bad_privacy.append(
                        f"{m['id']}.privacy.{pk}={pv!r}: must be boolean or null"
                    )
            elif pk == "apiLogging":
                if pv is not None and pv not in logging_values:
                    bad_privacy.append(
                        f"{m['id']}.privacy.apiLogging={pv!r}: not in {sorted(logging_values)}"
                    )
    if bad_privacy:
        failures.append(
            f"AC11 — privacy shape drift in {len(bad_privacy)} cell(s): "
            f"{bad_privacy[:5]}{' ...' if len(bad_privacy) > 5 else ''}"
        )

    # === MX4 — every filled bench cell has ≥1 sources.json entry (BLOCK) ===
    no_source_filled: list[str] = []
    for m in models:
        for k, v in (m.get("bench") or {}).items():
            if v is None:
                continue
            key = f"{m['id']}.{k}"
            entries = sources.get(key)
            if not isinstance(entries, list) or len(entries) == 0:
                no_source_filled.append(key)
    if no_source_filled:
        msg = (
            f"MX4 — {len(no_source_filled)} filled bench cell(s) have ZERO "
            f"sources.json entries: {no_source_filled[:5]}"
            f"{' ...' if len(no_source_filled) > 5 else ''}"
        )
        failures.append(msg)

    # === MX5 — weak provenance: cells with <2 distinct source URLs ===
    # 5.3: a single-source CORE-bench value flows into the composite at full
    # weight. MX5 stays WARN for non-core (and core, by default), but ESCALATES
    # to a merge-blocking FAILURE for core cells when
    # benchVerificationStrict._coreSingleSourceHardBlock is true. The flag is
    # held false while the snapshot still carries grandfathered single-source
    # core cells (the next full refresh-all adds 2nd sources); the mechanism is
    # always present + unit-testable.
    _schema_blk = whitelist.get("_schema") or {}
    core_keys = set(_schema_blk.get("coreBenchKeys") or [])
    hard_block_core = bool(
        (_schema_blk.get("benchVerificationStrict") or {}).get(
            "_coreSingleSourceHardBlock"
        )
    )
    weak_provenance: list[str] = []
    weak_core: list[str] = []
    for m in models:
        for k, v in (m.get("bench") or {}).items():
            if v is None:
                continue
            key = f"{m['id']}.{k}"
            entries = sources.get(key) or []
            if not isinstance(entries, list):
                continue
            distinct_urls = {e.get("url") for e in entries if e.get("url")}
            if len(distinct_urls) < 2:
                weak_provenance.append(key)
                if k in core_keys:
                    weak_core.append(key)
    if weak_provenance:
        msg = (
            f"MX5 — {len(weak_provenance)} filled bench cell(s) have <2 distinct "
            f"source URLs ({len(weak_core)} core) (quarantine candidates): "
            f"{weak_provenance[:5]}{' ...' if len(weak_provenance) > 5 else ''}"
        )
        warnings.append(msg)
    if hard_block_core and weak_core:
        failures.append(
            f"MX5-CORE — {len(weak_core)} CORE-bench cell(s) single-sourced (<2 "
            f"distinct URLs) flow into the composite at full weight, MERGE-BLOCKING: "
            f"{weak_core[:8]}{' ...' if len(weak_core) > 8 else ''}"
        )

    # === MX6 — bench-specific strict verification per
    # _schema.benchVerificationStrict (WARN). For each bench in the map, fail
    # cells that don't meet the bench's minDistinctIndependentSources threshold
    # against the listed knownIndependentDomains. ===
    strict_rules = (whitelist.get("_schema") or {}).get("benchVerificationStrict") or {}
    strict_violations: list[str] = []
    for bench_key, rule in strict_rules.items():
        if bench_key.startswith("_"):
            continue
        min_indep = int(rule.get("minDistinctIndependentSources") or 0)
        known_domains = [d.lower() for d in rule.get("knownIndependentDomains") or []]
        if not min_indep or not known_domains:
            continue
        for m in models:
            v = (m.get("bench") or {}).get(bench_key)
            if v is None:
                continue
            qbits = m.get("benchQuarantine") or {}
            if qbits.get(bench_key) is True:
                continue
            entries = sources.get(f"{m['id']}.{bench_key}") or []
            if not isinstance(entries, list):
                continue
            indep_domains = set()
            for e in entries:
                u = (e.get("url") or "").lower()
                for d in known_domains:
                    if d in u:
                        indep_domains.add(d)
                        break
            if len(indep_domains) < min_indep:
                strict_violations.append(
                    f"{m['id']}.{bench_key} (independent={len(indep_domains)}/{min_indep})"
                )
    if strict_violations:
        msg = (
            f"MX6 — {len(strict_violations)} bench cell(s) violate "
            f"_schema.benchVerificationStrict thresholds: "
            f"{strict_violations[:5]}"
            f"{' ...' if len(strict_violations) > 5 else ''}"
        )
        warnings.append(msg)
    # MX6 is WARN-only; agent + manual review handle remediation.

    # === Report ===
    print(f"Audit summary  ({len(models)} models, {len(canonical_bench)} bench keys)")
    print(f"  bench keys:        {sorted(canonical_bench)}")
    print(f"  model ids total:   {len(canonical_ids)}")
    print(f"  model ids active:  {len(active_ids)}")
    if not failures and not warnings:
        print("  ✓ FULL COHERENCE — every surface aligned")
        return 0

    if failures:
        print(f"\n  ✗ FAIL ({len(failures)} drift signal(s)):")
        for f in failures:
            print(f"    - {f}", file=sys.stderr)
    if warnings:
        print(f"\n  ⚠ WARN ({len(warnings)}):")
        for w in warnings:
            print(f"    - {w}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
