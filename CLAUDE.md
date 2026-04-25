# AICoderMap

> Compare AI coding models with coding-focused benchmarks weighted your way — cross-verified, contradiction-flagged, in Turkish and English.

## Project Status

**Pre-implementation.** Idea fully specified via BrainLedger (`~/.ideas/coding-models-tracker.json`), 7 production docs üretildi (`docs/`), 5 hafta solo part-time geliştirme planı.

## Stack

- **Frontend:** Vanilla HTML/CSS/JS — no build step, no framework
- **Hosting:** GitHub Pages (tek external service, $0 sürekli)
- **Browser APIs:** WebGPU (GPU detection), localStorage (preferences)
- **Vendored libs:** html2canvas (PNG export, repo `assets/vendor/`)
- **Data:** Static JSON files (`data/models.json`, `data/sources.json`, `data/gpu-database.json`, `i18n/{tr,en}.json`)

**No npm, no node_modules, no build, no backend, no DB.**

**No GitHub Actions, no workflows, no CI/CD pipelines.** GitHub Pages default `main` branch deploy yeterli. Hiçbir `.github/workflows/*.yml` dosyası eklenmeyecek. Manuel disiplin > otomasyon kompleksiti (hobi proje, solo, $0 sürekli).

## Folder Structure

```
aicodermap/
├── index.html          # Main page (structure + interactive UI)
├── assets/
│   ├── app.js         # data fetch + render + weights + filter + GPU detect + PNG
│   ├── app.css        # 3-breakpoint responsive
│   └── vendor/
│       └── html2canvas.min.js
├── data/
│   ├── models.json    # MODELS array (skill auto-regenerates)
│   ├── sources.json   # per-score provenance
│   └── gpu-database.json
├── i18n/
│   ├── tr.json
│   └── en.json
├── docs/              # PRD, TechSpec, ImplGuide, Tasks, Workflow, Pitch
├── README.md
├── CHANGELOG.md
└── .gitignore
```

## Coding Conventions

- **No external dependencies** — all libs vendored in `assets/vendor/` with SHA256 manuel verify
- **Vanilla JS only** — no React, Vue, Astro, etc.
- **Semantic HTML5** — accessibility first (Lighthouse a11y ≥90)
- **CSS variables** for theming (`--bg`, `--surface`, `--accent`, etc.)
- **3 breakpoint responsive:** mobile <640px, tablet 641-1024px, desktop >1024px
- **No inline event handlers** — `addEventListener` only
- **No `innerHTML`** — only `textContent` (XSS defense)
- **No `eval()` / `new Function()`** — never
- **Schema validation on JSON load** — wrong shape → reset-to-default

## Data Update Workflow

Manuel via Claude Code skill (see `docs/WORKFLOW.md`):

1. User: `/ledger-tracker-update` (skill invoke)
2. Skill → coding-models-research-agent (web fetch + cross-source)
3. Validation: ≥2 source per score (≥%95 coverage), contradiction >3pp flag, >5pp red block
4. Diff preview + user approve
5. Skill writes `data/*.json` + appends `CHANGELOG.md`
6. User: `git commit && git push`
7. GitHub Pages auto-deploy ~1-2 dk

**M5 metric:** ≤14 gün max update interval (anti-Aider-stale discipline).

## Compound Moat

4 birleşik avantaj — hiçbir rakipte yok:
- **A** Multi-language TR + EN coverage
- **B** Reusable BrainLedger skill+agent template (other domains'a clone)
- **C** Coding-focused composite + user-editable weights UI ("our default, you change")
- **D** Cross-source contradiction flagging + manuel doğrulama disiplini

## Critical Files

- `data/models.json` — source of truth for all model data
- `data/sources.json` — provenance + contradiction detection input
- `data/gpu-database.json` — VRAM lookup for compatibility filter
- `i18n/{tr,en}.json` — content translations
- `.claude/skills/aicodermap/SKILL.md` — update orchestrator **(project-scoped)**
- `.claude/agents/aicodermap-research-agent.md` — domain research agent **(project-scoped)**

**Project-scoped:** Skill ve agent sadece bu projede (D:\GitHub\aicodermap) görünür. Başka projelerde aicodermap skill listesinde olmaz.

## Roadmap

5 milestone × 5 hafta solo part-time:
- **M1** Foundation (Hafta 1) — Repo + JSON schemas + agent base
- **M2** Core (Hafta 2) — Live tracker render
- **M3** Integration (Hafta 3) — 13 must-features
- **M4** Polish (Hafta 4) — SEO + responsive + Lighthouse
- **M5** Launch (Hafta 5) — Simultane TR + Global + 2 hafta validation

Buffer: Hafta 6 opsiyonel.

## License

MIT — kod ve veri kamuya açık. Attribution rica edilir.

## See Also

- `docs/PRD.md` — Product Requirements
- `docs/TECHSPEC.md` — System architecture detayı
- `docs/IMPLGUIDE.md` — ⭐ Coding-ready implementation guide (Claude Code session için)
- `docs/TASKS.md` — 23 task / 5 milestone breakdown
- `docs/WORKFLOW.md` — Update workflow (14 + 5 exception)
- `~/.ideas/coding-models-tracker.json` — Full BrainLedger idea entry (44 decisions traceable)
