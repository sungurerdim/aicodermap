#!/usr/bin/env python3
"""ds-tune eval for aicodermap. Outputs TWO metrics in one run (the bench
runs once; ds-tune reads whichever metric .autotune.json points at).

PRIMARY (configurable via .autotune.json):
  predicted_reach: weighted fraction of (modelId, benchKey) pairs in
    data/models.json that have AT LEAST ONE whitelist leaderboard advertising
    the bench in its `publishes[]` AND a fetchable format. Format weight:
      1.0 for static_*, github_raw_*, meta_tag_extract, static_json_api
      0.7 for pdf_report
      0.5 for spa_partial / image_embedded
      0.3 for spa_full
      0.1 for bot_blocked
    Higher = more (model, bench) cells routable through high-quality paths
    in the orchestrator's deep-fetch loop. This is a PROXY for actual
    coverage — the necessary (not sufficient) condition for fill.

SECONDARY:
  hit_rate_at_1: slug-correctness on ds/tune/fixtures.json (already optimized
    to 0.96 in the prior tuning phase). Kept as monitoring guard so coverage
    experiments don't accidentally regress slug ordering.

No network calls. Runs in ~1s.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WHITELIST = ROOT / "data" / "sources-whitelist.json"
FIXTURES = Path(__file__).resolve().parent / "fixtures.json"
MODELS = ROOT / "data" / "models.json"

BENCH_KEYS = [
    "swePro",
    "sweV",
    "sweMulti",
    "tb2",
    "tbHard",
    "lcb",
    "tau2",
    "mcpA",
    "bfcl",
    "browseComp",
    "aaCoding",
    "aaAgentic",
    "aaIdx",
    "aaOmni",
    "cfElo",
    "mmluPro",
    "simpleQa",
    "mrcr",
    "arcAgi2",
    "gpqa",
    "aime26",
    "hle",
]

FORMAT_WEIGHTS = {
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


def family(model_id: str) -> str:
    """Strip trailing version-like tokens (digits or version-with-suffix).

    grok-3 -> grok; grok-3-mini -> grok; gemini-3-1-pro -> gemini;
    qwen3-coder-480b -> qwen3-coder.
    """
    parts = model_id.split("-")
    keep = []
    for p in parts:
        if re.fullmatch(r"\d+(\.\d+)?[a-z]*", p):
            break
        keep.append(p)
    return "-".join(keep) or model_id


def major_version(model_id: str) -> str:
    m = re.search(r"(\d+)", model_id)
    return m.group(1) if m else ""


def variant(model_id: str) -> str:
    """Trailing variant token (pro, flash, lite, mini, max)."""
    parts = model_id.split("-")
    for p in reversed(parts):
        if re.fullmatch(r"[a-z]+", p) and p in {
            "pro",
            "flash",
            "lite",
            "mini",
            "max",
            "plus",
            "fast",
            "high",
            "coder",
            "instruct",
            "chat",
            "moe",
        }:
            return p
    return ""


def strip_prefix(model_id: str, prefix: str) -> str:
    return (
        model_id[len(prefix) :] if prefix and model_id.startswith(prefix) else model_id
    )


def expand(
    template: str, model_id: str, vendor_prefix: str = "", vendor_suffix: str = ""
) -> str:
    """Substitute placeholders. {vendor_prefix} / {vendor_suffix} resolve via
    leaderboard's vendorPrefixMap[provider] / vendorSuffixMap[provider:variant
    | provider | default] (passed from caller). {id_no_prefix} strips the
    leading vendor_prefix from id (so claude-haiku-4-5 with prefix='claude-'
    becomes 'haiku-4-5'). All three enable vendor-conditional slug ordering
    without burning a slot per (provider, variant) combo."""
    return (
        template.replace("{vendor_prefix}", vendor_prefix)
        .replace("{vendor_suffix}", vendor_suffix)
        .replace("{id_no_prefix}", strip_prefix(model_id, vendor_prefix))
        .replace("{id}", model_id)
        .replace("{family}", family(model_id))
        .replace("{N}", major_version(model_id))
        .replace("{variant}", variant(model_id))
    )


def lookup_vendor_value(map_obj: dict, provider: str, var: str) -> str:
    """Compound-key lookup: tries `provider:variant`, then `provider`, then
    `default`. Returns empty string when no match."""
    if not map_obj:
        return ""
    if provider and var and (key := f"{provider}:{var}") in map_obj:
        return map_obj[key]
    if provider and provider in map_obj:
        return map_obj[provider]
    return map_obj.get("default", "")


def hostname(url: str) -> str:
    return url.split("//", 1)[-1].split("/", 1)[0].lstrip("www.").lower()


def compute_predicted_reach(wl, models):
    """For each (modelId, benchKey) pair, find the BEST format-weighted
    leaderboard that advertises the bench in its publishes[]. Sum of weights
    divided by total pairs = predicted_reach (0..1).

    Also reports per-bench-key reach so an experiment can target the worst
    bench keys directly. A pair with no advertised source contributes 0.
    """
    leaderboards = wl.get("leaderboards", []) or []

    # Per-bench: best-weight leaderboard advertising it
    bench_best_weight = {k: 0.0 for k in BENCH_KEYS}
    bench_source_count = {k: 0 for k in BENCH_KEYS}
    for lb in leaderboards:
        publishes = lb.get("publishes", []) or []
        fmt = lb.get("format", "static_html_table")
        w = FORMAT_WEIGHTS.get(fmt, 0.5)
        for k in publishes:
            if k in bench_best_weight:
                bench_source_count[k] += 1
                if w > bench_best_weight[k]:
                    bench_best_weight[k] = w

    # Pair sum: every (model, bench) pair gets the bench's best-weight, so
    # predicted_reach = mean(bench_best_weight) (uniform across models).
    # Justification: bench's reach is the same for every model in the catalog
    # (the leaderboard either covers the bench or it doesn't). Per-model
    # variation kicks in via slug resolvability — captured by hit_rate_at_1.
    total_pairs = len(models) * len(BENCH_KEYS)
    pair_sum = sum(bench_best_weight[k] for k in BENCH_KEYS) * len(models)
    predicted_reach = pair_sum / total_pairs if total_pairs else 0.0

    # Per-bench coverage report
    zero_source_keys = [k for k in BENCH_KEYS if bench_source_count[k] == 0]

    # Redundancy: counts high-weight sources (>=0.7) per bench, capped at 3 to
    # avoid runaway when a meta-aggregator claims all keys. Mean / 3 = score.
    REDUNDANCY_CAP = 3
    high_weight_count = {k: 0 for k in BENCH_KEYS}
    for lb in leaderboards:
        publishes = lb.get("publishes", []) or []
        fmt = lb.get("format", "static_html_table")
        w = FORMAT_WEIGHTS.get(fmt, 0.5)
        if w >= 0.7:
            for k in publishes:
                if k in high_weight_count:
                    high_weight_count[k] += 1
    redundancy_score = sum(
        min(high_weight_count[k], REDUNDANCY_CAP) for k in BENCH_KEYS
    ) / (len(BENCH_KEYS) * REDUNDANCY_CAP)

    return (
        predicted_reach,
        bench_best_weight,
        bench_source_count,
        zero_source_keys,
        redundancy_score,
        high_weight_count,
    )


def main():
    wl = json.loads(WHITELIST.read_text(encoding="utf-8"))
    fx_doc = json.loads(FIXTURES.read_text(encoding="utf-8"))
    fixtures = fx_doc["fixtures"]
    models = json.loads(MODELS.read_text(encoding="utf-8"))

    # Coverage proxies
    (
        pr,
        bench_weights,
        bench_counts,
        zero_keys,
        redundancy,
        bench_high_count,
    ) = compute_predicted_reach(wl, models)
    print(f"predicted_reach:  {pr:.4f}")
    print(f"redundancy_score: {redundancy:.4f}")

    by_lb_host = {}
    for e in wl.get("leaderboards", []) or []:
        url = e.get("url", "")
        if not url:
            continue
        by_lb_host[hostname(url)] = e

    vendors = wl.get("vendors", {}) or {}

    rank1 = rank3 = total = 0
    misses = []
    not_found = []

    for fx in fixtures:
        total += 1
        mid = fx["modelId"]
        correct = fx["correctSlug"]

        provider = fx.get("provider", "")
        var = variant(mid)
        if "leaderboard" in fx:
            entry = by_lb_host.get(fx["leaderboard"])
            variations = (entry or {}).get("slugVariations", []) or []
            vendor_prefix = lookup_vendor_value(
                (entry or {}).get("vendorPrefixMap", {}), provider, var
            )
            vendor_suffix = lookup_vendor_value(
                (entry or {}).get("vendorSuffixMap", {}), provider, var
            )
            label = f"lb:{fx['leaderboard']}"
        elif "vendor" in fx:
            v = vendors.get(fx["vendor"], {}) or {}
            via = fx.get("via", "postSlugVariations")
            variations = v.get(via, []) or []
            vendor_prefix = lookup_vendor_value(
                v.get("vendorPrefixMap", {}), provider, var
            )
            vendor_suffix = lookup_vendor_value(
                v.get("vendorSuffixMap", {}), provider, var
            )
            label = f"vendor:{fx['vendor']}.{via}"
        else:
            variations = []
            vendor_prefix = ""
            vendor_suffix = ""
            label = "?"

        expanded = [expand(t, mid, vendor_prefix, vendor_suffix) for t in variations]
        try:
            rank = expanded.index(correct) + 1
        except ValueError:
            rank = 99
            not_found.append((mid, label, correct, expanded[:5]))

        if rank == 1:
            rank1 += 1
        if rank <= 3:
            rank3 += 1
        if rank > 1:
            misses.append((mid, label, correct, rank, expanded[:5]))

    h1 = rank1 / total if total else 0.0
    h3 = rank3 / total if total else 0.0
    print(f"hit_rate_at_1:    {h1:.4f}")
    print(f"hit_rate_at_3:    {h3:.4f}")
    print(f"total_fixtures:   {total}")
    print(f"rank1:            {rank1}")
    print(f"rank3:            {rank3}")
    if misses:
        print(f"\nMisses (top 12 of {len(misses)}):")
        for mid, label, correct, rank, expanded in misses[:12]:
            print(
                f"  [{label}] {mid} -> expected '{correct}' rank={rank} chain={expanded}"
            )
    if not_found:
        print(
            f"\nNot in chain ({len(not_found)} fixtures lack the correct slug entirely):"
        )
        for mid, label, correct, expanded in not_found[:8]:
            print(f"  [{label}] {mid} -> '{correct}' MISSING; chain={expanded}")

    print("\n=== Coverage proxy (predicted_reach + redundancy per bench key) ===")
    for k in BENCH_KEYS:
        w = bench_weights[k]
        c = bench_counts[k]
        hc = bench_high_count[k]
        marker = " <-- ZERO" if c == 0 else (" <-- ONLY ONE HIGH-W" if hc < 2 else "")
        print(
            f"  {k:<10} best_weight={w:.2f} total_sources={c} high_weight_sources={hc}{marker}"
        )
    if zero_keys:
        print(
            f"\nBench keys with NO advertised source ({len(zero_keys)}): "
            f"{', '.join(zero_keys)}"
        )


if __name__ == "__main__":
    main()
