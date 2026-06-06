#!/usr/bin/env python3
"""Add NEW models discovered by this cycle's lineup agent (.aicodermap-lineup.json)
as schema-complete stubs. Bench cells start null (next refresh fills them); metadata
(provider/tier/license/context/pricing/released) traces to the lineup evidence notes.
i18n strengths/weaknesses are written for both TR and EN to keep parity audits green.

Generic: reads newModels[] from the lineup file. Per-model metadata that the lineup
captured in free-text notes is supplied via STUB_META below (each value traceable to
the model's evidenceUrl/notes). Provider display + bench-key set are mirrored from an
existing sibling model so the stub matches the audited schema exactly.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Per-model metadata, every field traceable to the lineup notes/evidenceUrl.
STUB_META = {
    "nemotron-3-ultra": dict(
        provider="Nvidia",
        tier="open-flagship",
        open=True,
        license="OpenMDW-1.1",
        context=None,
        released="2026-06-04",
        api=[],
        tr_s="550B toplam / 55B aktif Hybrid Mamba-Transformer MoE, açık ağırlık (Linux Foundation OpenMDW-1.1). aaIdx=48 ile en güçlü ABD açık-ağırlık modeli. HF + OpenRouter + NVIDIA NIM + AWS SageMaker üzerinde dağıtık.",
        tr_w="Computex 2026'da yeni duyuruldu (4 Haziran 2026); bağımsız benchmark doğrulaması henüz sınırlı. Fiyatlandırma sağlayıcıya göre değişken.",
        en_s="550B total / 55B active Hybrid Mamba-Transformer MoE, open weights (Linux Foundation OpenMDW-1.1). aaIdx=48, strongest US open-weight. Distributed via HF + OpenRouter + NVIDIA NIM + AWS SageMaker.",
        en_w="Just announced at Computex 2026 (June 4 2026); independent benchmark verification still limited. Pricing varies by provider.",
    ),
    "muse-spark": dict(
        provider="Meta",
        tier="frontier",
        open=False,
        license="proprietary",
        context=262144,
        released="2026-04-08",
        api=[],
        tr_s="Meta Superintelligence Labs'ın ilk Muse ailesi modeli; çok-kipli akıl yürütme, 262K bağlam. aaIdx=52. meta.ai üzerinde ücretsiz.",
        tr_w="Meta'nın ilk kapalı-ağırlık modeli; API yalnızca özel önizlemede. Parametre sayısı açıklanmadı; bağımsız benchmark sınırlı.",
        en_s="First model in Meta Superintelligence Labs' Muse family; multimodal reasoning, 262K context. aaIdx=52. Free at meta.ai.",
        en_w="Meta's first closed-weight model; API in private preview only. Parameter count undisclosed; independent benchmarks limited.",
    ),
    "step-3-7-flash": dict(
        provider="StepFun",
        tier="open-flagship",
        open=True,
        license="Apache-2.0",
        context=262144,
        released="2026-05-29",
        api=[
            {
                "provider": "official",
                "in": 0.20,
                "out": 1.15,
                "cacheHit": None,
                "throughput": None,
                "url": "https://www.marktechpost.com/2026/05/29/stepfun-releases-step-3-7-flash-a-198b-moe-vision-language-model-for-coding-agents-and-search-workflows/",
                "fetched": "2026-06-06",
            }
        ],
        tr_s="198B MoE (11B aktif) + 1.8B görüntü kodlayıcı, Apache 2.0, 256K bağlam. Kodlama ajanları ve arama akışları için. $0.20/$1.15 ucuz fiyat. OpenRouter + NVIDIA NIM.",
        tr_w="29 Mayıs 2026'da yeni çıktı; bench hücreleri henüz doldurulmadı (sonraki döngüde gelecek). Bağımsız doğrulama sınırlı.",
        en_s="198B MoE (11B active) + 1.8B vision encoder, Apache 2.0, 256K context. For coding agents and search workflows. Cheap $0.20/$1.15. OpenRouter + NVIDIA NIM.",
        en_w="Released May 29 2026; bench cells not yet filled (next cycle). Independent verification limited.",
    ),
    "glm-5": dict(
        provider="Z.ai (Zhipu AI)",
        tier="open-flagship",
        open=True,
        license="MIT",
        context=200000,
        released="2026-02-11",
        api=[
            {
                "provider": "official",
                "in": 1.0,
                "out": 3.20,
                "cacheHit": None,
                "throughput": None,
                "url": "https://docs.z.ai/guides/llm",
                "fetched": "2026-06-06",
            }
        ],
        tr_s="744B MoE (40B aktif), 200K bağlam, MIT lisans. Z.ai'nin frontier modeli; SWE-Verified ~%77.8, GPQA ~%86, AIME26 ~%92.7 (lineup kaynağı). Halefi glm-5-1 ayrıca takip ediliyor.",
        tr_w="Önceki döngüde atlanmıştı (11 Şubat 2026 çıkışlı); bench hücreleri sonraki tam taramada çok-kaynaklı provenance ile doldurulacak.",
        en_s="744B MoE (40B active), 200K context, MIT license. Z.ai frontier model; SWE-Verified ~77.8%, GPQA ~86%, AIME26 ~92.7% (lineup source). Successor glm-5-1 tracked separately.",
        en_w="Missed in a prior refresh (released Feb 11 2026); bench cells will be filled with multi-source provenance next full sweep.",
    ),
}


def main() -> int:
    lineup = json.loads((REPO / ".aicodermap-lineup.json").read_text(encoding="utf-8"))
    models_path = REPO / "data" / "models.json"
    models = json.loads(models_path.read_text(encoding="utf-8"))
    ms = models["models"] if isinstance(models, dict) else models
    existing = {m["id"] for m in ms}

    # Mirror the exact bench-key set from an audited sibling.
    sibling = next(m for m in ms if m["id"] == "step-3-5-flash")
    bench_keys = list(sibling["bench"].keys())

    tr = json.loads((REPO / "i18n" / "tr.json").read_text(encoding="utf-8"))
    en = json.loads((REPO / "i18n" / "en.json").read_text(encoding="utf-8"))

    added = []
    for nm in lineup.get("newModels", []):
        mid = nm["id"]
        if mid in existing:
            print(f"  skip (already present): {mid}")
            continue
        meta = STUB_META.get(mid)
        if not meta:
            print(f"  skip (no STUB_META): {mid}")
            continue
        api = meta["api"]
        ins = [a["in"] for a in api if a.get("in") is not None]
        outs = [a["out"] for a in api if a.get("out") is not None]
        rng = {
            "in": [min(ins), max(ins)] if ins else None,
            "out": [min(outs), max(outs)] if outs else None,
            "cacheHit": None,
        }
        stub = {
            "id": mid,
            "name": nm["name"],
            "provider": meta["provider"],
            "released": meta["released"],
            "tier": meta["tier"],
            "open": meta["open"],
            "license": meta["license"],
            "context": meta["context"],
            "pricing": {"api": api, "range": rng},
            "bench": {k: None for k in bench_keys},
            "providers": len(api) if api else None,
            "uptime": None,
            "ollamaSize": None,
            "unslothVariants": [],
            "vramRequirement": None,
            "strengthsKey": f"{mid}.strengths",
            "weaknessesKey": f"{mid}.weaknesses",
            "lastUpdated": NOW,
            "status": "active",
        }
        ms.append(stub)
        tr["models"][mid] = {"strengths": meta["tr_s"], "weaknesses": meta["tr_w"]}
        en["models"][mid] = {"strengths": meta["en_s"], "weaknesses": meta["en_w"]}
        added.append(mid)
        print(f"  + stub: {mid} ({meta['provider']}, {meta['tier']})")

    if added:
        models_path.write_text(
            json.dumps(models, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        (REPO / "i18n" / "tr.json").write_text(
            json.dumps(tr, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        (REPO / "i18n" / "en.json").write_text(
            json.dumps(en, ensure_ascii=False, indent=1), encoding="utf-8"
        )
    print(f"=== STUBS === added: {len(added)} {added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
