# AICoderMap

> A decision reference that cuts coding-LLM model selection from hours to seconds: ranked by your priorities (SWE / agentic / balanced / custom), source contradictions flagged ⚠/🚨, GPU-fitting local options labeled with the exact Unsloth quant that runs, refreshed every 14 days at most. Turkish + English UI.

## Project Status

**Implementation in progress (M3 onward).** Foundation seeded with TECHSPEC examples; full data populated via the project skill. Built solo, part-time over 5 weeks.

## Stack

- **Frontend:** Vanilla HTML/CSS/JS — no build step, no framework
- **Hosting:** GitHub Pages (single external service, $0 ongoing)
- **Browser APIs:** WebGPU (GPU detection), localStorage (preferences, theme, weights, filters, sort)
- **Vendored libs:** html2canvas (PNG export, repo `assets/vendor/`)
- **Data:** Static JSON files (`data/models.json`, `data/sources.json`, `data/gpu-database.json`, `i18n/{tr,en}.json`)

**No npm, no node_modules, no build, no backend, no DB.**

**No GitHub Actions, no workflows, no CI/CD pipelines.** GitHub Pages default `main`-branch deploy is enough. No `.github/workflows/*.yml` files will be added. Manual discipline beats automation complexity for a solo, $0-ongoing hobby project.

## Folder Structure

```
aicodermap/
├── index.html              # Main page (structure + interactive UI)
├── assets/
│   ├── js/                 # ES modules (browser-loaded, no build) — 15 files
│   │   ├── main.js         # bootstrap entry (split-phase init)
│   │   ├── core.js         # State + constants + STORAGE + schema validation
│   │   ├── i18n.js         # t() + applyI18n + loadI18n
│   │   ├── data.js         # fetch + score + contradiction + pricing + format
│   │   ├── gpu.js          # gpuCompat + WebGPU detect + filter predicate
│   │   ├── dom.js          # el + clear + cameraIconButton + showToast
│   │   ├── overlay.js      # tooltip + html2canvas export
│   │   ├── freshness.js    # ETag-based stale-data banner + auto-refresh
│   │   ├── sources.js      # provenance lookup + contradiction tier hand-off
│   │   ├── url-state.js    # URL ⇄ state codec (deep-link share + restore)
│   │   ├── render-controls.js  # weights editor + theme/lang sync
│   │   ├── render-card.js  # buildModelCard (split into 9 sub-builders)
│   │   ├── render-table.js # comparison table + model list + renderAll
│   │   ├── render-privacy.js   # privacy & compliance section table
│   │   └── events.js       # wireEvents (split by concern) + switchLanguage
│   ├── css/                # 3-breakpoint responsive, dark/light themes
│   │   ├── base.css        # vars, themes, reset, form controls, toggles
│   │   ├── layout.css      # header, nav, main, cards, footer, export
│   │   ├── table.css       # comparison table
│   │   ├── controls.css    # weights editor + filters
│   │   ├── models.css      # model cards, bench cells, badges, tooltip
│   │   ├── toast.css       # toast notification host
│   │   └── responsive.css  # tablet + desktop + reduced-motion
│   ├── test/
│   │   └── smoke.html      # vanilla in-browser unit harness (no deps)
│   └── vendor/
│       └── html2canvas.min.js
├── data/
│   ├── models.json         # MODELS array (skill auto-regenerates)
│   ├── sources.json        # per-score provenance
│   └── gpu-database.json
├── i18n/
│   ├── tr.json
│   └── en.json
├── docs/                   # PRD, TechSpec, ImplGuide, Tasks, Workflow, Pitch, TestPlan
├── README.md
├── CHANGELOG.md
├── LICENSE
├── CONTRIBUTING.md
├── .editorconfig
└── .gitignore
```

## Coding Conventions

- **No external dependencies** — all libs vendored in `assets/vendor/` with SHA256 manually verified
- **Vanilla JS only** — no React, Vue, Astro, etc.
- **Semantic HTML5** — accessibility first (Lighthouse a11y ≥90)
- **CSS variables** for theming (`--bg`, `--surface`, `--accent`, …) with `html[data-theme="light|dark"]` overrides
- **3 breakpoints:** mobile <640px, tablet 641–1024px, desktop >1024px
- **No inline event handlers** — `addEventListener` only
- **No `innerHTML`** — `textContent` only (XSS defense)
- **No `eval()` / `new Function()`** — never
- **Schema validation on JSON load** — wrong shape → reset-to-default
- **Turkish locale uppercase trap:** never use CSS `text-transform: uppercase` for mixed-language text. Write the uppercase form directly in i18n values (TR keeps diacritics, EN/loanwords keep dotless I).

## Data Update Workflow

Manual via Claude Code skill (see `docs/WORKFLOW.md`):

1. User: `/aicodermap` (skill invoke)
2. Skill → `aicodermap-research-agent` (web fetch + cross-source)
3. Validation: ≥2 sources per score (≥95% coverage), 3pp delta → ⚠ flag, 5pp delta → 🚨 release block
4. Diff preview + user approve
5. Skill writes `data/*.json` + appends `CHANGELOG.md`
6. User: `git commit && git push`
7. GitHub Pages auto-deploy ~1–2 min

**M5 metric:** ≤14-day max update interval (anti-Aider-stale discipline).

## Compound Moat

Four advantages — none of which any competitor combines:

- **A** Multi-language TR + EN coverage
- **B** Reusable skill+agent template (cloneable to other tracker domains)
- **C** Coding-focused composite + user-editable weights UI ("our default, you change")
- **D** Cross-source contradiction flagging + manual verification discipline

## Critical Files

- `data/models.json` — source of truth for all model data
- `data/sources.json` — provenance + contradiction detection input
- `data/gpu-database.json` — VRAM lookup for compatibility filter
- `i18n/{tr,en}.json` — content translations (the only place TR copy lives)
- `.claude/skills/aicodermap/SKILL.md` — update orchestrator **(project-scoped)**
- `.claude/agents/aicodermap-research-agent.md` — domain research agent **(project-scoped)**

**Project-scoped:** the skill and agent are visible only inside `D:\GitHub\aicodermap`. They do not appear in other projects' skill lists.

## Roadmap

5 milestones × 5 weeks solo part-time:

- **M1** Foundation (Week 1) — Repo + JSON schemas + research agent base
- **M2** Core (Week 2) — Live tracker render
- **M3** Integration (Week 3) — 13 must-have features
- **M4** Polish (Week 4) — SEO + responsive + Lighthouse
- **M5** Launch (Week 5) — Simultaneous TR + Global launch + 2-week validation

Buffer: Week 6 optional.

## License

MIT — code and data are public. Attribution appreciated.

## See Also

- `docs/PRD.md` — Product Requirements
- `docs/TECHSPEC.md` — System architecture detail
- `docs/IMPLGUIDE.md` — ⭐ Coding-ready implementation guide (for Claude Code sessions)
- `docs/TASKS.md` — 23-task / 5-milestone breakdown
- `docs/WORKFLOW.md` — Update workflow (14 happy-path + 5 exception steps)

## Blueprint Profile

**Project:** AICoderMap | **Type:** Frontend (vanilla SPA) | **Stack:** HTML5 + CSS3 + Vanilla JS + JSON | **Target:** Production

### Config
- **Priorities:** Security, Code Quality, Architecture, Documentation
- **Constraints:** Vanilla JS only, no build step, no runtime dependencies
- **Data:** No sensitive data (public model metadata only) | **Regulations:** none
- **Audience:** Public users | **Deploy:** GitHub Pages (main-branch auto-deploy)

### Project Map
```
Entry: index.html → assets/vendor/html2canvas.min.js (defer, SRI)
                  + assets/js/main.js (type="module")

Modules:
  assets/js/        → 15 ES modules (browser-loaded, no build, every file <500L)
    main.js         → bootstrap orchestrator (split-phase init)
    core.js         → State + STORAGE + BENCH_KEYS (26) + DEFAULTS + PRESETS (5) + schema validation
    i18n.js         → t() + applyI18n + loadI18n
    data.js         → fetch + score + contradiction + pricing + format
    gpu.js          → gpuCompat + WebGPU detect + filter predicate
    dom.js          → el + clear + cameraIconButton + showToast
    overlay.js      → contradiction tooltip + html2canvas export
    freshness.js    → ETag-based stale-data banner + auto-refresh prompt
    sources.js      → provenance lookup + tier hand-off for contradiction UI
    url-state.js    → URL query-string ⇄ live State codec (deep-link share)
    render-controls.js  → weights editor + theme/lang sync
    render-card.js  → buildModelCard split into 9 sub-builders (orchestrator 34L)
    render-table.js → comparison table + model list + renderAll
    render-privacy.js   → privacy & compliance section table
    events.js       → wireEvents (split into wireXxx by concern) + switchLanguage
  assets/css/       → 7 stylesheets (cascade-ordered in index.html)
    base / layout / table / controls / models / toast / responsive
  assets/test/      → smoke.html — vanilla in-browser unit harness (14 tests, no deps)
  assets/vendor/    → html2canvas.min.js (1.4.1, SHA256 e87e5507…8cb)
  data/             → JSON SSOT (3 canonical + whitelist + external/)
    models.json     → 60 models, schema v2 multi-provider pricing, 26 bench keys
    sources.json    → per-(modelId,benchKey) provenance with trustScore
    gpu-database.json     → NVIDIA / Apple / AMD / Intel + webgpuVendorMap + 8 featuredPresets
    sources-whitelist.json → research-agent allowed-fetch list (16 coreBenchKeys + 10 emerging + 3 deprecated, 35 leaderboards)
  i18n/             → content translations (tr.json + en.json, 323 keys each, 0 drift)
  scripts/          → skill helpers (stdlib-only Python + 2 Node scripts)
  auto/             → ds-tune harness (eval.py + bench.sh/bat + fixtures.json)
  docs/             → 7 spec docs (PRD, TECHSPEC, IMPLGUIDE, TASKS, WORKFLOW, PITCH, TEST_PLAN)
  .claude/          → project-scoped skill + agent

Data Flow:
  Page load → main.js bootstrapTheme → bootstrapPrefs → bootstrapI18n
            → bootstrapData (fetch + schema-validate) → restoreFilterUi → bootstrapGpu
            → renderWeightsEditor + renderAll (renderTable + renderModelCards) → wireEvents
  User input → writeStorage(localStorage) → debounced renderAll (search 200ms)
  Update cycle: /aicodermap → research-agent (WebSearch+WebFetch) → .aicodermap-agent-out.json
              → scripts/merge.py → data/*.json + CHANGELOG.md → git push → GitHub Pages deploy

External: html2canvas (vendored, SRI-pinned); WebGPU API (browser-native); localStorage (prefs);
          GitHub Pages (deploy); Anthropic Claude Code (skill+agent runtime, dev-time only)

Toolchain: Python 3.10+ stdlib only | Node for regex-lint + module syntax check
           bash + bat (cross-platform bench) | No CI/CD by design (CLAUDE.md policy)
           Tests: assets/test/smoke.html + docs/TEST_PLAN.md (manual runbook)
```

### Ideal Metrics
| Metric | Target |
|--------|--------|
| Coupling (avg deps per module) | ≤ 4 |
| Cohesion (LCOM low) | ≥ 0.7 |
| Cyclomatic Complexity / function | ≤ 15 |
| Function lines | ≤ 50 |
| File lines | ≤ 500 |
| Test coverage (lines) | ≥ 70% |

### Current Scores
| Dimension | Score | Status |
|-----------|-------|--------|
| Security & Privacy | 95 | OK |
| Code Quality | 92 | OK |
| Architecture | 90 | OK |
| Performance | 95 | OK |
| Resilience | 92 | OK |
| Testing | 70 | OK |
| Stack Health | 95 | OK |
| DX | 90 | OK |
| Documentation | 95 | OK |
| Overall | 90 | OK |

### Last Run
- 2026-04-28: ds-review --strategic --force-approve | Applied 15 (ES module split into 11 files + CSS split into 7 files + buildModelCard decomposed into 9 sub-builders + toast component replaces alert + smoke harness + TEST_PLAN.md) | Overall 75→90

## End Blueprint Profile
