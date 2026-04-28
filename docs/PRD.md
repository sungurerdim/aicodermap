# AICoderMap — Product Requirements Document

**Version:** 1.0 (24 April 2026)
**Owner:** Sungur Erdim
**Status:** Specification + Planning complete; implementation in progress
**License:** MIT

---

## 1. Executive Summary

"Which model should I use today?" reopens every two weeks in the coding-LLM market (Opus 4.7 → Kimi K2.6 → Qwen3.6-27B → DeepSeek V4 in the last quarter). Existing tools force the developer into hours of review, decisions from stale data or single-source self-reported scores, and a separate hunt for which quant runs on their GPU.

**AICoderMap** delivers four concrete time/trust gains:

1. **Decision in seconds:** ranked by your priority weights (SWE / agentic / balanced / custom) — drag the slider, ranking updates instantly.
2. **Protection against inflated scores:** every benchmark score lists its sources with tier (S/I/C). 3pp+ ⚠, 5pp+ 🚨; SWE-Verified 87 vs SWE-Pro 64 contradictions are visible in the tooltip.
3. **GPU-aware options:** WebGPU auto-detect; every local model labeled *"Fits (10 GB · UD-IQ2_XXS)"*; for non-fitting models, *"+3 GB RAM"* offload suggestion.
4. **No stale data:** M5 discipline — ≤14 days max gap. Aider's 5-month dead leaderboard does not happen here.

**Value proposition (EN):** *"Decide which coding model to use, in seconds. Ranked by your priorities, source contradictions surfaced, local options labeled with the exact quant that fits your GPU."*

**(TR — live UI):** *"Hangi kodlama modelini ne için kullanacağına saniyeler içinde karar ver. Senin önceliklerine göre sıralı, kaynak çelişkileri görünür, GPU'na sığacak yerel modeller hangi quant ile çalıştığı yazılı."*

---

## 2. Target Users

Three equally important personas:

### P1 — Sungur (Personal Reference)
Daily Claude Code / OpenCode model-selection live reference. Continuously re-evaluates which model to use for what. Primary ergonomic owner (single-command update, minimal onboarding).

### P2 — TR Developer Community
25-45 yo TR developers using Claude Code / Cursor / Copilot. Active on Twitter / HN-TR / Reddit r/programlama. Joins multi-page Claude Code / Cursor / AI comparison threads on Eksisozluk. **No tracker has Turkish coverage** — open greenfield.

### P3 — Global EN Developer Community
artificialanalysis.ai and llm-stats.com readers. Active on r/LocalLLaMA (694K members) and HN. Looking for coding-focused composite scoring (user-editable weights) and mixed closed/open + local model coverage.

**Market sizing:** TAM ≈ 30M AI-using developers (GitHub Copilot 13M+ paid, Cursor 2M+, Claude Code/Codeium 15M overlapping). SAM ≈ 3-5M actively choosing models + cost-conscious alternatives. SOM at 6 months: 500-2K unique/month (0.02-0.05% SAM penetration).

---

## 3. User Stories (10)

### P1 Sungur
- **P1-1**: I want to regenerate the 35-model tracker in <15 min via a single skill command, so my daily choice reflects this week's data.
- **P1-2**: I want to tune weights to my use case (agentic-heavy, SWE-heavy) so the top recommendations match real usage.
- **P1-3**: I want to see cross-source score contradictions so I can base decisions on Pro instead of inflated Verified.

### P2 TR Developer
- **P2-1**: I want to read comparisons in Turkish with local context (Claude Max $200/mo vs TL salary) without cultural translation tax.
- **P2-2**: I want preset weight profiles (SWE-focused, Agentic-focused) without learning 14 benchmark definitions.
- **P2-3**: I want to share PNG screenshots of the tracker on TR Twitter / HN / Eksisozluk.

### P3 Global EN Developer
- **P3-1**: I want SWE-bench Verified vs Pro contradictions surfaced explicitly — alternative trust to conflict-hiding competitors.
- **P3-2**: I want pricing (subscription + local TCO + API) in a unified view.
- **P3-3**: I want to re-weight the composite score to my own workflow (local-only / agentic-heavy / budget-constrained).

### Cross-Persona
- **UC-1**: I want WebGPU VRAM auto-detect (or manual entry) and a filter that shows only the local models (Unsloth UD variants + original) that fit.

---

## 4. Feature Requirements

### Must-Have (v1 launch — 13 features)

| ID | Feature | User-story trace |
|----|---------|------------------|
| F1 | Skill + research agent (manual trigger) | P1-1 |
| F2 | JS data array auto-regeneration | P1-1, outcome E |
| F3 | i18n TR/EN content + language switch | P2-1, moat A |
| F4 | GitHub Pages deploy | outcome B |
| F5 | GitHub Insights traffic measurement | outcome B |
| F6 | Diff/changelog automation | outcome D |
| F7 | Cross-source validation (≥2 sources) | outcome D, P3-1 |
| F8 | README + skill installation guide | outcome E |
| F9 | Dynamic weights editor UI + presets | P1-2, P2-2, P3-3, moat C |
| F10 | Screenshot/PNG export (section + full page) | P2-3, distribution |
| F11 | 3-breakpoint responsive design | all personas |
| F12 | Contradiction flagging (SWE-V vs Pro etc.) | P1-3, P3-1, moat D |
| F13 | GPU VRAM detection + Unsloth UD priority + filter | UC-1 |

### Should-Have (Phase 2, 3-6 months)
S1 RSS feed, S2 Discord webhook, S3 custom-preset save/share, S4 email opt-in, **S5 Unified pricing view (P3-2 — pricing data exists; the polished unified UI is deferred)**.

### Nice-to-Have (Phase 3, undetermined)
N1 API endpoint (programmatic JSON), N2 model browser (per-model deep-dive), N3 benchmark methodology docs (TR+EN), N4 historical trend graphs, N5 community contribution guide, N6 landing page.

---

## 5. Success Metrics (6 months out)

| ID | Metric | Target | Source |
|----|--------|--------|--------|
| M1 | Monthly unique visitors | ≥500/mo | GitHub Insights → Traffic (built-in) |
| M2 | GitHub stars | ≥100 | GitHub API |
| M3 | Organic mentions | ≥1 TR + ≥1 global (HN / r/LocalLLaMA) | Manual monitoring |
| M4 | Cross-source validation coverage | ≥95% benchmarks have ≥2 sources | Release gate |
| M5 | Update frequency | ≤14-day max gap | Git log (anti-Aider-stale) |
| M6 | Skill clone proof-of-concept | ≥1 other domain | Self-tracked |

---

## 6. Competition (HIGH-confidence research, 18 sources)

### Direct (general LLM trackers)
- **artificialanalysis.ai** ~1M+ unique/mo, 336 models, EN-only, no opinion
- **llm-stats.com** 500+ models, 50+ benchmarks, ad-monetized, EN-only
- **benchlm.ai** 202 models × 153 benchmarks, sponsorship, "verified vs provisional" transparency

### Direct (coding-specific)
- **aider.chat** 43.8K GitHub stars AMA leaderboard — **stale since November 2025 (5 months)**
- **LiveCodeBench** academic, contamination-free, ICLR 2025 spotlight
- **Berkeley BFCL V4** function-calling, ICML 2025
- **Scale SEAL** SWE-Pro 1865-task authority
- **SWE-rebench** academic, decontaminated
- **Vals.ai** B2B enterprise gated

### Adjacent
- **r/LocalLLaMA** 694K members, opinion-driven discussion active

### Five validated market gaps
1. Turkish coverage **zero** — only academic (TurkBench, OpenLLM Turkish HF Space)
2. Opinionated VRAM-tier verdict ("for X, use this model") **on no tracker**
3. **Aider 5 months stale** — coding-specific freshness gap
4. Subscription + local TCO + API pricing **no unified view**
5. **Cross-source contradiction flagging** (SWE-V 80% vs SWE-Pro 46% same model) **on no tracker**

### Compound moat (4 combined advantages — no competitor has all)
- **A** Multi-language TR + EN coverage
- **B** Reusable skill+agent template (cloneable to other tracker domains)
- **C** Coding-focused composite + user-editable weights UI ("our default, you change")
- **D** Cross-source contradiction flagging + manual verification discipline

---

## 7. Risks

### HIGH (Med×High)
- **R1 Scraping fragility** — Multi-source redundancy + retry+fallback + manual override; contingency: partial data + UI flag.
- **R2 Data extraction error** — Cross-source validation 95%+ + contradiction >3pp/>5pp + manual diff review; contingency: rollback + re-research.
- **R3 Solo burnout / discipline loss** — Content ≤4/mo hard cap + 14-day buffer + self-contained skill + ≤3 hr/task; contingency: stale-badge UI + recovery sprint.

### MEDIUM
- **R4** Opinion-bias criticism (largely neutralized by d13 dynamic weights)
- **R5** TR community traction misses (active seeding + LITE-mode contingency)
- **R6** Competitors add TR auto-translate (4-6 week first-mover + compound moat)
- **R7** Feature creep (HIGH probability — visible even in this discussion; 13-must hard cap + Phase-2 queue)

### LOW
- **R8** Legal/scraping (public data + attribution)

**No High×High risk.**

---

## 8. Timeline & Milestones

5 milestones × 5 weeks solo part-time (5-8 hr/week).

| Milestone | Week | Hours | Deliverable | Go/No-go |
|-----------|------|-------|-------------|----------|
| **M1 Foundation** | 1 | 3-4 | Public repo + 4 JSON schemas + research-agent base | T1-T4 + T12 complete |
| **M2 Core** | 2 | 4-5 | Live tracker static render | 50+ models render, TR/EN toggle, fetch <2s |
| **M3 Integration** | 3 | 6-8 | All 13 must-have features working | Weights 100% constraint, contradiction flag, GPU VRAM detect |
| **M4 Polish** | 4 | 3-4 | Production-ready | SEO meta, CHANGELOG, E2E 13 AC pass, Lighthouse ≥90 |
| **M5 Launch** | 5 | — | Public launch + content bootstrap + 2-week validation | Launch-day 10-15 channels, 2-week GO/PIVOT/LITE |

**Buffer:** Week 6 optional (timeline-slip contingency).
**Critical path:** T1→T12→T13→T15→T23→T19 = 10.5 hours sequential minimum.
**Calendar (with parallelism):** 15-20 hours.

---

## 9. Distribution Strategy

**Phase 1 — Launch day (simultaneous TR + Global)**
- TR: AI LAB Discord (40K), YazılımaOrg (59K), Patika.dev (200K), Eksisozluk topic entry, key TR Twitter (Utku Şen, Ali Tekin, Erhan Meydan), DonanımHaber tip.
- Global: HN Show, r/LocalLLaMA Show, simonw blog mention, BenchGecko / awesome-llm-benchmarks PR, Twitter announcement thread, dev.to crosspost, lobste.rs.

**Phase 2 — Post-launch 2 weeks (demand validation checkpoint)**
- Daily traffic check, weekly star growth, feedback triage.
- After 2 weeks: GO (continue CP2/CP3) / PIVOT (revise messaging) / LITE (reduce content).

**Pre-launch skipped** — direct launch + the product speaks for itself.

---

## 10. Roles & Ownership

**Fully solo model** — no collaborator in MVP or Phase 2.

| Role | Responsibility |
|------|----------------|
| Trigger | Skill invoke, scope selection, update kickoff |
| Approve | Diff preview review, contradiction resolution, override |
| Moderate | Community issue/PR triage (respond + redirect; no PR merge) |
| Publish | git push → GitHub Pages auto-deploy |

**SPOF trade-off accepted:** Editorial integrity (compound moat D) > continuity. No hand-off plan, but the skill is self-contained → quick recovery after illness.

---

## 11. Revenue Model

**Fully free, no monetization.** GitHub Pages free hosting (~$0/mo). No sponsorship/ads/premium — staying bias-free is critical to opinionated-verdict integrity.

---

## Appendix A — Stack

Single external service: **GitHub Pages**. html2canvas vendored in-repo. WebGPU native. Analytics = GitHub Insights Traffic. **Cost: $0 ongoing.**

## Appendix B — License

MIT — code and data public. If competitors reuse this data, attribution requested; no takedown power (public benchmark data).

## Appendix C — Decision Log

41 decisions (d1-d41) tracked in `~/.ideas/aicodermap.json`, traceable through a supersedes chain. Important refinements:
- **d13 (supersedes d9):** Compound moat C component "opinionated verdict" → "user-editable weights".
- **d16/d22 (supersedes chain):** MVP scope 9 → 13 components (PNG export + responsive + GPU VRAM).
- **d31:** Stack reduced from 11 tools to 1 external (GitHub Pages) minimum.
