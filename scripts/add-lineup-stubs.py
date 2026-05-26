#!/usr/bin/env python3
"""One-shot: add 5 lineup-stub models discovered from the 2026-05-06 user-supplied
lineup table (GLM-4.5 Air, GLM-4.7, Mistral Medium 3.5, Qwen3.5 9B, MiniMax M2.1).

Stubs carry no bench data; the next /aicodermap refresh cycle fills them.
i18n strengths/weaknesses populated for both TR and EN to keep parity audits green.
"""

import json
from datetime import date

PROJECT_ROOT = __file__.rsplit("/", 2)[0] if "/" in __file__ else ".."
TODAY = date.today().isoformat()

ALL_BENCH_KEYS = [
    "aaIdx",
    "swePro",
    "sweV",
    "sweMulti",
    "nl2Repo",
    "lcb",
    "tb2",
    "tbHard",
    "tau2",
    "tau3",
    "mcpA",
    "bfcl",
    "aaCoding",
    "aaAgentic",
    "browseComp",
    "cfElo",
    "webDevElo",
    "gpqa",
    "aime26",
    "hle",
    "aaOmni",
    "mmluPro",
    "simpleQa",
    "mrcr",
    "arcAgi2",
]

STUBS = [
    {
        "id": "glm-4-5-air",
        "name": "GLM-4.5 Air",
        "provider": "Z.ai (Zhipu AI)",
        "tier": "open-flagship",
        "open": True,
        "license": "MIT",
        "context": 128000,
        "vramRequirement": 24,
        "pricing_in": None,
        "pricing_out": None,
        "pricing_url": "https://z.ai/models",
        "strengths_en": "MoE with 12B active parameters; balanced cost-vs-capability for self-host; MIT-licensed.",
        "strengths_tr": "12B aktif parametreli MoE; self-host icin maliyet-yetenek dengesi iyi; MIT lisansli.",
        "weaknesses_en": "Bench coverage pending; agentic columns largely untested at publish time.",
        "weaknesses_tr": "Bench kapsami bekliyor; yayin aninda agentic kolonlar buyuk olcude test edilmemis.",
    },
    {
        "id": "glm-4-7",
        "name": "GLM-4.7",
        "provider": "Z.ai (Zhipu AI)",
        "tier": "open-flagship",
        "open": True,
        "license": "MIT",
        "context": 200000,
        "vramRequirement": 40,
        "pricing_in": None,
        "pricing_out": None,
        "pricing_url": "https://z.ai/models",
        "strengths_en": "Open-weight coding leader within the GLM series; targets frontier-class SWE behavior under MIT.",
        "strengths_tr": "GLM serisinde acik-agirlikli kodlama lideri; MIT altinda frontier-sinifi SWE davranisi hedefler.",
        "weaknesses_en": "Requires 40GB+ VRAM at usable quants; not realistic for consumer GPUs.",
        "weaknesses_tr": "Kullanilabilir quantlarda 40GB+ VRAM ister; tuketici GPU icin gercekci degil.",
    },
    {
        "id": "mistral-medium-3-5",
        "name": "Mistral Medium 3.5",
        "provider": "Mistral AI",
        "tier": "frontier",
        "open": False,
        "license": "Modified MIT (Mistral Research)",
        "context": 128000,
        "vramRequirement": None,
        "pricing_in": 1.50,
        "pricing_out": 7.50,
        "pricing_url": "https://docs.mistral.ai/getting-started/models/models_overview/",
        "strengths_en": "Mid-tier Mistral with strong European-language support and predictable pricing.",
        "strengths_tr": "Avrupa dilleri destegi guclu, fiyati ongorulebilir orta-seviye Mistral modeli.",
        "weaknesses_en": "Modified-MIT licensing restricts commercial redistribution; cloud-only.",
        "weaknesses_tr": "Modified-MIT lisansi ticari yeniden dagitimi kisitlar; yalnizca cloud.",
    },
    {
        "id": "qwen3-5-9b",
        "name": "Qwen3.5 9B",
        "provider": "Alibaba Qwen",
        "tier": "open-flagship",
        "open": True,
        "license": "Apache 2.0",
        "context": 128000,
        "vramRequirement": 6,
        "pricing_in": None,
        "pricing_out": None,
        "pricing_url": "https://qwen-lm.github.io/",
        "strengths_en": "Compact 9B Qwen suitable for 6-8GB consumer GPUs; Apache 2.0 unrestricted.",
        "strengths_tr": "6-8GB tuketici GPU icin uygun kompakt 9B Qwen; Apache 2.0 kisitsiz.",
        "weaknesses_en": "Smaller capacity than 27B/35B siblings on multi-file refactor; agentic gaps expected.",
        "weaknesses_tr": "Coklu-dosya refaktorde 27B/35B kardeslerinden daha dusuk kapasite; agentic bosluklar bekleniyor.",
    },
    {
        "id": "minimax-m2-1",
        "name": "MiniMax M2.1",
        "provider": "MiniMax",
        "tier": "open-flagship",
        "open": True,
        "license": "MiniMax Open Source License",
        "context": 1000000,
        "vramRequirement": None,
        "pricing_in": 0.30,
        "pricing_out": 1.20,
        "pricing_url": "https://platform.minimaxi.com/",
        "strengths_en": "1M-token context window at sub-$1/M tokens; useful for long-document and multi-file context tasks.",
        "strengths_tr": "Token basina 1$ altinda 1M-token baglam penceresi; uzun-dokuman ve coklu-dosya gorevleri icin faydali.",
        "weaknesses_en": "Local execution is impractical at full precision; cloud-first deployment.",
        "weaknesses_tr": "Tam hassasiyette yerel calistirma pratik degil; cloud-oncelikli dagitim.",
    },
]


def build_model(s):
    api_entry = {
        "provider": "official",
        "in": s["pricing_in"],
        "out": s["pricing_out"],
        "cacheHit": None,
        "throughput": None,
        "url": s["pricing_url"],
        "fetched": TODAY,
    }
    range_in = (
        [s["pricing_in"], s["pricing_in"]]
        if s["pricing_in"] is not None
        else [None, None]
    )
    range_out = (
        [s["pricing_out"], s["pricing_out"]]
        if s["pricing_out"] is not None
        else [None, None]
    )
    return {
        "id": s["id"],
        "name": s["name"],
        "provider": s["provider"],
        "released": None,
        "tier": s["tier"],
        "open": s["open"],
        "license": s["license"],
        "context": s["context"],
        "pricing": {
            "api": [api_entry],
            "subscription": None,
            "range": {"in": range_in, "out": range_out, "cacheHit": [None, None]},
        },
        "bench": {k: None for k in ALL_BENCH_KEYS},
        "benchUpdated": {},
        "benchQuarantine": {},
        "providers": None,
        "uptime": None,
        "ollamaSize": None,
        "ollama": None,
        "unslothVariants": None,
        "vramRequirement": s["vramRequirement"],
        "strengthsKey": s["id"] + ".strengths",
        "weaknessesKey": s["id"] + ".weaknesses",
        "lastUpdated": TODAY,
        "status": "active",
        "_stubReason": "lineup-discovery placeholder; bench cells pending next /aicodermap refresh cycle",
        "_stubAddedDate": TODAY,
        "_stubSource": "user-supplied lineup table 2026-05-06",
    }


def main():
    with open("data/models.json", encoding="utf-8") as f:
        models = json.load(f)
    existing = {m["id"] for m in models}
    added = []
    for s in STUBS:
        if s["id"] in existing:
            print("SKIP (already exists): " + s["id"])
            continue
        models.append(build_model(s))
        added.append(s)
    with open("data/models.json", "w", encoding="utf-8") as f:
        json.dump(models, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Added " + str(len(added)) + " models:")
    for s in added:
        print("  + " + s["id"].ljust(22) + " (" + s["name"] + ")")
    # i18n
    for lang_path, key in [("i18n/tr.json", "tr"), ("i18n/en.json", "en")]:
        with open(lang_path, encoding="utf-8") as f:
            d = json.load(f)
        d.setdefault("models", {})
        suffix = "_" + key
        for s in added:
            d["models"][s["id"] + ".strengths"] = s["strengths" + suffix]
            d["models"][s["id"] + ".weaknesses"] = s["weaknesses" + suffix]
        with open(lang_path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("updated " + lang_path)
    # parity check
    with open("i18n/tr.json", encoding="utf-8") as f:
        tr = json.load(f)
    with open("i18n/en.json", encoding="utf-8") as f:
        en = json.load(f)

    def flat(d, p=""):
        out = []
        for k, v in d.items():
            kk = (p + "." + k) if p else k
            if isinstance(v, dict):
                out.extend(flat(v, kk))
            else:
                out.append(kk)
        return out

    tk = set(flat(tr))
    ek = set(flat(en))
    print(
        "\ni18n parity TR="
        + str(len(tk))
        + " EN="
        + str(len(ek))
        + " drift_TR="
        + str(len(tk - ek))
        + " drift_EN="
        + str(len(ek - tk))
    )


if __name__ == "__main__":
    main()
