#!/usr/bin/env python3
"""
AICoderMap schema v1 -> v2 migration:
- pricing.api {in, out, cacheHit} -> array of provider entries + computed pricing.range
- pricing.subscription string -> array of {tier, price, currency, billing, notes}
- Add status: "active" default
- Compute trustScore for every entry in data/sources.json
- Backup originals to .bak3 (preserves prior .bak / .bak2 rotation)
Idempotent: re-running on already-migrated data is a no-op.
"""

import json
import os
import re
import shutil
from collections import Counter
from datetime import date, datetime

PROJECT = "D:/GitHub/aicodermap"
TODAY = date.today().isoformat()

VENDOR_PRICING_URL = {
    "Anthropic": "https://platform.claude.com/docs/en/about-claude/pricing",
    "OpenAI": "https://openai.com/api/pricing/",
    "Google DeepMind": "https://ai.google.dev/gemini-api/docs/pricing",
    "Google": "https://ai.google.dev/gemini-api/docs/pricing",
    "Mistral AI": "https://mistral.ai/news",
    "Mistral": "https://mistral.ai/news",
    "DeepSeek": "https://api-docs.deepseek.com/quick_start/pricing",
    "xAI": "https://docs.x.ai/docs/models",
    "Alibaba": "https://qwenlm.github.io/blog/",
    "Alibaba Cloud": "https://qwenlm.github.io/blog/",
    "Moonshot AI": "https://platform.moonshot.cn/",
    "Moonshot": "https://platform.moonshot.cn/",
    "Z.ai": "https://docs.z.ai/",
    "Zhipu": "https://docs.z.ai/",
    "Xiaomi": "https://mimo.xiaomi.com/",
    "MiniMax": "https://platform.minimaxi.com/",
    "Nvidia": "https://build.nvidia.com/",
    "NVIDIA": "https://build.nvidia.com/",
    "Meta": "https://huggingface.co/meta-llama",
    "StepFun": "https://www.stepfun.com/",
    "All Hands AI": "https://www.all-hands.dev/",
}

SUB_RE = re.compile(r"([A-Za-z][\w\s]*?)\s*\$([\d.]+)\s*/\s*(mo|yr|month|year)", re.I)


def vendor_url(provider):
    if not provider:
        return None
    return (
        VENDOR_PRICING_URL.get(provider)
        or VENDOR_PRICING_URL.get(provider.split()[0])
        or None
    )


def parse_subscription(s):
    if not s or not isinstance(s, str):
        return None
    parts = re.split(r"\s*\+\s*|\s*,\s*|\s*/\s*(?=\w+\s*\$)", s)
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        m = SUB_RE.search(p)
        if m:
            tier = m.group(1).strip()
            price = float(m.group(2))
            billing = "monthly" if m.group(3).lower().startswith("mo") else "annual"
            out.append(
                {
                    "tier": tier,
                    "price": price,
                    "currency": "USD",
                    "billing": billing,
                    "notes": None,
                }
            )
        else:
            out.append(
                {
                    "tier": p[:32] or "Unknown",
                    "price": None,
                    "currency": "USD",
                    "billing": "monthly",
                    "notes": p,
                }
            )
    return out if out else None


def compute_range(api_arr):
    if not api_arr:
        return None
    ins = [x.get("in") for x in api_arr if x.get("in") is not None]
    outs = [x.get("out") for x in api_arr if x.get("out") is not None]
    chs = [x.get("cacheHit") for x in api_arr if x.get("cacheHit") is not None]
    return {
        "in": [min(ins), max(ins)] if ins else None,
        "out": [min(outs), max(outs)] if outs else None,
        "cacheHit": [min(chs), max(chs)] if chs else None,
    }


def migrate_model(m):
    changed = False
    if "status" not in m:
        m["status"] = "active"
        changed = True

    p = m.get("pricing")
    if isinstance(p, dict):
        api = p.get("api")
        if isinstance(api, dict):
            entry = {
                "provider": "official",
                "in": api.get("in"),
                "out": api.get("out"),
                "cacheHit": api.get("cacheHit"),
                "throughput": None,
                "url": vendor_url(m.get("provider")),
                "fetched": m.get("lastUpdated"),
            }
            p["api"] = [entry]
            changed = True
        if isinstance(p.get("api"), list):
            p["range"] = compute_range(p["api"])

        sub = p.get("subscription")
        if isinstance(sub, str):
            p["subscription"] = parse_subscription(sub)
            changed = True

    return changed


def recency_decay(d):
    if not d:
        return 0.3
    try:
        dt = datetime.strptime(d, "%Y-%m-%d").date()
        age = (date.today() - dt).days
    except Exception:
        return 0.3
    if age < 30:
        return 1.0
    if age < 90:
        return 0.85
    if age < 180:
        return 0.7
    if age < 365:
        return 0.5
    return 0.3


TIER_W = {"I": 1.0, "S": 0.7, "C": 0.4, "U": 0.1}


def trust_score(entry, verifications=1):
    tier = entry.get("tier") or "S"
    tw = TIER_W.get(tier, 0.7)
    rd = recency_decay(entry.get("date") or entry.get("fetched"))
    v = max(1, min(verifications, 3))
    return round(tw * (v / 3) * rd, 3)


def main():
    models_path = f"{PROJECT}/data/models.json"
    sources_path = f"{PROJECT}/data/sources.json"

    for src in (models_path, sources_path):
        bak3 = src + ".bak3"
        if not os.path.exists(bak3):
            shutil.copy2(src, bak3)
            print(f"backup -> {bak3}")
        else:
            print(f"backup exists, skip: {bak3}")

    with open(models_path, encoding="utf-8") as fp:
        models = json.load(fp)

    n_changed = sum(1 for m in models if migrate_model(m))

    with open(models_path, "w", encoding="utf-8") as fp:
        json.dump(models, fp, indent=2, ensure_ascii=False)
        fp.write("\n")

    print(f"models migrated: {n_changed} / {len(models)}")

    with open(sources_path, encoding="utf-8") as fp:
        sources = json.load(fp)

    n_entries = 0
    for key, entries in sources.items():
        if not isinstance(entries, list):
            continue
        val_counts = Counter(
            json.dumps(e.get("value"), sort_keys=True) for e in entries
        )
        for e in entries:
            v = val_counts[json.dumps(e.get("value"), sort_keys=True)]
            e["trustScore"] = trust_score(e, verifications=v)
            n_entries += 1

    with open(sources_path, "w", encoding="utf-8") as fp:
        json.dump(sources, fp, indent=2, ensure_ascii=False)
        fp.write("\n")

    print(f"sources entries scored: {n_entries}")
    print("DONE")


if __name__ == "__main__":
    main()
