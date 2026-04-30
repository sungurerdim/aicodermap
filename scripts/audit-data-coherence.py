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

import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.matrix import active_models as _active_models  # noqa: E402

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
    canonical_bench = set((whitelist.get("_schema") or {}).get("coreBenchKeys") or [])
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
    # Most bench cells are percentages (0-100). cfElo stores raw Codeforces
    # ELO (range 0-3500); webDevElo stores raw LMArena WebDev Arena Elo
    # (allowed up to 2000 — top models in 2026 exceed the old 1500 cap).
    # See whitelist _benchKeyNotes.
    def _bench_max(key):
        if key == "cfElo":
            return 3500
        if key == "webDevElo":
            return 2000
        return 100

    data_bench_cells = set()
    bad_cells = []
    for m in models:
        for k, v in (m.get("bench") or {}).items():
            data_bench_cells.add(k)
            if v is not None:
                if not isinstance(v, (int, float)):
                    bad_cells.append(f"{m['id']}.{k}={v!r} (non-numeric)")
                else:
                    hi = _bench_max(k)
                    if v < 0 or v > hi:
                        bad_cells.append(f"{m['id']}.{k}={v} (out of [0,{hi}])")
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

    # === AC9 — notApplicableBenchKeys ⊆ coreBenchKeys ===
    bad_na: list[str] = []
    for m in models:
        for k in m.get("notApplicableBenchKeys", []) or []:
            if k not in canonical_bench:
                bad_na.append(f"{m['id']}.notApplicableBenchKeys[{k}]")
    if bad_na:
        failures.append(
            f"AC9 — notApplicableBenchKeys references {len(bad_na)} non-canonical "
            f"bench key(s): {bad_na[:5]}{' ...' if len(bad_na) > 5 else ''}"
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

    # === MX5 — quarantine flag for cells with <2 distinct source URLs (WARN) ===
    weak_provenance: list[str] = []
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
    if weak_provenance:
        msg = (
            f"MX5 — {len(weak_provenance)} filled bench cell(s) have <2 distinct "
            f"source URLs (quarantine candidates): {weak_provenance[:5]}"
            f"{' ...' if len(weak_provenance) > 5 else ''}"
        )
        warnings.append(msg)
    # MX5 is WARN-only.

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
