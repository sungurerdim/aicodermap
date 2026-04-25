# Coding Models Tracker

> Compare AI coding models with coding-focused benchmarks weighted your way — cross-verified, contradiction-flagged, in Turkish and English.

---

## Problem

Coding LLM pazarı son 3 ayda **2 haftada bir yeni frontier model** çıkarıyor (Opus 4.7 → Kimi K2.6 → Qwen3.6-27B → DeepSeek V4). Manuel research yetişemiyor; mevcut karşılaştırma siteleri ya İngilizce-only (artificialanalysis.ai, llm-stats, BenchLM) ya da güncel değil (**Aider leaderboard 5 ay stale**).

5 doğrulanmış pazar boşluğu:
1. **Türkçe coverage SIFIR** — hiçbir TR developer-facing tracker yok
2. Opinionated VRAM-tier verdict ("X için bu model") yok
3. Aider 5 ay stale (Kasım 2025'ten beri)
4. Subscription + local TCO + API pricing **unified view** yok
5. **Cross-source contradiction flagging** yok (SWE-V 80% vs Pro 46% aynı model — hiçbir tracker göstermiyor)

---

## Solution

**Living document** olarak coding LLM tracker:
- **TR + EN i18n** — hiçbir rakipte yok
- **User-editable composite weights** — "bizim default'umuz, sen değiştir" şeffaflığı (slider + presets: SWE-odaklı / Agentic-odaklı / Balanced / Benchmark-only)
- **Cross-source contradiction flagging** — 2+ kaynak arası >3pp fark görünür ⚠ + tooltip source breakdown
- **GPU VRAM detection + filter** — sadece GPU'nuza sığan modelleri gösterir (WebGPU auto + manuel fallback, Unsloth UD variants priority)
- **PNG export** — section veya tam sayfa, paylaşılabilir görsel artefakt
- **Manuel update disiplini** — solo dev, M5 metric ≤14 gün max aralık (anti-Aider-stale)

---

## Users

3 eşit önemli persona:
- **P1** Sungur — kişisel günlük model seçim referansı (Claude Code, OpenCode kararları)
- **P2** TR developer community — 25-45 yaş, Claude Code/Cursor/Copilot kullananlar (Twitter/HN-TR/Eksisozluk aktif, ~150K aktif TR dev)
- **P3** Global EN developer community — r/LocalLLaMA (694K), HN, opinion-driven verdict + karma kapalı/açık + lokal coverage arayan

---

## Why Now

4 faktör birleşimi:
- **Pazar momentum** — 2 haftada bir frontier release, manuel research yetersiz
- **Teknik hazırlık** — BrainLedger + ledger-research-agent mimarisi olgun (template clone hazır)
- **v0 hazır** — 35 model × 14 benchmark HTML raporu manuel olarak bitti, sadece otomasyona alma kaldı
- **Skill ekosistem ivmesi** — Claude Code skill ekosistemi yeni; ilk kapsamlı domain-research skill'lerinden biri

---

## MVP

5 hafta solo part-time × 30-35 saat. **Tek external service: GitHub Pages, $0/ay sürekli.**

13 must-have feature:
1. Skill + research agent (manuel trigger)
2. JS data array auto-regeneration
3. i18n TR/EN content + language switch
4. GitHub Pages deploy
5. GitHub Insights traffic ölçümü
6. Diff/changelog otomasyonu
7. Cross-source validation (≥2 kaynak)
8. README + skill installation guide
9. **Dynamic weights editor UI + presets**
10. **Screenshot/PNG export** (section + full page)
11. 3-breakpoint responsive design (mobile/tablet/desktop)
12. **Contradiction flagging** (SWE-V vs Pro vb)
13. **GPU VRAM detection + Unsloth UD priority + filter**

5 milestone: Foundation → Core → Integration → Polish → Launch.

**Launch:** Simultane TR + Global soft launch, 10-15 channel intro (AI LAB Discord 40K, YazılımaOrg 59K, Patika 200K, Eksisozluk başlık entry, key TR Twitter, HN Show, r/LocalLLaMA Show, simonw blog mention, BenchGecko PR), 2 hafta post-launch validation checkpoint (GO/PIVOT/LITE).

---

## 6 Ay Hedef

| Metric | Hedef |
|--------|-------|
| Trafik | ≥500 unique/ay |
| GitHub stars | ≥100 |
| Organic mentions | ≥1 TR + ≥1 global |
| Veri güvenilirliği | ≥%95 cross-source validation |
| Update cadence | ≤14 gün max aralık |
| Reusability | ≥1 başka domain'e clone (mobile app benchmark vs.) |

---

## License

**MIT** — kod ve veri public. Ücretsiz, monetization yok, sponsorship yok (bias-free editorial integrity).

---

🔗 **Repo:** github.com/sungurerdim/coding-models-tracker (yakında)
🔗 **Live:** sungurerdim.github.io/coding-models-tracker (yakında)
✉️ **Sungur Erdim** · sungurerdim@gmail.com
