# Coding Models Tracker — Task Breakdown

**Toplam:** 23 task / ~30-35 sa solo part-time / 5 hafta calendar
**Critical path:** T1 → T12 → T13 → T15 → T23 → T19 = 10.5 sa minimum sequential

---

## Task List

| ID | Title | Milestone | Estimate | Depends_on | Phase |
|----|-------|-----------|----------|------------|-------|
| **T1** | Repo init + GitHub Pages + .gitignore + README stub | M1 | 30 dk | — | Foundation |
| **T2** | data/models.json schema + migrate from HTML | M1 | 1 sa | T1 | Foundation |
| **T3** | data/sources.json provenance migrate | M1 | 1 sa | T1 | Foundation |
| **T4** | data/gpu-database.json (NVIDIA + Apple + AMD + Intel) | M1 | 1.5 sa | T1 | Foundation |
| **T12** | coding-models-research-agent.md (clone ledger template + specialize) | M1 | 1.5 sa | T1 | Foundation |
| **T5** | index.html structure + 3-breakpoint responsive CSS | M2 | 2 sa | T1 | Core |
| **T6** | app.js data fetch + render MODELS | M2 | 1 sa | T2, T5 | Core |
| **T13** | SKILL.md orchestrator (14 happy + 5 exception) | M2 | 2 sa | T12, T2, T3 | Core |
| **T7** | Dynamic weights editor UI (slider + presets + localStorage) | M3 | 2 sa | T6 | Features |
| **T8** | i18n TR/EN switch (runtime + localStorage) | M3 | 1.5 sa | T6 | Features |
| **T9** | Contradiction flagging UI (>3pp ⚠, >5pp 🚨, tooltip) | M3 | 1 sa | T6, T3 | Features |
| **T10** | PNG export (html2canvas vendor, section + full page) | M3 | 1 sa | T5, T6 | Features |
| **T11** | GPU VRAM detection (WebGPU + manual fallback + filter) | M3 | 2 sa | T6, T4 | Features |
| **T15** | Cross-source validation logic (≥2 source + contradiction detect) | M3 | 1 sa | T13, T3 | Features |
| **T14** | Skill install script + docs | M4 | 30 dk | T13 | Polish |
| **T21** | SEO: meta + OG + JSON-LD + hreflang + sitemap + robots | M4 | 1 sa | T5, T8 | Polish |
| **T22** | CHANGELOG.md bootstrap + format convention | M4 | 30 dk | T13 | Polish |
| **T23** | E2E test: tüm 13 AC | M4 | 2-3 sa | T7, T8, T9, T10, T11, T15, T21, T22 | Test |
| **T16** | README.md TR+EN + skill installation guide | M5 | 1 sa | T14 | Launch |
| **T17** | 2 CP1 launch-day analizi (DeepSeek V4 + Qwen3.6-27B) | M5 | 2 sa | T23 | Launch |
| **T18** | 1 CP2 evergreen rehber: "8GB VRAM dev için top 5" (QW1) | M5 | 2 sa | T23 | Launch |
| **T19** | 1 CP3 quarterly: "SWE-V vs Pro: %35 puanlık fark neden?" (QW2) | M5 | 3 sa | T23 | Launch |
| **T20** | Launch playbook: kanal listesi + ready-to-post text TR+EN | M5 | 1.5 sa | T23, T16 | Launch |

---

## Milestones

### M1 — Foundation (Hafta 1, 3-4 sa)
**Deliverable:** Public repo + 4 JSON schema + research agent base
**Tasks:** T1, T2, T3, T4, T12
**Go criteria:** JSON validates against schema, agent invocation test passes
**Demo:** Browse JSON files on GitHub
**Rollback:** Delete repo (trivial)

### M2 — Core (Hafta 2, 4-5 sa)
**Deliverable:** Live tracker static render
**Tasks:** T5, T6, T13
**Go criteria:** 35 model render, TR/EN toggle works, data fetch <2sn (AC5)
**Demo:** GitHub Pages URL live
**Rollback:** `git revert` to M1

### M3 — Integration (Hafta 3, 6-8 sa — en ağır)
**Deliverable:** Tüm 13 must-feature working
**Tasks:** T7, T8, T9, T10, T11, T15
**Go criteria:** Weights 100% constraint, contradiction ≥3pp flag, GPU VRAM detect+filter, PNG export
**Demo:** E2E walkthrough 13 features
**Rollback:** Feature flag disable per-feature

### M4 — Polish (Hafta 4, 3-4 sa)
**Deliverable:** Production-ready
**Tasks:** T14, T21, T22, T23
**Go criteria:** SEO meta all pages, CHANGELOG format, E2E 13 AC pass, Lighthouse SEO+a11y ≥90
**Demo:** Lighthouse audit report
**Rollback:** Specific polish revert

### M5 — Launch (Hafta 5)
**Deliverable:** Public launch + content bootstrap + 2 hafta validation
**Tasks:** T16, T17, T18, T19, T20
**Go criteria:** Launch day executed (10-15 channel intro), 2 hafta post-launch validation
**Demo:** 2-week checkpoint M1≥100 trafik + M2≥30 star + M3≥1 mention → GO / PIVOT / LITE
**Rollback:** N/A (launched, post-launch iyileştirme)

**Buffer:** Hafta 6 opsiyonel (timeline slip contingency).

---

## Risks (özet — detay PRD §7)

| ID | Severity | Mitigation |
|----|----------|------------|
| R1 Scraping kırılganlığı | Med×High | Multi-source ≥2 + retry+fallback + manuel override |
| R2 Veri extraction hatası | Med×High | Cross-source ≥%95 + contradiction >3pp/>5pp + diff manual review |
| R3 Solo burnout | Med×High | Content ≤4/ay + 14gün buffer + self-contained skill + ≤3sa/task |
| R4 Opinion bias | L×M | Dynamic weights editor şeffaflığı (d13) |
| R5 TR traction | M×M | Aktif seeding + LITE mode contingency |
| R6 Rakip TR copy | L-M×M | First-mover 4-6 hafta + compound moat |
| R7 Feature creep | **H×M** | 13 must hard cap + Faz 2 queue + YAGNI gate |
| R8 Hukuki | L×L | Public data + attribution |

**No High×High risk.**

---

## Critical Path

```
T1 (0.5 sa) → T12 (1.5 sa) → T13 (2 sa) → T15 (1 sa) → T23 (2.5 sa) → T19 (3 sa) = 10.5 sa
```

Toplam 30-35 sa work, paralel execution ile calendar 15-20 sa (solo + haftasonu).

### Phase paralelism

- **Phase 1** (T1 root): T1 → [T2, T3, T4, T12] paralel
- **Phase 2** (after Phase 1): T5, T6, T13 paralel (T2/T3/T12 sonra)
- **Phase 3** (after T6): T7, T8, T9, T10, T11, T15 paralel
- **Phase 4** (paralel): T14, T21, T22
- **Phase 5** (sync gate): T23
- **Phase 6** (after T23): T16, T17, T18, T19, T20 paralel

---

## GitHub Issues import

Bu task listesi GitHub Issues olarak import edilebilir. Format:

```
Title: T7 — Dynamic weights editor UI
Body:
**Milestone:** M3 Integration (Hafta 3)
**Estimate:** 2 sa
**Depends on:** #T6
**User story trace:** P1-2, P2-2, P3-3
**Feature trace:** F9
**Acceptance criteria:** AC-F9 (total=100% constraint, live recalc <100ms, 4 preset works, reset-to-default works)
Labels: type:feature, milestone:m3-integration, priority:p1
```

`gh issue create` ile bash script ile bulk import edilebilir. Faz 2'ye ertele.
