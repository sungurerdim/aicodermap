# Coding Models Tracker — Product Requirements Document

**Sürüm:** 1.0 (24 Nisan 2026)
**Sahip:** Sungur Erdim
**Durum:** Specification + Planning tamamlandı, Implementation öncesi
**Lisans:** MIT

---

## 1. Yönetici Özeti

Manuel olarak derlenmiş coding LLM karşılaştırma raporu (35 model × 14 benchmark) iki haftada bir eskiyor. Coding LLM pazarı son 3 ayda her 2 haftada bir yeni frontier model çıkardı (Opus 4.7 → Kimi K2.6 → Qwen3.6-27B → DeepSeek V4); manuel research bu tempoya yetişemiyor.

**Coding Models Tracker**, dört katmanlı bir ihtiyacı tek bir living document'ta çözer:
1. Kişisel günlük model seçim kararları için her zaman güncel referans
2. Developer community (TR + global EN) için açık-erişimli karşılaştırma boşluğunu doldurma
3. Tekrar kullanılabilir research-skill + agent kalıbı (başka domain'lere de uygulanabilir)
4. Snapshot değil "living document" — son güncellenme anksiyetesi olmadan güvenilebilen veri

**Değer Önerisi:** *"Compare AI coding models with coding-focused benchmarks weighted your way — cross-verified, contradiction-flagged, in Turkish and English."* / *"AI kodlama modellerini sizin ağırlıklarınızla karşılaştırın — çapraz doğrulanmış, çelişki işaretli, Türkçe ve İngilizce."*

---

## 2. Hedef Kullanıcılar

3 eşit önemli persona:

### P1 — Sungur (Kişisel Referans)
Günlük Claude Code/OpenCode model seçim kararları için canlı referans. Hangi modeli ne için kullanacağını sürekli yeniden değerlendiriyor. Birincil ergonomi sahibi (tek-komut update, minimal onboarding).

### P2 — TR Developer Community
25-45 yaş, Claude Code/Cursor/Copilot kullanan TR yazılımcılar. Twitter/HN-TR/Reddit r/programlama aktif. Eksisozluk'ta multi-page Claude Code/Cursor/AI karşılaştırma tartışmalarına katılıyor. **Türkçe coverage'da hiçbir tracker yok** — açık greenfield.

### P3 — Global EN Developer Community
artificialanalysis.ai, llm-stats.com okuyucusu. r/LocalLLaMA (694K üye) ve HN aktif. Coding-focused composite scoring (user-editable weights) ve karma kapalı/açık + lokal model coverage'ı arıyor.

**Pazar Büyüklüğü:** TAM ~30M AI-using developer (GitHub Copilot 13M+ paid, Cursor 2M+, Claude Code/Codeium 15M overlapping) / SAM ~3-5M aktif model seçimi yapan + cost-conscious alternatif arayan / SOM 6 ay: 500-2K unique/ay (%0.02-0.05 SAM penetrasyonu).

---

## 3. Kullanıcı Hikayeleri (10 Story)

### P1 Sungur
- **P1-1**: Tek skill komutu ile 35 modelin tracker'ını <15 dk regenerate etmek istiyorum ki günlük seçimimi bu haftanın verisine göre yapabileyim.
- **P1-2**: Kullanım durumuma göre ağırlıkları ayarlamak istiyorum (agentic-heavy, SWE-heavy), top öneriler gerçek kullanımla eşleşsin.
- **P1-3**: Kaynaklar arası skor çelişkilerini görmek istiyorum ki şişirilmiş Verified yerine Pro'yu baz alabileyim.

### P2 TR Developer
- **P2-1**: Türkçe karşılaştırmaları yerel bağlamla (Claude Max $200/ay vs TL maaş) okumak istiyorum, kültürel çeviri yükü olmadan.
- **P2-2**: Hazır ağırlık profilleri (SWE-odaklı, Agentic-odaklı) kullanmak istiyorum, 14 benchmark tanımını öğrenmeden.
- **P2-3**: Tracker'ın PNG ekran görüntüsünü TR Twitter/HN/Ekşi'de paylaşmak istiyorum.

### P3 Global EN Developer
- **P3-1**: SWE-bench Verified ile Pro çelişkilerini açıkça görmek istiyorum — conflict-hiding rakiplere alternatif güven.
- **P3-2**: Pricing'i (subscription + local TCO + API) tek görünümde görmek istiyorum.
- **P3-3**: Composite skoru kendi workflow'uma göre yeniden ağırlıklandırmak istiyorum (local-only/agentic-heavy/budget-constrained).

### Cross-Persona
- **UC-1**: GPU VRAM otomatik tespit (WebGPU) veya manuel girişi belirtip sadece o VRAM'e sığan local modelleri (Unsloth UD variants + original) görmek/filtrelemek istiyorum.

---

## 4. Özellik Gereksinimleri

### Must-Have (v1 launch — 13 feature)

| ID | Feature | User Story Trace |
|----|---------|------------------|
| F1 | Skill + research agent (manuel trigger) | P1-1 |
| F2 | JS data array auto-regeneration | P1-1, outcome E |
| F3 | i18n TR/EN content + language switch | P2-1, moat A |
| F4 | GitHub Pages deploy | outcome B |
| F5 | GitHub Insights traffic ölçümü | outcome B |
| F6 | Diff/changelog otomasyonu | outcome D |
| F7 | Cross-source validation (≥2 kaynak) | outcome D, P3-1 |
| F8 | README + skill installation guide | outcome E |
| F9 | Dynamic weights editor UI + presets | P1-2, P2-2, P3-3, moat C |
| F10 | Screenshot/PNG export (section + full page) | P2-3, distribution |
| F11 | 3-breakpoint responsive design | tüm persona |
| F12 | Contradiction flagging (SWE-V vs Pro vb) | P1-3, P3-1, moat D |
| F13 | GPU VRAM detection + Unsloth UD priority + filter | UC-1 |

### Should-Have (Faz 2, 3-6 ay)
S1 RSS feed, S2 Discord webhook, S3 custom preset save/share, S4 email opt-in, **S5 Unified pricing view (P3-2 story — pricing data zaten var, fancy unified UI ertelendi)**

### Nice-to-Have (Faz 3, belirsiz)
N1 API endpoint (JSON programmatic), N2 model browser (per-model deep-dive), N3 benchmark methodology docs (TR+EN), N4 historical trend graphs, N5 community contribution rehberi, N6 landing page

---

## 5. Başarı Metrikleri (6 ay sonra)

| ID | Metrik | Hedef | Kaynak |
|----|--------|-------|--------|
| M1 | Monthly unique visitors | ≥500/ay | GitHub Insights → Traffic (built-in) |
| M2 | GitHub stars | ≥100 | GitHub API |
| M3 | Organic mentions | ≥1 TR + ≥1 global (HN/r/LocalLLaMA) | Manuel monitoring |
| M4 | Cross-source validation coverage | ≥%95 benchmark ≥2 kaynak | Release gate |
| M5 | Update frequency | ≤14 gün max aralık | Git log (anti-Aider-stale) |
| M6 | Skill clone proof-of-concept | ≥1 başka domain | Self-tracked |

---

## 6. Rekabet (HIGH confidence research, 18 kaynak)

### Direct (genel LLM trackerlar)
- **artificialanalysis.ai** ~1M+ unique/ay, 336 model, EN-only, opinion yok
- **llm-stats.com** 500+ model, 50+ benchmark, ad-monetized, EN-only
- **benchlm.ai** 202 model × 153 benchmark, sponsorship, "verified vs provisional" transparency

### Direct (coding-spesifik)
- **aider.chat** 43.8K GitHub stars AMA leaderboard **Kasım 2025'ten beri 5 ay stale**
- **LiveCodeBench** academic, contamination-free, ICLR 2025 spotlight
- **Berkeley BFCL V4** function-calling, ICML 2025
- **Scale SEAL** SWE-Pro 1865 task authority
- **SWE-rebench** academic, decontaminated
- **Vals.ai** B2B enterprise gated

### Adjacent
- **r/LocalLLaMA** 694K üye, opinion-driven discussion aktif

### Doğrulanmış 5 Pazar Boşluğu
1. Türkçe coverage **sıfır** — sadece academic (TurkBench, OpenLLM Turkish HF Space)
2. Opinionated VRAM-tier verdict ("X için bu modeli kullan") **hiçbir tracker'da yok**
3. **Aider 5 ay stale** — coding-spesifik tracker'da freshness gap
4. Subscription + local TCO + API pricing **unified view yok**
5. **Cross-source contradiction flagging** (SWE-V 80% vs SWE-Pro 46% aynı model) **hiçbir tracker'da yok**

### Compound Moat (4 birleşik avantaj — hiçbir rakipte yok)
- **A** Multi-language TR+EN coverage
- **B** Reusable BrainLedger skill+agent kalıbı
- **C** Coding-focused composite + user-editable weights UI ("our default, you change" şeffaflığı)
- **D** Cross-source contradiction flagging + manuel doğrulama disiplini

---

## 7. Riskler

### HIGH (Med×High)
- **R1 Scraping kırılganlığı** — Multi-source redundancy + retry+fallback + manuel override; Contingency: partial data + UI flag
- **R2 Veri extraction hatası** — Cross-source validation %95+ + contradiction >3pp/>5pp + diff manual review; Contingency: rollback + re-research
- **R3 Solo burnout/disiplin kaybı** — Content ≤4/ay hard cap + 14gün buffer + self-contained skill + ≤3sa/task; Contingency: stale badge UI + recovery sprint

### MEDIUM
- **R4** Opinion bias eleştirisi (d13 dynamic weights ile büyük ölçüde nötralize)
- **R5** TR community traction gelmez (aktif seeding + LITE mode contingency)
- **R6** Rakipler TR auto-translate ekler (first-mover 4-6 hafta + compound moat)
- **R7** Feature creep (HIGH probability — bu konuşmada bile görüldü; 13 must hard cap + Faz 2 queue)

### LOW
- **R8** Hukuki/scraping (public data + attribution)

**High×High risk yok.**

---

## 8. Timeline & Milestones

5 milestone × 5 hafta solo part-time (5-8 sa/hafta).

| Milestone | Hafta | Saat | Deliverable | Go/No-go |
|-----------|-------|------|-------------|----------|
| **M1 Foundation** | 1 | 3-4 | Public repo + 4 JSON schema + research agent base | T1-T4+T12 complete |
| **M2 Core** | 2 | 4-5 | Live tracker static render | 35 model render, TR/EN toggle, fetch <2sn |
| **M3 Integration** | 3 | 6-8 | Tüm 13 must-feature working | Weights 100% constraint, contradiction flag, GPU VRAM detect |
| **M4 Polish** | 4 | 3-4 | Production-ready | SEO meta, CHANGELOG, E2E 13 AC pass, Lighthouse ≥90 |
| **M5 Launch** | 5 | — | Public launch + content bootstrap + 2-week validation | Launch day 10-15 channel, 2 hafta GO/PIVOT/LITE |

**Buffer:** Hafta 6 opsiyonel (timeline slip contingency).
**Critical path:** T1→T12→T13→T15→T23→T19 = 10.5 saat sequential minimum.
**Calendar (paralel ile):** 15-20 saat.

---

## 9. Distribution Stratejisi

**Faz 1 — Launch Day (simultane TR + Global)**
- TR: AI LAB Discord (40K), YazılımaOrg (59K), Patika.dev (200K), Eksisozluk başlık entry, key TR Twitter (Utku Şen, Ali Tekin, Erhan Meydan), DonanımHaber tip
- Global: HN Show, r/LocalLLaMA Show, simonw blog mention, BenchGecko/awesome-llm-benchmarks PR, Twitter announcement thread, dev.to crosspost, lobste.rs

**Faz 2 — Post-launch 2 hafta (demand validation checkpoint)**
- Günlük trafik check, weekly star growth, feedback triage
- 2 hafta sonra: GO (continue CP2/CP3) / PIVOT (messaging revize) / LITE (content azalt)

**Pre-launch atlandı** — direct launch + ürün kendi için konuşur.

---

## 10. Roller & Sahiplik

**Tam solo model** — hem MVP'de hem Faz 2'de collaborator yok.

| Rol | Sorumluluk |
|-----|------------|
| Trigger | Skill invoke, scope seçimi, update başlatma |
| Approve | Diff preview review, contradiction resolution, override |
| Moderate | Community issue/PR triage (yanıt + yönlendirme, PR merge yok) |
| Publish | Git push → GitHub Pages auto-deploy |

**SPOF tradeoff bilinçli:** Editorial integrity (compound moat D) > continuity. Hand-off planı yok ama skill self-contained → hastalık sonrası hızlı geri dönüş.

---

## 11. Gelir Modeli

**Tamamen ücretsiz, monetization yok.** GitHub Pages free hosting (~$0/ay). Sponsorship/ads/premium yok — opinionated verdict bütünlüğü için bias-free kalmak kritik.

---

## Appendix A — Kullanılan Stack

Tek external service: **GitHub Pages**. html2canvas vendored repo içi. WebGPU native. Analytics = GitHub Insights Traffic. **Maliyet: $0 sürekli.**

## Appendix B — Lisans

MIT — kod ve veri. Rakipler bu veriyi kullanırsa attribution rica edilir, takedown power yok (public benchmark verisi).

## Appendix C — Karar Kayıtları

41 decision (d1-d41) `~/.ideas/coding-models-tracker.json` içinde, supersedes chain ile traceable. Önemli refinement decisions:
- d13 (supersedes d9): Compound moat C bileşeni "opinionated verdict" → "user-editable weights"
- d16/d22 (supersedes chain): MVP scope 9 → 13 bileşen (PNG export + responsive + GPU VRAM)
- d31: Stack 11 araç → 1 external (GitHub Pages) minimal
