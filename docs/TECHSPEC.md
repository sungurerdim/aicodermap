# Coding Models Tracker — Technical Specification

**Sürüm:** 1.0 | **24 Nisan 2026**

---

## 1. Genel Bakış

Static web tracker (GitHub Pages) + local Claude Code skill orchestrator + research agent. No backend, no DB, no auth. Vanilla JS, no build step. Tek external service: GitHub Pages.

**Teknoloji yığını:** HTML5 + CSS3 (3 breakpoint responsive) + Vanilla JS (no framework) + JSON data files + WebGPU API (browser-native) + html2canvas (vendored). Skill yerel `~/.claude/skills/coding-models-tracker/` + agent `~/.claude/agents/coding-models-research-agent.md`.

---

## 2. Sistem Mimarisi

### Katmanlar

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
  tr.json              — Türkçe content
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
coding-models-research-agent.md  — ledger-research-agent template clone, domain-specialized
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
  → GitHub Pages auto-deploy (~1-2 dk)

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

## 3. Veri Modeli

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
    "subscription": "Max $200/ay"
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

**Local model entry farkı:**
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

**Contradiction rule:** 2+ source arasında **>3pp fark → ⚠ flag**, **>5pp → 🚨 red flag** (user manual resolution).

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
    "compare": "Karşılaştır",
    "weightsEditor": "Ağırlık Editörü",
    "exportPng": "PNG Olarak İndir",
    "vramFilter": "GPU VRAM'ime göre filtrele"
  },
  "models": {
    "opus-4-7.strengths": "SWE-Pro lider; Agentic tool chain en olgun; Claude Code ekosistem",
    "opus-4-7.weaknesses": "Tokenizer 1.0-1.35× token artışı; verbose output"
  },
  "benchmarks": {
    "swePro.name": "SWE-bench Pro",
    "swePro.desc": "Contamination-resistant gold standard; 1865 task, 41 repo, multi-language"
  },
  "verdicts": {
    "preset.sweFocused": "SWE-odaklı",
    "preset.agenticFocused": "Agentic-odaklı",
    "preset.balanced": "Dengeli",
    "preset.benchmarkOnly": "Sadece Benchmark"
  },
  "errors": {
    "fetchFailed": "Veri yüklenemedi, sayfayı yenileyin",
    "weightsInvalid": "Ağırlıklar toplamı 100 olmalı"
  }
}
```

---

## 4. API Tasarımı

**Public API yok.** 4 internal API boundary.

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
  include_unsloth: <boolean — local models için Unsloth UD variants araştır>
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
| Agent fetch | HTTP fail | Retry 1× → fallback WebSearch → user "kısmi veri, devam?" |
| Browser JSON parse | Parse error | Error banner + reload button |
| WebGPU | Unsupported | Silent fallback to manual VRAM input + GPU dropdown |
| html2canvas | Canvas taint / iframe | User alert: "Export failed, sayfa yenileyin veya farklı bölüm deneyin" |

---

## 5. Güvenlik

### XSS
- User-editable weights: sadece integer 0-100 (`type="number"` + regex whitelist)
- Hiç `innerHTML`, sadece `textContent`
- Hiç `eval()` veya `new Function()`

### localStorage
- Schema validation on read (wrong shape → reset-to-default)
- Versiyonlu key: `cmt.v1.weights`, `cmt.v1.language`, `cmt.v1.vram`
- Migration plan v2'ye geçişte mevcut

### GDPR / Privacy
- GitHub Insights traffic ölçümü (cookie-free, no PII)
- localStorage user preferences only (no analytics)
- Footer notu: "Bu site cookie kullanmaz, GitHub Insights ile anonim trafik ölçümü yapar"

### Data Integrity
- Agent output strictly `JSON.parse` (no innerHTML)
- `strengths`/`weaknesses` fields: sadece textContent render
- URL fields: `https://` prefix enforced, allowlist yok ama scheme validated

### Supply Chain
- `html2canvas` self-hosted (`assets/vendor/html2canvas.min.js`, SHA256 manuel verify)
- Content Security Policy meta tag:
  ```html
  <meta http-equiv="Content-Security-Policy"
        content="default-src 'self'; script-src 'self' 'sha256-...'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;">
  ```

### Git/Repo
- No secrets in repo (no API keys)
- `.gitignore` comprehensive (`.env`, `node_modules/`, tmp)
- Pre-commit hook: `grep -r 'sk-\|ghp_\|api_key' src/` block

**Top 3 threat mitigated:** XSS, scraped content injection, supply chain.

---

## 6. Ölçeklenebilirlik

**Static site = trivially scalable.** GitHub Pages CDN handles up to 100GB/ay bandwidth (free tier). 35 model × 14 benchmark JSON ~50KB; 1M visitor/ay = ~50GB → well within limits.

**Bottleneck:** Skill update workflow throughput (manuel + research agent), max ~1-2 update/gün pratik. M5 metrik (≤14 gün) bu kapasitenin çok altında.

**Faz 2 ölçek noktaları:**
- 100K+ unique/ay → Cloudflare Pages mirror düşün
- 50+ model → JSON pagination veya per-tier files
- Custom analytics (Plausible/GoatCounter) → 5K+ unique/ay'da değer

---

## 7. Non-Functional Requirements

| Kategori | Hedef |
|----------|-------|
| **Performance** | First Contentful Paint < 1sn, Time to Interactive < 2sn, JSON fetch < 2sn |
| **Accessibility** | Lighthouse a11y ≥ 90, keyboard navigation full, ARIA labels |
| **SEO** | Lighthouse SEO ≥ 90, JSON-LD structured data, hreflang i18n, sitemap.xml |
| **Browser support** | Chrome/Edge ≥ son 2 sürüm, Firefox ≥ son 2, Safari ≥ son 2, iOS Safari ≥ 17 |
| **Responsive** | Mobile <640px, tablet 641-1024px, desktop >1024px — overflow=0 her birinde |
| **Uptime** | GitHub Pages SLA (~99.9%) |

---

## Appendix — External Dependencies

| Dependency | Versiyon | Lisans | Self-host? |
|------------|----------|--------|------------|
| html2canvas | latest stable (1.4.x) | MIT | ✅ vendor |
| GitHub Pages | — | platform | external |
| WebGPU API | browser-native | platform | — |

**Build/runtime dependency yok** — vanilla, no npm/yarn, no node_modules.
