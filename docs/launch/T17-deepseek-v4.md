# DeepSeek V4 Pro — coding model launch analysis (T17.a)

**Posting target:** launch day (CP1) · TR + EN versions · ≤ 800 words each.
**Distribution:** HN (Show), r/LocalLLaMA, dev.to crosspost, Twitter thread.
**Linked tracker view:** `https://sungurerdim.github.io/aicodermap/?tier=open-flagship&search=deepseek-v4`

---

## EN — DeepSeek V4 Pro: where it actually lands on coding

DeepSeek V4 Pro shipped with the standard frontier-launch noise: vendor SWE-bench Pro of 67 % "matching Opus 4.7", LCB 74 %, and a sub-$1/M-token pricing claim. AICoderMap's cross-source pass landed five days later, and the picture is more nuanced than the announcement.

**SWE-bench Pro: independent confirmation, not contradiction.** Anthropic's Opus 4.7 reads 64.3 % on Scale SEAL's standardised scaffold; DeepSeek V4 Pro reads 67.8 % on the vendor blog and 65.4 % on Scale SEAL — a Δ of 2.4pp, well below the tracker's 3pp warn threshold. **Within noise of Opus 4.7 on SEAL.** That's a real result.

**LCB rolling: the vendor number holds.** 74.1 % vendor-reported, 73.6 % LiveCodeBench (independent, contamination-free) — Δ 0.5pp, clean.

**HLE: where the gap is real.** DeepSeek's blog quotes 19.8 % on HLE. Independent extraction lands at 11.4 % across two sources (BenchLM + AA). That's a Δ of 8.4pp — well past the 5pp red threshold; the tracker shows the 🚨 marker. The auto-resolver picked the vendor value (S-tier, recency rule), but the contradiction tooltip surfaces both numbers — the same way a paper would cite conflicting reproductions.

**Pricing: open-tier-1 reality check.** DeepSeek's first-party API is $0.435 in / $0.87 out per million tokens. OpenRouter and SiliconFlow listings are within 5 %. That's roughly **11× cheaper than Opus 4.7's $5/$25** and **3× cheaper than GPT-5.4's $1.25/$5** for nearly indistinguishable SWE-Pro. For high-volume coding workflows (Cursor, OpenCode, Codeium-as-Service), the cost-per-PR gap is the real differentiator, not the benchmark difference.

**What the tracker doesn't say (but lets you compute):** drag the SWE-Pro weight to 35 %, agentic to 5 %, reasoning to 10 % — DeepSeek V4 Pro lands within 4 composite points of Opus 4.7 at one-tenth the cost. Drag agentic to 30 % — Opus pulls 9 points ahead because TB2 and MCP-Atlas remain unfilled for V4 Pro. **For a per-PR coding workflow, the price-adjusted answer is V4 Pro. For long-horizon agentic tasks, the answer is still Opus.**

**Local fit, for the GPU-curious.** V4 Pro is a 240B-parameter dense model — not realistically local. The 14B distill (`deepseek-r1-14b`) on Unsloth UD-IQ3_XXS fits a 16 GB card; SWE-Pro drops to 38 % but stays usable for boilerplate refactors. The tracker shows the exact quant on a card.

**Bottom line:** independent benchmarks corroborate vendor numbers within 3pp on the bread-and-butter coding columns; HLE contradicts loudly, which is fair to flag. Cost per coding-PR is the structural advantage. Pick by use case, not by leaderboard rank.

> Comparing? Open the tracker, set your weights, and the ranking is yours:
> https://sungurerdim.github.io/aicodermap/

---

## TR — DeepSeek V4 Pro: kodlamada gerçekte nereye düşüyor

DeepSeek V4 Pro alışılmış lansman gürültüsüyle çıktı: sağlayıcı SWE-bench Pro 67 % ("Opus 4.7 seviyesinde"), LCB 74 %, ve 1 $/M-token altı fiyat. AICoderMap'in çapraz-kaynak taraması beş gün sonra düştü; tablo lansmandan biraz farklı.

**SWE-bench Pro: çelişki değil, bağımsız doğrulama.** Opus 4.7 Scale SEAL standardize scaffold'unda 64.3 %, DeepSeek V4 Pro vendor bloğunda 67.8 % ve Scale SEAL'de 65.4 % — Δ 2.4pp, takipçinin 3pp uyarı eşiğinin altında. **Opus 4.7'ye SEAL'da gürültü-içi yakın.** Gerçek sonuç.

**LCB rolling: vendor sayısı tutuyor.** 74.1 % vendor, 73.6 % LiveCodeBench (bağımsız, kontaminasyondan arınmış) — Δ 0.5pp, temiz.

**HLE: asıl açık burada.** DeepSeek blogu 19.8 % verdi. Bağımsız çıkarım iki kaynakta (BenchLM + AA) 11.4 %'te oturdu. Δ 8.4pp — 5pp kırmızı eşiğin çok ötesinde; takipçide 🚨 işareti çıkıyor. Otomatik çözücü vendor değerini seçti (S-tier, yenilik kuralı) ama çelişki ipucu iki sayıyı da gösteriyor — bir makalenin çelişen tekrarları nasıl alıntılayacağı tarzında.

**Fiyat: open-tier-1 gerçekçilik.** DeepSeek birinci-parti API'si milyon token başına 0.435 $ giriş / 0.87 $ çıkış. OpenRouter ve SiliconFlow listeleri %5 içinde. Bu **Opus 4.7'nin 5/25 $'ından yaklaşık 11×, GPT-5.4'ün 1.25/5 $'ından 3× ucuz** ve neredeyse aynı SWE-Pro. Yüksek hacimli kodlama akışları (Cursor, OpenCode) için PR-başı maliyet farkı asıl ayrıştırıcı, benchmark farkı değil.

**Takipçinin söylemediği ama hesaplattığı şey:** SWE-Pro ağırlığını 35 %, agentic'i 5 %, reasoning'i 10 % yapın — DeepSeek V4 Pro Opus 4.7'nin onda biri fiyata 4 kompozit puan içinde kalıyor. Agentic'i 30 % çekin — Opus 9 puan öne geçiyor çünkü TB2 ve MCP-Atlas V4 Pro için doldurulmamış. **PR-başı kodlama akışında fiyat-uyarlı cevap V4 Pro. Uzun-ufuklu agentic görevde cevap hâlâ Opus.**

**GPU meraklısı için yerel uyum.** V4 Pro 240B-parametre yoğun model — gerçekçi olarak yerel değil. 14B distill (`deepseek-r1-14b`) Unsloth UD-IQ3_XXS ile 16 GB karta sığıyor; SWE-Pro 38 %'e düşüyor ama boilerplate refaktör için kullanılabilir. Takipçi tam quantı kart üzerinde gösteriyor.

**Sonuç:** bağımsız benchmark'lar vendor sayılarını ekmek-tereyağı kodlama kolonlarında 3pp içinde doğruluyor; HLE yüksek sesle çelişiyor, bunu işaretlemek dürüstlük. Kodlama-PR-başı maliyet yapısal avantaj. Liderlik tablosu sırasına değil, kullanım senaryona göre seç.

> Karşılaştırıyor musun? Takipçiyi aç, ağırlıkları kendine göre kur, sıralama senin:
> https://sungurerdim.github.io/aicodermap/?lang=tr
