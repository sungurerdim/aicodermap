# AICoderMap — Technical Specification

**Version:** 1.0 | **April 24, 2026**

---

## 1. Overview

Static web tracker (GitHub Pages) + local Claude Code skill orchestrator + research agent. No backend, no DB, no auth. Vanilla JS, no build step. Single external service: GitHub Pages.

**Technology stack:** HTML5 + CSS3 (3-breakpoint responsive) + Vanilla JS (no framework) + JSON data files + WebGPU API (browser-native) + html2canvas (vendored). Skill is local at `.claude/skills/aicodermap/` + agent at `.claude/agents/aicodermap-research-agent.md`.

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

**Skill (local, `.claude/skills/aicodermap/`):**
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

The canonical 26-key bench universe is defined in
`data/sources-whitelist.json._schema.coreBenchKeys` and mirrored by
`assets/js/core.js BENCH_KEYS`. Pricing is a per-provider array
(multi-provider rule) — each entry pins to a single provider and is
attributed in `data/sources.json` separately.

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
    "api": [
      {
        "provider": "official",
        "in": 5.00,
        "out": 25.00,
        "cacheHit": 0.50,
        "throughput": null,
        "url": "https://platform.claude.com/docs/en/about-claude/pricing",
        "fetched": "2026-04-30"
      }
    ],
    "subscription": "Max $200/month"
  },
  "bench": {
    "aaIdx": 57,
    "swePro": 64.3, "sweV": 87.6, "sweMulti": 79.3, "nl2Repo": null,
    "lcb": null, "tb2": 69.4, "tbHard": null,
    "tau2": 59, "tau3": null, "mcpA": 77.3, "bfcl": null,
    "aaCoding": 53, "aaAgentic": null, "browseComp": null,
    "cfElo": null, "webDevElo": null,
    "gpqa": 94.2, "aime26": null, "hle": 46.9, "aaOmni": null,
    "mmluPro": null, "simpleQa": null, "mrcr": null, "arcAgi2": null
  },
  "benchUpdated": {
    "swePro": "2026-04-30",
    "sweV": "2026-04-30"
  },
  "notApplicableBenchKeys": [],
  "benchQuarantine": {},
  "providers": 4,
  "uptime": 99.8,
  "ollamaSize": null,
  "unslothVariants": null,
  "vramRequirement": null,
  "strengthsKey": "opus-4-7.strengths",
  "weaknessesKey": "opus-4-7.weaknesses",
  "lastUpdated": "2026-04-30"
}
```

**Schema notes (post-2026-04-29.d reform):**

- `notApplicableBenchKeys[]` — list of `coreBenchKeys` where this model is
  structurally not measurable (e.g. an embedded edge model on agentic
  tool-use benchmarks). MX1 invariant counts these as `notApplicable`,
  not `gap` — closes silent-omission loophole.
- `benchQuarantine{}` — `{ benchKey: true }` map for cells where the only
  available source disagreed with itself across two recent fetches; UI
  warns but does not red-flag (MX5 single-publisher rule).
- `benchUpdated{}` — optional per-cell ISO date; freshness banner reads it.

**Local model entry difference:**

```json
{
  "id": "qwen-3-6-27b",
  ...
  "ollamaSize": "18 GB (Q4_K_M, community)",
  "ollama": {
    "pullCmd": "ollama pull qwen-3-6-27b",
    "tags": ["27b", "27b-q4_k_m", "27b-q8_0"],
    "pullCount": 412000,
    "architecture": "qwen3",
    "parameters": "27B",
    "license": "Apache 2.0",
    "releasedISO": "2026-03-22",
    "ollamaUrl": "https://ollama.com/library/qwen3"
  },
  "unslothVariants": [
    { "name": "UD-IQ2_XXS", "size": "9.39 GB", "vram": 10 },
    { "name": "UD-IQ3_XXS", "size": "11.2 GB", "vram": 12 },
    { "name": "Q4_K_M",     "size": "18 GB",   "vram": 20 }
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

**FAZ 8.A.3b contradiction resolution algorithm (2026-05-18).** Five
pathologies are now handled systematically:

1. **Scaffold disagreement** — same model evaluated under different
   agentic scaffolds (e.g. agentless vs swe-agent) produces split
   values. `tag_evaluation_context()` annotates observations whose URL
   or notes carry scaffold hints (`agentless | swe-agent | aider |
   openhands | moatless`). `should_quarantine` fires when any cluster
   member is scaffold-tagged.
2. **Tool-condition split** — observations carrying `tools=on/off`
   hints get an `evaluationContext.condition` annotation; merge.py
   prefers to keep them in distinct cells via the
   `notApplicableRules`-driven path, not collapse them.
3. **Category bleed** — a URL feeding multiple bench cells with the
   same value (e.g. an LCB extractor mis-routing a row into the sweV
   column) is flagged via `detect_category_bleed`; flagged
   observations are dropped from clustering.
4. **Vendor-version drift** — multi-cycle posterior estimate via
   `bayesian_aggregate()` smooths vendor revisions against historical
   pool. Cold-start guard (≥3 historical values required) defers
   activation until ~3 cycles post-deploy.
5. **Pseudo-source contamination** — observations whose `source ∈
   {snapshot-extraction, auto-resolution candidate, synth-backfill}`
   never anchor clustering. `filter_pseudo_sources()` extracts them
   into the artifact for audit; their weight is dampened (`×0.2`) when
   rescued as sole evidence.

**Multi-cycle instability mitigation:** `I_TIER_MIN_VERIFICATIONS = 2`
prevents a single-shot fresh I-tier observation from overriding an
existing multi-source S-tier consensus on the strength of recency alone.

**Cell confidence + quarantine.** `pick_winner` returns
`{confidence, quarantine, bayesianPoint}` per cell. Frontend
`compositeScore` confidence-weights every cell contribution and skips
quarantined cells entirely. `merge.py` stamps `model.benchQuarantine[bk]`
when `confidence < 0.2` OR `consecutive_gap_count >= 5`.

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
subagent_type: "aicodermap-research-agent"
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
GET /sitemap.xml              → SEO crawl hints (TR + EN + x-default)
GET /robots.txt               → crawler policy
```

No auth, no query params, CORS-friendly static asset. The dataset's
`distribution[]` is also discoverable from the JSON-LD `Dataset` block in
`/index.html` for AI agents and crawlers.

### 4.5 URL state (deep-linkable view)

The page's full visible state lives in the address bar — sharing a URL
shares the exact ranking the recipient will see. State precedence at first
load: **URL params > localStorage > defaults**. Subsequent mutations
(slider drag, filter change, language toggle, theme switch) push the state
back into the URL via `history.replaceState` (debounced 250 ms).

| Key          | Domain |
|--------------|--------|
| `lang`       | `tr` \| `en` |
| `theme`      | `dark` \| `light` |
| `preset`     | `balanced` \| `swe-focused` \| `agentic-focused` \| `reasoning-focused` \| `benchmark-only` \| `custom` |
| `w`          | `<benchKey>:<weight>,...` — only honoured when `preset=custom`; missing keys default to 0; total must be in `validateWeights` shape (sums to 100) |
| `tier`       | `frontier` \| `open-flagship` \| `coder-specialized` \| `gemma` \| `ollama-local` \| `all` |
| `deployment` | `all` \| `cloud` \| `local` |
| `provider`   | URL-encoded vendor name \| `all` |
| `vram`       | integer GB 1..256 |
| `gpu`        | webgpu vendor key (per `data/gpu-database.json._webgpuVendorMap`) \| `auto` |
| `open`       | `1` \| `0` |
| `search`     | URL-encoded substring |
| `sort`       | `<columnKey>-<asc\|desc>` |

Stability contract: param names, value sets, and shape are versioned with
`acm.v1.*` localStorage keys — bumping to v2 implies a coordinated rename.
Consumers (CLI, agents, embedded preview tools) can rely on the codec
documented above. `assets/js/url-state.js` is the reference implementation.

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
- Versioned keys (canonical, see `assets/js/core.js:STORAGE`):
  `acm.v1.weights`, `acm.v1.language`, `acm.v1.vram`, `acm.v1.gpu`,
  `acm.v1.filters`, `acm.v1.sort`, `acm.v1.theme`, `aicm.pricingBaseline`.
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

**Static site = trivially scalable.** GitHub Pages CDN handles up to 100GB/month bandwidth (free tier). ~50 models × 16 benchmarks JSON ~95KB; 1M visitors/month = ~95GB → within free tier limits.

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

---

## Appendix — Information-Theoretic Verification Scaling (Phase R2)

Trust score formula (Phase R2):

```
trustScore = tierWeight × verif_factor(verifications) × recencyDecay(date)
verif_factor(v) = min( log(1 + v) / log(4),  1.5 )
```

`verif_factor` replaced the prior linear `min(v, 3) / 3` so that
independent measurements beyond v=3 still contribute to trust accumulation.

**Calibration table**

| v   | min(v,3)/3 | log(1+v)/log(4) | applied |
|-----|------------|------------------|---------|
| 0   | 0.000      | 0.000            | 0.00    |
| 1   | 0.333      | 0.500            | 0.50    |
| 2   | 0.667      | 0.792            | 0.79    |
| 3   | 1.000      | 1.000            | 1.00 ←anchor |
| 5   | 1.000      | 1.293            | 1.29    |
| 10  | 1.000      | 1.661            | 1.50 ←capped |
| 100 | 1.000      | 3.322            | 1.50 ←capped |

**Why log base 4?**

Anchoring at v=3 → 1.0 preserves the calibration of the prior formula
(the most common cell distribution) while extending the curve to reward
deeper consensus.

**Why log scaling (vs. linear)?**

Per Bayesian information theory, each additional independent measurement
contributes information proportional to the KL divergence between the
prior and the updated posterior:

```
ΔI(n) ≈ ½ · log(precision(n+1) / precision(n))
```

For independent Gaussian-like observations, precision scales linearly
with the sample count `n`, so cumulative information scales as `log(n)`.
The 1.5 cap acknowledges that a single high-tier observation should never
fully replace the cross-source ground truth that the Beta-Binomial
reliability posterior (Phase R3) provides.

**Why a 1.5 ceiling (not unbounded)?**

Two reasons:

1. A single inflated tier weight × runaway verif_factor would let a
   verbose-but-shallow data path beat the Beta-Binomial reliability
   posterior (Phase R3) that aggregates per-source track records.
2. Practical cell densities rarely exceed v=10 distinct independent
   leaderboards; the cap is reached at v=10 (1.66 → 1.5).

**Backwards compatibility**

Cells with v ≤ 3 preserve their pre-R2 trust ordering up to a constant
factor — within-cluster argmax never flips. Cells with v ≥ 4 see a small
boost: a 4-source cluster gains ~9% trust over its 3-source equivalent.
The composite-score deltas are bounded by `(1.5/1.0 - 1) ≈ 50%` in the
extreme; in production data the median composite shift was < 5 points.
