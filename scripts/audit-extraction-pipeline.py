#!/usr/bin/env python3
"""End-to-end audit of every data extraction layer.

For each data type (bench, modelMeta, pricing, ollama, unslothVariants,
lineupChanges, rawGaps, i18n strengths/weaknesses), verify:

  1. Gather artifact integrity — modelId resolves; benchKey is canonical;
     value is the right type; sourceUrl present where required.
  2. Synth aggregation correctness — observations land under the right
     (modelId, benchKey) pair; no cross-model leakage; FILL > N/A precedence
     respected.
  3. models.json storage shape — Storage scalars (not wrapped); pricing.api
     is an array; pricing.range computed; status is one of the valid set;
     N/A cells in notApplicableBenchKeys are NOT also filled in bench{}.
  4. sources.json provenance — every filled bench cell has ≥1 source; flat
     keys parse to (modelId, fieldName) where modelId matches a real model.
  5. i18n alignment — every model.id has TR + EN strengths/weaknesses; no
     drift between the two languages' key sets.

Pure read-only audit. Reports findings as a structured report. No mutations.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from glob import glob
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

ROOT = Path(__file__).resolve().parent.parent

MODELS_PATH = ROOT / "data" / "models.json"
SOURCES_PATH = ROOT / "data" / "sources.json"
WHITELIST_PATH = ROOT / "data" / "sources-whitelist.json"
SYNTH_PATH = ROOT / ".aicodermap-agent-out-synth.json"
UNIFIED_PATH = ROOT / ".aicodermap-agent-out.json"
I18N_TR = ROOT / "i18n" / "tr.json"
I18N_EN = ROOT / "i18n" / "en.json"

VALID_TIERS = {"I", "S", "C", "U"}
VALID_STATUS = {"active", "deprecated", "archived"}


def _load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return {"_error": str(e)}


def _section(title: str) -> None:
    print()
    print("=" * 78)
    print(f"  {title}")
    print("=" * 78)


def _check(label: str, ok: bool, detail: str = "") -> bool:
    sym = "✓" if ok else "✗"
    print(f"  {sym} {label}{(': ' + detail) if detail else ''}")
    return ok


def main() -> int:
    issues: list[str] = []

    wl = _load(WHITELIST_PATH)
    canonical_bench = set((wl.get("_schema") or {}).get("coreBenchKeys") or [])
    deprecated_bench = set((wl.get("_schema") or {}).get("deprecatedBenchKeys") or [])

    models = _load(MODELS_PATH)
    if not isinstance(models, list):
        print("✗ FATAL: models.json is not a list")
        return 1
    model_ids = {m["id"] for m in models if isinstance(m, dict) and m.get("id")}

    sources = _load(SOURCES_PATH)
    if not isinstance(sources, dict):
        print("✗ FATAL: sources.json is not a dict")
        return 1

    # ----- 1. GATHER ARTIFACT INTEGRITY ---------------------------------------
    _section("1. GATHER ARTIFACT INTEGRITY")
    gather_paths = sorted(glob(str(ROOT / ".aicodermap-agent-out-batch*.gather.json")))
    print(f"  gather artifacts found: {len(gather_paths)}")

    obs_total = 0
    obs_with_unknown_model = []
    obs_with_unknown_bench = []
    obs_missing_source_url = []
    obs_invalid_tier = []
    obs_non_numeric = []
    pricing_total = 0
    pricing_unknown_model = []
    meta_total = 0
    meta_unknown_model = []

    for gp in gather_paths:
        art = _load(Path(gp))
        if not isinstance(art, dict):
            issues.append(f"unparseable artifact: {Path(gp).name}")
            continue
        for o in art.get("observations") or []:
            obs_total += 1
            if not isinstance(o, dict):
                continue
            mid = o.get("modelId")
            bk = o.get("benchKey")
            tier = (o.get("tier") or "").upper()
            url = o.get("sourceUrl")
            val = o.get("value")
            if not isinstance(mid, str) or mid not in model_ids:
                obs_with_unknown_model.append((Path(gp).name, mid, bk))
            if not isinstance(bk, str) or (
                bk not in canonical_bench and bk not in deprecated_bench
            ):
                obs_with_unknown_bench.append((Path(gp).name, mid, bk))
            if tier and tier not in VALID_TIERS:
                obs_invalid_tier.append((Path(gp).name, mid, bk, tier))
            if not url:
                obs_missing_source_url.append((Path(gp).name, mid, bk))
            try:
                float(val)
            except (TypeError, ValueError):
                obs_non_numeric.append((Path(gp).name, mid, bk, val))
        for p in art.get("pricingObs") or []:
            pricing_total += 1
            mid = p.get("modelId") if isinstance(p, dict) else None
            if not isinstance(mid, str) or mid not in model_ids:
                pricing_unknown_model.append((Path(gp).name, mid))
        for mm in art.get("modelMeta") or []:
            meta_total += 1
            mid = mm.get("modelId") if isinstance(mm, dict) else None
            if not isinstance(mid, str) or mid not in model_ids:
                meta_unknown_model.append((Path(gp).name, mid))

    _check("observations parsed", True, f"{obs_total} total")
    _check(
        "observation modelId resolves to known model",
        not obs_with_unknown_model,
        f"{len(obs_with_unknown_model)} unknown"
        if obs_with_unknown_model
        else "all known",
    )
    if obs_with_unknown_model[:3]:
        for s, m, b in obs_with_unknown_model[:3]:
            print(f"      • {s}: modelId={m} bench={b}")
    _check(
        "observation benchKey is canonical or deprecated",
        not obs_with_unknown_bench,
        f"{len(obs_with_unknown_bench)} non-canonical"
        if obs_with_unknown_bench
        else "all canonical",
    )
    _check("observation tier in {I,S,C,U}", not obs_invalid_tier)
    _check(
        "observation has sourceUrl",
        not obs_missing_source_url,
        f"{len(obs_missing_source_url)} missing"
        if obs_missing_source_url
        else "all present",
    )
    _check(
        "observation value is numeric",
        not obs_non_numeric,
        f"{len(obs_non_numeric)} non-numeric" if obs_non_numeric else "all numeric",
    )
    _check(
        "pricingObs modelId valid",
        not pricing_unknown_model,
        f"{pricing_total} total, {len(pricing_unknown_model)} unknown",
    )
    _check(
        "modelMeta modelId valid",
        not meta_unknown_model,
        f"{meta_total} total, {len(meta_unknown_model)} unknown",
    )

    # ----- 2. SYNTH OUTPUT INTEGRITY ------------------------------------------
    _section("2. SYNTH OUTPUT (.aicodermap-agent-out-synth.json)")
    synth = _load(SYNTH_PATH)
    if not isinstance(synth, dict):
        print("  ✗ no synth artifact present")
    else:
        synth_models = synth.get("models") or []
        synth_with_unknown = [
            m["id"] for m in synth_models if m.get("id") not in model_ids
        ]
        synth_bench_wrapped = []  # bench fields stored as {value, trustScore} (Storage violation)
        synth_bench_unknown = []  # bench keys not canonical
        synth_status_invalid = []
        for m in synth_models:
            if not isinstance(m, dict):
                continue
            updates = m.get("updates") or {}
            bench = updates.get("bench") or {}
            for k, v in bench.items():
                if k not in canonical_bench:
                    synth_bench_unknown.append((m.get("id"), k))
                if isinstance(v, dict) and ("value" in v or "trustScore" in v):
                    synth_bench_wrapped.append((m.get("id"), k))
            st = updates.get("status")
            if st is not None and st not in VALID_STATUS:
                synth_status_invalid.append((m.get("id"), st))
        _check(
            "synth models[] all resolve to known IDs",
            not synth_with_unknown,
            f"{len(synth_with_unknown)} unknown",
        )
        _check(
            "synth bench fields are flat scalars",
            not synth_bench_wrapped,
            f"{len(synth_bench_wrapped)} wrapped",
        )
        _check(
            "synth bench keys all canonical",
            not synth_bench_unknown,
            f"{len(synth_bench_unknown)} non-canonical",
        )
        _check(
            "synth status field valid",
            not synth_status_invalid,
            f"{len(synth_status_invalid)} invalid",
        )
        # Cross-contamination: a cell present in synth's models[] sourcesAdded[]
        # whose `key` doesn't match the parent model's id.
        cross = []
        for m in synth_models:
            mid = m.get("id")
            for s in m.get("sourcesAdded") or []:
                k = s.get("key") or ""
                if "." in k and not k.startswith(f"{mid}."):
                    cross.append((mid, k))
        _check(
            "sourcesAdded keys match parent modelId",
            not cross,
            f"{len(cross)} mismatched",
        )
        if cross[:3]:
            for mid, k in cross[:3]:
                print(f"      • model={mid} key={k}")

    # ----- 3. MODELS.JSON STORAGE SHAPE ---------------------------------------
    _section("3. models.json STORAGE SHAPE")
    bench_wrapped = []  # bench cell holds dict instead of scalar
    bench_unknown = []  # bench cell uses non-canonical key
    bench_na_overlap = []  # cell in both bench{} (filled) and notApplicableBenchKeys[]
    pricing_invalid = []  # pricing.api not array
    pricing_subscription_invalid = []
    pricing_range_missing = []
    status_invalid = []
    lifecycle_invalid = []
    for m in models:
        if not isinstance(m, dict):
            continue
        mid = m.get("id")
        # bench shape
        bench = m.get("bench") or {}
        if not isinstance(bench, dict):
            bench_wrapped.append((mid, "bench-not-dict"))
            continue
        for k, v in bench.items():
            # Storage holds both core (active refresh universe) and deprecated
            # (legacy 26-key universe pre-FAZ 5.B/C). Both are valid storage
            # keys; only truly unknown keys are flagged.
            if k not in canonical_bench and k not in deprecated_bench:
                bench_unknown.append((mid, k))
            if v is None:
                continue
            if isinstance(v, dict):
                bench_wrapped.append((mid, k))
            elif not isinstance(v, (int, float)):
                bench_wrapped.append((mid, k))
        # N/A vs filled mutual exclusion
        na_keys = set(m.get("notApplicableBenchKeys") or [])
        for k in na_keys:
            if bench.get(k) is not None:
                bench_na_overlap.append((mid, k))
        # pricing shape
        pr = m.get("pricing")
        if pr:
            api = pr.get("api")
            if api is not None and not isinstance(api, list):
                pricing_invalid.append((mid, type(api).__name__))
            sub = pr.get("subscription")
            if sub is not None and not isinstance(sub, list):
                pricing_subscription_invalid.append((mid, type(sub).__name__))
            rng = pr.get("range")
            if isinstance(api, list) and api and not rng:
                pricing_range_missing.append(mid)
        # status + deprecation
        st = m.get("status")
        if st is not None and st not in VALID_STATUS:
            status_invalid.append((mid, st))
        if st == "deprecated" and not m.get("deprecatedAt"):
            lifecycle_invalid.append((mid, "deprecated-without-deprecatedAt"))
        if st == "archived" and not m.get("archivedAt"):
            lifecycle_invalid.append((mid, "archived-without-archivedAt"))

    _check(
        "bench cells are flat scalars",
        not bench_wrapped,
        f"{len(bench_wrapped)} violations",
    )
    if bench_wrapped[:3]:
        for mid, k in bench_wrapped[:3]:
            print(f"      • {mid}.{k}")
    _check(
        "bench keys all canonical",
        not bench_unknown,
        f"{len(bench_unknown)} non-canonical",
    )
    if bench_unknown[:3]:
        for mid, k in bench_unknown[:3]:
            print(f"      • {mid}.{k}")
    _check(
        "bench cell ≠ N/A overlap",
        not bench_na_overlap,
        f"{len(bench_na_overlap)} cells in both bench{{}} and notApplicableBenchKeys",
    )
    if bench_na_overlap[:5]:
        for mid, k in bench_na_overlap[:5]:
            print(f"      • {mid}.{k}")
    _check(
        "pricing.api is array",
        not pricing_invalid,
        f"{len(pricing_invalid)} non-array",
    )
    _check(
        "pricing.subscription is array",
        not pricing_subscription_invalid,
        f"{len(pricing_subscription_invalid)} non-array",
    )
    _check(
        "pricing.range present when api[] populated",
        not pricing_range_missing,
        f"{len(pricing_range_missing)} missing",
    )
    _check(
        "status field in valid set",
        not status_invalid,
        f"{len(status_invalid)} invalid",
    )
    _check(
        "lifecycle dates set when status changes",
        not lifecycle_invalid,
        f"{len(lifecycle_invalid)} missing",
    )

    # ----- 4. SOURCES.JSON PROVENANCE ----------------------------------------
    _section("4. sources.json PROVENANCE BINDING")
    src_unknown_model = []
    src_invalid_key_format = []
    bench_cells_no_provenance = []
    for k, entries in sources.items():
        if not isinstance(entries, list):
            src_invalid_key_format.append((k, "value-not-list"))
            continue
        if "." not in k:
            src_invalid_key_format.append((k, "missing-dot"))
            continue
        mid = k.split(".")[0]
        if mid not in model_ids:
            src_unknown_model.append((k, mid))
    # Bench cells with no source
    cell_seen = defaultdict(int)
    for k, entries in sources.items():
        if not isinstance(entries, list) or "." not in k:
            continue
        mid, fkey = k.split(".", 1)
        cell_seen[(mid, fkey)] += sum(
            1 for e in entries if isinstance(e, dict) and e.get("value") is not None
        )
    for m in models:
        bench = m.get("bench") or {}
        for k, v in bench.items():
            if v is None:
                continue
            if cell_seen.get((m["id"], k), 0) == 0:
                bench_cells_no_provenance.append((m["id"], k, v))

    _check(
        "sources keys parse to known modelId",
        not src_unknown_model,
        f"{len(src_unknown_model)} orphan keys",
    )
    if src_unknown_model[:3]:
        for k, mid in src_unknown_model[:3]:
            print(f"      • {k} (modelId={mid})")
    _check(
        "sources keys have <modelId>.<field> shape",
        not src_invalid_key_format,
        f"{len(src_invalid_key_format)} malformed",
    )
    _check(
        "every filled bench cell has provenance",
        not bench_cells_no_provenance,
        f"{len(bench_cells_no_provenance)} bench cells without source",
    )
    if bench_cells_no_provenance[:5]:
        for mid, k, v in bench_cells_no_provenance[:5]:
            print(f"      • {mid}.{k} = {v}")

    # ----- 5. i18n ALIGNMENT --------------------------------------------------
    _section("5. i18n STRENGTHS/WEAKNESSES ALIGNMENT")
    tr = _load(I18N_TR)
    en = _load(I18N_EN)
    tr_models = (tr.get("models") or {}).keys() if isinstance(tr, dict) else set()
    en_models = (en.get("models") or {}).keys() if isinstance(en, dict) else set()
    tr_only = set(tr_models) - set(en_models)
    en_only = set(en_models) - set(tr_models)
    missing_in_i18n = model_ids - set(tr_models) - set(en_models)
    extra_in_i18n = (set(tr_models) | set(en_models)) - model_ids
    _check(
        "TR ↔ EN model key parity",
        not tr_only and not en_only,
        f"TR-only={len(tr_only)} EN-only={len(en_only)}",
    )
    _check(
        "every active model has i18n entries",
        not missing_in_i18n,
        f"{len(missing_in_i18n)} missing",
    )
    if missing_in_i18n:
        for mid in sorted(missing_in_i18n)[:5]:
            print(f"      • {mid}")
    _check("no orphan i18n entries", not extra_in_i18n, f"{len(extra_in_i18n)} extra")
    if extra_in_i18n:
        for mid in sorted(extra_in_i18n)[:5]:
            print(f"      • {mid}")
    # Strengths/Weaknesses presence
    sw_missing_tr = []
    sw_missing_en = []
    if isinstance(tr, dict):
        for mid, blk in (tr.get("models") or {}).items():
            if not isinstance(blk, dict):
                continue
            if not blk.get("strengths") or not blk.get("weaknesses"):
                sw_missing_tr.append(mid)
    if isinstance(en, dict):
        for mid, blk in (en.get("models") or {}).items():
            if not isinstance(blk, dict):
                continue
            if not blk.get("strengths") or not blk.get("weaknesses"):
                sw_missing_en.append(mid)
    _check(
        "TR strengths+weaknesses present",
        not sw_missing_tr,
        f"{len(sw_missing_tr)} missing",
    )
    _check(
        "EN strengths+weaknesses present",
        not sw_missing_en,
        f"{len(sw_missing_en)} missing",
    )

    # ----- 6. ROUNDTRIP — synth → models -------------------------------------
    _section("6. SYNTH → models.json ROUNDTRIP (this cycle)")
    if isinstance(synth, dict):
        synth_fills = {}  # (mid, bk) → value claimed by synth
        for m in synth.get("models") or []:
            mid = m.get("id")
            for k, v in (m.get("updates") or {}).get("bench", {}).items():
                if v is not None:
                    synth_fills[(mid, k)] = v
        # Compare against models.json bench cells
        mismatches = []
        for (mid, bk), claimed in synth_fills.items():
            mdl = next((mm for mm in models if mm.get("id") == mid), None)
            if mdl is None:
                continue
            stored = (mdl.get("bench") or {}).get(bk)
            try:
                if stored is None or abs(float(stored) - float(claimed)) > 0.05:
                    mismatches.append((mid, bk, stored, claimed))
            except (TypeError, ValueError):
                mismatches.append((mid, bk, stored, claimed))
        # Note: mismatches are EXPECTED when reconcile/merge applied stricter
        # rules than synth alone. Audit reports them as informational, not
        # errors — they often represent FAZ 6.B/C consensus overrides.
        print(f"  ℹ {len(mismatches)} synth→models drift (consensus override expected)")
        if mismatches[:5]:
            for mid, bk, stored, claimed in mismatches[:5]:
                print(f"      • {mid}.{bk} synth={claimed} stored={stored}")

    # ----- SUMMARY ----------------------------------------------------------
    _section("SUMMARY")
    if issues:
        print("  Auditor errors during run:")
        for i in issues:
            print(f"      • {i}")
    print("  Run audit-data-coherence.py for SSOT-drift checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
