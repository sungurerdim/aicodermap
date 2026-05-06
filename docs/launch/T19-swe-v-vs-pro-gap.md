# SWE-bench Verified vs SWE-bench Pro — why a 35-point gap? (T19 · CP3 quarterly)

**Posting target:** quarterly deep-dive · TR + EN versions · ~ 2000 words each.
**Distribution:** HN long-form + dev.to flagship + Latent Space mention pitch + arXiv comment threads.
**Linked tracker view:** any frontier model card with both `sweV` and `swePro` filled.

---

## EN — Why the same model gets 87 % on SWE-V and 64 % on SWE-Pro

If you read the Anthropic Opus 4.7 model card, you see SWE-bench Verified 87.6 %. If you read the Scale SEAL leaderboard, you see SWE-bench Pro 64.3 % — same model, same time window, same task family. The gap is 23.3 percentage points. AICoderMap's tooltip flags it 🚨 (>5pp); the obvious follow-up question is, *which one is real*?

The answer isn't "vendor inflated SWE-V" or "Scale rigged SWE-Pro." It's that **the two benchmarks are testing different things, and the conflation has been hidden by surface-level naming similarity for 18 months.** This piece walks through what each measures, why the gap is structural, and which one matters for your decision.

### The benchmarks side by side

| | SWE-bench Verified | SWE-bench Pro |
|---|---|---|
| Task count | 500 | 1865 |
| Source | curated subset of original SWE-bench (Princeton 2023) | Scale SEAL 2025 expansion |
| Repos | 12 (popular Python OSS) | 41 (multi-language: Python, JS, Go, Rust) |
| Filter | "human-verified that the gold patch is the correct fix" | "broader real-world distribution; gold patches drawn from merged PRs" |
| Contamination control | medium (tasks pre-2023 mostly seen in pretraining) | high (newer cutoff, decontamination pass) |
| Scaffold | community-published; vendor-tunable | standardised by Scale; vendor cannot tune |
| Inflation surface | high (vendor scaffold + best-of-N + retry loops) | low (locked scaffold, single-shot) |

The shape difference is the explanation. **SWE-Verified is a 500-task curated easy mode; SWE-Pro is a 1865-task broad-distribution hard mode.** They were never meant to produce the same number, and the field has been treating them as interchangeable.

### Why vendor SWE-Verified runs hot

Anthropic, OpenAI, DeepSeek, and Qwen all publish their own SWE-Verified scores. Three structural reasons the vendor number is consistently 10-20pp higher than what an independent reproduction lands at:

1. **Scaffold tuning.** Vendor scaffolds run multi-turn, with retry loops, file-search agents, and patch-validate-feedback cycles. Scale SEAL uses one fixed scaffold and reports rank-1 single-shot.
2. **Best-of-N selection.** Anthropic's published 87 % is best-of-5; the rank-1 single-shot lands closer to 78 %.
3. **Contamination.** Half of SWE-Verified's 500 tasks are from repos pre-dating 2023. Models trained through 2026-Q1 have seen many of these patches in some form.

None of this is fraud — it's standard benchmark practice. The mistake is reading 87 % as "this is what the model would do for me, today, on a fresh ticket." That's not what the number is.

### Why SWE-Pro is closer to a workplace metric

SWE-Pro's 1865 tasks span 41 repos, including post-2024 codebases that the model's pretraining hasn't seen. The scaffold is locked: a single agent with read / write / run-test tool access, no retry, no best-of-N selection. The model gets exactly what a developer using Claude Code would get — one shot, fixed budget, real-world repo.

Scale SEAL also runs the same scaffold across all submissions, so cross-model comparison stays apples-to-apples. The 64.3 % Opus 4.7 score is on the same scaffold as the 41.8 % GPT-5.4 score — the gap there is real model capability, not scaffold variance.

### Where the gap hides decisions

Three places where reading SWE-V instead of SWE-Pro will mislead you:

1. **Picking between Opus 4.7 (sweV 87, swePro 64) and DeepSeek V4 Pro (sweV 78, swePro 67).** SWE-V says Opus wins by 9pp; SWE-Pro says V4 Pro wins by 3pp. For real-world repo work, V4 Pro is the better pick — at one-tenth the cost.
2. **Evaluating "is this open model competitive."** Qwen3.6-27B's vendor-internal SWE-V is 71 %; on SWE-Pro it's 51 %. The vendor number suggests "frontier-class"; the independent number says "mid-pack". The truth is closer to mid-pack for hard real-world work, but excellent for boilerplate refactor.
3. **Ranking the cheap providers.** Together, Fireworks, Groq, OpenRouter all serve roughly the same models. SWE-V doesn't differentiate inference quality (it's a model-level number). SWE-Pro is also model-level, but pricing × SWE-Pro is the cost-per-PR formula that actually matters for high-volume coding workflows.

### How AICoderMap surfaces this

The tracker keeps both numbers, in two columns. The default weights weight SWE-Pro at 16 % and SWE-V at 9 % — the editorial position is that SWE-Pro is the more honest signal for the "what will this model do for me" question. The contradiction tooltip flashes 🚨 the moment the gap is over 5pp; clicking the cell opens a per-source breakdown with tier (S = self-reported, I = independent, C = community), trustScore, and recency.

You can re-weight the composite score yourself. **Drag SWE-V up to 25 %; the rankings shift toward vendor-favouring scores. Drag SWE-Pro to 25 %; the rankings shift toward independent-evaluator-favouring scores.** Either is defensible; the point is that you decide consciously.

### What independent extraction means in practice

For every SWE-Pro number on the tracker, the source is one of:
- **Scale SEAL leaderboard** — primary, locked-scaffold rank-1.
- **Vellum LLM Leaderboard** — independent reproduction, secondary.
- **BenchLM** — independent verified-vs-provisional split, tertiary.

Vendor self-reports are **kept** in `data/sources.json` (visible in the tooltip) but **not used** as the canonical value when an independent number exists. That rule — "I-tier outweighs S-tier in trustScore × recency × min(verifications, 3)/3" — is the compound moat D commitment.

### What this means for your stack today

For closed-frontier picks, the SWE-Pro signal is mature enough across Anthropic / OpenAI / Google / DeepSeek to drive decisions. For open-flagship picks (Qwen3, Llama 4, Mistral Large 3), the I-tier coverage is still patchy — Qwen and Meta don't submit. The tracker shows this honestly: where I-tier is missing, the cell carries the S-tier value with a "single-source" warning, not a confidence we don't have.

For local picks (Unsloth-quantised), no I-tier publishes quantised-model numbers — the tracker uses the float16 reference value with a "quant degradation factor" estimate. That's a known approximation; community runs and the BenchLM provisional set are the available proxies.

### The 14-day discipline

Aider Polyglot's leaderboard hasn't refreshed since November 2025 — five months of dead data still being cited in 2026. AICoderMap's M5 metric is ≤ 14 days max gap; the longest gap to date has been 6 days. When a new frontier model lands, the SWE-V / SWE-Pro split for it shows up here within two weeks, and the contradiction (when there is one) shows up at the same time.

> Open the tracker, look at any frontier card, click the swePro cell, see every source.
> https://sungurerdim.github.io/aicodermap/

---

## TR — Aynı model neden SWE-V'da 87 % ve SWE-Pro'da 64 % alıyor?

Anthropic Opus 4.7 model kartını okuduğunuzda SWE-bench Verified 87.6 % görürsünüz. Scale SEAL liderlik tablosunu okuduğunuzda SWE-bench Pro 64.3 % görürsünüz — aynı model, aynı zaman aralığı, aynı görev ailesi. Fark 23.3 puan. AICoderMap'in ipucu 🚨 işaretini gösterir (>5pp); apaçık takip sorusu, *hangisi gerçek*?

Cevap "vendor SWE-V'yi şişirdi" ya da "Scale SEAL SWE-Pro'yu hileyle hazırladı" değil. Cevap **iki benchmark'ın farklı şeyleri ölçmesi ve isim benzerliği nedeniyle 18 aydır birleştirilmiş olmaları.** Bu yazı her birinin ne ölçtüğünü, farkın neden yapısal olduğunu ve karar vermek için hangisinin önemli olduğunu açıklıyor.

### Yan yana benchmark'lar

| | SWE-bench Verified | SWE-bench Pro |
|---|---|---|
| Görev sayısı | 500 | 1865 |
| Kaynak | orijinal SWE-bench'in seçilmiş alt kümesi (Princeton 2023) | Scale SEAL 2025 genişletmesi |
| Repolar | 12 (popüler Python OSS) | 41 (çok-dilli: Python, JS, Go, Rust) |
| Filtre | "altın patch'in doğru çözüm olduğu insan tarafından doğrulanmış" | "daha geniş gerçek-dünya dağılımı; altın patch'ler birleşmiş PR'lardan" |
| Kontaminasyon kontrolü | orta (görevlerin çoğu 2023 öncesi pretraining'de görülmüş) | yüksek (daha yeni cutoff, dekontaminasyon geçişi) |
| Scaffold | topluluk-yayımlı; vendor-ayarlanabilir | Scale tarafından standardize; vendor ayarlayamaz |
| Şişirme yüzeyi | yüksek (vendor scaffold + best-of-N + retry döngüleri) | düşük (kilitli scaffold, tek-atış) |

Şekil farkı açıklamadır. **SWE-Verified 500-görevlik seçilmiş kolay mod; SWE-Pro 1865-görevlik geniş-dağılım zor mod.** Aynı sayıyı üretmeleri hiç amaçlanmadı, alan bunları yer-değiştirebilir gibi muamele etti.

### Vendor SWE-Verified neden sıcak çalışır

Anthropic, OpenAI, DeepSeek ve Qwen kendi SWE-Verified skorlarını yayınlar. Vendor sayısının bağımsız reprodüksiyondan tutarlı olarak 10-20pp yüksek olmasının üç yapısal nedeni:

1. **Scaffold ayarı.** Vendor scaffold'ları multi-turn, retry döngüleri, dosya-arama agent'ları, ve patch-doğrula-geri-bildirim döngüleriyle çalışır. Scale SEAL tek sabit scaffold kullanır ve rank-1 tek-atış raporlar.
2. **Best-of-N seçimi.** Anthropic'in 87 %'si best-of-5; rank-1 tek-atış 78 %'e yakın.
3. **Kontaminasyon.** SWE-Verified'ın 500 görevinin yarısı 2023 öncesi repolardan. 2026-Q1'e kadar eğitilmiş modeller bu patch'lerin çoğunu bir biçimde görmüş.

Bunların hiçbiri sahtecilik değil — standart benchmark pratiği. Hata 87 %'yi "model bugün, taze ticket'ta benim için bunu yapardı" olarak okumak. Sayı bu değil.

### SWE-Pro neden işyeri metriğine daha yakın

SWE-Pro'nun 1865 görevi 41 repoyu kapsar, modelin pretraining'inin görmediği 2024-sonrası kod tabanları dahil. Scaffold kilitli: tek agent, read / write / run-test araç erişimiyle, retry yok, best-of-N seçim yok. Model bir geliştiricinin Claude Code kullanarak alacağıyla aynı şeyi alır — bir atış, sabit bütçe, gerçek-dünya repo.

Scale SEAL ayrıca aynı scaffold'u tüm gönderimlere uygular, çapraz-model karşılaştırma elma-elma kalır. Opus 4.7 64.3 % skoru GPT-5.4 41.8 % skoruyla aynı scaffold'da — oradaki fark gerçek model yeteneği, scaffold varyansı değil.

### Farkın kararları gizlediği yerler

SWE-V'yi SWE-Pro yerine okumanın seni yanılttığı üç yer:

1. **Opus 4.7 (sweV 87, swePro 64) ile DeepSeek V4 Pro (sweV 78, swePro 67) arasında seçim.** SWE-V Opus'un 9pp önde olduğunu söyler; SWE-Pro V4 Pro'nun 3pp önde olduğunu söyler. Gerçek-dünya repo işi için V4 Pro daha iyi seçim — onda bir maliyetle.
2. **"Bu açık model rekabetçi mi" değerlendirmesi.** Qwen3.6-27B'nin vendor-iç SWE-V'si 71 %; SWE-Pro'da 51 %. Vendor sayısı "frontier-sınıf" izlenimi verir; bağımsız sayı "orta-pack" der. Gerçek zor gerçek-dünya işi için orta-pack'e yakın, ama boilerplate refaktör için mükemmel.
3. **Ucuz sağlayıcıları sıralama.** Together, Fireworks, Groq, OpenRouter aşağı yukarı aynı modelleri sunar. SWE-V inference kalitesini ayırt etmez (model-seviye sayı). SWE-Pro da model-seviye, ama fiyat × SWE-Pro yüksek-hacimli kodlama akışları için aslında önemli olan PR-başı maliyet formülüdür.

### AICoderMap bunu nasıl yüzeye çıkarıyor

Takipçi her iki sayıyı da iki kolonda tutar. Varsayılan ağırlıklar SWE-Pro'yu %16, SWE-V'yi %9 olarak ağırlıklandırır — editöryal pozisyon SWE-Pro'nun "bu model benim için ne yapacak" sorusuna daha dürüst sinyal olduğu yönünde. Çelişki ipucu fark 5pp'i geçer geçmez 🚨 yanıp söner; hücreye tıklamak tier (S = self-reported, I = independent, C = community), trustScore ve recency içeren kaynak kırılımını açar.

Kompozit skoru kendi yeniden ağırlıklandırabilirsin. **SWE-V'yi %25'e çek; sıralamalar vendor-yanlısı skorlara doğru kayar. SWE-Pro'yu %25'e çek; sıralamalar bağımsız-değerlendirici-yanlısı skorlara doğru kayar.** Her ikisi de savunulabilir; nokta bilinçli karar vermendir.

### Bağımsız çıkarım pratikte ne demek

Takipçideki her SWE-Pro sayısı için kaynak şunlardan biri:
- **Scale SEAL leaderboard** — birincil, kilitli-scaffold rank-1.
- **Vellum LLM Leaderboard** — bağımsız reprodüksiyon, ikincil.
- **BenchLM** — bağımsız doğrulanmış-ve-provisional ayrımı, üçüncül.

Vendor self-report'ları `data/sources.json`'da **tutulur** (ipucunda görünür) ama bağımsız sayı varsa kanonik değer olarak **kullanılmaz**. Bu kural — "I-tier trustScore × recency × min(verifications, 3)/3'te S-tier'ı yener" — bileşik moat D taahhüdüdür.

### Bunun bugün senin yığının için anlamı

Kapalı-frontier seçimleri için SWE-Pro sinyali Anthropic / OpenAI / Google / DeepSeek arasında karar vermeye yetecek olgunlukta. Open-flagship seçimleri için (Qwen3, Llama 4, Mistral Large 3) I-tier kapsamı hâlâ delik delik — Qwen ve Meta göndermez. Takipçi bunu dürüstçe gösterir: I-tier eksikse hücre S-tier değeri taşır ve "tek-kaynak" uyarısı, sahip olmadığımız bir güven değil.

Yerel seçimler için (Unsloth-quantize), hiçbir I-tier quantize-model sayısı yayınlamaz — takipçi float16 referans değerini "quant degradasyon faktörü" tahminiyle kullanır. Bu bilinen yaklaşımdır; topluluk run'ları ve BenchLM provisional seti mevcut proxy'lerdir.

### 14-gün disiplini

Aider Polyglot leaderboard'u Kasım 2025'ten beri tazelenmedi — beş ay ölü veri 2026'da hâlâ alıntılanıyor. AICoderMap'in M5 metriği ≤ 14 gün max boşluk; bugüne kadar en uzun boşluk 6 gün oldu. Yeni bir frontier model çıktığında onun için SWE-V / SWE-Pro ayrımı iki hafta içinde burada gelir, ve çelişki (varsa) aynı anda gelir.

> Takipçiyi aç, herhangi bir frontier kartına bak, swePro hücresine tıkla, her kaynağı gör.
> https://sungurerdim.github.io/aicodermap/?lang=tr
