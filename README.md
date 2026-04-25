# AICoderMap

> **Decide which coding model to use, in seconds.** Ranked by your priorities, source contradictions surfaced, local options labeled with the exact quant that fits your GPU. Available in English and Turkish in the live UI.

---

## Why AICoderMap?

A new coding LLM ships every two weeks — Opus 4.7, Kimi K2.6, Qwen3.6-27B, DeepSeek V4 in just the last month. When you actually need to pick one, today's trackers leave you stuck:

- **artificialanalysis.ai / llm-stats / BenchLM** force you into hours of review — no opinion, conflicting scores side by side, you interpret them.
- **aider.chat** has not updated since November 2025 (5 months stale). You are deciding from rotten data.
- **No Turkish coverage anywhere.** Translating each global benchmark page is a separate time tax.

AICoderMap answers the questions that actually shape the decision:

| Question | AICoderMap's answer |
|----------|---------------------|
| **"Which model fits my workflow?"** | Slide the weights to your priorities (SWE-focused, agentic-focused, balanced, or custom) — ranking updates instantly. Four built-in presets plus your own custom mix. |
| **"SWE-Verified 87 vs SWE-Pro 64 — which is real?"** | Every score carries a ⚠ / 🚨 flag when sources disagree. The tooltip lists each source (Anthropic / Scale SEAL / community) with its tier (S = self-reported, I = independent, C = community). Decide on raw evidence, not inflated headlines. |
| **"What runs on my RTX 3070?"** | WebGPU auto-detects your hardware on page load. Every local model gets a label like *"Fits (10 GB · UD-IQ2_XXS)"* — exact quant name plus GB. For models that overflow, you also see *"+3 GB RAM"* offload recommendations. |
| **"How fresh is the data?"** | Each row shows its last-updated date. Refreshed every 14 days at most — none of Aider's 5-month staleness. |
| **"I want to share this on Twitter/Discord."** | One click → PNG export for a card, the comparison table, or the full page. No screenshot fiddling. |
| **"I want to read it in Turkish."** | Every UI label and every benchmark description is written in TR — no translation tax to use the tool. |

---

## 🚀 Status

**Pre-launch — implementation in progress.** 5-week solo part-time plan (M1 Foundation → M5 Launch).

| Document | What it covers |
|----------|----------------|
| [PRD](docs/PRD.md) | Product Requirements (users, features, metrics) |
| [TechSpec](docs/TECHSPEC.md) | Technical Specification (architecture, data, API, security) |
| [ImplGuide](docs/IMPLGUIDE.md) | ⭐ Coding-ready implementation guide |
| [Tasks](docs/TASKS.md) | 23-task / 5-milestone breakdown |
| [Workflow](docs/WORKFLOW.md) | Update workflow (14 happy-path + 5 exception steps) |
| [Pitch](docs/PITCH.md) | Short pitch — for sharing |

---

## 🛠️ Stack

**Single external service: GitHub Pages.** Ongoing cost: $0.

- Vanilla HTML/CSS/JS (no build step, no framework)
- Static JSON data files (the skill regenerates them)
- WebGPU API (browser-native GPU detect)
- html2canvas (vendored, PNG export)
- Local Claude Code skill + research agent (manual update workflow)

---

## 📋 Roadmap (5 weeks)

- [x] **M1 Foundation** (Week 1) — Repo + 4 JSON schemas + research agent
- [x] **M2 Core** (Week 2) — Live tracker static render, TR/EN toggle
- [x] **M3 Integration** (Week 3) — 13 must-have features (weights editor + GPU VRAM + contradiction flags + PNG)
- [ ] **M4 Polish** (Week 4) — SEO + responsive + Lighthouse ≥90 + E2E
- [ ] **M5 Launch** (Week 5) — Simultaneous TR + Global soft launch + 2-week validation

---

## 🤝 Contributing

Currently pre-launch / solo development. Issues and discussions will open in Phase 2. For now:

- ⭐ Star the repo to follow progress
- 🐛 Open an issue for benchmark-data corrections (after launch)
- 💡 Open a discussion for feature requests

---

## 📜 License

MIT — code and data are public. Attribution appreciated; no takedown power (public benchmark data).

---

## 🧠 Built with

A reusable Claude Code skill + research-agent template — domain-agnostic, cloneable to other tracker projects.

**Author:** [Sungur Erdim](https://github.com/sungurerdim) · sungurerdim@gmail.com
