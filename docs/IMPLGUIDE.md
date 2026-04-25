# AICoderMap — Implementation Guide

**Version:** 1.0 | **April 24, 2026** | **Coding-ready** for Claude Code session

---

## 1. Quick Start

```bash
# 1. Repo init
cd ~/projects
git init coding-models-tracker
cd coding-models-tracker
gh repo create coding-models-tracker --public --description "Compare AI coding models with coding-focused benchmarks weighted your way"

# 2. Skill setup (local)
mkdir -p ~/.claude/skills/coding-models-tracker
mkdir -p ~/.claude/agents

# Copy SKILL.md and agent.md from export (see Project Kickstart)

# 3. Folder structure
mkdir -p assets/vendor data i18n
touch index.html assets/app.js assets/app.css
touch data/models.json data/sources.json data/gpu-database.json
touch i18n/tr.json i18n/en.json
touch CHANGELOG.md README.md .gitignore

# 4. html2canvas vendor file
curl -o assets/vendor/html2canvas.min.js \
  https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js
# SHA256 verify (security)
echo "<expected_sha>  assets/vendor/html2canvas.min.js" | sha256sum -c

# 5. GitHub Pages
# Settings → Pages → Source: main branch / root → Save
# (Auto-deploy, no GitHub Actions required)
```

---

## 2. Architecture Overview

**Stack:** Vanilla HTML/CSS/JS + JSON data files + GitHub Pages (no build step, no backend, no DB).

**Layers:**
1. **Frontend** — Browser fetches JSON, renders, handles interactions
2. **Skill orchestrator** — Local Claude Code skill, triggers update workflow
3. **Research agent** — Local Claude Code agent, scrapes data sources
4. **External services** — GitHub Pages (static hosting), GitHub Insights (analytics)

**Data flow:** User triggers skill → agent scrapes → validate ≥2 sources → diff preview → user approve → write data/*.json → git commit → GitHub Pages auto-deploy → browser loads new data on next visit.

---

## 3. Data Schema (DDL-equivalent JSON)

### `data/models.json` — Array of model entries

```typescript
type ModelEntry = {
  id: string;                    // e.g., "opus-4-7"
  name: string;                  // "Claude Opus 4.7"
  provider: string;              // "Anthropic"
  released: string;              // ISO date "2026-04-16"
  tier: "frontier" | "open-tier1" | "openrouter" | "gemma" | "ollama";
  open: boolean;
  license: string;               // "MIT" | "Apache 2.0" | "Proprietary" | ...
  context: number;               // tokens
  pricing: {
    api: { in: number; out: number; cacheHit: number | null };
    subscription: string | null;
  };
  bench: {
    swePro: number | null;
    sweV: number | null;
    tb2: number | null;
    lcbV6: number | null;
    aider: number | null;
    tau2: number | null;
    aaCoding: number | null;
    aaAgentic: number | null;
    mcpA: number | null;
    gpqa: number | null;
    sweMulti: number | null;
    hle: number | null;
    aaIdx: number | null;
  };
  providers: number;             // OpenRouter provider count
  uptime: number;                // 0-100 percentage
  ollamaSize: string | null;     // local only: "18 GB (Q4_K_M)"
  unslothVariants: Array<{       // local only
    name: string;                // "UD-IQ2_XXS"
    size: string;                // "9.39 GB"
    vram: number;                // GB int
  }> | null;
  vramRequirement: number | null; // GB int, local only
  strengthsKey: string;          // i18n lookup "opus-4-7.strengths"
  weaknessesKey: string;
  lastUpdated: string;           // ISO date
};
```

### `data/sources.json` — Per-score provenance

```typescript
type SourcesMap = {
  [modelIdDotBenchKey: string]: Array<{
    value: number;
    source: string;
    url: string;
    date: string;                // ISO
    tier: "S" | "I" | "C";       // self-reported / independent / community
  }>;
};
// Example key: "opus-4-7.swePro"
```

### `data/gpu-database.json` — GPU lookup

```typescript
type GpuDatabase = {
  nvidia: Record<string, { vram: number; displayName: string; released?: string }>;
  apple: Record<string, { vram: number; displayName: string; unifiedMemory: boolean; usableRatio: number }>;
  amd: Record<string, { vram: number; displayName?: string }>;
  intel: Record<string, { vram: number; displayName?: string }>;
  webgpuVendorMap: Record<string, string>;  // "nvidia_rtx_4090" → "nvidia.rtx-4090"
};
```

### `i18n/{tr,en}.json` — Content

```typescript
type I18n = {
  ui: Record<string, string>;            // button labels, tooltips
  models: Record<string, string>;        // strengthsKey/weaknessesKey content
  benchmarks: Record<string, string>;    // benchmark names + descriptions
  verdicts: Record<string, string>;      // preset profile names
  errors: Record<string, string>;        // error messages
};
```

---

## 4. API Contracts

### 4.1 Skill → Research Agent

**Invocation:**
```typescript
Agent({
  subagent_type: "coding-models-research-agent",
  model: "sonnet",  // or "haiku" for search/local scope
  prompt: `
    scope: full
    query: <constructed research query>
    idea_context: ${JSON.stringify(idea_summary)}
    target_model_ids: ${JSON.stringify(model_ids)}
    include_unsloth: true
  `
});
```

### 4.2 Research Agent → Skill (return)

**Schema:** See TechSpec §4.2 for full structure. Required fields: `confidence`, `synthesis`, `models[]`, `contradictions[]`, `sources[]`, `gaps[]`, `validationCoverage`.

**Validation by skill:**
```javascript
function validateAgentOutput(out) {
  if (!out.confidence || !["HIGH","MEDIUM","LOW"].includes(out.confidence)) throw new Error("confidence missing");
  if (!Array.isArray(out.models)) throw new Error("models missing");
  if (out.validationCoverage < 0.95) {
    return { ok: false, reason: "coverage_below_threshold", coverage: out.validationCoverage };
  }
  return { ok: true };
}
```

### 4.3 Browser fetch

```javascript
async function loadData() {
  const [models, sources, gpu, i18n] = await Promise.all([
    fetch('/data/models.json').then(r => r.json()),
    fetch('/data/sources.json').then(r => r.json()),
    fetch('/data/gpu-database.json').then(r => r.json()),
    fetch(`/i18n/${getLang()}.json`).then(r => r.json())
  ]);
  return { models, sources, gpu, i18n };
}
```

---

## 5. Implementation Order (numbered, dependencies)

**Phase 1 — Foundation (T1-T4 + T12, parallel after T1)**

1. **T1 [30 min]** — Repo init + GitHub Pages setup
   - `gh repo create`, push initial commit, enable Pages
   - Create folder structure, `.gitignore`, README stub
2. **T2 [1 hr]** — `data/models.json` schema + migrate from `docs/coding-models-comparison-2026-04-22.html`
   - Extract MODELS array from HTML, transform to new schema with nested `pricing` object, `lastUpdated`
3. **T3 [1 hr]** — `data/sources.json` provenance migrate
   - Per-score source attribution from existing HTML notes
4. **T4 [1.5 hr]** — `data/gpu-database.json` build
   - NVIDIA RTX 40/30/20, Apple M1-M4 tiers, AMD RX 7000, Intel Arc
5. **T12 [1.5 hr]** — `aicodermap-research-agent.md` definition
   - Project-scoped agent under `.claude/agents/`
   - Domain-customize source list (AA, llm-stats, BenchLM, aider, Scale SEAL, vals.ai, LiveCodeBench, BFCL, SWE-rebench, HF, official blogs, Ollama, Unsloth)

**Phase 2 — Core (T5, T6, T13, parallel after Phase 1)**

6. **T5 [2 hr]** — `index.html` structure + `assets/app.css` 3-breakpoint responsive
   - Mobile <640px, tablet 641-1024px, desktop >1024px
   - Copy CSS variables from existing HTML report (`--bg`, `--surface`, `--accent`, etc.)
7. **T6 [1 hr]** — `assets/app.js` data fetch + render MODELS
   - `loadData()` (see §4.3), render to `<table>` or `<div class="models-grid">`
   - Reactive: data load → render → user interactions trigger re-render
8. **T13 [2 hr]** — `~/.claude/skills/coding-models-tracker/SKILL.md` orchestrator
   - 14 happy path steps (see WORKFLOW.md)
   - User scope selection (full/specific/new), agent delegation, validation gate, diff preview, write JSON, append CHANGELOG, git commit prompt

**Phase 3 — Features (T7-T11, T15, parallel after T6)**

9. **T7 [2 hr]** — Dynamic weights editor UI
   - `<input type="number" min="0" max="100">` per benchmark
   - Total=100% live constraint (auto-rebalance other sliders proportionally)
   - Live composite recalc < 100ms
   - 4 preset buttons: SWE-focused, Agentic-focused, Balanced, Benchmark-only
   - Reset-to-default button
   - localStorage persist: `cmt.v1.weights`
10. **T8 [1.5 hr]** — i18n TR/EN switch
    - Runtime fetch `/i18n/{lang}.json`
    - `<html lang>` attribute update
    - All `data-i18n-key` attributes → textContent replace
    - localStorage persist: `cmt.v1.language`
11. **T9 [1 hr]** — Contradiction flagging UI
    - For each cell with score: lookup `sources.json[modelId.bench]`
    - If 2+ values with delta > 3pp: render warning badge
    - If delta > 5pp: red badge
    - Click → tooltip with source breakdown (value, source, url, date, tier)
12. **T10 [1 hr]** — PNG export (html2canvas vendored)
    - Per-section button: `<button data-export-section="master">PNG</button>`
    - Full-page button: `<button id="export-full">Full page PNG</button>`
    - Export-mode CSS class: hide sticky nav, no overflow clipping, print-friendly
    - `html2canvas(element, {scale: 2, backgroundColor: '#0b0d10'}).then(canvas => canvas.toBlob(blob => download(blob)))`
13. **T11 [2 hr]** — GPU VRAM detection + filter
    - Auto: `await navigator.gpu.requestAdapter()` → `requestAdapterInfo()` → lookup in `gpu-database.json.webgpuVendorMap`
    - Manual fallback: `<select>` GPU dropdown + `<input type="number">` VRAM override
    - Filter UI: `<input type="checkbox">` "Show only models that run on my GPU"
    - Per local model: compatibility badge (fits ≤vram-1, offload ≤vram, too-large >vram)
    - Unsloth UD priority: select highest-quality variant ≤ user vram, recommend
    - localStorage persist: `cmt.v1.vram`
14. **T15 [1 hr]** — Skill validation logic
    - In `SKILL.md`: validate agent output (≥2 sources per score, ≥95% coverage, contradiction detect)
    - Block release if coverage < 95%, show user warning + force-override option
    - >5pp contradiction: red flag + user manual pick required

**Phase 4 — Polish (parallel)**

15. **T14 [30 min]** — Skill install script + docs (`README.md` skill section)
16. **T21 [1 hr]** — SEO: meta tags + Open Graph + JSON-LD (Article + Dataset) + hreflang + sitemap.xml + robots.txt
17. **T22 [30 min]** — `CHANGELOG.md` bootstrap + format convention (Keep a Changelog style)

**Phase 5 — Test (sync gate)**

18. **T23 [2-3 hr]** — End-to-end: all 13 AC pass
    - Manual test plan: weights total constraint, contradiction render, GPU filter, PNG export iOS Safari + Chrome Android, responsive 3 breakpoints, i18n switch, skill invocation E2E

**Phase 6 — Content + Launch (parallel after T23)**

19. **T16 [1 hr]** — README.md TR+EN + skill installation guide
20. **T17 [2 hr]** — 2 launch-day CP1 analysis posts (deep-dive on DeepSeek V4 + Qwen3.6-27B)
21. **T18 [2 hr]** — 1 CP2 evergreen guide: "Top 5 coding models for 8GB VRAM devs" (QW1)
22. **T19 [3 hr]** — 1 CP3 quarterly: "SWE-bench Verified vs Pro: why a 35-point gap?" (QW2)
23. **T20 [1.5 hr]** — Launch playbook: channel list + ready-to-post text TR+EN

---

## 6. Error Handling Matrix

| Layer | Scenario | Detection | Action | User Visible? |
|-------|----------|-----------|--------|---------------|
| Agent | HTTP fetch fail | catch network error | Retry 1x → fallback WebSearch → user "partial data, continue?" | Yes (skill prompt) |
| Agent | Empty/invalid response | schema validation | Skill abort, show last known good state | Yes |
| Skill | Validation coverage <95% | M4 release gate | Warning + missing source list + force-override option | Yes |
| Skill | Contradiction >5pp | sources.json delta calc | Red flag + source breakdown + user manual pick | Yes |
| Skill | User declines diff | user input "no" | Rollback (no file write, no commit) | Yes (confirmation) |
| Skill | Git conflict (parallel edit) | `git push` fails | Skill abort + "pull first" message | Yes |
| Browser | JSON parse fail | try/catch JSON.parse | Error banner + reload button | Yes |
| Browser | WebGPU unsupported | `navigator.gpu === undefined` | Silent fallback → manual VRAM input | No (graceful) |
| Browser | localStorage corrupt | schema validation | Reset-to-default + console warn | No |
| Browser | html2canvas fail | catch promise reject | Alert: "Export failed, refresh the page" | Yes |
| Browser | i18n fetch fail | catch network error | Fallback to TR (default), console warn | No |
| GitHub Pages | Deploy delay >5 min | manual check post-push | Skill warns user, suggest GitHub status check | Yes |

---

## 7. Deployment

### Initial Setup
1. Push to `main` branch
2. GitHub Settings → Pages → Source: `main` branch / root → Save
3. Wait ~1-2 min for first deploy
4. Verify at `https://<username>.github.io/coding-models-tracker/`

### Update Deploy (every skill run)
1. Skill writes data/*.json + CHANGELOG.md
2. User runs `git add . && git commit -m "data: update <date>" && git push`
3. GitHub Pages auto-deploy (~1-2 min)
4. Verify M5 metric (≤14 days max update interval) via git log

### No-build verification
- No `package.json`, `npm`, `node_modules`
- No CI/CD workflow (default Pages deploy is sufficient)
- All assets in repo (`assets/vendor/html2canvas.min.js`)

---

## 8. Configuration Reference

### `WEIGHTS` (default editorial weights — `app.js`)

```javascript
const DEFAULT_WEIGHTS = {
  swePro: 0.22,
  tb2: 0.15,
  lcbV6: 0.15,
  sweV: 0.10,
  aider: 0.10,
  aaCoding: 0.07,
  aaAgentic: 0.05,
  tau2: 0.05,
  mcpA: 0.05,
  gpqa: 0.02,
  sweMulti: 0.02,
  hle: 0.02
};
// Total: 1.00 (100%)
```

### Preset profiles

```javascript
const PRESETS = {
  "swe-focused":     { swePro: 0.30, sweV: 0.20, sweMulti: 0.15, tb2: 0.10, lcbV6: 0.10, aider: 0.10, aaCoding: 0.05 },
  "agentic-focused": { tb2: 0.25, mcpA: 0.20, tau2: 0.15, aaAgentic: 0.15, swePro: 0.10, lcbV6: 0.10, gpqa: 0.05 },
  "balanced":        DEFAULT_WEIGHTS,
  "benchmark-only":  { swePro: 0.20, sweV: 0.15, tb2: 0.15, lcbV6: 0.15, aider: 0.10, gpqa: 0.10, sweMulti: 0.10, hle: 0.05 }
};
```

### Contradiction thresholds

```javascript
const CONTRADICTION_WARN = 3.0;  // ≥3pp delta → warning flag
const CONTRADICTION_BLOCK = 5.0; // ≥5pp delta → red flag (release block)
```

### Validation gate

```javascript
const VALIDATION_COVERAGE_MIN = 0.95;  // ≥95% of benchmarks must have ≥2 sources (M4 metric)
const STALE_THRESHOLD_DAYS = 14;       // M5 metric: ≤14 days max update interval
```

### Latest stable versions (verify before final commit)

| Library | Version | URL | SHA256 |
|---------|---------|-----|--------|
| html2canvas | 1.4.1 (Apr 2024 latest) | https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js | manual verify on download |

**Action:** Run `Agent` with `scope: dependency` to verify the latest stable version before T10 implementation.

---

## 9. Testing & Validation

### E2E test plan (T23)

| AC | Test |
|----|------|
| AC1 Agent research | Run skill, verify ≥15 source fetches + structured JSON return |
| AC2 ≥2 source coverage | Inspect `validationCoverage`, must be ≥0.95 |
| AC3 Contradiction flag | Force a 5pp delta in sources.json, verify red flag UI |
| AC4 Diff preview | Run skill update, verify diff UI shows changed fields |
| AC5 GitHub Pages deploy | Push commit, verify live in <2 min + JSON fetch <2s |
| AC-F1 Skill+agent | Invoke `/ledger-tracker-update`, verify <5s agent start |
| AC-F3 i18n switch | Toggle TR↔EN, verify no reload, localStorage persist |
| AC-F9 Weights editor | Slide swePro to 50%, verify others auto-rebalance to 50% total |
| AC-F10 PNG export | Export section + full page, verify no clipping iOS Safari + Chrome Android |
| AC-F11 Responsive | DevTools 375×667 (mobile) + 768×1024 (tablet) + 1920×1080 (desktop), verify overflow=0 |
| AC-F12 Contradiction render | Verify 3pp warning, 5pp red, tooltip source breakdown |
| AC-F13 GPU VRAM | Test on RTX 4090 (auto), test fallback in Firefox (manual), verify badge per local model |

### Lighthouse minimums (M4 polish gate)
- Performance ≥ 90
- Accessibility ≥ 90
- Best Practices ≥ 90
- SEO ≥ 90

---

## 10. Project Kickstart Checklist

After all 23 tasks complete + M4 polish:

- [ ] Public repo created (`gh repo create coding-models-tracker --public`)
- [ ] All files in `main` branch
- [ ] GitHub Pages enabled, live URL verified
- [ ] `~/.claude/skills/coding-models-tracker/SKILL.md` installed
- [ ] `~/.claude/agents/coding-models-research-agent.md` installed
- [ ] First skill run successful (validation passes)
- [ ] CHANGELOG v1.0 entry committed
- [ ] README TR+EN reviewed
- [ ] All 13 AC E2E tests pass
- [ ] Lighthouse audit ≥90 all categories
- [ ] M5 launch playbook ready (`T20` deliverable)
- [ ] 3 launch-day posts drafted (DeepSeek V4 + Qwen3.6-27B + 8GB VRAM guide)
- [ ] Pinned issue: "Launch Day [date]"

**Ready for M5 Launch Day.**
