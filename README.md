# AICoderMap

> **Compare AI coding models with coding-focused benchmarks weighted your way — cross-verified, contradiction-flagged, in Turkish and English.**
>
> *AI kodlama modellerini sizin ağırlıklarınızla karşılaştırın — çapraz doğrulanmış, çelişki işaretli, Türkçe ve İngilizce.*

---

## Why AICoderMap?

Coding LLM pazarı her 2 haftada bir yeni frontier model çıkarıyor (Opus 4.7, Kimi K2.6, Qwen3.6-27B, DeepSeek V4 son ay içinde). Mevcut tracker'lar:
- **artificialanalysis.ai / llm-stats / BenchLM** — EN-only, opinion yok, contradiction gizli
- **aider.chat** — Kasım 2025'ten beri 5 ay stale
- **Türkçe coverage** — sıfır

AICoderMap **5 doğrulanmış pazar boşluğunu** kapatıyor:

1. 🇹🇷 **Türkçe + İngilizce** içerik (i18n)
2. ⚖️ **User-editable composite weights** — "bizim default'umuz, sen değiştir" (slider + presetler)
3. ⚠ **Cross-source contradiction flagging** — SWE-V vs Pro 35pp fark görünür
4. 💰 **Subscription + local TCO + API pricing** unified context
5. 🖥️ **GPU VRAM detection** — sadece GPU'na sığan local modeller (WebGPU + manual + Unsloth UD priority)

---

## 🚀 Status

**Pre-launch — implementation aşamasında.** 5 hafta solo part-time geliştirme planı (M1 Foundation → M5 Launch).

| Doküman | Açıklama |
|---------|----------|
| [PRD](docs/PRD.md) | Product Requirements (kullanıcı + özellik + metrik) |
| [TechSpec](docs/TECHSPEC.md) | Technical Specification (mimari + veri + API + güvenlik) |
| [ImplGuide](docs/IMPLGUIDE.md) | ⭐ Coding-ready implementation guide |
| [Tasks](docs/TASKS.md) | 23 task / 5 milestone breakdown |
| [Workflow](docs/WORKFLOW.md) | Update workflow (14 happy + 5 exception) |
| [Pitch](docs/PITCH.md) | Kısa özet — paylaşım için |

---

## 🛠️ Stack

**Tek external service: GitHub Pages.** Maliyet: $0 sürekli.

- Vanilla HTML/CSS/JS (no build step, no framework)
- Static JSON data files (skill auto-regenerates)
- WebGPU API (browser-native GPU detect)
- html2canvas (vendored, PNG export)
- Local Claude Code skill + research agent (manuel update workflow)

---

## 📋 Roadmap (5 hafta)

- [ ] **M1 Foundation** (Hafta 1) — Repo + 4 JSON schema + research agent
- [ ] **M2 Core** (Hafta 2) — Live tracker static render, TR/EN toggle
- [ ] **M3 Integration** (Hafta 3) — 13 must-feature (weights editor + GPU VRAM + contradiction flag + PNG)
- [ ] **M4 Polish** (Hafta 4) — SEO + responsive + Lighthouse ≥90 + E2E
- [ ] **M5 Launch** (Hafta 5) — Simultane TR + Global soft launch + 2 hafta validation

---

## 🤝 Contributing

Şu an pre-launch / solo development. Faz 2'de issue/discussion açılacak. Şimdilik:
- ⭐ Star the repo to follow progress
- 🐛 Open issue for benchmark data corrections (after launch)
- 💡 Open discussion for feature requests

---

## 📜 License

MIT — kod ve veri kamuya açık. Attribution rica edilir, takedown power yok (public benchmark verisi).

---

## 🧠 Built with

[BrainLedger](https://github.com/sungurerdim/BrainLedger) — idea-to-production mentor (Claude Code skill).

**Project author:** [Sungur Erdim](https://github.com/sungurerdim) · sungurerdim@gmail.com
