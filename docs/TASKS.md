# AICoderMap — Task Breakdown

**Total:** 23 tasks / ~30-35 hr solo part-time / 5-week calendar
**Critical path:** T1 → T12 → T13 → T15 → T23 → T19 = 10.5 hr minimum sequential

---

## Task List

| ID | Title | Milestone | Estimate | Depends_on | Phase |
|----|-------|-----------|----------|------------|-------|
| **T1** | Repo init + GitHub Pages + .gitignore + README stub | M1 | 30 min | — | Foundation |
| **T2** | data/models.json schema + migrate from HTML | M1 | 1 hr | T1 | Foundation |
| **T3** | data/sources.json provenance migrate | M1 | 1 hr | T1 | Foundation |
| **T4** | data/gpu-database.json (NVIDIA + Apple + AMD + Intel) | M1 | 1.5 hr | T1 | Foundation |
| **T12** | aicodermap-research-agent.md (clone ledger template + specialize) | M1 | 1.5 hr | T1 | Foundation |
| **T5** | index.html structure + 3-breakpoint responsive CSS | M2 | 2 hr | T1 | Core |
| **T6** | app.js data fetch + render MODELS | M2 | 1 hr | T2, T5 | Core |
| **T13** | SKILL.md orchestrator (14 happy + 5 exception) | M2 | 2 hr | T12, T2, T3 | Core |
| **T7** | Dynamic weights editor UI (slider + presets + localStorage) | M3 | 2 hr | T6 | Features |
| **T8** | i18n TR/EN switch (runtime + localStorage) | M3 | 1.5 hr | T6 | Features |
| **T9** | Contradiction flagging UI (>3pp warn, >5pp red, tooltip) | M3 | 1 hr | T6, T3 | Features |
| **T10** | PNG export (html2canvas vendor, section + full page) | M3 | 1 hr | T5, T6 | Features |
| **T11** | GPU VRAM detection (WebGPU + manual fallback + filter) | M3 | 2 hr | T6, T4 | Features |
| **T15** | Cross-source validation logic (≥2 sources + contradiction detect) | M3 | 1 hr | T13, T3 | Features |
| **T14** | Skill install script + docs | M4 | 30 min | T13 | Polish |
| **T21** | SEO: meta + OG + JSON-LD + hreflang + sitemap + robots | M4 | 1 hr | T5, T8 | Polish |
| **T22** | CHANGELOG.md bootstrap + format convention | M4 | 30 min | T13 | Polish |
| **T23** | E2E test: all 13 AC | M4 | 2-3 hr | T7, T8, T9, T10, T11, T15, T21, T22 | Test |
| **T16** | README.md TR+EN + skill installation guide | M5 | 1 hr | T14 | Launch |
| **T17** | 2 CP1 launch-day analyses (DeepSeek V4 + Qwen3.6-27B) | M5 | 2 hr | T23 | Launch |
| **T18** | 1 CP2 evergreen guide: "Top 5 for 8GB VRAM devs" (QW1) | M5 | 2 hr | T23 | Launch |
| **T19** | 1 CP3 quarterly: "SWE-V vs Pro: why a 35-point gap?" (QW2) | M5 | 3 hr | T23 | Launch |
| **T20** | Launch playbook: channel list + ready-to-post text TR+EN | M5 | 1.5 hr | T23, T16 | Launch |
| **T24** | ✅ Mobile card-stack: ≤640px card list instead of table (`responsive.css @media`) | M4 | 2 hr | T5, T6 | Polish — done |
| **T25** | ⏳ Custom preset save/load (localStorage + import/export) — deferred to Phase 2 | M4→Phase 2 | 1.5 hr | T7 | Deferred |
| **T26** | ✅ SEO polish: sitemap.xml + robots.txt + canonical + JSON-LD + OG/Twitter + a11y skip-link | M4 | 1.5 hr | T5, T8 | Polish — done 2026-05-06 |
| **T27** | ✅ Doc drift sweep (CLAUDE.md modules / TECHSPEC schema / IMPLGUIDE weights / TEST_PLAN AC) | M4 | 1 hr | — | Polish — done 2026-05-06 |

---

## Milestones

### M1 — Foundation (Week 1, 3-4 hr)
**Deliverable:** Public repo + 4 JSON schemas + research agent base
**Tasks:** T1, T2, T3, T4, T12
**Go criteria:** JSON validates against schema, agent invocation test passes
**Demo:** Browse JSON files on GitHub
**Rollback:** Delete repo (trivial)

### M2 — Core (Week 2, 4-5 hr)
**Deliverable:** Live tracker static render
**Tasks:** T5, T6, T13
**Go criteria:** 50+ models render, TR/EN toggle works, data fetch <2s (AC5)
**Demo:** GitHub Pages URL live
**Rollback:** `git revert` to M1

### M3 — Integration (Week 3, 6-8 hr — heaviest)
**Deliverable:** All 13 must-have features working
**Tasks:** T7, T8, T9, T10, T11, T15
**Go criteria:** Weights 100% constraint, contradiction ≥3pp flag, GPU VRAM detect+filter, PNG export
**Demo:** E2E walkthrough of 13 features
**Rollback:** Feature flag disable per-feature

### M4 — Polish (Week 4, 3-4 hr)
**Deliverable:** Production-ready
**Tasks:** T14, T21, T22, T23
**Deferred (optional):** T24 (mobile card-stack), T25 (custom preset save/load)
**Go criteria:** SEO meta on all pages, CHANGELOG format, E2E 13 AC pass, Lighthouse SEO+a11y ≥90
**Demo:** Lighthouse audit report
**Rollback:** Specific polish revert

### M5 — Launch (Week 5)
**Deliverable:** Public launch + content bootstrap + 2-week validation
**Tasks:** T16, T17, T18, T19, T20
**Go criteria:** Launch day executed (10-15 channel intro), 2-week post-launch validation
**Demo:** 2-week checkpoint M1≥100 traffic + M2≥30 stars + M3≥1 mention → GO / PIVOT / LITE
**Rollback:** N/A (launched, post-launch improvement)

**Buffer:** Week 6 optional (timeline slip contingency).

---

## Risks (summary — detail in PRD §7)

| ID | Severity | Mitigation |
|----|----------|------------|
| R1 Scraping fragility | Med×High | Multi-source ≥2 + retry+fallback + manual override |
| R2 Data extraction error | Med×High | Cross-source ≥95% + contradiction >3pp/>5pp + manual diff review |
| R3 Solo burnout | Med×High | Content ≤4/month + 14-day buffer + self-contained skill + ≤3hr/task |
| R4 Opinion bias | L×M | Dynamic weights editor transparency (d13) |
| R5 TR traction | M×M | Active seeding + LITE mode contingency |
| R6 Competitor TR copy | L-M×M | First-mover 4-6 weeks + compound moat |
| R7 Feature creep | **H×M** | 13-must hard cap + Phase 2 queue + YAGNI gate |
| R8 Legal | L×L | Public data + attribution |

**No High×High risk.**

---

## Critical Path

```
T1 (0.5 hr) → T12 (1.5 hr) → T13 (2 hr) → T15 (1 hr) → T23 (2.5 hr) → T19 (3 hr) = 10.5 hr
```

Total 30-35 hr work; with parallel execution, 15-20 hr calendar (solo + weekends).

### Phase parallelism

- **Phase 1** (T1 root): T1 → [T2, T3, T4, T12] in parallel
- **Phase 2** (after Phase 1): T5, T6, T13 in parallel (after T2/T3/T12)
- **Phase 3** (after T6): T7, T8, T9, T10, T11, T15 in parallel
- **Phase 4** (parallel): T14, T21, T22
- **Phase 5** (sync gate): T23
- **Phase 6** (after T23): T16, T17, T18, T19, T20 in parallel

---

## GitHub Issues import

This task list can be imported as GitHub Issues. Format:

```
Title: T7 — Dynamic weights editor UI
Body:
**Milestone:** M3 Integration (Week 3)
**Estimate:** 2 hr
**Depends on:** #T6
**User story trace:** P1-2, P2-2, P3-3
**Feature trace:** F9
**Acceptance criteria:** AC-F9 (total=100% constraint, live recalc <100ms, 4 presets work, reset-to-default works)
Labels: type:feature, milestone:m3-integration, priority:p1
```

Bulk import via `gh issue create` in a bash script. Defer to Phase 2.
