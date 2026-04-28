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
import sys
from datetime import date, datetime, timezone
from urllib.parse import urlparse

PROJECT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
TODAY = date.today().isoformat()
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
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


def restore_from_bak(paths):
    """Roll back the just-written files to the .bak snapshot taken before the
    merge. Used when post-write SSOT audit detects drift — leaves the working
    tree in the pre-merge state so the user can investigate without polluted
    data files. Returns the list of paths that were rolled back."""
    rolled = []
    for p in paths:
        bak = p + ".bak"
        if os.path.exists(bak):
            shutil.copy2(bak, p)
            rolled.append(p)
    return rolled


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
            if "benchUpdated" not in model or not isinstance(
                model.get("benchUpdated"), dict
            ):
                model["benchUpdated"] = {}
            for bk, bv in v.items():
                if isinstance(bv, dict) and "value" in bv:
                    bv = bv["value"]
                # Per-cell lastUpdated: stamp ONLY when the agent successfully
                # extracted a value for this (model, bench) pair this cycle.
                # Null / missing returns leave the prior date untouched.
                if bv is None:
                    continue
                if model["bench"].get(bk) != bv:
                    model["bench"][bk] = bv
                    touched = True
                model["benchUpdated"][bk] = TODAY
        elif k == "ollama" and isinstance(v, dict):
            model["ollama"] = v
            touched = True
        elif k == "lastUpdated":
            continue
        else:
            if model.get(k) != v:
                model[k] = v
                touched = True
    # Model-level lastUpdated: full ISO 8601 datetime (UTC, e.g.
    # "2026-04-28T17:23:45Z"). Stamping with the wallclock cycle time — not
    # the per-bench date — disambiguates same-day reruns. Lex-sortable since
    # ISO 8601 with Z preserves chronological order and beats date-only
    # strings when compared via max().
    bu = model.get("benchUpdated")
    bench_max = max(bu.values()) if isinstance(bu, dict) and bu else None
    if touched:
        model["lastUpdated"] = NOW
    elif bench_max:
        model["lastUpdated"] = max(model.get("lastUpdated") or "", bench_max)
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


_FORMAT_WEIGHTS = {
    "static_html_table": 1.0,
    "static_html_article": 1.0,
    "static_markdown": 1.0,
    "static_json_api": 1.0,
    "github_raw_json": 1.0,
    "github_raw_markdown": 1.0,
    "meta_tag_extract": 1.0,
    "pdf_report": 0.7,
    "spa_partial": 0.5,
    "image_embedded": 0.5,
    "spa_full": 0.3,
    "bot_blocked": 0.1,
}


def _build_bench_advertised_count():
    """For each bench key, count high-weight (>=0.7) leaderboards advertising
    it in publishes[]. Used by adaptive gate."""
    try:
        with open(WHITELIST, encoding="utf-8") as fp:
            wl = json.load(fp)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    counts = {}
    for lb in wl.get("leaderboards", []) or []:
        fmt = lb.get("format", "static_html_table")
        if _FORMAT_WEIGHTS.get(fmt, 0.5) < 0.7:
            continue
        for k in lb.get("publishes", []) or []:
            counts[k] = counts.get(k, 0) + 1
    return counts


def _load_bench_key_universe():
    """Bench-key universe = whitelist._schema.coreBenchKeys ∪ every
    leaderboard's publishes[] entry. Loaded fresh from whitelist on each
    merge run so a leaderboard adding a new bench key in publishes[] flows
    through automatically."""
    try:
        with open(WHITELIST, encoding="utf-8") as fp:
            wl = json.load(fp)
    except (FileNotFoundError, json.JSONDecodeError):
        return set()
    universe = set()
    schema = wl.get("_schema") or {}
    for k in schema.get("coreBenchKeys", []) or []:
        universe.add(k)
    for lb in wl.get("leaderboards", []) or []:
        for k in lb.get("publishes", []) or []:
            universe.add(k)
    return universe


def _extract_bench_key(g):
    """Per the agent contract a gap entry carries `field` as the bare bench
    key (e.g. "swePro"). Returns the bare key as-is."""
    return g.get("field") or ""


def validate_gaps(out):
    """GAP_VALIDITY_GATE — audit-only (reformed 2026-04-28).

    Earlier behaviour stripped gaps[] entries whose triedSources count fell
    below clamp(advertised_high_weight, 3, 5). That pressured the agent to
    silently omit hard-to-reach pairs rather than transparently log them.

    The reform: NEVER strip a gap. Every gaps[] entry is preserved exactly as
    the agent emitted it. The function still walks the list to compute a
    "low-effort suspicion" record so a human reviewer can spot gaps that
    deserved more effort, but the gap stays.

    Returns the suspicion list (audit) for the orchestrator's diff summary.
    """
    bench_advertised = _build_bench_advertised_count()
    raw = out.get("gaps", []) or []
    suspicions = []
    for g in raw:
        ts = g.get("triedSources") or []
        tq = g.get("triedQueries") or []
        tf = g.get("triedFormats") or []
        ts_n, tq_n, tf_n = len(ts), len(tq), len(tf)

        bench_key = _extract_bench_key(g)
        n_advertised = bench_advertised.get(bench_key, 0)
        # advisory floor (3 minimum, scale with advertised, cap at 5)
        suggested_floor = min(max(n_advertised, 3), 5)

        if ts_n < suggested_floor:
            suspicions.append(
                {
                    "modelId": g.get("modelId"),
                    "field": g.get("field"),
                    "bench_key": bench_key,
                    "reason": g.get("reason"),
                    "counts": {
                        "triedSources": ts_n,
                        "triedQueries": tq_n,
                        "triedFormats": tf_n,
                    },
                    "n_advertised": n_advertised,
                    "suggested_floor": suggested_floor,
                }
            )
    runtime = out.setdefault("runtime", {})
    if suspicions:
        runtime.setdefault("fabricatedSuspicions", []).extend(suspicions)
    return suspicions


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

    fabricated_suspicions = validate_gaps(out)

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
        "fabricated_suspicions": fabricated_suspicions,
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

    BENCH_KEYS = _load_bench_key_universe()
    for c in out.get("contradictions", []) or []:
        mid = c["modelId"]
        # Agent contract: `field` is the bare bench key, `autoResolveWinner` is
        # the wrapped {value, trustScore, sourceUrl, tier} dict — Storage extracts
        # `.value` for models.json, full dict goes into sources.json provenance.
        bench_field = c["field"]
        winner = c.get("autoResolveWinner")
        if winner is None:
            continue
        winner_value = winner["value"]
        m = find(models, mid)
        if m is not None and bench_field in BENCH_KEYS:
            if "bench" not in m:
                m["bench"] = {}
            if "benchUpdated" not in m or not isinstance(m.get("benchUpdated"), dict):
                m["benchUpdated"] = {}
            prev_value = m["bench"].get(bench_field)
            m["bench"][bench_field] = winner_value
            m["benchUpdated"][bench_field] = TODAY
            if prev_value != winner_value:
                m["lastUpdated"] = NOW
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
            target["lastUpdated"] = NOW
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
        coverage_warn = f" [WARN: very low cumulative provenance coverage {cov_pct}%]"
    elif coverage < 0.85:
        coverage_warn = (
            f" [WARN: cumulative provenance coverage {cov_pct}% below 85% target]"
        )

    # PRE_EMIT_SELF_AUDIT verification — advisory log, never blocks (UNCAPPED).
    # The agent is contractually required to compute coverageMatrix and the
    # invariant filledCells + gapsRecorded == totalCells. We re-verify here so
    # a forgotten/skipped agent self-audit doesn't slip past silently. Output
    # is a CHANGELOG line + console warning; commit + push proceeds either way.
    matrix_warn = ""
    matrix = out.get("coverageMatrix")
    if not isinstance(matrix, dict):
        matrix_warn = (
            " [WARN: artifact missing coverageMatrix; agent skipped self-audit]"
        )
    else:
        total = matrix.get("totalCells")
        filled = matrix.get("filledCells")
        gaps_recorded = matrix.get("gapsRecorded")
        if not all(isinstance(x, int) for x in (total, filled, gaps_recorded)):
            matrix_warn = " [WARN: coverageMatrix has non-int totalCells/filledCells/gapsRecorded]"
        elif filled + gaps_recorded != total:
            short = total - (filled + gaps_recorded)
            matrix_warn = (
                f" [WARN: coverageMatrix invariant violated — "
                f"{short} cell(s) silently missing (filled={filled} + gaps={gaps_recorded} ≠ total={total})]"
            )
    if matrix_warn:
        coverage_warn = (coverage_warn + matrix_warn) if coverage_warn else matrix_warn

    # SSOT coherence audit — HARD BLOCK gate. Runs against the just-written
    # data files. On drift: roll the data files back to their .bak snapshots,
    # print a loud failure with the audit's stderr, and exit non-zero so the
    # skill orchestrator (and any caller) sees the merge did not complete.
    # No CHANGELOG entry, no commit-eligible state — drift never reaches main.
    import subprocess

    proc = subprocess.run(
        [sys.executable, f"{PROJECT}/scripts/audit-data-coherence.py"],
        capture_output=True,
        text=True,
        check=False,
    )
    coherence_ok = proc.returncode == 0
    if not coherence_ok:
        rolled = restore_from_bak([models_path, sources_path])
        print("\n" + "=" * 72, file=sys.stderr)
        print("✗ MERGE ABORTED — SSOT coherence drift in artifact", file=sys.stderr)
        print("=" * 72, file=sys.stderr)
        for line in (proc.stderr or "").strip().splitlines():
            print(f"  {line}", file=sys.stderr)
        print("", file=sys.stderr)
        if rolled:
            print(
                f"  Rolled back {len(rolled)} file(s) from .bak so the working tree "
                f"matches the pre-merge state:",
                file=sys.stderr,
            )
            for p in rolled:
                print(f"    - {os.path.relpath(p, PROJECT)}", file=sys.stderr)
        print("", file=sys.stderr)
        print(
            "  Fix the drift in .aicodermap-agent-out.json (the agent's artifact) "
            "or the underlying SSOT files, then re-run merge. Commit is blocked "
            "until audit passes.",
            file=sys.stderr,
        )
        print("=" * 72, file=sys.stderr)
        sys.exit(1)

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
    if matrix_warn:
        print(f"  audit:     {matrix_warn.lstrip(' [').rstrip(']')}")
    elif isinstance(matrix, dict):
        print(
            f"  audit:      coverageMatrix OK "
            f"(filled={matrix.get('filledCells')}/{matrix.get('totalCells')}, "
            f"gaps={matrix.get('gapsRecorded')})"
        )

    print("  coherence:  ✓ SSOT (bench keys + model ids aligned across surfaces)")
    if log["format_warnings"]:
        print(f"  format warnings: {len(log['format_warnings'])} (non-blocking)")
        for w in log["format_warnings"][:5]:
            print(f"    - {w}")
        if len(log["format_warnings"]) > 5:
            print(f"    - ... and {len(log['format_warnings']) - 5} more")
    if log.get("fabricated_suspicions"):
        n = len(log["fabricated_suspicions"])
        print(
            f"  low-effort gap suspicions: {n} (advisory only — "
            f"suggested triedSources = clamp(advertised_high_weight, 3, 5)). "
            f"Originals retained in gaps[]."
        )
        for fg in log["fabricated_suspicions"][:8]:
            print(
                f"    - {fg.get('modelId')}.{fg.get('bench_key', fg.get('field'))}: "
                f"triedSources={fg['counts']['triedSources']} "
                f"suggested>={fg.get('suggested_floor', 3)} "
                f"(advertised_high_weight={fg.get('n_advertised', 0)})"
            )
        if n > 8:
            print(f"    - ... and {n - 8} more")
    if issues:
        print("self-check issues:")
        for i in issues:
            print(f"  - {i}")
    else:
        print("self-check: PASS")
    print(f"total models: {len(models)}")


if __name__ == "__main__":
    main()
