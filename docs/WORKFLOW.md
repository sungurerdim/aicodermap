# AICoderMap — Workflow Documentation

**Version:** 1.0 | **April 24, 2026** | **Audience:** Sungur (operational reference)

---

## 1. Update Workflow — 14 Happy Path Steps

```
┌──────────────────────────────────────────────────────────────────┐
│  HAPPY PATH                                                      │
├──────────────────────────────────────────────────────────────────┤
│ 1. User → Claude Code → /ledger-tracker-update (skill invoke)    │
│ 2. Skill reads idea context (last launch, known models, defs)    │
│ 3. Skill asks: "Full refresh? Specific model? New release?"      │
│ 4. Scope selection:                                              │
│    - Full refresh → all models                                   │
│    - Specific model → single-model deep                          │
│    - New release → new model detection + full profile            │
│ 5. Skill → coding-models-research-agent (structured prompt)      │
│ 6. Agent: web scraping + cross-source + validation               │
│ 7. Agent returns JSON {models[], contradictions[], coverage}     │
│ 8. Skill validation:                                             │
│    - ≥2 sources per score (M4 release gate)                      │
│    - Contradictions flag (>3pp warn, >5pp red)                   │
│    - lastUpdated auto-set to today                               │
│ 9. Skill diff preview:                                           │
│    - Changed fields highlight                                    │
│    - New models list                                             │
│    - Contradictions table                                        │
│10. User review + approve (or override per-entry)                 │
│11. Skill writes data/models.json + data/sources.json             │
│12. Skill appends CHANGELOG.md entry                              │
│13. User git commit + push (or skill auto with confirmation)      │
│14. GitHub Pages auto-deploy (~1-2 min) → confirmation            │
└──────────────────────────────────────────────────────────────────┘
```

**Typical duration:** 10-15 minutes (full refresh) / 3-5 minutes (single model update).

---

## 2. Exception Handling — 5 Scenarios

| # | Scenario | Detection | Behavior |
|---|----------|-----------|----------|
| **a** | Agent HTTP fetch fail | Network error caught | Retry 1x → fallback WebSearch → user prompt: "Partial data obtained, do you want to continue?" |
| **b** | Validation coverage <95% | M4 gate check | Warning + show missing source list + user force-override option |
| **c** | Contradiction >5pp | sources.json delta calc | Red flag + show source breakdown → user manual pick (which source is correct?) or flag both |
| **d** | User declines diff | User input "no" / cancel | Rollback (no file write, no commit) — tracker stays in previous state |
| **e** | Git conflict (parallel edit) | `git push` failure | Skill abort + "Run `git pull` first, then retry" message |

---

## 3. Roles (Solo Model)

**Fully solo — all 4 responsibilities sit with Sungur.** No collaborators in MVP or Phase 2.

| Role | Responsibility | Cadence |
|------|----------------|---------|
| **Trigger** | Skill invoke, scope selection, kicking off the update | Weekly + event-driven (new model launch) |
| **Approve** | Diff preview review, contradiction resolution, override decisions, git commit confirmation | Every update |
| **Moderate** | Community issue/PR triage (respond + route); no collaborator merge rights | Weekly (issues), daily (Twitter mentions) |
| **Publish** | Git push → GitHub Pages auto-deploy, asset serving | Every update (automatic) |

### SPOF Mitigation
- Skill + research agent are **self-contained + documented** → fast return after illness/vacation
- M5 metric: ≤14-day buffer tolerates 1 missed update
- Editorial integrity > continuity tradeoff is **consciously accepted**

---

## 4. Tools & Systems (Minimal Stack)

**Single external service: GitHub Pages.** Everything else is browser-native, in-repo, or a local tool.

| Item | Where | Cost |
|------|-------|------|
| GitHub Pages | github.com | $0 (public repo) |
| Claude Code CLI | local machine `~/.claude/` | existing subscription |
| html2canvas | repo `assets/vendor/html2canvas.min.js` | $0 |
| WebGPU API | browser-native | platform |
| GitHub Insights (M1 traffic) | github.com built-in Traffic tab | $0 |

**Cost:** $0 ongoing.
**External dependency:** 1 (GitHub).
**Custom domain:** optional ($12/year); `*.github.io` is sufficient for MVP.

---

## 5. Acceptance Criteria

### Workflow Gates (5)

| Gate | Pass Criteria | Fail Action |
|------|---------------|-------------|
| **AC1** Agent research | ≥15 source fetches + structured JSON return + confidence field set | Retry 1x → fallback WebSearch |
| **AC2** Validation ≥2 sources | Coverage ≥95% (M4 release gate) | Force-override requires user confirmation |
| **AC3** Contradiction flag | >3pp marker, >5pp red flag, source-breakdown tooltip | UI render test fail → block |
| **AC4** Diff preview | Changed fields highlight + new models list + contradictions table | User cancel → rollback |
| **AC5** GitHub Pages deploy | Live within 2 min + 0 404s + JSON fetch <2s | Deploy fail → manual retry |

### Feature-Level AC (8)

| Feature | Pass Criteria |
|---------|---------------|
| **F1** Skill+agent | `/ledger-tracker-update` is invokable, agent delegation starts <5s |
| **F3** i18n switch | Instant change, no reload, localStorage persist |
| **F7** Cross-source validation | Release gate enforced (warning if <95%) |
| **F9** Weights editor | Total=100% constraint, live recalc <100ms, 4 presets work, reset-to-default works |
| **F10** PNG export | Section export no clipping, full page scroll-aware, iOS Safari + Chrome Android tests pass |
| **F11** Responsive | Mobile <640px + tablet 641-1024 + desktop >1024 — overflow=0 in each |
| **F12** Contradiction flagging | ≥3pp delta renders warning in UI, tooltip source breakdown |
| **F13** GPU VRAM | Auto-detect when WebGPU is supported + manual fallback when unsupported; compatibility badge fits/offload/too-large correct for each local model |

**Other must-have features (F2/F4/F5/F6/F8) are covered by implicit ACs:**
- F2 data regen → AC1 + AC4
- F4 deploy → AC5
- F5 GitHub Insights → built-in (no custom AC)
- F6 changelog → workflow step 12
- F8 README → documentation audit

---

## 6. Operational Disciplines

### Update Discipline (M5 metric: ≤14 days)
- **Target cadence:** weekly (event-triggered: when a new frontier model lands, the update happens anyway)
- **Hard cap:** 14-day max interval → stale badge appears in UI
- **Anti-pattern reference:** Aider 5-month-stale (leaderboard not updated since November 2025)

### Content Discipline (R3 burnout defense)
- **Hard cap:** ≤4 posts/month
- **Cadence:** CP1 event-triggered + CP2 1-2/month + CP3 quarterly
- **Burnout signals:** 1 missed update → recovery sprint, 2 missed updates → activate LITE mode

### Editorial Discipline (compound moat D)
- Cross-source ≥2 mandatory (M4 ≥95% coverage)
- Flag contradictions openly, do not hide them
- Default weights are editorial — document any change with rationale in the commit message

---

## 7. Update Walkthrough Example

**Scenario:** New Kimi K2.7 release; existing tracker is out of date.

```
1. /ledger-tracker-update
2. Skill: "Last update was 9 days ago. What scope?"
3. User: "New release: Kimi K2.7"
4. Skill → agent (scope: full, target_model_ids: ["kimi-k2-7"], include_unsloth: true)
5. Agent fetches: Moonshot blog + AA + llm-stats + BenchLM + LiveCodeBench + r/LocalLLaMA mentions
6. Agent returns: { confidence: HIGH, models: [{ id: "kimi-k2-7", updates: {...} }], contradictions: [], coverage: 0.97 }
7. Skill validates: ≥2 sources per score, no contradictions, 97% coverage
8. Skill diff preview:
   "Kimi K2.7 added. SWE-Pro: 60.2 (Moonshot), 58.9 (Scale SEAL). Δ=1.3pp OK.
    Bench coverage: 8/12"
9. User: "Approve, weight K2.7 entry standard"
10. Skill writes data/models.json (entry added) + data/sources.json (sources)
11. Skill appends CHANGELOG.md:
    ## 2026-04-24
    ### Added
    - Kimi K2.7 (Moonshot AI) — SWE-Pro 60.2, LCB 89.4, MIT license
12. User: git commit -m "data: add Kimi K2.7" && git push
13. GitHub Pages deploy ~1.5 min
14. Skill: "Live: https://sungurerdim.github.io/coding-models-tracker/"
```

---

## 8. Troubleshooting

| Problem | Solution |
|---------|----------|
| Skill not running | Check that `~/.claude/skills/coding-models-tracker/SKILL.md` exists |
| Agent timeout | Retry, then fallback WebSearch (skill does this automatically) |
| GitHub Pages 404 | Verify Settings → Pages → Source `main` branch / `/ (root)` |
| Weights editor not 100% | Use reset-to-default button, clear localStorage |
| WebGPU detect wrong | Use manual fallback dropdown |
| PNG export broken | Try scale: 1 in iOS Safari, scale: 2 in Chrome |
| TR/EN switch not working | Check i18n/{tr,en}.json files, clear localStorage |
| Validation <95% warning | Add missing sources manually or force-override + accept risk |
| Git conflict | `git pull --rebase` then push again |
