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

Five advantages — none of which any competitor combines:

- **A** Multi-language TR + EN coverage
- **B** Reusable skill+agent template (cloneable to other tracker domains)
- **C** **Coding-focused, user-editable composite, on top of vendor consensus** — site default is honest "vendor consensus" (median rank across AA Idx + AA Coding + AA Agentic); SWE-focused / agentic-focused / reasoning-focused / balanced editorial presets remain prominent for users who want a coding-oriented lens; full slider customization for everyone who knows their own workload.
- **D** Cross-source contradiction flagging + manual verification discipline (provenance trail + trustScore on every cell + ⚠/🚨 rozet)
- **E** **Cross-validation panel (AICM vs vendor composite)** — every model card surfaces an agreement indicator (🟢 consensus / 🟡 mild gap / 🔴 controversy) between our atomic-only composite and the vendor-aggregated composites we deliberately excluded from our score (no double-counting). Gives users a free second opinion + flags suspicious rankings automatically.

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
