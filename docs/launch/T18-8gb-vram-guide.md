# Top 5 coding models for 8 GB VRAM developers (T18 · CP2 evergreen)

**Posting target:** post-launch week 1 (CP2) · TR + EN versions · ~ 1500 words each.
**Distribution:** r/LocalLLaMA primary, dev.to long-form, awesome-llm-benchmarks PR mention, TR Twitter thread.
**Linked tracker view:** `https://sungurerdim.github.io/aicodermap/?deployment=local&search=`

---

## EN — Top 5 coding models that actually run on 8 GB VRAM

The "what runs on 8 GB" question dominates r/LocalLLaMA every week. Vendor model cards list 16+ GB VRAM expectations and call it a day; the Unsloth dynamic-quant ecosystem has changed that, but the trade-off matrix lives in 600-comment threads, not in a single page. Here it is.

**Hardware assumed:** an 8 GB consumer card (RTX 3070 / 4060 / 2080 / 6700 XT / Arc A770) or an Apple M-series with ≥ 12 GB unified memory and 0.66 usable ratio. The picks all run in pure GPU; offloading to RAM is noted where the tracker flags it.

### #1 — `qwen25-coder-7b` · UD-IQ4_K_M · ~ 5.4 GB

Coding-tuned 7B from the late-2025 Qwen2.5-Coder series. SWE-bench Verified 68 %, LCB 70 %, Aider-historical 88 %. The Unsloth UD-IQ4_K_M variant is the sweet spot: ~ 5.4 GB on disk, runs in ~ 6.5 GB VRAM with a 32 K context budget. UD-Q5_K_M (6.6 GB on disk) also fits comfortably with shorter contexts.

**Strengths:** Best-in-class coverage of Aider Polyglot among 7Bs (last frozen value, but representative). Fast inference (~ 80 tok/s on RTX 4060). Fill-in-the-Middle support is native — works inside Continue.dev / OpenCode tab-completion mode out of the box.

**Weaknesses:** Long-context recall (MRCR-style) drops sharply past 16 K tokens. No tool-calling fine-tune — agentic columns are essentially zero. Don't try to use it for terminal-bench scenarios.

### #2 — `deepseek-r1-14b` · UD-IQ2_XXS · ~ 4.2 GB

The 14B reasoning-distilled variant of DeepSeek R1. SWE-Verified 56 %, LCB 64 %, GPQA 73 %. UD-IQ2_XXS at ~ 4.2 GB is the only quant that comfortably fits 8 GB with a usable context budget; UD-IQ3_XXS (5.6 GB) needs ~ 7 GB VRAM and can be marginal under heavy KV cache load.

**Strengths:** First open model under 7 GB on disk that gives meaningful chain-of-thought for math + reasoning columns (GPQA 73 % is real). Reasoning-focused preset on the tracker pulls it up to composite 41 — within 12 points of Opus 4.7.

**Weaknesses:** Tokenizer is 1.0–1.35× verbose vs Llama-tokenizer baseline; outputs feel longer per task. The IQ2_XXS quantisation level shows degradation on complex multi-file refactor (vs IQ3_XXS, the difference is ~ 4pp on SWE-Verified).

### #3 — `gemma-4-e4b` · Q4_K_M · ~ 3.0 GB

Google's Gemma 4 edge series (e4b = 4B "edge" parameter count). Built for laptop / mobile inference; the Q4_K_M reference quant is 3 GB on disk. Tracker shows it fitting comfortably even in 6 GB cards.

**Strengths:** Default inference on a single iGPU works. AA Index 15 (low but consistent), LCB 52 %. Fine for "rename this variable across the file", "explain this function", "scaffold a CRUD route" — boilerplate refactor that doesn't need world-model.

**Weaknesses:** No SWE-bench scores published — the tracker shows `–` for sweV / swePro / sweMulti, with the explicit `notApplicableBenchKeys` flag. Treat it as a fast assistant, not a reasoning partner.

### #4 — `qwen25-coder-14b` · UD-IQ2_XXS · ~ 4.4 GB · *with offload*

If you want 14B with the 8 GB constraint, this is the one to try. Tracker labels: **"+ 1 GB RAM offload"** — meaning UD-IQ2_XXS at 4.4 GB on disk needs ~ 9 GB total VRAM under load; the 1 GB shortfall can offload to RAM at ~ 12 % throughput cost.

**Strengths:** Step up from 7B on multi-file context — the model "remembers" the call graph across 3-4 source files better than the 7B sibling. Aider-historical 91 %.

**Weaknesses:** Throughput drops to ~ 32 tok/s on the offload path, vs 70 tok/s pure-GPU on a 16 GB card. If you've never used llama.cpp's offload tuning, the experience can feel choppy on first run; once the layer split is right, it's fine.

### #5 — `codestral-22b` · UD-IQ1_S · ~ 5.2 GB · *with offload, quality trade*

Mistral's coder model. The 22B size officially needs 24 GB; the Unsloth UD-IQ1_S quant pushes it under 6 GB on disk by accepting some quality loss. Tracker shows: **"+ 2 GB RAM offload, IQ1 quality penalty ~ 5pp"** — so SWE-Verified 60 % becomes ~ 55 % at IQ1 vs ~ 65 % at Q4_K_M reference.

**Strengths:** When it works, the 22B base gives noticeably better multi-language coverage than the 14B Qwens — Rust + Go + Kotlin reasoning is closer to frontier-class. The Codestral attention head pattern handles long Python class hierarchies well.

**Weaknesses:** IQ1 occasionally hallucinates on edge syntax (Python walrus, Rust lifetime annotations). Throughput on the offload path is ~ 22 tok/s — usable for "thinking pause" workflows, painful for tab-completion.

---

### What the tracker filters answer for you

- **VRAM filter:** type `8` in the VRAM input → only models with `vramRequirement ≤ 8` (or `≤ 9` with offload) remain visible.
- **Open-only checkbox:** filters out frontier closed models you can't run anyway.
- **Tier dropdown:** "Open Tier-1" gives you the small but flagship-quality set (the Qwens, Codestral, R1 distill); "Local Ollama" gives you the desktop-runner set with Ollama metadata.
- **Pricing baseline:** even if you run local, the tracker can tell you what an OpenRouter spillover costs vs Cursor's $20/mo — useful when you're on a 4 GB card today.

### When to upgrade

The tracker re-renders the moment your VRAM number changes. Punch in `12`, `16`, `24` and watch the suggested quant climb. The structural break-points: **8 GB → 14 GB → 16 GB → 24 GB**. Each break gates a distinct quant tier (Q2 → Q3 → Q4 → Q5/Q8). Below 8 GB you're in 4B territory; above 24 GB you're in MoE territory (Qwen3-235B-A22B at UD-Q4_K_XL fits 32 GB).

> Set your VRAM, the tracker does the rest:
> https://sungurerdim.github.io/aicodermap/?deployment=local

---

## TR — 8 GB VRAM geliştiricileri için gerçekten çalışan 5 kodlama modeli

"8 GB'da ne çalışır?" sorusu r/LocalLLaMA'da her hafta zirvede. Vendor model kartları 16+ GB VRAM bekler ve günü kapatır; Unsloth dinamik-quant ekosistemi bunu değiştirdi ama trade-off matrisi 600-yorumluk başlıklarda yaşıyor, tek sayfada değil. İşte tek sayfa.

**Varsayılan donanım:** 8 GB tüketici kartı (RTX 3070 / 4060 / 2080 / 6700 XT / Arc A770) ya da ≥ 12 GB birleşik bellekli bir Apple M-serisi (0.66 kullanılabilir oran). Seçimlerin tümü saf GPU'da çalışır; RAM'a offload gereken yerlerde takipçi işaretliyor.

### #1 — `qwen25-coder-7b` · UD-IQ4_K_M · ~ 5.4 GB

2025 sonu Qwen2.5-Coder serisinden kodlama-uyarlanmış 7B. SWE-bench Verified 68 %, LCB 70 %, Aider-tarihsel 88 %. Unsloth UD-IQ4_K_M varyantı sweet-spot: diskte ~ 5.4 GB, ~ 6.5 GB VRAM'de 32 K context bütçesi. UD-Q5_K_M (diskte 6.6 GB) kısa context'lerle rahat sığar.

**Güçlü:** 7B sınıfında Aider Polyglot kapsamı en iyisi (son donmuş değer, temsilî). Hızlı inference (~ 80 tok/s RTX 4060'da). Fill-in-the-Middle native — Continue.dev / OpenCode tab-tamamlama modunda kutudan çıkar çıkmaz çalışır.

**Zayıf:** Uzun-context geri çağırma (MRCR tipi) 16 K token üzerinde keskin düşer. Tool-calling fine-tune yok — agentic kolonlar esasen sıfır. Terminal-bench senaryolarında kullanmaya çalışmayın.

### #2 — `deepseek-r1-14b` · UD-IQ2_XXS · ~ 4.2 GB

DeepSeek R1'in 14B reasoning-distill varyantı. SWE-Verified 56 %, LCB 64 %, GPQA 73 %. UD-IQ2_XXS ~ 4.2 GB ile 8 GB'a kullanılabilir context bütçesiyle rahat sığan tek quant; UD-IQ3_XXS (5.6 GB) ~ 7 GB VRAM ister, ağır KV cache yükünde marjinal olabilir.

**Güçlü:** Diskte 7 GB altında matematik + reasoning kolonlarında anlamlı chain-of-thought veren ilk açık model (GPQA 73 % gerçek). Takipçideki reasoning-focused preset kompoziti 41'e — Opus 4.7'ye 12 puan içine çekiyor.

**Zayıf:** Tokenizer Llama-baseline'a göre 1.0–1.35× ayrıntılı; çıktılar görev başına daha uzun hissettirir. IQ2_XXS quantizasyon seviyesi karmaşık çoklu-dosya refaktöründe degradasyon gösterir (IQ3_XXS'e karşı SWE-Verified'da fark ~ 4pp).

### #3 — `gemma-4-e4b` · Q4_K_M · ~ 3.0 GB

Google Gemma 4 edge serisi (e4b = 4B "edge" parametre). Laptop / mobil inference için yapıldı; Q4_K_M referans quant'ı diskte 3 GB. Takipçi 6 GB kartlarda bile rahat sığdığını gösteriyor.

**Güçlü:** Tek iGPU üzerinde varsayılan inference çalışır. AA Index 15 (düşük ama tutarlı), LCB 52 %. "Bu değişkeni dosyada yeniden adlandır", "bu fonksiyonu açıkla", "bir CRUD route iskeletle" — dünya-modeli gerektirmeyen boilerplate refaktör için yeterli.

**Zayıf:** Yayınlanmış SWE-bench skoru yok — takipçide sweV / swePro / sweMulti `–` gösterir, açık `notApplicableBenchKeys` bayrağıyla. Hızlı asistan olarak değerlendir, reasoning ortağı değil.

### #4 — `qwen25-coder-14b` · UD-IQ2_XXS · ~ 4.4 GB · *offload ile*

8 GB kısıtıyla 14B istiyorsan deneyeceğin bu. Takipçi etiketi: **"+ 1 GB RAM offload"** — UD-IQ2_XXS diskte 4.4 GB, yük altında ~ 9 GB toplam VRAM ister; 1 GB eksiklik RAM'a ~ %12 throughput maliyetiyle offload olur.

**Güçlü:** Çoklu-dosya context'inde 7B'den ileri adım — model çağrı grafiğini 3-4 kaynak dosya boyunca 7B kardeşinden daha iyi "hatırlar". Aider-tarihsel 91 %.

**Zayıf:** Offload yolunda throughput ~ 32 tok/s'e düşer; 16 GB kartta saf-GPU 70 tok/s'e karşı. llama.cpp offload tuning yapmadıysan ilk çalıştırmada deneyim takılır; layer-split doğru olunca düzelir.

### #5 — `codestral-22b` · UD-IQ1_S · ~ 5.2 GB · *offload + kalite tradeoff*

Mistral coder modeli. 22B boyut resmi olarak 24 GB ister; Unsloth UD-IQ1_S quant'ı kalite kaybını kabul ederek diskte 6 GB altına indirir. Takipçi gösterir: **"+ 2 GB RAM offload, IQ1 kalite cezası ~ 5pp"** — yani SWE-Verified 60 %, IQ1'de ~ 55 %, Q4_K_M referansta ~ 65 % olur.

**Güçlü:** Çalıştığında 22B taban 14B Qwen'lerden gözle görülür şekilde daha iyi çoklu-dil kapsamı verir — Rust + Go + Kotlin akıl yürütmesi frontier-sınıfa daha yakın. Codestral attention head deseni uzun Python sınıf hiyerarşilerini iyi işler.

**Zayıf:** IQ1 sınır syntax'ta ara sıra halüsinasyon görür (Python walrus, Rust lifetime annotation). Offload yolunda throughput ~ 22 tok/s — "düşünme molası" akışları için kullanılabilir, tab-tamamlama için acı verici.

---

### Takipçi filtrelerinin senin için cevapladığı şey

- **VRAM filtresi:** VRAM girişine `8` yaz → sadece `vramRequirement ≤ 8` olan modeller (offload ile `≤ 9`) kalır.
- **Open-only checkbox:** zaten çalıştıramayacağın frontier kapalı modelleri filtreler.
- **Tier dropdown:** "Open Tier-1" sana küçük ama flagship-kalite seti verir (Qwen'ler, Codestral, R1 distill); "Local Ollama" Ollama metadata'lı desktop-runner setini verir.
- **Pricing baseline:** yerel çalıştırsan bile takipçi OpenRouter taşma maliyetini Cursor'un 20 $/aylık fiyatına karşı söyleyebilir — bugün 4 GB karttaysan faydalı.

### Ne zaman yükseltmeli

Takipçi VRAM sayını değiştirir değiştirmez yeniden render'lar. `12`, `16`, `24` gir ve önerilen quant'ı tırmanırken izle. Yapısal kırılma noktaları: **8 GB → 14 GB → 16 GB → 24 GB**. Her kırılma ayrı bir quant katmanını açar (Q2 → Q3 → Q4 → Q5/Q8). 8 GB altında 4B alanındasın; 24 GB üstünde MoE alanına geçersin (Qwen3-235B-A22B UD-Q4_K_XL ile 32 GB'a sığar).

> VRAM'ini ayarla, takipçi gerisini yapsın:
> https://sungurerdim.github.io/aicodermap/?lang=tr&deployment=local
