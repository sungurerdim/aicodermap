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
  js/                  — 17 ES modules (main, core, data, scoring, format,
                         gpu, i18n, dom, overlay, freshness, sources,
                         url-state, events, render-controls/-card/-table/-privacy)
  css/                 — 7 stylesheets (base, layout, table, controls,
                         models, toast, responsive)
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

**Research Agent (project-scoped, `.claude/agents/`):**
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

- N/A retired (2026-05-26): there is no `notApplicableBenchKeys`. Every
  (model, bench) cell is FILLED or GAP — an unmeasured cell is a gap,
  re-researched every cycle (freshness-skip is the only skip). The MX1
  invariant is `filled + gaps == totalCells`.
- `benchQuarantine{}` — `{ benchKey: true }` map for cells where the only
  available source disagreed with itself across two recent fetches; UI
  warns but does not red-flag (MX5 single-publisher rule).
- `benchUpdated{}` — optional per-cell ISO date; freshness banner reads it.

**Local model entry difference:**

```json
{
  "id": "qwen3-6-27b",
  ...
  "ollamaSize": "18 GB (Q4_K_M, community)",
  "ollama": {
    "pullCmd": "ollama pull qwen3-6-27b",
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
   prefers to keep them in distinct cells via the tool-condition
   annotation path, not collapse them.
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

### 4.4 URL state (deep-linkable view)

The page's full visible state lives in the address bar — sharing a URL
shares the exact ranking the recipient will see. State precedence at first
load: **URL params > localStorage > defaults**. Subsequent mutations
(slider drag, filter change, language toggle, theme switch) push the state
back into the URL via `history.replaceState` (debounced 250 ms).

| Key          | Domain |
|--------------|--------|
| `lang`       | `tr` \| `en` |
| `theme`      | `dark` \| `light` |
| `preset`     | `consensus` \| `balanced` \| `swe-focused` \| `agentic-focused` \| `reasoning-focused` \| `benchmark-only` \| `custom` |
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

### 4.5 Browser → External Services

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
  `acm.v1.filters`, `acm.v1.sort`, `acm.v1.theme`.
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
- Pre-commit hook (`scripts/hooks/pre-commit`, installed via `scripts/install-hooks.sh`): data-coherence audit gate; no automated secrets scan — manual discipline + defensive `.gitignore`

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

---

## Appendix — Source Reliability v2 (Phases R1 – R6)

The reliability subsystem layers a Beta-Binomial posterior on top of the
verif-factor formula. The goal: rank a source's contribution by *how
often it has agreed with cross-source consensus on this benchmark*,
without hardcoded allowlists.

### Composite trust formula

```
T(obs) = tierWeight × verif_factor(v) × reliability(s, b) × recencyDecay(date, type)

verif_factor(v)        = min(log(1+v)/log(4), 1.5)                  ← Phase R2
reliability(s, b)      = posterior_mean if n(s,b) ≥ COLD_START_N    ← Phase R3
                         else posterior_mean of source global pool
                         else 1.0                                    (cold-start neutral)
recencyDecay(date, t)  = piecewise INTERVAL_DECAY_CURVES[t]         ← Phase R5
```

### Beta-Binomial posterior

`reliability(s, b)` is the posterior mean of a Beta-Binomial conjugate
update with uniform prior Beta(1, 1):

```
α_post(s, b) = 1 + decayedAgree(s, b)
β_post(s, b) = 1 + decayedDisagree(s, b)
mean         = α_post / (α_post + β_post)
CI_95(p)     = p ± 1.96·√(p(1-p)/n)    (Wald approximation; n ≥ 30 for tight bounds)
```

Each cycle:

1. **Decay** — every counter shrinks by `0.5^(Δdays / 21)` (3-cycle
   half-life × 7 days/cycle = 21-day half-life). Decay is applied before
   any new evidence so single-cycle spikes can't permanently anchor the
   ledger.
2. **Update** — `update_reliability(url, bench, agreed)` increments
   `decayedAgree` or `decayedDisagree` by 1.0 and the raw lifetime
   counter by 1. Raw counters are audit-only and never decayed.
3. **Lookup** — `reliability_multiplier(ledger, url, bench)` walks the
   hierarchy: per-(source, bench) → per-source global → cold-start 1.0.

The hierarchy is a manual James-Stein-style shrinkage: sparse cells
borrow the source's global track record before falling back to neutral.

### Cold-start

A source with fewer than `COLD_START_N = 10` decayed samples on the bench
*and* fewer than 10 globally returns multiplier 1.0 — its trust score is
identical to pre-R3. Fresh sources are never penalized; they enter the
ledger via the normal update path and earn or lose reliability over time.

### Exceptional source override (R4)

Phase R4 adds `_exceptional_source_override` between the I-tier override
and `_single_outlier_guard`. A single I-tier observation bypasses the
multi-source guard when, on the specific bench:

| Gate | Threshold | Why |
|------|-----------|-----|
| `n` (decayedAgree + decayedDisagree) | ≥ 20 | Wilson CI tight enough |
| posterior accuracy | ≥ 0.90 | track record matters, not just tier |
| recency_decay | ≥ 0.85 | < ~90 days old |
| tier | "I" | independent leaderboards only |

This is the "1 trusted source can beat 5 unreliable sources" rule, but
*every gate is data-derived* — no source allowlist, no hardcoded patches.
A source has to earn the override by surviving cycles of agreement.

### Per-source recency curves (R5)

`recency_decay(date, source_type)` picks a curve from
`INTERVAL_DECAY_CURVES` based on the source's publishing cadence. The
default curve matches the pre-R5 piecewise; vendor entries with
`vendorUpdateInterval: "quarterly"` use a flatter curve so a 100-day-old
vendor release notes page still carries 0.85 weight (vs 0.70 default).

### Worked example: 1-vs-5

Setup: one I-tier source (`trusted.com`, n=20, 95% accuracy, today's
fetch) vs five C-tier sources (n=20, 40% accuracy, today's fetch).

```
verif_factor(6 distinct URLs) = log(7)/log(4) = 1.404

Trusted obs:
  T = tier(I) × verif_factor × reliability × recency
    = 1.0 × 1.404 × (1+19)/(2+20) × 1.0
    = 1.0 × 1.404 × 0.909 × 1.0
    = 1.277

Each unreliable obs:
  T = 0.4 × 1.404 × (1+8)/(2+20) × 1.0
    = 0.4 × 1.404 × 0.409 × 1.0
    = 0.230

Cluster sum_trust:
  trusted_cluster   = 1.277  (1 member)
  unreliable_cluster = 1.150  (5 × 0.230)
```

Even before R4, the trusted cluster wins on raw `sum_trust`. The
`_single_outlier_guard` would normally demote it, so R4 lets it survive
when its track record meets the override gates. The math falls out
naturally — no thresholds hardcoded into the winner-selection path.

### Frontend mirror (R6)

`assets/js/data.js` mirrors:
- `sourceIdentity` — hostname canonicalization.
- `posteriorMean` — Beta posterior mean.
- `sourceReliability(url, benchKey)` — hierarchical multiplier.
- `sourceReliabilityBadge(url, benchKey)` — `{kind, accuracy, n}` for the
  card-footer badge (`exceptional` / `low` / `normal`, null for
  cold-start).

`INTERVAL_DECAY_CURVES` is also mirrored as a frozen export for future
documentation/visualisation needs.
