#!/usr/bin/env python3
"""
Merge an aicodermap-research-agent return into data/{models,sources}.json
+ append CHANGELOG entry.

Reads .aicodermap-agent-out.json (the agent's return JSON saved by the skill).
Performs schema-complete merge per SKILL.md MERGE_RULES:
- Multi-provider pricing.api array dedupe by provider
- Recompute pricing.range from merged api[]
- Subscription array merge by tier
- Contradiction auto-resolution: write autoResolveWinner, append all candidates
  to data/sources.json with trustScores
- sourcesAdded entries append to data/sources.json (dedupe by url+value)
- Lifecycle: status field, deprecation transitions
- Backup rotation: bak2 dropped, bak -> bak2, current -> bak (preserve bak3)
- lastUpdated touched only on models with deltas
"""

import json
import os
import shutil
from datetime import date
from urllib.parse import urlparse

PROJECT = "D:/GitHub/aicodermap"
TODAY = date.today().isoformat()
ARTIFACT = f"{PROJECT}/.aicodermap-agent-out.json"
WHITELIST = f"{PROJECT}/data/sources-whitelist.json"

# Formats whose primary fetch is "skip" — fetching their canonical URL directly
# should be rare. A sourcesAdded entry that points at one of these formats and
# claims a high tier deserves a non-blocking warning so an operator can verify
# the agent reached the data via the documented fallback chain (mirror /
# WebSearch / image OCR) rather than scraping the SPA directly.
SKIP_PRIMARY_FORMATS = {"spa_full", "bot_blocked", "image_embedded"}


def rotate_backup(path):
    bak = path + ".bak"
    bak2 = path + ".bak2"
    if os.path.exists(bak2):
        os.remove(bak2)
    if os.path.exists(bak):
        os.rename(bak, bak2)
    shutil.copy2(path, bak)


def deep_merge(dst, src):
    """Recursively merge src into dst. Arrays are replaced unless handled specially."""
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            deep_merge(dst[k], v)
        else:
            dst[k] = v


def merge_pricing(dst_pricing, src_pricing):
    """Multi-provider pricing array merge: dedupe api[] by provider, recompute range."""
    if "api" in src_pricing and isinstance(src_pricing["api"], list):
        existing = dst_pricing.get("api") or []
        if not isinstance(existing, list):
            existing = []
        merged_by_provider = {e.get("provider"): e for e in existing}
        for entry in src_pricing["api"]:
            prov = entry.get("provider")
            if not prov:
                continue
            cur = merged_by_provider.get(prov, {})
            cur_fetched = cur.get("fetched") or "1970-01-01"
            new_fetched = entry.get("fetched") or "1970-01-01"
            if (prov not in merged_by_provider) or (new_fetched >= cur_fetched):
                merged_by_provider[prov] = entry
        dst_pricing["api"] = list(merged_by_provider.values())
    if "subscription" in src_pricing:
        if (
            isinstance(src_pricing["subscription"], list)
            or src_pricing["subscription"] is None
        ):
            dst_pricing["subscription"] = src_pricing["subscription"]
    api = dst_pricing.get("api") or []
    if isinstance(api, list) and api:
        ins = [e["in"] for e in api if e.get("in") is not None]
        outs = [e["out"] for e in api if e.get("out") is not None]
        chs = [e["cacheHit"] for e in api if e.get("cacheHit") is not None]
        dst_pricing["range"] = {
            "in": [min(ins), max(ins)] if ins else None,
            "out": [min(outs), max(outs)] if outs else None,
            "cacheHit": [min(chs), max(chs)] if chs else None,
        }


def apply_model_update(model, updates):
    touched = False
    for k, v in updates.items():
        if k == "pricing" and isinstance(v, dict):
            if "pricing" not in model or not isinstance(model["pricing"], dict):
                model["pricing"] = {"api": [], "subscription": None, "range": None}
            merge_pricing(model["pricing"], v)
            touched = True
        elif k == "bench" and isinstance(v, dict):
            if "bench" not in model:
                model["bench"] = {}
            for bk, bv in v.items():
                if isinstance(bv, dict) and "value" in bv:
                    bv = bv["value"]
                if bv is not None and model["bench"].get(bk) != bv:
                    model["bench"][bk] = bv
                    touched = True
        elif k == "ollama" and isinstance(v, dict):
            model["ollama"] = v
            touched = True
        elif k == "lastUpdated":
            continue
        else:
            if model.get(k) != v:
                model[k] = v
                touched = True
    if touched:
        model["lastUpdated"] = TODAY
    return touched


def find(models, mid):
    for m in models:
        if m.get("id") == mid:
            return m
    return None


def build_whitelist_index():
    """Hostname → (format, tier) lookup for format-consistency log. Non-fatal
    on missing/malformed whitelist."""
    try:
        with open(WHITELIST, encoding="utf-8") as fp:
            wl = json.load(fp)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    idx = {}
    for cat in ("leaderboards", "aggregators", "community", "local", "registries"):
        for e in wl.get(cat, []) or []:
            url = e.get("url")
            if not url:
                continue
            try:
                host = urlparse(url).hostname or ""
            except Exception:
                continue
            host = host.lower().lstrip("www.")
            if host and host not in idx:
                idx[host] = (e.get("format"), e.get("tier"))
    return idx


def format_consistency_warn(source_entry, wl_idx):
    """Log non-blocking warning when a sourcesAdded entry's URL hostname is
    classified as a 'skip primary' format (spa_full / bot_blocked /
    image_embedded) yet the artifact tags it as a high-tier source. Either
    the agent reached the data via the documented fallback chain (fine — but
    the URL recorded should reflect the mirror), or the agent fetched the
    SPA/blocked page directly (suspect)."""
    url = source_entry.get("url") or ""
    if not url:
        return None
    try:
        host = (urlparse(url).hostname or "").lower().lstrip("www.")
    except Exception:
        return None
    info = wl_idx.get(host)
    if not info:
        return None
    fmt, _wl_tier = info
    if fmt in SKIP_PRIMARY_FORMATS and source_entry.get("tier") in ("I", "S"):
        return (
            f"format-consistency: url={url} format={fmt} but tier="
            f"{source_entry.get('tier')} — confirm this came via fallback "
            f"chain (mirror/WebSearch/OCR) and not direct SPA scrape"
        )
    return None


def validate_gaps(out):
    """GAP_VALIDITY_GATE per agent spec (2026-04-27).

    Every gaps[] entry MUST carry triedSources>=2 + triedQueries>=2 + triedFormats>=2.
    Entries failing the gate are fabricated (agent emitted "no data" without
    attempting). They are stripped from out.gaps[] so they don't pollute the
    next-cycle retry queue, logged loudly, and counted under
    runtime.contractViolations so the violation surfaces in the diff summary.

    Returns: list of stripped fabricated-gap descriptors for caller logging.
    """
    raw = out.get("gaps", []) or []
    valid = []
    fabricated = []
    for g in raw:
        ts = g.get("triedSources") or []
        tq = g.get("triedQueries") or []
        tf = g.get("triedFormats") or []
        ts_n, tq_n, tf_n = len(ts), len(tq), len(tf)
        # Permissive: accept if at least one effort signal has >=2 entries.
        # Strict: require triedSources>=2 (the load-bearing one for "I tried").
        if ts_n < 2:
            fabricated.append(
                {
                    "modelId": g.get("modelId"),
                    "field": g.get("field"),
                    "reason": g.get("reason"),
                    "counts": {
                        "triedSources": ts_n,
                        "triedQueries": tq_n,
                        "triedFormats": tf_n,
                    },
                }
            )
        else:
            valid.append(g)
    out["gaps"] = valid
    runtime = out.setdefault("runtime", {})
    if fabricated:
        runtime["contractViolations"] = runtime.get("contractViolations", 0) + len(
            fabricated
        )
        runtime.setdefault("fabricatedGaps", []).extend(fabricated)
    return fabricated


def append_source(sources, key, entry):
    if key not in sources:
        sources[key] = []
    arr = sources[key]
    sig = (entry.get("url"), entry.get("value"))
    for existing in arr:
        if (existing.get("url"), existing.get("value")) == sig:
            for k in ("trustScore", "tier", "fetched", "verifications", "source"):
                if entry.get(k) is not None:
                    existing[k] = entry[k]
            return False
    arr.append(entry)
    return True


def main():
    with open(ARTIFACT, encoding="utf-8") as fp:
        out = json.load(fp)

    fabricated_gaps = validate_gaps(out)

    models_path = f"{PROJECT}/data/models.json"
    sources_path = f"{PROJECT}/data/sources.json"
    rotate_backup(models_path)
    rotate_backup(sources_path)

    with open(models_path, encoding="utf-8") as fp:
        models = json.load(fp)
    with open(sources_path, encoding="utf-8") as fp:
        sources = json.load(fp)

    wl_idx = build_whitelist_index()

    log = {
        "updated": [],
        "added": [],
        "lineup_deprecated": [],
        "lineup_renamed": [],
        "contradictions": [],
        "sources_appended": 0,
        "format_warnings": [],
        "gaps": [],
        "fabricated_gaps": fabricated_gaps,
    }

    for upd in out.get("models", []):
        mid = upd["id"]
        m = find(models, mid)
        if m is None:
            log["gaps"].append(f"unknown id in updates: {mid}")
            continue
        if apply_model_update(m, upd.get("updates", {})):
            log["updated"].append(mid)
        for s in upd.get("sourcesAdded", []) or []:
            warn = format_consistency_warn(s, wl_idx)
            if warn:
                log["format_warnings"].append(f"{mid}: {warn}")
            if append_source(
                sources,
                s["key"],
                {
                    "value": s.get("value"),
                    "source": s.get("source"),
                    "url": s.get("url"),
                    "date": s.get("fetched") or TODAY,
                    "tier": s.get("tier"),
                    "verifications": s.get("verifications", 1),
                    "trustScore": s.get("trustScore"),
                },
            ):
                log["sources_appended"] += 1

    for nm in out.get("newModels", []) or []:
        if find(models, nm["id"]) is None:
            models.append(nm)
            log["added"].append(nm["id"])

    BENCH_KEYS = {
        "sweV",
        "swePro",
        "tb2",
        "lcbV6",
        "aider",
        "tau2",
        "aaCoding",
        "aaAgentic",
        "mcpA",
        "bfcl",
        "aime26",
        "aaOmni",
        "gpqa",
        "sweMulti",
        "hle",
        "aaIdx",
    }
    for c in out.get("contradictions", []) or []:
        mid = c["modelId"]
        field = c["field"]
        winner = c.get("autoResolveWinner")
        if winner is None:
            continue
        # DATA_CONTRACT defensive unwrap: winner may arrive as wrapped dict {value, trustScore, sourceUrl, tier}.
        # Storage shape is scalar; extract .value before writing to models.json.
        winner_value = (
            winner["value"]
            if isinstance(winner, dict) and "value" in winner
            else winner
        )
        # Bare-key normalize: agent contract says field is bare ("swePro"), but tolerate "bench.swePro" too.
        bench_field = field.split(".", 1)[1] if field.startswith("bench.") else field
        m = find(models, mid)
        if m is not None and bench_field in BENCH_KEYS:
            if "bench" not in m:
                m["bench"] = {}
            m["bench"][bench_field] = winner_value
            m["lastUpdated"] = TODAY
        key = f"{mid}.{bench_field}"
        for cand in c.get("candidates", []) or []:
            append_source(
                sources,
                key,
                {
                    "value": cand.get("value"),
                    "source": cand.get("source") or "auto-resolution candidate",
                    "url": cand.get("url"),
                    "date": cand.get("fetched") or TODAY,
                    "tier": cand.get("tier"),
                    "verifications": cand.get("verifications", 1),
                    "trustScore": cand.get("trustScore"),
                    "contradictionRole": "winner"
                    if cand.get("value") == winner_value
                    else "loser",
                },
            )
            log["sources_appended"] += 1
        log["contradictions"].append(
            f"{key}: winner={winner} (severity={c.get('severity') or 'GREEN'}, Δ{c.get('delta')})"
        )

    lineup = out.get("lineupChanges", {}) or {}
    for d in lineup.get("deprecated", []) or []:
        if find(models, d.get("id")) is not None:
            target = find(models, d["id"])
            target["status"] = "deprecated"
            target["deprecatedAt"] = d.get("deprecationDate") or TODAY
            if d.get("successor"):
                target["successor"] = d["successor"]
            target["lastUpdated"] = TODAY
            log["lineup_deprecated"].append(d["id"])
    for r in lineup.get("renamed", []) or []:
        log["lineup_renamed"].append(f"{r.get('from')} -> {r.get('to')}")

    issues = []
    for m in models:
        p = m.get("pricing")
        if isinstance(p, dict):
            if "api" in p and not isinstance(p["api"], list):
                issues.append(f"{m['id']}: pricing.api not array")
            if "subscription" in p and isinstance(p.get("subscription"), str):
                issues.append(f"{m['id']}: pricing.subscription still string")
        if m.get("status") not in (None, "active", "deprecated", "archived"):
            issues.append(f"{m['id']}: invalid status {m.get('status')}")

    with open(models_path, "w", encoding="utf-8") as fp:
        json.dump(models, fp, indent=2, ensure_ascii=False)
        fp.write("\n")
    with open(sources_path, "w", encoding="utf-8") as fp:
        json.dump(sources, fp, indent=2, ensure_ascii=False)
        fp.write("\n")

    coverage = out.get("validationCoverage", 0)
    cov_pct = round(coverage * 100, 1)
    coverage_warn = ""
    if coverage < 0.50:
        coverage_warn = f" [WARN: partial coverage {cov_pct}%]"

    cl_path = f"{PROJECT}/CHANGELOG.md"
    cl_lines = [f"\n## [{TODAY}] — autonomous refresh-all{coverage_warn}\n"]
    if log["added"]:
        cl_lines.append("\n### Added\n")
        for mid in log["added"]:
            cl_lines.append(f"- `{mid}` — new model from vendor lineup discovery\n")
    if log["updated"]:
        cl_lines.append("\n### Updated\n")
        cl_lines.append(
            f"- {len(log['updated'])} models: {', '.join(f'`{x}`' for x in log['updated'])}\n"
        )
    if log["lineup_deprecated"]:
        cl_lines.append("\n### Deprecated\n")
        for mid in log["lineup_deprecated"]:
            cl_lines.append(f"- `{mid}` — vendor-marked deprecated\n")
    if log["lineup_renamed"]:
        cl_lines.append("\n### Renamed\n")
        for r in log["lineup_renamed"]:
            cl_lines.append(f"- {r}\n")
    if log["contradictions"]:
        cl_lines.append("\n### Resolved (auto via trustScore)\n")
        for c in log["contradictions"]:
            cl_lines.append(f"- {c}\n")
    if out.get("gaps"):
        cl_lines.append(
            f"\n### Gaps ({len(out['gaps'])} entries — see data/known-gaps.json or next refresh)\n"
        )
        for g in out["gaps"][:8]:
            cl_lines.append(f"- `{g.get('key')}`: {g.get('reason')}\n")
        if len(out["gaps"]) > 8:
            cl_lines.append(f"- ... and {len(out['gaps']) - 8} more\n")

    cl_blob = "".join(cl_lines)
    if os.path.exists(cl_path):
        with open(cl_path, encoding="utf-8") as fp:
            existing = fp.read()
        with open(cl_path, "w", encoding="utf-8") as fp:
            fp.write(cl_blob + "\n" + existing)
    else:
        with open(cl_path, "w", encoding="utf-8") as fp:
            fp.write("# Changelog\n\n" + cl_blob)

    print("merge complete:")
    print(f"  added:      {len(log['added'])} -> {log['added']}")
    print(f"  updated:    {len(log['updated'])}")
    print(f"  deprecated: {len(log['lineup_deprecated'])}")
    print(f"  renamed:    {len(log['lineup_renamed'])}")
    print(f"  contradictions auto-resolved: {len(log['contradictions'])}")
    print(f"  sources appended: {log['sources_appended']}")
    print(f"  coverage:   {cov_pct}%{' (PARTIAL WARN)' if coverage < 0.50 else ''}")
    if log["format_warnings"]:
        print(f"  format warnings: {len(log['format_warnings'])} (non-blocking)")
        for w in log["format_warnings"][:5]:
            print(f"    - {w}")
        if len(log["format_warnings"]) > 5:
            print(f"    - ... and {len(log['format_warnings']) - 5} more")
    if log.get("fabricated_gaps"):
        n = len(log["fabricated_gaps"])
        print(
            f"  fabricated gaps stripped: {n} (agent claimed 'no data' without "
            f"triedSources>=2 — see GAP_VALIDITY_GATE)"
        )
        for fg in log["fabricated_gaps"][:6]:
            print(
                f"    - {fg['modelId']}.{fg['field']}: "
                f"triedSources={fg['counts']['triedSources']} reason='{fg['reason']}'"
            )
        if n > 6:
            print(f"    - ... and {n - 6} more")
    if issues:
        print("self-check issues:")
        for i in issues:
            print(f"  - {i}")
    else:
        print("self-check: PASS")
    print(f"total models: {len(models)}")


if __name__ == "__main__":
    main()
