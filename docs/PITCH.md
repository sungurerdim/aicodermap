# AICoderMap

> Cuts the answer to "which coding model should I use today?" from hours of review to seconds. Ranked by your priorities, source contradictions surfaced, local options labeled with the exact quant that fits your GPU.

---

## Problem

A new frontier coding LLM ships every two weeks (Opus 4.7 → Kimi K2.6 → Qwen3.6-27B → DeepSeek V4 just last month). The practical impact for any developer trying to decide:

- **You spend hours reviewing scores.** Existing trackers (artificialanalysis.ai, llm-stats, BenchLM) place numbers side by side without an opinion. You see SWE-Verified 87 / SWE-Pro 64 for the same model — which do you trust?
- **You decide from stale data.** The Aider leaderboard has been frozen since November 2025 (5 months). New models' coding performance simply is not there.
- **No Turkish coverage anywhere.** Each benchmark description costs separate translation time.
- **Local vs cloud?** The answer depends on "what quant runs on your GPU." No tracker shows it. You experiment manually with llama.cpp / Unsloth / Ollama.

---

## What AICoderMap gives you

| Your problem | AICoderMap's answer |
|--------------|---------------------|
| **"Which score is real?"** | Every score lists its sources with a tier (S = self-reported, I = independent, C = community). 5pp+ disagreements raise a 🚨; tooltip shows the breakdown. |
| **"Which fits my workflow?"** | Drag the SWE-Pro weight to 30%, agentic to 5%; ranking updates instantly. Four presets + custom + reset. |
| **"What runs on my GPU?"** | WebGPU detect on page load → every local model labeled *"Fits (10 GB · UD-IQ2_XXS)"*. If VRAM is short, you also see a *"+3 GB RAM"* offload suggestion. |
| **"How fresh is this?"** | `lastUpdated` per row. M5 discipline: ≤14 days max gap — none of Aider's 5-month death state. |
| **"I want to share the comparison."** | Camera icon → one-click PNG for a card / the table / the full page. |
| **"I want to read in Turkish."** | Every UI element and every benchmark description is written in TR — zero translation tax. |

---

## Users

Three equally important personas:

- **P1** Sungur — personal daily model-selection reference (Claude Code, OpenCode decisions)
- **P2** TR developer community — 25-45 yo, Claude Code/Cursor/Copilot users (Twitter/HN-TR/Eksisozluk active, ~150K active TR devs)
- **P3** Global EN developer community — r/LocalLLaMA (694K), HN, looking for opinionated verdict + mixed closed/open + local coverage

---

## Why now

Four converging factors:

- **Market momentum** — frontier release every two weeks; manual research can't keep up.
- **Technical readiness** — the skill + research-agent architecture is mature and clone-ready for other tracker domains.
- **v0 done** — 78+ models × 29 benchmarks compiled and continuously refreshed; the skill+agent automation layer ships every 14 days at most.
- **Skill ecosystem timing** — Claude Code skill ecosystem is new; this is one of the first comprehensive domain-research skills.

---

## MVP

5 weeks solo part-time × 30-35 hours. **Single external service: GitHub Pages, $0/mo ongoing.**

13 must-have features:

1. Skill + research agent (manual trigger)
2. JS data array auto-regeneration
3. i18n TR/EN content + language switch
4. GitHub Pages deploy
5. GitHub Insights traffic measurement
6. Diff/changelog automation
7. Cross-source validation (≥2 sources)
8. README + skill installation guide
9. **Dynamic weights editor UI + presets**
10. **Screenshot/PNG export** (section + full page)
11. 3-breakpoint responsive design (mobile/tablet/desktop)
12. **Contradiction flagging** (SWE-V vs Pro etc.)
13. **GPU VRAM detection + Unsloth UD priority + filter**

5 milestones: Foundation → Core → Integration → Polish → Launch.

**Launch:** Simultaneous TR + Global soft launch, 10-15 channel intro (AI LAB Discord 40K, YazılımaOrg 59K, Patika 200K, Eksisozluk topic entry, key TR Twitter, HN Show, r/LocalLLaMA Show, simonw blog mention, BenchGecko PR), 2-week post-launch validation checkpoint (GO / PIVOT / LITE).

---

## 6-month targets

| Metric | Target |
|--------|--------|
| Traffic | ≥500 unique/month |
| GitHub stars | ≥100 |
| Organic mentions | ≥1 TR + ≥1 global |
| Data reliability | ≥95% cross-source validation |
| Update cadence | ≤14 days max gap |
| Reusability | ≥1 clone to another domain (mobile-app benchmark, etc.) |

---

## License

**MIT** — code and data public. Free, no monetization, no sponsorship (bias-free editorial integrity).

---

🔗 **Repo:** github.com/sungurerdim/aicodermap (soon)
🔗 **Live:** sungurerdim.github.io/aicodermap (soon)
✉️ **Sungur Erdim** · sungurerdim@gmail.com
