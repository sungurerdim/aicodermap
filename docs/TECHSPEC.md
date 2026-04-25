# AICoderMap — Technical Specification

**Version:** 1.0 | **April 24, 2026**

---

## 1. Overview

Static web tracker (GitHub Pages) + local Claude Code skill orchestrator + research agent. No backend, no DB, no auth. Vanilla JS, no build step. Single external service: GitHub Pages.

**Technology stack:** HTML5 + CSS3 (3-breakpoint responsive) + Vanilla JS (no framework) + JSON data files + WebGPU API (browser-native) + html2canvas (vendored). Skill is local at `~/.claude/skills/coding-models-tracker/` + agent at `~/.claude/agents/coding-models-research-agent.md`.

---

## 2. System Architecture

### Layers

**Frontend (GitHub Pages serves):**
```
index.html              — structure + interactive UI
assets/
  app.js               — fetch + render + weights editor + filter + PNG + GPU detect
  app.css              — responsive 3-breakpoint
  vendor/
    html2canvas.min.js — PNG export, self-hosted SRI
data/
  models.json          — MODELS array (skill auto-regenerates)
  sources.json         — per-score provenance (cross-source)
  gpu-database.json    — GPU → VRAM lookup
i18n/
  tr.json              — Turkish content
  en.json              — English content
CHANGELOG.md           — release history
README.md              — installation guide
```

**Skill (local, `~/.claude/skills/coding-models-tracker/`):**
```
SKILL.md               — orchestrator definition
```

**Research Agent (local, `~/.claude/agents/`):**
```
aicodermap-research-agent.md    — domain-specialized research-agent definition
```

### Communication Flow

```
User → Claude Code → Skill invocation
  → Agent (WebFetch, WebSearch) → return structured JSON
  → Skill validate (≥2 source, contradiction detect)
  → Diff preview UI
  → User approve
  → Skill write data/*.json
  → Skill append CHANGELOG.md
  → Git commit + push
  → GitHub Pages auto-deploy (~1-2 min)

Browser load:
  → fetch data/models.json + sources.json + gpu-database.json + i18n/{lang}.json
  → render
  → user interactions: weights editor, GPU filter, language toggle, PNG export
```

### Topology
- **Client:** browser only
- **Hosting:** GitHub Pages (CDN, SSL, free)
- **Backend:** none
- **Database:** none (JSON files)
- **Auth:** none (public read-only content)

---

## 3. Data Model

### `data/models.json` — MODELS array entry

```json
{
  "id": "opus-4-7",
  "name": "Claude Opus 4.7",
  "provider": "Anthropic",
  "released": "2026-04-16",
  "tier": "frontier",
  "open": false,
  "license": "Proprietary",
  "context": 1000000,
  "pricing": {
    "api": { "in": 5.00, "out": 25.00, "cacheHit": 0.50 },
    "subscription": "Max $200/month"
  },
  "bench": {
    "swePro": 64.3, "sweV": 87.6, "tb2": 69.4,
    "lcbV6": null, "aider": null, "tau2": 59,
    "hle": 46.9, "mcpA": 77.3, "gpqa": 94.2,
    "aime26": null, "mmmu": 77.3, "sweMulti": 79.3,
    "bfcl": null, "aaIdx": 57, "aaAgentic": null, "aaCoding": 53
  },
  "providers": 4,
  "uptime": 99.8,
  "ollamaSize": null,
  "unslothVariants": null,
  "vramRequirement": null,
  "strengthsKey": "opus-4-7.strengths",
  "weaknessesKey": "opus-4-7.weaknesses",
  "lastUpdated": "2026-04-24"
}
```

**Local model entry difference:**
```json
{
  "id": "qwen-3-6-27b",
  ...
  "ollamaSize": "18 GB (Q4_K_M, community)",
  "unslothVariants": [
    { "name": "UD-IQ2_XXS", "size": "9.39 GB", "vram": 10 },
    { "name": "UD-IQ3_XXS", "size": "11.2 GB", "vram": 12 },
    { "name": "Q4_K_M", "size": "18 GB", "vram": 20 }
  ],
  "vramRequirement": 18,
  ...
}
```

### `data/sources.json` — Per-score provenance

```json
{
  "opus-4-7.swePro": [
    { "value": 64.3, "source": "Anthropic official", "url": "https://...", "date": "2026-04-16", "tier": "S" },
    { "value": 62.1, "source": "Scale SEAL", "url": "https://labs.scale.com/...", "date": "2026-04-20", "tier": "I" }
  ]
}
```

**Contradiction rule:** between 2+ sources, **>3pp difference → flag**, **>5pp → red flag** (user manual resolution).

### `data/gpu-database.json` — GPU → VRAM lookup

```json
{
  "nvidia": {
    "rtx-4090": { "vram": 24, "displayName": "NVIDIA RTX 4090" },
    "rtx-4080": { "vram": 16, "displayName": "NVIDIA RTX 4080" },
    "rtx-3090": { "vram": 24, "displayName": "NVIDIA RTX 3090" },
    "rtx-3070": { "vram": 8, "displayName": "NVIDIA RTX 3070" }
  },
  "apple": {
    "m3-max-64gb": { "vram": 42, "displayName": "Apple M3 Max 64GB", "unifiedMemory": true, "usableRatio": 0.66 },
    "m4-pro-48gb": { "vram": 32, "displayName": "Apple M4 Pro 48GB", "unifiedMemory": true, "usableRatio": 0.66 }
  },
  "amd": {
    "rx-7900-xtx": { "vram": 24 }
  },
  "intel": {
    "arc-a770": { "vram": 16 }
  },
  "webgpuVendorMap": {
    "nvidia_rtx_4090": "nvidia.rtx-4090",
    "apple_gpu_m3_max": "apple.m3-max-64gb"
  }
}
```

### `i18n/{tr,en}.json` — Translations

```json
{
  "ui": {
    "compare": "Compare",
    "weightsEditor": "Weights Editor",
    "exportPng": "Download as PNG",
    "vramFilter": "Filter by my GPU VRAM"
  },
  "models": {
    "opus-4-7.strengths": "SWE-Pro leader; most mature agentic tool chain; Claude Code ecosystem",
    "opus-4-7.weaknesses": "Tokenizer 1.0-1.35x token inflation; verbose output"
  },
  "benchmarks": {
    "swePro.name": "SWE-bench Pro",
    "swePro.desc": "Contamination-resistant gold standard; 1865 tasks, 41 repos, multi-language"
  },
  "verdicts": {
    "preset.sweFocused": "SWE-focused",
    "preset.agenticFocused": "Agentic-focused",
    "preset.balanced": "Balanced",
    "preset.benchmarkOnly": "Benchmark-only"
  },
  "errors": {
    "fetchFailed": "Could not load data, please refresh the page",
    "weightsInvalid": "Weights must total 100"
  }
}
```

---

## 4. API Design

**No public API.** 4 internal API boundaries.

### 4.1 Skill → Research Agent (Claude Code Agent tool)

```
subagent_type: "coding-models-research-agent"
model: "sonnet"  // full scope (default)
        "haiku"  // search/local scope (faster, cheaper)
prompt:
  scope: <local | full | dependency | search>
  query: <constructed research query>
  idea_context: <compact JSON: confirmed dim summary>
  target_model_ids: <array, optional — specific models to refresh>
  include_unsloth: <boolean — research Unsloth UD variants for local models>
```

### 4.2 Research Agent → Skill (return JSON)

```json
{
  "confidence": "HIGH" | "MEDIUM" | "LOW",
  "synthesis": "1-2 sentence summary",
  "models": [
    {
      "id": "opus-4-7",
      "updates": {
        "bench": { "swePro": { "value": 64.3, "source": "Anthropic", "url": "...", "date": "2026-04-16" } },
        "pricing": { ... },
        "unslothVariants": [ ... ]
      }
    }
  ],
  "contradictions": [
    {
      "modelId": "opus-4-7",
      "benchmark": "swePro",
      "values": [
        { "value": 64.3, "source": "Anthropic" },
        { "value": 61.2, "source": "Scale SEAL" }
      ],
      "delta": 3.1
    }
  ],
  "sources": [...],
  "gaps": [...],
  "validationCoverage": 0.97
}
```

### 4.3 Browser → Data Files

```
GET /data/models.json         → MODELS array
GET /data/sources.json        → provenance map
GET /data/gpu-database.json   → GPU lookup
GET /i18n/tr.json | en.json   → translations
```

No auth, no query params, CORS-friendly static asset.

### 4.4 Browser → External Services

| Service | Method |
|---------|--------|
| GitHub Pages | Static fetch (built-in) |
| WebGPU | `navigator.gpu.requestAdapter()` → `requestAdapterInfo()` → `{vendor, architecture, device}` |
| html2canvas | `html2canvas(element, {scale:2, backgroundColor:'#0b0d10'}).then(canvas => canvas.toBlob())` |

### Error Handling

| Boundary | Failure | Action |
|----------|---------|--------|
| Agent fetch | HTTP fail | Retry 1x → fallback WebSearch → user "partial data, continue?" |
| Browser JSON parse | Parse error | Error banner + reload button |
| WebGPU | Unsupported | Silent fallback to manual VRAM input + GPU dropdown |
| html2canvas | Canvas taint / iframe | User alert: "Export failed, refresh the page or try a different section" |

---

## 5. Security

### XSS
- User-editable weights: integers 0-100 only (`type="number"` + regex whitelist)
- No `innerHTML`, only `textContent`
- No `eval()` or `new Function()`

### localStorage
- Schema validation on read (wrong shape → reset-to-default)
- Versioned keys: `cmt.v1.weights`, `cmt.v1.language`, `cmt.v1.vram`
- Migration plan to v2 already in place

### GDPR / Privacy
- GitHub Insights traffic measurement (cookie-free, no PII)
- localStorage user preferences only (no analytics)
- Footer note: "This site uses no cookies; anonymous traffic is measured via GitHub Insights"

### Data Integrity
- Agent output strictly via `JSON.parse` (no innerHTML)
- `strengths`/`weaknesses` fields: rendered via textContent only
- URL fields: `https://` prefix enforced, no allowlist but scheme validated

### Supply Chain
- `html2canvas` self-hosted (`assets/vendor/html2canvas.min.js`, SHA256 manually verified)
- Content Security Policy meta tag:
  ```html
  <meta http-equiv="Content-Security-Policy"
        content="default-src 'self'; script-src 'self' 'sha256-...'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;">
  ```

### Git/Repo
- No secrets in repo (no API keys)
- `.gitignore` comprehensive (`.env`, `node_modules/`, tmp)
- Pre-commit hook: `grep -r 'sk-\|ghp_\|api_key' src/` block

**Top 3 threats mitigated:** XSS, scraped content injection, supply chain.

---

## 6. Scalability

**Static site = trivially scalable.** GitHub Pages CDN handles up to 100GB/month bandwidth (free tier). 35 models × 14 benchmarks JSON ~50KB; 1M visitors/month = ~50GB → well within limits.

**Bottleneck:** Skill update workflow throughput (manual + research agent), practical max ~1-2 updates/day. The M5 metric (≤14 days) is well below this capacity.

**Phase 2 scale points:**
- 100K+ unique/month → consider a Cloudflare Pages mirror
- 50+ models → JSON pagination or per-tier files
- Custom analytics (Plausible/GoatCounter) → worthwhile at 5K+ unique/month

---

## 7. Non-Functional Requirements

| Category | Target |
|----------|-------|
| **Performance** | First Contentful Paint < 1s, Time to Interactive < 2s, JSON fetch < 2s |
| **Accessibility** | Lighthouse a11y ≥ 90, full keyboard navigation, ARIA labels |
| **SEO** | Lighthouse SEO ≥ 90, JSON-LD structured data, hreflang i18n, sitemap.xml |
| **Browser support** | Chrome/Edge ≥ last 2 versions, Firefox ≥ last 2, Safari ≥ last 2, iOS Safari ≥ 17 |
| **Responsive** | Mobile <640px, tablet 641-1024px, desktop >1024px — overflow=0 in each |
| **Uptime** | GitHub Pages SLA (~99.9%) |

---

## Appendix — External Dependencies

| Dependency | Version | License | Self-host? |
|------------|---------|---------|------------|
| html2canvas | latest stable (1.4.x) | MIT | yes (vendor) |
| GitHub Pages | — | platform | external |
| WebGPU API | browser-native | platform | — |

**No build/runtime dependencies** — vanilla, no npm/yarn, no node_modules.
