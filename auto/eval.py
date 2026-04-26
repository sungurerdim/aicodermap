#!/usr/bin/env python3
"""ds-tune eval for aicodermap PER_MODEL_URL_EXPANSION cascade.

Reads data/sources-whitelist.json + auto/fixtures.json. For each fixture
(modelId, source, correctSlug), expands the source's slugVariations[] using
{id}/{family}/{N}/{variant} substitution and finds the rank of correctSlug.

Output (grep-able):
  hit_rate_at_1:    <float 0..1>   ← primary metric (higher better)
  hit_rate_at_3:    <float 0..1>   ← secondary
  total_fixtures:   <int>
  Misses (top N):   ← list of fixtures not at rank 1, with expanded chain

No network calls. Runs in ~1s. Used by ds-tune autonomous loop.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WHITELIST = ROOT / "data" / "sources-whitelist.json"
FIXTURES = ROOT / "auto" / "fixtures.json"


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
        }:
            return p
    return ""


def strip_prefix(model_id: str, prefix: str) -> str:
    return (
        model_id[len(prefix) :] if prefix and model_id.startswith(prefix) else model_id
    )


def expand(template: str, model_id: str, vendor_prefix: str = "") -> str:
    """Substitute placeholders. {vendor_prefix} resolves via leaderboard's
    vendorPrefixMap[provider] (passed from caller). {id_no_prefix} strips the
    leading vendor_prefix from id (so claude-haiku-4-5 with prefix='claude-'
    becomes 'haiku-4-5'). Both enable vendor-conditional slug ordering without
    burning all variation slots on dead alternatives."""
    return (
        template.replace("{vendor_prefix}", vendor_prefix)
        .replace("{id_no_prefix}", strip_prefix(model_id, vendor_prefix))
        .replace("{id}", model_id)
        .replace("{family}", family(model_id))
        .replace("{N}", major_version(model_id))
        .replace("{variant}", variant(model_id))
    )


def hostname(url: str) -> str:
    return url.split("//", 1)[-1].split("/", 1)[0].lstrip("www.").lower()


def main():
    wl = json.loads(WHITELIST.read_text(encoding="utf-8"))
    fx_doc = json.loads(FIXTURES.read_text(encoding="utf-8"))
    fixtures = fx_doc["fixtures"]

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
        if "leaderboard" in fx:
            entry = by_lb_host.get(fx["leaderboard"])
            variations = (entry or {}).get("slugVariations", []) or []
            prefix_map = (entry or {}).get("vendorPrefixMap", {}) or {}
            vendor_prefix = prefix_map.get(provider, prefix_map.get("default", ""))
            label = f"lb:{fx['leaderboard']}"
        elif "vendor" in fx:
            v = vendors.get(fx["vendor"], {}) or {}
            via = fx.get("via", "postSlugVariations")
            variations = v.get(via, []) or []
            prefix_map = v.get("vendorPrefixMap", {}) or {}
            vendor_prefix = prefix_map.get(provider, prefix_map.get("default", ""))
            label = f"vendor:{fx['vendor']}.{via}"
        else:
            variations = []
            vendor_prefix = ""
            label = "?"

        expanded = [expand(t, mid, vendor_prefix) for t in variations]
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


if __name__ == "__main__":
    main()
