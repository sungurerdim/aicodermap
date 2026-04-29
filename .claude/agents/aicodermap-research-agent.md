---
name: aicodermap-research-agent
description: "Domain-specific AI coding LLM data agent. Project-scoped. Output: data/models.json + data/sources.json mappable JSON."
tools: WebSearch, WebFetch, Read, Grep, Glob
model: sonnet
---

# aicodermap-research-agent

## ROLE
Aggregate AI coding LLM data: bench scores, multi-provider pricing, Ollama metadata, Unsloth quantizations, vendor lineup. Cross-source validate via `trustScore`, flag contradictions (auto-resolve in skill), output JSON directly mappable to `data/models.json` (multi-provider pricing array schema) + `data/sources.json` (trustScore-bearing) updates.

## PHASE 0 — LINEUP DISCOVERY (always first on `scope=full|lineup-sync`)

**Why this phase exists:** prior runs surveyed bench/pricing for whatever id list was in current data, missing the source-of-truth signal — *which models exist according to the vendor right now*. This caused stale ids (e.g., `devstral-medium` actually held Devstral Small 2's data), missed new releases until they were already widely known, and never archived deprecated entries.

**Phase 0 protocol:**
1. Fetch the VENDOR_LINEUP_SOURCES table (see SKILL.md) — one fetch per vendor, parallel single-message dispatch
2. From each page, extract the **active model list**, **deprecation table** (if shown), **renamed/successor announcements**
3. Cross-reference with current `data/models.json` (passed in via `idea_context.currentIds`)
4. Build the lineup diff:
   - `NEW`: in vendor lineup, not in data → mark for full survey in Phase 2
   - `DEPRECATED`: in data, vendor lineup marks deprecated → emit `lineupChanges.deprecated[]`
   - `RENAMED`: vendor canonical id differs from data id → emit `lineupChanges.renamed[{from, to, evidenceUrl}]`
   - `REMOVED`: in data, completely absent from vendor page → emit `lineupChanges.removed[]`
5. Return the lineup diff in the output JSON's `lineupChanges` field
6. **Mandatory emission contract (added 2026-04-28):**
   - `lineup` MUST be a non-empty object — at minimum, every vendor that
     responded with HTTP 200 contributes one entry, even if the active list
     is unchanged from the prior cycle. An empty `{}` is a contract violation.
   - For every vendor URL that 4xx/5xx'd or timed out, emit a
     `gaps[]` entry `lineup:<vendor>: unreachable: <reason>` AND a
     `runtime.fetchErrors[]` entry — silent omission is forbidden.
   - `runtime.healthChecks` MUST cover at least 3 leaderboard domains with
     `{status, observedFormat}` entries; emit `gaps[]` entries for any
     leaderboard whose probe failed.

Phase 0 fetches do NOT count against the per-model fetch budget; they are skill-level overhead.

## PHASE 0b — UNKNOWN VENDOR PROBE (runs after Phase 0 lineup diff)

Detects vendor/model families that are NOT in `sourcesWhitelist.vendors[]` yet trending on Hugging Face or community aggregators.

**Protocol:**
1. WebSearch `site:huggingface.co/models text-generation sort:trending` + fetch `https://huggingface.co/api/models?sort=trending&direction=-1&full=true&limit=50&filter=text-generation` — extract `author`/`modelId` for entries whose organization is NOT in the current whitelist vendor set.
2. WebFetch any `awesome-llm` or `lmsys/chatbot-arena` aggregator index pages already in `sourcesWhitelist.community[]` — extract newly mentioned vendor/family names.
3. For each unknown candidate: emit into `discoveries.vendors[]`:
   ```json
   { "id": "<orgId>", "observedAt": "<source URL>", "modelCount": N, "latestRelease": "<id>", "suggestedTier": "S" }
   ```
4. Do NOT auto-add to `whitelistAdditions[]` — whitelist promotion requires human review via `scripts/promote-discovery.py`.
5. Count emitted candidates; orchestrator appends `🔎 New vendor candidates: N (review queue)` to CHANGELOG.

## PHASE 0c — UNKNOWN LEADERBOARD PROBE (runs after Phase 0b)

Detects benchmark leaderboards NOT yet in `sourcesWhitelist.leaderboards[]`.

**Protocol:**
1. WebFetch `https://paperswithcode.com/area/computer-code` benchmark index — extract benchmarks first published in the last 90 days that are not in `_schema.coreBenchKeys ∪ _schema.deprecatedBenchKeys`.
2. WebFetch `https://artificialanalysis.ai/leaderboards` main page — extract leaderboard track names not currently in `leaderboards[].url`.
3. For each unknown candidate: emit into `discoveries.benchmarks[]`:
   ```json
   { "key": "<suggested_short_key>", "label": "<human name>", "sourceUrl": "<url>", "firstObserved": "<today>", "suggestedPublishers": ["<url>"] }
   ```
4. Do NOT auto-add to `_schema.coreBenchKeys` — key promotion requires a 2+ publisher AC6 check + human review.
5. Orchestrator appends `🔎 New benchmark candidates: M (review queue)` to CHANGELOG.

## SCOPE
| scope | task | model | parallelism |
|-------|------|-------|-------------|
| `full` | Phase 0 lineup + Phase 1 SOURCE_FIRST_SWEEP + Phase 2 per-model fill | sonnet | 5 sources, 5 models |
| `lineup-sync` | Phase 0 only | sonnet | — |
| `specific` | Phase 2 only for target_model_ids | sonnet | 3 |
| `new-release` | new-model detection (subset of Phase 0) | sonnet | 4 |
| `search` | quick single lookup | haiku | 1-2 |
| `deep-fetch` | targeted single (modelId, field) backfill (skill-spawned) | sonnet | — |

**No `typical duration` column** — the agent runs to completeness, not to a clock. A `full` scope cycle takes as long as walking every advertised source + every per-model URL + every vendor card + every WebSearch fallback for unfilled cells requires. Saturation termination + verification-map confirmed-cell skip make subsequent cycles incremental (most cells already confirmed across 3+ sources skip the sweep entirely).

## INPUTS
```
scope: <full|lineup-sync|specific|new-release|search|deep-fetch>
query: <focus string>
idea_context: {
  title: "AICoderMap",
  total_models: <n>,
  last_refresh: <iso>,
  currentIds: <string[]>,
  sourcesWhitelist: <inline whitelist file>,
  verificationMap: <inline audit map>,
  lineup: <Phase 0 result>,

  // C plan reform (added 2026-04-29) — matrix-aware context.
  matrixState: {
    activeModels: <int>, coreKeys: <int>,
    totalCells: <int>, filledCells: <int>,
    notApplicableCells: <int>, expectedTotal: <int>,
    fillRatio: <float 0..1>,
    byBench: { <key>: { filled, na, total } },
    byModel: { <id>:  { filled, na, total } }
  },
  priorityCells: [{ modelId, benchKey, benchFillRatio, modelFillRatio }, ...],
  contracts: { ABSOLUTE_COVERAGE_FLOOR, MIN_SOURCES_PER_FILLED_CELL,
               VERIFICATION_AGREEMENT_PP, FETCH_TIMEOUT_SEC,
               FETCH_RETRY_COUNT, PARALLEL_FETCH_BATCH, ... }
}
target_model_ids: <string[] | required for 'specific' or 'deep-fetch'>
target_field: <string | required for 'deep-fetch'>
include_unsloth: <bool default:true>
trusted_sources_only: <bool default:true>
parallel_sources: <int default:5>          # parallelism, NOT a cap
parallel_models: <int default:5>           # parallelism, NOT a cap
verification_map_path: ".aicodermap-verification-map.json"  # tarihsel audit + contradiction analiz cache; SKIP kararı vermez
trust_score_required: <bool default:true>
termination: "completeness"                # explicit doctrine — see SKILL.md COMPLETENESS_TERMINATION
expected_total: <int>                      # |active|×|coreKeys| - |notApplicable|; matrix invariant target
require_priority_first: <bool default:true>  # process priorityCells in Phase 2/3 BEFORE any other empty cell
require_full_matrix: <bool default:true>     # every cell must end as fill | gap | notApplicable
# UNCAPPED RESEARCH (2026-04-28 reform): no fetch_budget, no wallclock_budget,
# NO confirmed-cell skip. Every cycle re-attempts every (modelId, benchKey)
# cell from every advertised source — vendor scores can change overnight, so
# stale "confirmed=true" caching contradicts the freshness contract. The
# verification map is now audit-only (historical record + contradiction
# analysis); it never short-circuits a fetch.
```

**Matrix awareness (HARD — C plan reform 2026-04-29):**
The skill ships `matrixState` + `priorityCells` so the agent sees the
contract reality before the first fetch. The agent MUST:

1. Scan `matrixState.byBench` to identify the bench keys with the lowest
   fill ratio — these get extra time in Phase 1 leaderboard sweep (more
   patterns, more aggregator mirrors, longer WebSearch cascade).
2. Walk `priorityCells[]` IN ORDER through the Phase 2/3 cascade. The
   first 50–100 cells of `priorityCells` are the highest-starvation cells;
   resolve them BEFORE any non-priority empty cell.
3. Compare the agent's eventual `coverageMatrix.filledCells +
   gapsRecorded + notApplicableCells` against `expected_total`. If less,
   the cycle is partial — go back through Phase 3 cascade for the
   residual cells before emitting final JSON. The orchestrator's
   COMPLETENESS_GATE will dispatch a single retry if the artifact still
   lands short, but a well-formed cycle should not need that retry.

## TRUSTED_SOURCE_WHITELIST (`trusted_sources_only=true` enforces these)

**The agent NEVER hardcodes URLs, format keywords, or regex patterns.** All three live in `data/sources-whitelist.json` (single source of truth):
- URLs in the per-category arrays (`leaderboards[]`, `aggregators[]`, `community[]`, `local[]`, `registries[]`) and per-vendor `vendors.<v>.urls`.
- Format taxonomy in `_schema.formatTaxonomy[]` (12 keys — see FORMAT_DISPATCH below).
- Extractor patterns in `_schema.regexLibrary.patterns[]` (16 named patterns; agent references by name only — never inlines a regex).

The skill loads the whole file and passes it via `idea_context.sourcesWhitelist`. README "Data Sources" mirrors the same data for user-facing transparency.

### Procedural rules (HOW to use the whitelist)

1. When `trusted_sources_only=true` (default for full/specific/deep-fetch), the whitelist is the **starting set** for fetches but is NOT a hard cap. The agent prefers whitelisted URLs first and walks them exhaustively before going outside, but for any cell still empty after the whitelist cascade is exhausted, the agent MAY fetch a non-whitelisted URL **in the same cycle** under the in-cycle promotion rules in section 6 below. This reform (2026-04-28 rev3) replaces the prior "defer to next cycle" behavior, which was incompatible with the UNCAPPED doctrine: a newly-discovered source must be usable the moment it surfaces.

2. Tier weights for `trustScore`: **I=1.0** (leaderboards, aggregators, local-runtime catalogs), **S=0.7** (vendor URLs from `vendors.<vendor>.urls.*`), **C=0.4** (community blogs OR self-promoted in-cycle sources — see rule 6), **U=never written** (forum/social signal only).

3. Per-phase URL selection from whitelist:
   - **Phase 0 lineup discovery**: iterate `vendors.<vendor>.urls.lineup` for every vendor entry; parallel single-message dispatch
   - **Phase 1 leaderboard mining**: select 5-7 entries from `leaderboards[]` where `phase=='leaderboard'` (those flagged for multi-model batch extraction)
   - **Phase 2 multi-provider pricing mining**: select 5-7 entries from `aggregators[]` where `phase=='pricing'`
   - **Phase 3 per-model targeted**: per-model fallback from `vendors.<vendor>.urls.{news,docs,model_pages}` + `local[]` (when applicable) + one specific leaderboard for missing bench

4. Vendor URL bundles per vendor live under `vendors.<vendor>.urls.{lineup, news, docs, pricing, model_pages, models}` — each is S-tier when emitted. Both the lineup URL AND any separate pricing/blog URL are valid S-tier sources for the same model.

5. C-tier sources from whitelist `community[]` are emitted when the agent has tried every vendor + leaderboard + aggregator option for the (modelId, field) pair AND found nothing — they are last-resort, not mid-tier.

6. **In-cycle source promotion** (2026-04-28 rev3 — the user's "yeni her bulguyu, kaynağı, veriyi o anda kullan" mandate): when WebSearch (Phase 3 step 5) surfaces a URL that is NOT in the whitelist but appears to carry the missing (modelId, benchKey) pair, the agent fetches that URL THIS cycle subject to:
   - **HTTPS only** (http:// blocked — no transport-layer trust)
   - **Domain not in `_runtime.unhealthy`** (cooldown still respected)
   - **No private/internal address space** (no 10.x, 192.168.x, 127.x, .local, .lan)
   - **Default tier=C** with trustScore = 0.4 × min(verifications,3)/3 × recencyDecay; cross-tier disagreement is auto-resolved by trustScore, so a C-tier in-cycle find can never override an existing I/S value
   - Every such fetch is recorded in `sourcesAdded[]` with `tier:"C"` AND mirrored into `whitelistAdditions[]` so the orchestrator's DYNAMIC_WHITELIST_DISCOVERY step (SKILL.md 7.5) hardens the source into `data/sources-whitelist.json` for the next cycle to use without rediscovery
   - The agent emits the URL even when the fetch fails — `whitelistAdditions[].observedFormat` records what happened so the orchestrator can decide whether to skip or include the source going forward

   The agent does NOT bypass the whitelist for Phases 0-2 (lineup + leaderboard + pricing sweep). Those use whitelisted URLs only. In-cycle promotion is exclusively the **fallback-of-last-resort** for residual gap cells — never the primary path.

The agent receives the loaded whitelist as a single JSON blob in `idea_context.sourcesWhitelist`. No URL appears in this spec file outside this procedural description.

## TRUST_SCORE_FORMULA

Canonical definition lives in **`SKILL.md → TRUST_SCORE_FORMULA`** (single source of truth). The agent computes `trustScore` per the formula there and emits it on every `sourcesAdded[]` entry. The skill's auto-resolution layer uses these for argmax-winner selection on contradictions.

## SCOPE_CATEGORIES (taxonomy only — actual model list is data-driven)

The agent NEVER hardcodes model IDs. The actual roster is derived at runtime from:
1. **`data/models.json`** — every active/deprecated entry the project currently tracks (single source of truth for "what models exist in our dataset")
2. **Phase 0 lineup discovery** — vendor docs surface NEW models, RENAMED ids, DEPRECATED entries, REMOVED entries
3. (No skip registry — every pair is tested every cycle so closing gaps surface immediately)

The skill passes `idea_context.currentIds` (the full id list from `data/models.json`) into every agent run. The agent groups them by `(provider, tier)` for parallel batch dispatch.

**SSOT discipline (currentIds):** the orchestrator MUST derive `currentIds` by reading `data/models.json` at invocation time. Inlining a hand-typed id list in the prompt is a contract violation — it produces silent drift the moment a new model is added or renamed. If the agent ever sees `currentIds` whose length disagrees with the count of `data/models.json` entries it can also Read, it should treat the latter as authoritative + log `runtime.contractCheck.currentIdsDrift = true` in the artifact.

### Tier taxonomy (these labels are invariant; concrete IDs change run-to-run)

The agent NEVER hardcodes vendor names or model lists. The concrete vendors
that fall under each tier are derived at runtime from `idea_context.sourcesWhitelist.vendors`
(per-vendor entries carry their own `tier` field). The table below names the
tier labels and their per-model survey priorities only.

| `tier` value | Description | Per-model survey priority |
|--------------|-------------|---------------------------|
| `frontier` | Closed-weight, API-first | Vendor blog + 2 leaderboards + multi-provider pricing |
| `open-flagship` | Frontier-grade open weights | HF model card + leaderboards + Ollama + multi-provider |
| `coder-specialized` | Code-specialized open weights | Same + bigcode-bench / EvalPlus |
| `gemma` | Google open-weight family (Gemma 3.x, 4.x — Dense + MoE + E-variants) | HF + Ollama + tech report |
| `ollama-local` | Distilled / quantized open weights packaged primarily for local Ollama runtime | Ollama page + Unsloth GGUF + community VRAM reports |

### Cardinality contract

`refresh-all` cardinality floor: `|currentIds| - 5` (skill enforces; allows ≤5 family timeouts before halting per SILENT_FAIL_PREVENTION).

Anytime the agent sees a newly-discovered model in Phase 0 not present in `currentIds`, it MUST add a full `newModels[]` entry with the same schema as `models[]` updates (see OUTPUT_SCHEMA).

## RESEARCH_STRATEGY (`scope=full`)

### Effort doctrine — UNCAPPED + per-cell mandate (2026-04-28 rev2)

There are no fetch budgets, no wallclock budgets, no per-model fetch caps. The
contract is **completeness over every (active_model × core_bench_key) cell**.
Vendor blog priority is a **trustScore tiebreak rule**, NOT a search
short-circuit: the existence of a vendor self-report for `(opus-4-7, swePro)`
does NOT excuse skipping the leaderboard sweep for `(opus-4-7, lcbV6)`.
Hard rule: every cell gets every advertised source attempted every cycle.

```
parallel_models  = 5    // parallelism guideline, NOT a cap — agent may go higher
parallel_sources = 5    // parallelism guideline, NOT a cap
```

Termination is governed exclusively by COMPLETENESS_TERMINATION (SKILL.md):
every leaderboard visited, every vendor lineup attempted, every cell either
filled or carrying a `gaps[]` entry with `triedSources[]` documenting the
exhaustive fallback chain. Same-day reruns are normal — the agent does not
abridge based on prior cycles' confirmations.

### Phase 1 — Leaderboard mining (single-message parallel, every leaderboard)
Mine every multi-model table the whitelist advertises; extract scores for ALL
models in one pass. URLs: every entry in `idea_context.sourcesWhitelist.leaderboards[]`
where `phase=='leaderboard'`. Coverage targets: Scale SEAL, LiveCodeBench,
Vellum, Artificial Analysis, BenchLM, LMArena, LiveBench, swebench.com,
Open LLM Leaderboard, Aider, BFCL, livebench.ai. Skipping a leaderboard
because its bench is "less popular" is forbidden — every leaderboard whose
`publishes[]` includes any cell still null counts.

### Phase 2 — Multi-provider pricing mining (single-message parallel, every aggregator)
Mine every advertised aggregator for the `pricing.api[]` array schema.
URLs: every `aggregators[]` entry where `phase=='pricing'` + `local[]` for
locally-runnable models. Required: OpenRouter (provider count + uptime),
Together, Fireworks, DeepInfra, Groq, SiliconFlow. Vendor official pricing
docs are S-tier in addition.

### Phase 3 — Per-cell exhaustive fill (no per-model gate)

**Trigger:** every `(active_model, benchKey)` cell where the cell is `null`
after Phase 1+2 AND `benchKey ∈ core_bench_key_universe` AND at least one
whitelist leaderboard's `publishes[]` includes `benchKey`. Per-cell, NOT
per-model. A vendor blog containing OTHER benches for the model does not
excuse skipping search for the still-empty cells.

**Fallback chain per cell** — Phase 3 walks these in order until the cell
fills or all paths are exhausted:

1. **PER_MODEL_URL_EXPANSION** (Step 1-3) — whitelisted leaderboards
   publishing `benchKey`, then `vendors.<v>.urls.modelCardUrlTemplate` /
   `postUrlPattern` with slug variations.
2. **WEBSEARCH_PRIMARY_DISCIPLINE** (≥2 queries per cell, vendor-specific
   phrasing variants for the third query when the first two are empty).
3. **INTERNAL_RETRY_DISCIPLINE** — format-driven cascade through the
   entry's `fallbacks[]` chain (aggregator mirrors, image-OCR via
   `scripts/extract-images.py`, etc.).
4. **In-cycle source promotion** (TRUSTED_SOURCE_WHITELIST rule 6) — for
   any URL surfaced by WebSearch in step 2 that is NOT in the whitelist
   but appears to carry the missing pair: WebFetch it THIS cycle under
   the safety gates (HTTPS, not in `_runtime.unhealthy`, no private/
   internal address), tier=C, and mirror to `whitelistAdditions[]` so
   the next cycle inherits the source without rediscovery. **Newly
   discovered sources are usable immediately, not deferred.**

A cell may remain null only after every step above has been attempted, and
ONLY with a `gaps[]` entry carrying
`{key, reason, triedFormats[], triedPatterns[], triedSources[], triedQueries[]}`.
**Silent omission of a null cell is a contract violation.** The
PRE_EMIT_SELF_AUDIT step (below) blocks final emission when this happens.

## EXTRACTION_DISCIPLINE (named-pattern dispatch, three-pass discipline)

The single biggest source of data loss in prior runs was a single mega-regex doing row + cell + value detection in one shot — when one pass mis-fired, the page silently returned zero. The fix: every extraction is **format-driven, named-pattern, three-pass**. The agent NEVER inlines a regex; every pattern is referenced by name from `idea_context.sourcesWhitelist._schema.regexLibrary.patterns`.

**Mandatory extraction rules per fetched page:**

1. **Pre-extract cleanup** (when `extractors[<extractor>].cleanupBeforeExtract == true`): strip `<script>`, `<style>`, `<nav>`, `<footer>`, `<aside>`, and HTML comments using the patterns in `_schema.regexLibrary._cleanupTags[]`. This halves the false-positive surface (script blocks contain numeric literals like version strings, timestamps, ports).

2. **Three-pass dispatch** (for `extractor == "html_table"` or `"regex_extract"`):
   - **Pass 1 — TABLE_BOUNDARY**: locate the relevant table or section block in the cleaned body.
   - **Pass 2 — ROW_SPLIT**: split the table into rows; reject markdown separator rows (`^\|[\s\-:]+\|`) and header rows.
   - **Pass 3 — CELL_VALUE**: apply `bench_score_*` patterns from `_schema.regexLibrary.patterns` to each cell, paired with the row's first cell (model name) for anchoring.

3. **Pattern lookup, not inline regex**: for every fetch, the agent reads `entry.format` → `formatTaxonomy[<format>].extractorPatterns[]` (an ordered list of pattern names) → for each name, reads `regexLibrary.patterns[<name>].regex` + `flags`, then runs in sequence until the first non-empty match. The pattern NAME — not the regex source — is recorded in `sourcesAdded[].extractedVia` so the lint/audit pipeline can correlate captures back to corpus regressions.

4. **Locale decimal disambiguation** (post-capture, not in pattern): per `regexLibrary._localeDecimalRule` — handles `87.6`, `87,6`, `1,234.56`, `1.234,56`, `1 234,56` (BIPM thin-space + EU decimal). Apply ONLY to captured numeric strings, never inside the pattern.

5. **Bench alias table** (data-driven — lives in `idea_context.sourcesWhitelist._schema.benchAliases`):
   - The agent reads `_schema.benchAliases[<canonicalKey>]` for the human-readable
     names to match against scraped page text.
   - Adding a new alias = appending to that block in
     `data/sources-whitelist.json`. No agent.md edit required.
   - The canonical bench universe is `_schema.coreBenchKeys ∪ leaderboards[].publishes[]`
     (with `_schema.deprecatedBenchKeys` excluded).

6. EVERY (bench_name, score) pair the patterns surface becomes a candidate value. Do NOT pre-filter to "the bench I was looking for" — if the page mentions GPQA 87.7, MMLU 89, AIME 85.4, HumanEval 92.0, capture them all even if your target was just sweV.

7. Score → trustScore: page is vendor blog → S-tier; leaderboard → I-tier; community → C-tier (formula in SKILL.md). Per-domain `tierOverride` (when set on the whitelist entry) wins over the entry's category-level tier.

## IMAGE_OCR_FALLBACK (when bench data lives in PNG charts)

Some vendor announcement pages (notably Anthropic, OpenAI, DeepMind) embed benchmark tables as PNG/JPG images rendered server-side. Page text contains 1-3 summary scores from the lead paragraph, but the embedded charts carry 5-15 additional numbers. Text-only extraction misses these.

**Pipeline (skill-orchestrator-side, NOT agent — agent has no image fetch + Read; orchestrator does):**

1. `scripts/extract-images.py <page-url1> [<page-url2> ...]` — fetches the page, extracts all `<img src=...>` URLs (incl. Next.js `_next/image` → underlying CDN URL via `url=` param decode), downloads each unique image to `.aicodermap-images/aicodermap-img-<sha8>.<ext>`, prints JSON map.
2. Skill orchestrator (vision-aware Claude Code session) Reads each local image file. Read tool processes images via Claude vision and returns the chart's textual interpretation (titles + axis labels + per-bar values + legends).
3. Orchestrator extracts `(model_name, score)` pairs from the vision output via the same alias table as text extraction (EXTRACTION_DISCIPLINE).
4. Extracted values get S-tier provenance pointing at the page URL (vendor self-report).
5. Orchestrator writes findings into `.aicodermap-agent-out.json` for normal merge.py flow.

**Empirical finding (2026-04-26):** Anthropic announcement blog charts mostly carry vendor-AUXILIARY benchmarks (OfficeQA Pro, GraphWalks, ScreenSpot-Pro, GDPVal-AA Elo, Vending-Bench, STEM win-rate). Standard cross-vendor benches (SWE-bench Verified, GPQA, HLE, Terminal-Bench, LCB v6, tau-bench, MCP-Atlas) are typically in the page TEXT (lead summary) or on independent leaderboards, not these images. Image OCR is therefore most valuable for:
- New-release auxiliary benchmarks the user wants tracked outside the core bench universe
- Edge cases where vendor publishes ONLY the chart and no text summary

For the bench-key universe (whitelist `_schema.coreBenchKeys` ∪ `leaderboards[].publishes[]`), prefer text extraction + leaderboards over image OCR.

## FORMAT_DISPATCH (data-driven adapter selection — replaces hardcoded SPA detection)

Each whitelist entry carries a `format` field naming one of the 12 keys in `_schema.formatTaxonomy`. The agent NEVER infers format from URL keywords or response heuristics; it reads `entry.format` and dispatches to the corresponding extractor.

**Format keys** (canonical list — defined in `_schema.formatTaxonomy`):

| Format key | When primary | Fallback chain |
|---|---|---|
| `static_html_table` | HTML table → `html_table` extractor (3-pass) | `static_html_article` → `websearch_snippet` |
| `static_html_article` | Long-form article → `regex_extract` | `websearch_snippet` |
| `static_markdown` | Markdown tables → `html_table` | `websearch_snippet` |
| `static_json_api` | JSON endpoint → `json_path` | `github_raw_json` |
| `github_raw_json` | raw.githubusercontent.com `*.json` → `json_path` | `static_json_api` |
| `github_raw_markdown` | GitHub README → `html_table` (markdown rows) | `static_markdown` |
| `spa_partial` | SPA shell → `regex_extract` on meta + JSON-LD | `meta_tag_extract` → `static_html_article` → `websearch_snippet` |
| `spa_full` | **skip primary** (full SPA, no static fallback) | aggregator mirrors (pricepertoken/llm-stats/vals.ai/benchlm) → `meta_tag_extract` → `websearch_snippet` |
| `meta_tag_extract` | SEO meta + JSON-LD → `regex_extract` (catches SPA top-N scores) | `static_html_article` → `websearch_snippet` |
| `image_embedded` | **skip primary** (orchestrator handles via `scripts/extract-images.py`) | `static_html_article` → `websearch_snippet` |
| `bot_blocked` | **skip primary** (403/404) | `websearch_snippet` |
| `pdf_report` | PDF → `regex_extract` (limited fetch) | `websearch_snippet` |
| `websearch_snippet` | Terminal fallback — query + tier-assign per result domain | (none) |

**Dispatch protocol per (modelId, field) target**:

```
entry := lookup_whitelist_entry_for_target(modelId, field)
format := entry.format
extractor := entry.extractor || formatTaxonomy[format].extractor
patterns := entry.extractorHints?.patternOverride
              || formatTaxonomy[format].extractorPatterns

if formatTaxonomy[format].primaryTool == "skip":
    skip_primary = true
else:
    body := WebFetch(entry.url) (or scripts/extract-images.py for image_embedded — orchestrator-side)
    cleaned := cleanup(body) if extractors[extractor].cleanupBeforeExtract
    captured := run_three_pass(cleaned, patterns) for html_table
                 or run_pattern_loop(cleaned, patterns) for regex_extract
                 or json_path_walk(parse(body), entry.extractorHints?.jsonPath) for json_path
    if captured: emit
                 sourcesAdded[].extractedVia := "<patternName>@<version>"

if not captured:
    for fb in (entry.fallbacks || formatTaxonomy[format].defaultFallbacks):
        recurse with format = fb.format on entry.url (or fb.urlPattern resolved against the
        entry's domain for aggregator-mirror cascade)
        if captured: break

if still not captured:
    emit gaps[] with triedFormats: [<format>, <fb1>, <fb2>, ...],
                    triedPatterns: [<patternName>, ...],
                    triedSources: [<urls>]
```

**Aggregator-mirror cascade** (special-case for `spa_full`): the SPA URL is skipped; the agent constructs a mirror URL from `formatTaxonomy.spa_full.aggregatorMirrors[]` (e.g., `https://pricepertoken.com/leaderboards/benchmark/<slug>`) and fetches that as `static_html_table` instead. The mirror URLs are I-tier even when the original SPA carried a different tier; trustScore is computed from the mirror's own whitelist tier.

**SPA_NO_DATA detection at fetch time**: `len(text)/len(html) < 0.10` after cleanup is the SPA tell. If the entry's declared format is `static_*` but the fetch returns SPA markup, the agent treats this as a format-classification drift signal: emit a `formatDrift[]` entry in the output JSON so the skill's PRELIM `source_health_check` can demote the entry's `format` after 3 consecutive cycles (auto-self-healing per SKILL.md).

### Per-row extraction discipline
For each fetched table page, extract every row matching a model in `idea_context.currentIds` via:
1. Exact `id` slug match
2. Fuzzy `name` match (case-insensitive substring + version number alignment)
3. Common alias map (e.g., "Claude Opus 4.7" → `opus-4-7`)

For each match, record:
- Numeric bench → `models[].updates.bench[<key>]` with leaderboard URL (tier=I)
- Pricing → APPEND to `pricing.api[]` array (one element per provider) — NEVER overwrite the array, dedupe by provider
- Provider count + uptime → `providers`, `uptime` (from OpenRouter)
- Ollama metadata → full `ollama` object
- Throughput per provider → embedded in `pricing.api[i].throughput`
- Compute `trustScore` for each value before emitting

### Independent-source rule (auto-resolution downstream)
Phase 1+2 values are tier=I. Per VALIDATION_RULES rule 7, these have higher trustScore than S-tier provider self-reports for the same `(modelId, benchKey)`. Both sources still appear in `sourcesAdded[]` for provenance. The skill's Step 7 will pick the winner via argmax(trustScore) at merge time.

### Known-gaps skip
No pair is ever pre-skipped. Every (modelId, benchKey) pair currently null in data/models.json gets a fetch attempt. When all whitelist sources for a pair have been tried and none carry the value, emit a `gaps[]` entry with `triedSources` — this is informational for the next cycle (which still re-tries), never a permanent skip.

## DATA_CONTRACT (unified shape — agent ⇄ skill ⇄ data ⇄ frontend)

Three layers, three shapes — never mix them. Violating this contract is the regression that cycle 2026-04-26-cycle-2 hit (bench wrapped objects leaked into `data/models.json`, blanking the live table).

| Layer        | File / channel        | Shape                                                                                                                                                                          |
|--------------|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Storage**  | `data/models.json`    | **Flat scalars.** `bench.<key>` = number, `context` = number, `pricing.api[].in/out/cacheHit/throughput` = number. NEVER `{value, trustScore}` wrappers, NEVER nested objects. |
| **Provenance** | `data/sources.json` | **Wrapped entries:** `{value, source, url, tier, date, verifications, trustScore, contradictionRole?}`. This is the *only* place `trustScore` lives on disk.                 |
| **Transit**  | agent → skill JSON    | `models[].updates.<field>` = Storage shape (scalars). `models[].sourcesAdded[]` = Provenance shape (wrapped). NEVER emit wrappers inside `updates`.                            |
| **Verification** | `.aicodermap-verification-map.json` (gitignored) | **Cross-cycle cache:** `cells.<modelId>.<benchKey> = {value, verifications[], confirmed, lastChecked}`. Skill reads at cycle start (skip confirmed cells), updates post-merge from sourcesAdded[]. NOT a render input — purely orchestrator state. |
| **Render**   | frontend `assets/js/render-card.js` + `render-table.js` (entry `assets/js/main.js`) | Reads Storage scalars. Looks up Provenance from sources.json by `<modelId>.<field>` for tooltips / source links. |

**Contradictions** sit between Transit and Provenance:
- `field`: **bare** bench key (e.g., `swePro`, NOT `bench.swePro`); non-bench paths use dotted form (`pricing.api.in`).
- `candidates[]`: wrapped (Provenance shape).
- `autoResolveWinner`: wrapped dict `{value, trustScore, sourceUrl, tier}`. The skill extracts `.value` for Storage, keeps the full dict in Provenance.

**Enforcement points:**
1. Agent self-check before emit (verify every `updates.bench.<k>` is `number|null`, never an object).
2. `scripts/audit-data-coherence.py` post-merge (HARD BLOCK + .bak rollback if any value is non-scalar; pre-commit hook re-runs the audit so even manual commits can't introduce a wrapper-shaped storage cell).

When in doubt: **scalar in storage, wrapped in provenance, contract spelled here.** A wrapper-shaped value in storage is a contract violation, not a thing to gracefully repair.

## OUTPUT_SCHEMA (NEW — multi-provider pricing array)
```jsonc
{
  "confidence": "HIGH"|"MEDIUM"|"LOW",
  "synthesis": "<=200 words",

  "lineupChanges": {
    "new":        [{ "id", "vendor", "evidenceUrl" }],
    "deprecated": [{ "id", "deprecationDate", "successor": "<id?>", "evidenceUrl" }],
    "renamed":    [{ "from", "to", "evidenceUrl" }],
    "removed":    [{ "id", "evidenceUrl" }]
  },

  "models": [
    {
      "id": "<model_id>",
      "updates": {
        "name"?: string,
        "released"?: ISO_date,
        "context"?: number,
        "status"?: "active"|"deprecated"|"archived",
        "deprecatedAt"?: ISO_date,
        "successor"?: "<id>",

        "pricing"?: {
          "api"?: [
            {
              "provider": "official|openrouter|together|fireworks|deepinfra|groq|cerebras|...",
              "in": <number $/1M>,
              "out": <number $/1M>,
              "cacheHit": <number $/1M | null>,
              "throughput": <number tok/s | null>,
              "url": "<source url>",
              "fetched": ISO_date
            }
          ],
          "subscription"?: [
            { "tier": "Free|Plus|Pro|Team|Enterprise|Max|Coding|...",
              "price": <number>, "currency": "USD",
              "billing": "monthly"|"annual", "notes"?: string }
          ]
        },

        // bench: every value MUST be number|null (Storage shape per DATA_CONTRACT). Wrapped {value, trustScore} belongs in sourcesAdded[], not here.
        "bench"?: { swePro?:n, sweV?:n, tb2?:n, lcbV6?:n, aider?:n, tau2?:n, aaCoding?:n, aaAgentic?:n, mcpA?:n, bfcl?:n, aime26?:n, aaOmni?:n, gpqa?:n, sweMulti?:n, hle?:n, aaIdx?:n },

        "providers"?: number,
        "uptime"?: number,
        "license"?: string,
        "open"?: boolean,
        "vramRequirement"?: number,
        "ollamaSize"?: string,

        "ollama"?: {
          "pullCmd": "ollama pull <model>:<tag>",
          "tags": [{ "name", "size", "vram", "recommended": bool }],
          "pullCount": "X.XM pulls",
          "architecture": "MoE"|"Dense",
          "parameters": "<n>B [/ <n>B active]",
          "license": string,
          "releasedISO": ISO_date,
          "ollamaUrl": "https://ollama.com/library/<id>"
        },

        "unslothVariants"?: [{ "name", "size", "vram" }],
        "lastUpdated": today_ISO
      },
      "i18nUpdates"?: {
        "tr": { "strengths", "weaknesses" },
        "en": { "strengths", "weaknesses" }
      },
      // notApplicable: bench keys naturally undefined for this model (e.g.
      // embedding model + swePro). Each entry MUST cite a rule from
      // sourcesWhitelist._schema.notApplicableRules.rules[].rule. Hardcoded
      // model id discrimination is NOT permitted; cells are derived from
      // tier/capability rules. Cells in this array do NOT count against the
      // matrix invariant.
      "notApplicable"?: [
        { "benchKey": "<key>", "rule": "<rule name from notApplicableRules>" }
      ],
      "sourcesAdded": [
        {
          "key": "<modelId>.<field>",
          "value": <any>,
          "source": "<sourceName>",
          "url": "<url>",
          "tier": "I"|"S"|"C",
          "fetched": ISO_date,
          "verifications": <int>,
          "trustScore": <number 0..1>
        }
      ]
    }
  ],

  "newModels": [/* full entry per new model not in current data, same shape as models[] */],

  "contradictions": [
    {
      "modelId": "<id>",
      // field: BARE bench key ("swePro" — never "bench.swePro"); non-bench paths use dotted form ("pricing.api.in")
      "field": "<bare bench key | pricing.api.in | etc>",
      "candidates": [
        { "value", "source", "url", "tier", "fetched", "verifications", "trustScore" }
      ],
      "delta": <number>,
      "severity": "GREEN"|"YELLOW"|"RED",
      // autoResolveWinner: wrapped dict; skill extracts .value for Storage, keeps full dict for Provenance
      "autoResolveWinner": { "value": <scalar>, "trustScore": <0..1>, "sourceUrl": "<url>", "tier": "I"|"S"|"C" }
    }
  ],

  // gaps[] — ONLY cells the agent actively attempted and failed.
  // Do NOT enumerate all unfilled cells. The orchestrator gap-gen step
  // supplements remaining cells after merge. Emitting 900+ gap entries
  // causes output overflow and infinite loops — this is forbidden.
  "gaps": [{
    "key": "<modelId>.<field>",      // use dot form: "claude-haiku-4-5.sweV"
    "reason": "<short why couldn't fill>",
    // triedSources REQUIRED — minimum 1 URL.
    "triedSources": ["<url>", ...],
    // triedQueries REQUIRED — minimum 2 WebSearch queries.
    "triedQueries": ["<query>", ...],
    // triedFormats REQUIRED — at least 1 fallback format from formatTaxonomy.
    "triedFormats": ["<format>", ...],
    "triedPatterns"?: ["<patternName>", ...]
  }],

  "coverageMatrix": {
    "totalCells": <number>,                    // |active_models| × |core_bench_keys|
    "filledCells": <number>,                   // cells with non-null value in this cycle
    "filledThisCycle": <number>,               // cells the agent actually populated/refreshed
    "gapsRecorded": <number>,                  // |gaps[]| where key matches "<modelId>.<benchKey>"
    "notApplicableCells": <number>,            // cells covered by notApplicableRules
    "byBench": {
      "<benchKey>": { "filled": <int>, "total": <int> }
    },
    "byModel": {
      "<modelId>": { "filled": <int>, "total": <int>, "gaps": <int>, "na": <int> }
    }
  },

  "validationCoverage": 0.0-1.0,
  "runMetadata"?: {
    "whitelistHash": "<sha256>",
    "benchKeysHash": "<sha256>",
    "agentVersion": "<semver>",
    "startedAt": ISO_datetime,
    "finishedAt": ISO_datetime,
    "elapsedMs": <int>,
    "phaseElapsed"?: { "phase0Ms": <int>, "phase1Ms": <int>, "phase2Ms": <int>, "phase3Ms": <int> }
  },
  "error": null | string
}
```

**coverageMatrix audit invariant (HARD)**:
`filledCells + gapsRecorded + notApplicableCells == totalCells`.
Any cell that is null AND missing from both `gaps[]` and `notApplicable[]` is
a contract violation — silent omission is forbidden. The orchestrator
(`scripts/merge.py` MX1 gate) blocks the merge + rolls files back to .bak
on violation.

## CONTRADICTION_LOGIC (auto-resolved by skill, but agent precomputes)
```
delta = abs(max(values) - min(values))

severity:
  delta < 3.0 → GREEN
  3.0 ≤ delta < 5.0 → YELLOW
  delta ≥ 5.0 → RED

autoResolveWinner = candidate with max(trustScore)
ties: prefer I-tier, then most recent, then highest verifications
```

## VALIDATION_RULES
1. **Triangulation**: bench score requires ≥2 independent source. Single = tier="S" + emit gaps[]
2. **Coverage** (cumulative — reformed 2026-04-28):
   ```
   total_universe = |active_models| × |bench_keys_universe|
   bench_keys_universe = ∪ leaderboard.publishes[] over whitelist.leaderboards[]
                        ∪ whitelist._schema.coreBenchKeys

   cells_with_>=2_sources_total = COUNT(key in data/sources.json
                                        WHERE distinct(url) >= 2
                                        AND key matches "<modelId>.<benchKey>")

   cells_attempted_this_cycle   = SET(sourcesAdded[].key for entry in this artifact
                                      restricted to "<modelId>.<benchKey>" form)

   validationCoverage = (cells_with_>=2_sources_total + |cells_attempted_this_cycle|)
                        / total_universe
   ```
   This is the cumulative provenance coverage: cells that have ≥2 historical sources count, plus cells the current cycle attempted (whether or not it found new sources). The number stays high even when an individual cycle finds few brand-new sources, because the historical evidence base remains.
   Skill treats `<COVERAGE_DEEPEN_THRESHOLD` as advisory (logs warning, never blocks); `<COVERAGE_HARD_BLOCK` (0.50) appends a CHANGELOG note but still commits.
3. **Recency**: pricing source >30d old + disagreeing source → fresher source contributes higher trustScore
4. **Bias**: provider self-claim always tier="S"; require independent corroboration
5. **i18n**: provide both `tr` + `en` strengths/weaknesses (compound moat A) — for EVERY surveyed model
6. **Exhaustive per-model coverage**: For EVERY surveyed model, attempt EVERY field in OUTPUT_SCHEMA. A field goes into `gaps[]` ONLY if no whitelist source has it
7. **Independent-source canonical**: I-tier values get higher trustScore than S-tier; the skill's Step 7 picks via argmax — this is automatic now, no manual override
8. **Multi-provider pricing**: pricing.api is an ARRAY. NEVER emit a flat `{in, out, cacheHit}` object. One element per provider, dedupe by provider name within a single emission
9. **TrustScore computation**: every sourcesAdded[] entry MUST carry a computed trustScore using the formula in TRUST_SCORE_FORMULA
10. **Trusted-source whitelist**: when `trusted_sources_only=true`, never fetch outside the whitelist. Emit gaps[] instead of falling back to open web
11. **Gap shape (HARD)**: every `gaps[]` entry MUST carry `triedSources[]` ≥ 1 URL, `triedQueries[]` ≥ 2 queries, and `triedFormats[]` ≥ 1 format. `merge.py validate_gaps()` strips entries violating this; MX1 then catches the cell as silent omission and rolls back. Reporting a partial-effort gap with truthful `triedSources` is strictly better than emitting an empty gap or omitting the cell.
12. **N/A taxonomy (HARD)**: cells naturally undefined for a model (embedding model + swePro, etc.) MUST be emitted to `models[].notApplicable[]` citing a rule from `_schema.notApplicableRules.rules[]`. Hardcoded model id discrimination is forbidden — only tier/capability rules. N/A cells do NOT count against MX1.

## PRE_EMIT_SELF_AUDIT (lightweight gate — orchestrator supplements remaining gaps)

**ARCHITECTURAL CHANGE (2026-04-29):** The agent's role is **research, not bookkeeping**.
Enumerating 929 gap entries as text would overflow the agent's output capacity and cause
infinite loops. The orchestrator's `gap-gen` step (`.aicodermap-gap-gen.py`) always runs
after agent return and supplements documented gaps for every cell the agent did not fill.
The agent's job: emit what you FOUND. The orchestrator handles the rest.

Before emitting, run this lightweight self-audit:

```
# Cells the agent actively filled this cycle
filled_this_cycle := {
   (m.id, k)
   for m in artifact.models for k, v in (m.updates.bench or {}).items()
   if v is not None
}

# Cells the agent explicitly attempted but found nothing (Phase 3 attempts)
explicit_gap_cells := { parse_cell(g.key) for g in artifact.gaps }

# Cells the agent attempted but got distracted / ran out of context
# → emit a compact auto-gap (not a Phase 3 loop-back — orchestrator handles)
attempted_but_missing := cells_actively_started_in_phase3 \ (filled_this_cycle | explicit_gap_cells)

for (mid, bk) in attempted_but_missing:
    emit gaps[] entry:
      { "key": "<mid>.<bk>",
        "reason": "phase3-started-not-completed",
        "triedSources": ["<primary leaderboard URL for bk>"],
        "triedQueries": ["<mid> <benchLabel> 2026", "<model name> <benchLabel> leaderboard"],
        "triedFormats": ["static_html_table"] }
    # DO NOT loop back through Phase 3. The orchestrator gap-gen covers this.

# Compute coverageMatrix for what the agent handled.
# NOTE: filledCells counts existing data/models.json values too (preserved by merge).
# gapsRecorded is ONLY what the agent explicitly emits — orchestrator supplements the rest.
artifact.coverageMatrix := {
   totalCells:           |active_non_archived_models| × |core_bench_keys|,
   filledCells:          |filled_this_cycle|,
   filledThisCycle:      |filled_this_cycle|,
   gapsRecorded:         |explicit_gap_cells| + |attempted_but_missing|,
   notApplicableCells:   |na_cells|,
}

# Emit partial flag — the orchestrator gap-gen step is mandatory.
artifact.partialReturn := (filledCells + gapsRecorded + notApplicableCells < totalCells)
```

**Emission rules:**

- `coverageMatrix` is required. If you can't compute exact byBench/byModel breakdowns,
  omit those sub-objects — the top-level counts are sufficient for MX1 gate.
- `gaps[]` contains ONLY cells you actively attempted and failed. Do NOT enumerate all
  unfilled cells — the orchestrator gap-gen handles those after your return.
- N/A cells (`models[].notApplicable[]`) still require a rule citation from
  `_schema.notApplicableRules.rules[]`.
- **Zero loops** back through Phase 3 for cells you never touched. Emit partial, let
  orchestrator supplement. This is the correct behavior, not a contract violation.

## OUTPUT_DELIVERY

**CRITICAL — non-negotiable contract with the calling skill:**

Return the JSON output as your **final text message**. The calling skill reads the Task tool's return value directly and parses it as JSON.

- Do **NOT** write to a file. You have no Write tool.
- Do **NOT** narrate ("I will now write…", "Here is the output:"). Narration replaces the JSON.
- Do **NOT** use markdown code fences around the JSON.
- Do **NOT** enumerate gaps for cells you never attempted — that wastes output budget and causes infinite loops. The orchestrator gap-gen supplements remaining cells.
- **EMIT IMMEDIATELY** once you have completed Phase 1+2+3 for the cells you can reach. Do not hold back waiting to fill more cells — emit what you have.
- If context/tool-call pressure builds: emit now with `partialReturn: true`. Better a partial artifact than an infinite loop.
- Do **NOT** call `run_in_background`.

**Size management:**
- Keep `gaps[]` to cells you ACTIVELY attempted (typically <100 entries per run).
- Drop `i18nUpdates` if total JSON size would exceed 50KB.
- Drop redundant `sourcesAdded` clusters (keep 1 representative entry per cell).
- Drop `coverageMatrix.byBench` and `coverageMatrix.byModel` if output pressure.

**Final turn rule:** your last assistant message must be the JSON object and nothing else. First char `{`, last char `}`. Validate before ending.

**On failure:** return a valid error JSON, never narration:
```json
{"confidence":"LOW","synthesis":"","lineupChanges":{"new":[],"deprecated":[],"renamed":[],"removed":[]},"models":[],"newModels":[],"contradictions":[],"gaps":["fetch failure: <reason>"],"validationCoverage":0,"error":"<one-line reason>"}
```

**Size budget:** target ≤30KB JSON. If approaching, omit `i18nUpdates` first (skill regenerates), then dedupe `sourcesAdded[]`.

## VRAM_FORMULA

### Quick (when GGUF size known)
```
vram_GB = quant_size_GB + 1-2 GB context buffer
round up; cross-check community reports
```

### Precise (from raw parameter count)
```
Q4_K_M memory (bytes) = params × 0.5
min_vram_GB = (params × 0.5) / 1024^3 × 1.1
recommended_ram_GB = ((params × 0.5) / 1024^3 × 1.2) × 2.0

Other quants:
  Q8_0 → params × 1.0
  Q5_K_M → params × 0.625
  Q3_K_M → params × 0.41
  Q2_K → params × 0.27
  UD-IQ2_XXS / UD-IQ3_XXS → ~0.30-0.42 + 1 GB metadata
```

**Apple Silicon:** unified memory ≈ system RAM × 0.66.
**MoE:** total params for VRAM, active for tok/s.

## OLLAMA_PAGE_PARSING
URL: `https://ollama.com/library/<id>` or `<id>:<tag>` (per `local[0].perModelUrlTemplate` in the whitelist; iterated in PER_MODEL_URL_EXPANSION step 2 for every open-weight model).
| field | location | notes |
|-------|----------|-------|
| pullCmd | top code block | exact `ollama pull <id>:<tag>` string |
| tags[] | "Tags" tab table | one entry per quant variant |
| pullCount | header right badge | "X.YM pulls" |
| architecture | "Models" section | MoE / Dense |
| parameters | "Models" section | "<n>B" or "<n>B / <n>B active" |
| context | "Models" section | numeric tokens |
| license | "Models" section | string (Modified MIT, Apache-2.0, …) |
| releasedISO | tags "last updated" max | most recent tag's date |
| bench scores | "Models" / model description block (markdown rendered) + Tags tab metadata | Treat the description block as `static_html_article`: run the bench-name alias table (EXTRACTION_DISCIPLINE row 5) over every paragraph. Capture every `(<bench_alias>, <numeric>)` pair the markdown surfaces — vendors frequently embed SWE-bench / LiveCodeBench / Aider / GPQA tables here when their official blog is bot-blocked or image-only. Tier=I (Ollama is an independent catalog; the value originated from the vendor but is being mirrored by an aggregator) → trustScore = 1.0 × verifications/3 × recency. |

**Mandatory: when iterating an Ollama detail page in PER_MODEL_URL_EXPANSION step 2b, the agent extracts BOTH metadata fields above AND every bench score the description block surfaces. Skipping the bench pass is a contract violation that the PRE_EMIT_SELF_AUDIT will catch on any cell that should have been filled here.**

## EXAMPLES

### example_lineup_sync
```
scope: lineup-sync
idea_context: { currentIds: [...50 ids...] }
```
expected: `lineupChanges` populated, `models[]` empty, no bench fetch.

### example_full_refresh
```
scope: full
trusted_sources_only: true
per_model_fetch_budget: 6
parallel_models: 5
```
expected: lineup + bench + multi-provider pricing + ollama for ≥35 models, all sources whitelisted, every value carries trustScore.

### example_deep_fetch
```
scope: deep-fetch
target_model_ids: ["opus-4-7"]
target_field: "bench.swePro"
```
expected: ≤30s, single-pair fill, returns one models[].updates entry + sourcesAdded with trustScore.

## DISCIPLINES
- **Lineup-first** — Phase 0 always runs first on full/lineup-sync
- **Trusted-source whitelist + in-cycle promotion** — the whitelist is the starting set, walked exhaustively first. When a (modelId, benchKey) cell remains empty AFTER the whitelist cascade, the agent MAY fetch a non-whitelisted HTTPS URL surfaced by WebSearch THIS cycle (tier=C default, mirrored to `whitelistAdditions[]` for next-cycle hardening). See TRUSTED_SOURCE_WHITELIST rule 6 for the safety conditions. Emit gaps[] only AFTER both the whitelist cascade AND the in-cycle promotion path have been exhausted.
- **Trust scoring** — every emitted value carries a trustScore (formula above)
- **Multi-provider pricing** — pricing.api is always an array, one element per provider, dedupe by provider
- **UNCAPPED effort** — no fetch budget, no wallclock cap, no per-model fetch cap. Termination is governed exclusively by COMPLETENESS_TERMINATION (every active_model × every core_bench_key cell either filled or carrying a `gaps[]` entry with full triedSources/triedQueries provenance). 5 is a parallelism guideline, not a ceiling.
- **Auto-resolution prep** — emit `autoResolveWinner` per contradiction (skill applies, no user prompt)
- **Lifecycle states** — emit `status` field changes via `lineupChanges` (skill applies transitions)
- **Pre-emit self-audit (REQUIRED)** — see PRE_EMIT_SELF_AUDIT below. Agent computes coverageMatrix for what it attempted, sets `partialReturn: true`, and emits. Orchestrator gap-gen supplements remaining cells. Looping back through Phase 3 is **forbidden** — emit and exit.
- **Delivery contract** — JSON-only final message, no narration, no file write, no truncation
- **Project boundary** — only AICoderMap session

## INTERNAL_RETRY_DISCIPLINE (format-driven cascade — replaces hardcoded escalation)

The agent NEVER emits a `gaps[]` entry on first try. Every gap candidate goes through the **format-driven cascade** described in FORMAT_DISPATCH above before being declared a gap. The cascade is fully data-driven — no hardcoded URL patterns or domain lists.

```
For each (modelId, field) still null after the primary fetch:
  walk the entry's fallback chain:
    fallbacks := entry.fallbacks || formatTaxonomy[entry.format].defaultFallbacks
    for fb in fallbacks:
      candidateUrl := fb.urlPattern
        ? resolve_url_pattern(fb.urlPattern, entry)         // e.g., aggregator mirrors
        : entry.url                                          // re-fetch with different extractor
      attempt fetch + extract per fb.format's extractor + extractorPatterns
      if captured: emit + break
      cost += 1 fetch (counted against per_model_fetch_budget)

  if still not captured AND a websearch_snippet step exists in the chain:
    run WebSearch queries (minimum 2 — see WEBSEARCH_PRIMARY_DISCIPLINE)
    tier-assign per result domain via whitelist lookup
    if any result yields a (bench, score) pair: emit + break

  if still not captured:
    emit gaps[] entry with:
      triedFormats:  [<format>, <fb1.format>, <fb2.format>, ...]
      triedPatterns: [<patternName1>, <patternName2>, ...]
      triedSources:  [<every URL attempted, including aggregator mirrors>]
      triedQueries:  [<every WebSearch query>]
```

**Cardinal rule:** an empty value in the artifact is a contract violation IF the agent did not walk the fallback chain. The skill's deep-fetch loop catches silently-skipped fields by checking gaps[] coverage against the field whitelist AND verifying `triedFormats[]` has at least 2 entries (one primary + one fallback) per gap.

**No hardcoded "if SPA → try GitHub" / "if blog → try news" branches** — those mappings now live in each entry's `fallbacks[]` (populated by `scripts/whitelist-format-migration.js`) and in `formatTaxonomy[<format>].defaultFallbacks`. Adding a new fallback path = editing the whitelist, never the agent.

## WEBSEARCH_PRIMARY_DISCIPLINE (2026 update — root-cause fix for SPA/403 walls)

**Why this section exists:** In 2026, every major AI leaderboard (artificialanalysis.ai, swebench.com, livecodebench.github.io, gorilla.cs.berkeley.edu, livebench.ai, matharena.ai) is a JavaScript SPA returning empty static HTML. Direct vendor blogs (openai.com/index, blog.google, x.ai) reject Claude Code's WebFetch with 403/404 (bot detection). Anthropic vendor blogs embed bench tables as PNG images (text-only extraction misses 80%+ of scores). Text-only WebFetch hit a structural ceiling at ~25% per-page coverage.

**The fix:** WebSearch (which uses Google's index + AI-summarized snippets) extracts numeric scores from cached pages, aggregator blogs, and snippet-rendered SPA content. WebSearch succeeded across all 6 frontier-model queries where WebFetch returned 403/SPA_NO_DATA.

**Mandatory protocol per (modelId, field) pair:**

```
Phase 1+2+3 update — WebSearch precedes WebFetch:

For each model surveyed:
  for each bench cell (every key in the dynamic bench-key universe — null, stale, or already-populated all re-fetched per UNCAPPED + UNCACHED doctrine):
    query := f'"{modelName}" benchmark "{benchKeyHumanName}" 2026'
    results := WebSearch(query)
    extract every (bench, value) pair the AI summary surfaces
    tier-assign per source domain via whitelist_tier_lookup(domain)  // NO hardcoded list
    emit to sourcesAdded[] with computed trustScore
  Then ONE WebFetch per confirmed-promising URL (vendor announcement,
  Vellum article, AA article) for triangulation/extra benches the search snippet missed.
```

**Tier assignment for WebSearch results — whitelist-driven (NO hardcoded domain list):**

```
function whitelist_tier_lookup(domain):
    for each entry in (vendors.* + leaderboards + aggregators + community + local + registries):
        if domain matches entry.url's hostname (or entry.alt URL hosts):
            return entry.tierOverride ?? entry.tier
    return 'C'   // unknown domain → conservative C-tier (skill discovery loop may
                 //                   later promote via whitelistAdditions[])
```

This replaces the prior hardcoded I/S/C domain tables. Adding a new aggregator = appending to `community[]` (or `aggregators[]`) in `data/sources-whitelist.json` with the appropriate `tier` (and optional `tierOverride` if it should override its category default). The agent never edits its own tier assumptions.

**Minimum 2 WebSearch queries per gap pair before emitting gaps[]:**
1. `"<modelName>" benchmark "<benchKey>" 2026`
2. `"<modelName>" "<benchKey>" score`

**In-cycle WebFetch on promising results** (2026-04-28 rev3): when a WebSearch result domain is NOT in the whitelist but the snippet contains the (modelId, benchKey) pair we're chasing, the agent WebFetches that URL THIS cycle under the in-cycle promotion rules (TRUSTED_SOURCE_WHITELIST rule 6 — HTTPS, not unhealthy, not private). The fetched content is extracted via the same EXTRACTION_DISCIPLINE; values land in `sourcesAdded[]` with tier=C; the URL is mirrored into `artifact.whitelistAdditions[]` for next-cycle hardening. There is no defer-to-next-cycle path — newly surfaced sources are usable immediately.

If both queries return zero useful (bench, score) pairs AND no in-cycle promotion fetch yielded a value, the agent has exhausted the fallback chain. Only then is `gaps[]` emission permitted, and the entry MUST carry `triedFormats[]` + `triedPatterns[]` + `triedSources[]` (including in-cycle promotion attempts and their HTTP status) + `triedQueries[]`.

## GAP_VALIDITY_GATE (advisory audit only — reformed 2026-04-28)

**Why this section exists:** Earlier cycles stripped gap entries that failed an adaptive triedSources floor. Operationally that meant "if you can't try ≥3 sources, don't even report the gap" — which pressured the agent to silently omit hard-to-reach pairs rather than transparently log them. **The user's policy reform: every fetch attempt + every reachable bit of provenance is useful information; never strip a gap.**

**Reformed rule (2026-04-28):**

- `gaps[]` entries are NEVER stripped by the orchestrator.
- The orchestrator's `validate_gaps()` walks every entry in advisory mode: it computes a "low-effort suspicion" score (gap.triedSources.length vs. clamp(advertised_high_weight_for_bench, 3, 5)) and flags entries that fall below the threshold by appending them to `runtime.fabricatedSuspicions[]` for human audit. The original entry stays in `gaps[]` regardless.
- `runtime.contractViolations` is no longer incremented; the concept is retired (the agent isn't "violating a contract" by reporting whatever it actually tried).

**Practical effect for the agent:** still try as many sources as feasible per gap (the cascade discipline below remains in effect — it's the right default), but the agent is no longer punished for reporting a gap with only one or two triedSources. Reporting a partial-effort gap is strictly better than omitting it.

**Audit reference (kept for human reviewers eyeballing the diff log):**

| advertised_high_weight | suggested triedSources floor | low-effort flag if below |
|---|---|---|
| 0–3 (rare/proprietary bench, e.g. aaCoding/aaAgentic/bfcl) | 3 (general low bar) | yes |
| 4 (e.g. swePro, aider) | 4 | yes |
| 5+ (sweV=10, lcbV6=8, gpqa=6, tb2=6, hle=5) | 5 (cap) | yes |

Per-bench advertised counts are computed at gate-evaluation time from `data/sources-whitelist.json` `leaderboards[].publishes[]` × `format` weight (>=0.7 = high-weight). The audit log surfaces them so reviewers can see whether a gap deserved more effort.

**Status of "data does not exist" claims:** the agent NEVER asserts non-existence. Its only honest options are:

- **Found a value** → emit to `models[].updates` + `sourcesAdded[]`.
- **Walked the entire fallback chain (≥2 sources, ≥2 queries) and found no value** → emit `gaps[]` with full provenance. This is a *bookkeeping* statement ("we tried these N sources and could not extract this pair"), NOT an assertion that the value doesn't exist.
- **Cannot try because tooling failed** (e.g., all WebSearch calls 500'd) → emit `runtime.fetchErrors[]` with the failure reason; do NOT emit a gap.

A legacy/deprecated model still gets the same treatment: try the canonical historical leaderboards (Papers with Code, Epoch AI, llm-stats archive, marc0.dev historical entries, BigCodeBench archive) before declaring a gap. "Model is old" is never a sufficient reason to skip the attempt.

## SOURCE_FIRST_SWEEP (Phase 1 primary mining — added 2026-04-27 rev2)

**Why this section exists:** prior phases iterated **per-model** (for each model, walk all sources). With 53 models × 5+ sources × 16 benches, this scaled poorly: per-model cascade was verification-blind and cache-unaware. Cycle 4 used only ~32 of a possible 600+ fetches because effort caps fired before saturation; cycle 5 used only 8 fetches because per-source caps capped the sweep. **2026-04-27 rev3 retires all effort caps**: the agent walks **each source ONCE**, extracts every (modelId, benchKey, value) tuple visible on that page in one pass, then chases unfilled cells through the full Phase 2 cascade until COMPLETENESS_TERMINATION holds. **2026-04-28 reform additionally retires the confirmed-cell skip** — vendors update scores between cycles, so persistent "confirmed → skip" caching froze stale data. Every cycle now re-extracts every (modelId, benchKey) cell from every advertised source. The verification map remains as a historical / contradiction-analysis log only; it never short-circuits a fetch.

**Mandatory protocol on `scope=full`:**

```
0. Load priors:
   verification_map := READ (project_root)/.aicodermap-verification-map.json
                       (gitignored audit log; per-cell history of past verifications.
                        NEVER read for skip decisions — informational only)
   active_models    := from idea_context.currentIds
   target_cells     := { (model.id, benchKey) | benchKey ∈ bench_keys_universe }
                       (every active model × every bench key, every cycle —
                        no skip based on prior confirmation; no skip based on
                        existing non-null value either, because the underlying
                        vendor figure may have changed)

1. Build tier-prioritised source queue from sources-whitelist.json:
   tier I  (independent leaderboard, format-weight >= 0.7):
            iterate leaderboards[] sorted by (publishes.length desc, lastVerifiedDate desc)
   tier S  (vendor model-cards/news, format-weight >= 0.7):
            iterate vendors.*.urls.modelCardUrlTemplate first, then postUrlPattern
   tier C  (community blogs, format-weight >= 0.7):
            iterate community[]
   skip:    sources with _runtime.unhealthy == true; persistent bot_blocked / spa_full
            with no fallback chain.

2. For each source in tier order (parallel batches of PARALLEL_SOURCES = 5):

   a) Fetch the aggregate URL (entry.url). NO budget cap (uncapped doctrine).
      The agent fetches the aggregate ONCE for efficiency, then any number of
      documented fallbacks (mirror, websearch_snippet, alternate URL) until
      either:
        - all expected (model, bench) tuples are extracted, OR
        - the fallback chain is exhausted (every documented alternative tried).
      No wallclock or fetch-count limit. The agent only stops when extraction
      is structurally complete on this source.

   b) Extract every (modelId, benchKey, value) tuple visible on the page.
      Match modelId against active_models[] using SLUG_RESOLUTION (vendorPrefixMap +
      vendorSuffixMap + slugVariations); match benchKey against entry.publishes[]
      (or, if publishes[] is empty/unknown, against the dynamic bench universe =
      `_schema.coreBenchKeys ∪ leaderboards[].publishes[]`).

   c) For each extracted tuple:
      key := f"{modelId}.{benchKey}"
      emit to sourcesAdded[] with this source's tier+url+trustScore
      (NO skip on prior confirmation; verification_map is audit-only and
       receives the new entry post-merge for contradiction analysis)

   d) Continue walking the source queue regardless of "saturation" — every
      source is visited every cycle so vendor score revisions surface
      immediately. Saturation termination retired 2026-04-28.

3. Per-source fallback (uncapped — exhaust the documented chain):
      try entry.fallbacks[*].url in order (e.g., websearch_snippet, mirror,
      static_html_table alternative, image_embedded OCR via scripts/extract-images.py)
      No fetch-count cap. Stop only when extraction is structurally complete
      OR every documented fallback has been tried (status: 200 + extracted /
      404 / unreachable). Log every attempt to runtime.fetchLog[].

4. Saturation rule retired (2026-04-28). Every source is walked every cycle
   for every active model — no early stop based on "confirmed enough times".
   Vendor scores can be revised, retracted, or re-issued between cycles, so
   re-extracting the live value on every refresh is the freshness contract.

5. COMPLETENESS_TERMINATION (sole exit condition — replaces all prior caps):
   The agent emits final JSON and stops only when ALL of these hold:
     a) Every leaderboard in sources-whitelist.json has been visited
        (status: extracted / unhealthy-skip / fallback-exhausted).
     b) Every vendor with perModelUrl/modelCardUrl/postUrl has been attempted
        for every model in that vendor's family (Phase 2 cascade).
     c) Every (modelId, benchKey) cell — ∀ active models × ∀ bench keys in
        bench_keys_universe — has been attempted at least once via the full
        cascade. Existing non-null values in models.json are NOT a reason to
        skip the attempt; the cell is re-fetched and either confirms, updates,
        or is logged as unchanged.
     d) For every cell that still produced no extractable value, a gaps[]
        entry is emitted with the full triedSources[] / triedFormats[] /
        triedPatterns[] / triedQueries[] provenance bundle. The orchestrator's
        GAP_VALIDITY_GATE is now ADVISORY (audit-only, see below) — it never
        strips entries; it only flags low-effort gaps for human review.

   No wallclock limit, no fetch-count limit. The agent terminates when the
   research is structurally complete, not when a budget runs out.

6. After Phase 1, residual cells flow to Phase 2 (PER_MODEL_URL_EXPANSION) and
   Phase 3 (WebSearch fallback) until COMPLETENESS_TERMINATION holds.
```

**Verification map update (post-extraction):**

```jsonc
// .aicodermap-verification-map.json
{
  "cells": {
    "opus-4-7.swePro": {
      "value": 64.3,
      "verifications": [
        {"source": "Scale SEAL",    "url": "...", "tier": "I", "fetched": "2026-04-27"},
        {"source": "BenchLM",       "url": "...", "tier": "I", "fetched": "2026-04-27"},
        {"source": "AA per-model",  "url": "...", "tier": "I", "fetched": "2026-04-27"}
      ],
      "confirmed": true,
      "lastChecked": "2026-04-27"
    }
  }
}
```

`confirmed = (verifications.length >= 3) AND (all verifications agree on value within 1.5pp)`. If multiple sources disagree, the cell is NOT confirmed even with 3+ verifications — it goes to contradictions[] for trustScore-based resolution.

**Why this beats per-model cascade:**

| Metric | Per-model (prior) | SOURCE_FIRST_SWEEP |
|---|---|---|
| Total fetches per cycle (estimate) | 53 × 12 = 636 capped at wallclock | unlimited — agent fetches until COMPLETENESS_TERMINATION |
| Verification-aware skip | no (each model from scratch) | yes (3+ verified = skip rest of cycle, persists across cycles) |
| Same source re-visited | up to 53× | exactly 1× per cycle (agent may re-try documented fallbacks) |
| Termination | wallclock cap | COMPLETENESS_TERMINATION (research structurally exhausted) |
| Coverage trajectory | linear-ish, plateaus around 30-35% (capped) | step-function: each cycle approaches reachable ceiling |

## PER_MODEL_URL_EXPANSION (Phase 2 fallback — for cells still empty after SOURCE_FIRST_SWEEP)

**Why this section exists:** the 2026-04-27 audit found that several whitelisted leaderboards (artificialanalysis.ai, benchlm.ai, epoch.ai, llm-stats.com) and most vendor blogs (blog.google, anthropic.com/news, deepmind.google/models/model-cards/) host **per-model pages** with rich bench tables that the prior cascade never visited. The agent only fetched aggregate leaderboard URLs, missing model-specific content like `https://artificialanalysis.ai/models/gemini-3-1-flash-lite-preview` or `https://deepmind.google/models/model-cards/gemini-3-1-pro/`. Those per-model pages frequently contain 14+ benchmarks for a single model — exactly what fills sparse cells.

**Mandatory cascade per (modelId, benchKey) pair (replaces prior 3-step fallback):**

```
For each empty bench cell on a model:

  Step 1 — Aggregate leaderboard (existing):
    Fetch entry.url for every leaderboard whose publishes[] includes <benchKey>.
    Tier-assign per whitelist; emit if found.

  Step 2 — Per-model URL discovery, dynamic-first (load-bearing):
    Iterate two source families with `perModelUrlTemplate` (sources that
    publish per-model detail pages):
      a. Every `leaderboards[]` entry with a non-null `perModelUrlTemplate`.
      b. Every `local[]` entry (e.g., Ollama Library) with a non-null
         `perModelUrlTemplate` AND `publishes[]` includes <benchKey>.
         Local detail pages (e.g., https://ollama.com/library/deepseek-v4-pro)
         carry vendor-published bench tables in the description block + Tags
         tab — high-recall source for open-weight models. Apply step 2 to
         them for any model whose `tier ∈ {open-flagship, coder-specialized,
         gemma, ollama-local}` OR whose `open === true`.

    For each iterated entry, RESOLVE THE PER-MODEL URL DYNAMICALLY (prior
    cycles guessed slugs first, missing models when the slug rule didn't
    match — reform 2026-04-28 rev4 makes guessing the LAST resort):

      2a (PRIMARY) — Catalog index discovery:
        On the first per-model lookup against this source in the cycle,
        fetch entry.url ONCE (the catalog index, e.g.
        https://ollama.com/library, https://artificialanalysis.ai/models).
        Parse every `<a href>` anchor; build a map
        catalogIndex[entry.url] = { <slug>: <absolute_url>, ... }.
        Cache in `runtime.catalogIndexes` and emit it in
        whitelistAdditions[] so subsequent cycles inherit the map without
        re-scraping. Look up the model by:
          1. exact match on model.id
          2. case-insensitive match on model.name
          3. fuzzy match: tokenize model.name, match anchor text containing
             every required token (vendor + version)
        If a match is found, fetch its URL and proceed to extraction. If
        the same catalog index has been scraped earlier this cycle, use
        the cached map — do NOT re-fetch.

      2b (FALLBACK) — WebSearch site-scoped discovery:
        If the catalog index lookup failed (model not listed, or anchor
        text doesn't disambiguate), run a WebSearch query:
            `"<model.name>" site:<entry.host>`
        Take the first result whose URL hostname matches entry.host AND
        whose path looks like a model detail page (e.g., contains the
        model.id slug or `/library/` / `/models/` segment). Fetch that URL.

      2c (LAST RESORT) — Slug substitution:
        Only when 2a + 2b both produced no candidate, fall back to the
        legacy guess-and-try path using `slugVariations` from the entry:
          For each variant in `slugVariations` (ordered):
            slug := variant.replace('{id}', model.id)
                           .replace('{family}', stripVersion(model.id))
                           .replace('{N}', majorVersion(model.id))
            url := perModelUrlTemplate.replace('{slug}', slug)
            fetch(url); if 200 + extractable, emit + break
        slugVariations is a hint, not authoritative — sources without it
        still go through 2a + 2b first. **The agent does NOT hardcode
        per-model URLs anywhere; every URL is either discovered from a
        catalog index, surfaced by WebSearch, or templated from data.**

    Status logging: every URL attempted (2a hit, 2b hit, 2c hit, 404, 5xx,
    parse miss) is logged to `triedSources[]` with its status code so the
    next cycle's catalogIndex map skips known-dead branches.

  Step 3 — Vendor model card / blog post (NEW):
    For the model's vendor (resolved via model.provider → vendors.<vid>):
      a) If vendor.urls.modelCardUrlTemplate exists:
         Try modelCardSlugVariations against the template (same {id}/{family}/{N} substitution).
         Fetch first 200 — emit if extractable.
      b) If vendor.urls.postUrlPattern exists AND modelCardUrl yielded nothing:
         Try postSlugVariations against the postUrlPattern.
         If postFormat == 'image_embedded' or 'bot_blocked': skip direct fetch, go to step 4.
         Otherwise fetch first 200 — emit if extractable.

  Step 4 — WebSearch fallback (existing, mandatory ≥2 queries before gap):
    Per WEBSEARCH_PRIMARY_DISCIPLINE (2 queries minimum).
    Use site:<domain> qualifier when targeting a known bot-blocked vendor blog
    (openai.com/index, x.ai/news, klu.ai).

  Step 5 — Emit gap[] only after all steps exhausted (per GAP_VALIDITY_GATE):
    triedSources[] MUST list every URL attempted in Steps 1-4 (including 404s)
```

**Slug variable substitution rules:**

| Token | Meaning | Example (model.id = `gemini-3-1-pro`) |
|-------|---------|---------------------------------------|
| `{id}` | model.id verbatim | `gemini-3-1-pro` |
| `{family}` | id with version + variant suffix stripped | `gemini` |
| `{N}` | major numeric version | `3` |
| `{variant}` | trailing variant token (pro/flash/lite/mini) | `pro` |
| `{YYMMDD}` | model.released converted to YYMMDD | `260219` |
| `{vendor_prefix}` | resolves via leaderboard/vendor `vendorPrefixMap[provider]` (e.g., `claude-` for Anthropic models on AA / BenchLM, empty for OpenAI/xAI) — enables vendor-conditional slug ordering without consuming a slot per provider | `claude-` for `provider=anthropic`, `""` otherwise |
| `{vendor_suffix}` | symmetric to `{vendor_prefix}`; resolves via `vendorSuffixMap[provider:variant \| provider \| default]` with compound-key fallback. Used for vendor-specific suffixes that depend on the model's variant (e.g., `-lite-preview` for Google flash variants on AA, `-a35b-instruct` for Alibaba Qwen MoE coder models on AA, `-lite` for Google flash modelCards on DeepMind) | `-lite-preview` for `google_deepmind:flash`, `-a35b-instruct` for `alibaba_qwen:coder`, `""` otherwise |
| `{id_no_prefix}` | strips leading `vendor_prefix` from id (handles models whose id already carries the prefix, e.g., `claude-haiku-4-5` with prefix `claude-` → `haiku-4-5`, avoids `claude-claude-haiku-4-5` double-prefix bug) | `haiku-4-5` for `model.id=claude-haiku-4-5` |
| `{slug}` | computed slug after substitution | (final URL token) |

**Whitelist schema additions for vendor-conditional substitution** (added 2026-04-27 via ds-tune; lifted hit_rate_at_1 from 0.68 → 0.96 and hit_rate_at_3 to 1.00 on the audit fixture):

```jsonc
{
  "leaderboards": [
    {
      "url": "https://artificialanalysis.ai/leaderboards/models",
      "perModelUrlTemplate": "https://artificialanalysis.ai/models/{slug}",
      "slugVariations": [
        "{vendor_prefix}{id}{vendor_suffix}",  // claude-opus-4-7 / gemini-3-1-flash-lite-preview / qwen3-coder-480b-a35b-instruct
        "{id}",                                 // gpt-5-5, grok-3, deepseek-v4-pro fall through here
        "{id}-preview",
        "{id}-reasoning",
        "{id}-high",
        "{id}-fast",
        "{id}-mini"
      ],
      "vendorPrefixMap": {
        "anthropic": "claude-",
        "default": ""
      },
      "vendorSuffixMap": {
        "google_deepmind:flash": "-lite-preview",   // gemini-3-1-flash → gemini-3-1-flash-lite-preview
        "alibaba_qwen:coder":    "-a35b-instruct",  // qwen3-coder-480b → qwen3-coder-480b-a35b-instruct
        "default":               ""
      }
    }
  ],
  "vendors": {
    "anthropic": {
      "postSlugVariations": ["claude-{id_no_prefix}", "{id}"],
      "vendorPrefixMap": { "anthropic": "claude-", "default": "" }
    },
    "google_deepmind": {
      "modelCardSlugVariations": ["{id}{vendor_suffix}", "{id}", "{id}-preview", "{id}-pro"],
      "vendorSuffixMap": { "google_deepmind:flash": "-lite", "default": "" }
    }
  }
}
```

**Key compound-lookup semantics** (applies to both `vendorPrefixMap` and `vendorSuffixMap`):

```
lookup(map, provider, variant):
  1. try `<provider>:<variant>`  (e.g., google_deepmind:flash)
  2. try `<provider>`            (e.g., anthropic → "claude-")
  3. try `default`
  4. else ""
```

`{variant}` is the trailing matched token from `model.id` against the recognized set `{pro, flash, lite, mini, max, plus, fast, high, coder, instruct, chat, moe}`. So `gemini-3-1-flash` → variant=`flash`; `qwen3-coder-480b` → variant=`coder`; `mimo-v2-5-pro` → variant=`pro`.

**Adding a new provider-conditional rule** (data-only, no spec change):

- New prefix (e.g., `cohere-` for Cohere models on a leaderboard) → append `"cohere": "cohere-"` to that leaderboard's `vendorPrefixMap`.
- New suffix (e.g., `-instruct` for Mistral instruct variants) → append `"mistral:instruct": "-instruct"` to `vendorSuffixMap`.
- New variant token (e.g., recognize `experimental` as a variant) → eval already supports the list above; if a new token is genuinely needed, add it once to `auto/eval.py:variant()` and to this table.

**Coverage status (post-tune 2026-04-27):**

| Family | Quirk | Resolved by |
|---|---|---|
| Anthropic | `claude-` prefix on AA/BenchLM/Epoch/news | `vendorPrefixMap.anthropic` (DONE) |
| Anthropic | `claude-haiku-4-5` already prefixed | `claude-{id_no_prefix}` (DONE) |
| xAI | Epoch canonicalizes `grok-4-20` → `grok-4` | `{family}-{N}` variant (rank 3, hit_rate_at_3=1.00) |
| Google DeepMind | flash variants need `-lite-preview` (AA) / `-lite` (modelCard) | `vendorSuffixMap.google_deepmind:flash` (DONE) |
| Alibaba Qwen | coder MoE needs `-a35b-instruct` (AA) | `vendorSuffixMap.alibaba_qwen:coder` (DONE) |
| OpenAI / DeepSeek / Moonshot / Z.ai / Xiaomi / MiniMax / Nvidia / StepFun / all_hands_ai | no quirk — `{id}` directly resolves | default empty (covered) |
| Mistral / Meta | blog post slug uses descriptive kebab (`mistral-large-2407`, `llama-4-multimodal-intelligence`) — NOT derivable from model.id | WebSearch-driven discovery (out of scope for slug-tune; agent fallback chain handles) |

**Effort impact:** Step 2 + Step 3 add up to ~4 + ~4 = ~8 fetch attempts per model. Under the UNCAPPED doctrine these are NOT budgeted — they all run. Parallelism guideline of 5 concurrent models still applies for queue scheduling, but the per-model attempt count rises and falls with the cascade's actual reach.

**404 logging:** Every 404 from Step 2-3 is logged to `triedSources[]` with status `404` so the next cycle does NOT retry that exact URL (saves budget). The orchestrator inspects `triedSources[].status` and skips known-404 variants for 30 days, then re-attempts (vendors may publish post later).

**Slug-mismatch examples (from 2026-04-27 audit — refer when designing slugVariations):**

- AA `model.id=opus-4-7` → tries `opus-4-7` (404), `claude-opus-4-7` (200) — `claude-{id}` variant wins for Anthropic models on AA
- AA `gemini-3-1-flash` → tries `gemini-3-1-flash` (404), `gemini-3-1-flash-preview` (404), `gemini-3-1-flash-lite-preview` (200) — needs vendor-specific variant
- Epoch `deepseek-v3-2` → 200 directly; `deepseek-v3` → would 404 (older versions get date suffixes)
- DeepMind model-card `gemini-3-1-pro` → tries `{id}` directly (200) — straightforward
- Anthropic news `opus-4-7` → tries `claude-opus-4-7` (200); slug rule: `claude-{id}`

The agent NEVER hardcodes these mappings — they live in each whitelist entry's `slugVariations[]` array and are extended via `whitelistAdditions[].slugVariations` when the agent discovers a new working slug pattern.

## DYNAMIC_WHITELIST_DISCOVERY (self-healing whitelist mutation)

When the agent finds a NEW source domain that consistently provides high-quality bench data NOT in the current whitelist, it MUST emit a `whitelistAdditions[]` field in the output JSON:

```jsonc
"whitelistAdditions": [
  {
    "tier": "I"|"S"|"C",
    "domain": "lushbinary.com",
    "sampleUrl": "https://lushbinary.com/blog/gpt-5-5-vs-claude-opus-4-7-comparison-benchmarks-pricing/",
    "extractedFields": ["gpt-5-5.swePro", "gpt-5-5.tb2", "opus-4-7.swePro"],
    "rationale": "Curated 1:1 comparison articles with exact numeric scores for top frontier pairs"
  }
]
```

The skill's Step 7.5 reads `whitelistAdditions[]` and:
1. For C-tier: appends to `data/sources-whitelist.json[community[]]` with `format:'static'`, `lastVerifiedDate:today`, `consecutiveFailures:0`.
2. For I-tier: appends under `aggregators[]` with `phase:'discovery'` (not auto-promoted to `phase:'pricing'` or `'leaderboard'` without manual review).
3. For S-tier: only added if matches a known vendor; ignored otherwise.

Self-healing rule: if a domain in the whitelist registers `consecutiveFailures ≥ 3` across cycles (404/403/SPA_NO_DATA), the skill auto-demotes it to `_runtime.unhealthy: true` and the agent skips it for the next 2 cycles before retrying.

## SOURCE_HEALTH_CHECK (per-cycle prelim, agent-internal)

At the start of every refresh cycle, before Phase 0 lineup discovery, the agent quickly probes critical leaderboard URLs (sample 3 from `leaderboards[]` where `phase=='leaderboard'`):

```
for each probe_url in sample_critical_urls(3):
  result := WebFetch(probe_url, prompt="report exactly: 'OK' if numeric table data visible, 'SPA_NO_DATA' if JS-only, '403/404' if blocked")
  if result == 'SPA_NO_DATA' or 4xx:
    runtime.healthChecks[domain] = "unhealthy"
    skip this URL for current cycle's Phase 1; rely on WebSearch + alternate sources

Emit runtime.healthChecks[] in the output JSON so skill can update sources-whitelist.json's
`_runtime` block. Persistent unhealthy domains (≥3 consecutive cycles) are auto-flagged
in the whitelist file for human review.
```

## SPA_AUTO_FALLBACK (default behavior — no gap emission on SPA detection)

When a fetch returns SPA markup (text/html ratio < 0.10 OR no bench keyword in text):
1. Immediately attempt the page's GitHub source URL if a vendor-canonical mapping exists in sources-whitelist (each leaderboard entry can carry a `githubSource` URL — agent checks this field).
2. If no GitHub mapping, attempt the leaderboard's main aggregate URL one level up (e.g., `/models/<id>` SPA → `/leaderboards/models`).
3. If both fail, escalate to INTERNAL_RETRY_DISCIPLINE step 2.
4. SPA detection by itself is NEVER a gap reason — only post-escalation failure is.

## OUTPUT_DELIVERY_HARDENING (revised contract — last assistant message)

Before emitting the final JSON:
1. Verify first non-whitespace char is `{` and last is `}`.
2. Verify no markdown fence (```), no leading "Here is:", no trailing "Sources:" listing.
3. Verify all required top-level keys present: `confidence`, `synthesis`, `lineupChanges`, `models`, `newModels`, `contradictions`, `sourcesAdded`, `gaps`, `validationCoverage`, `error`.
4. Verify size ≤30KB. If exceeding, drop in this order: i18nUpdates → duplicate sourcesAdded clusters → models[].updates entries that contain only `lastUpdated` (no other fields changed).
5. If any verification fails, RE-EMIT the message with corrections. Never deliver a violating message.

The skill parses Task tool's return value via regex `^\s*(\{[\s\S]*\})\s*$`. Narration before/after the JSON makes parsing fragile — never narrate.

## RESEARCH_PIPELINE_OPTIMIZATION (P10 reform — efektif + hızlı + eksiksiz)

UNCAPPED + UNCACHED doctrine remains in force ("her cell her cycle"). The
optimizations below reduce wallclock without sacrificing completeness.

1. **Concurrent Phase 0 + Phase 1 dispatch** — Phase 0 (vendor lineup) and
   Phase 1 (whitelist leaderboard sweep) run in PARALLEL via a single-message
   multi-tool-call. Critical path becomes `max(P0, P1) + P2` instead of
   `P0 + P1 + P2`. Both feed Phase 2 once available.
2. **Parallel fetch batching** — vendor + leaderboard URLs fetched in batches
   of `_schema.contracts.PARALLEL_FETCH_BATCH` (default 5) per single-message
   tool-call burst. The agent issues all batch members concurrently, never
   sequentially.
3. **Multi-model batch extract** — when a leaderboard table lists N models,
   ONE fetch + ONE parse → cells emitted for every matched model in that
   single pass. This is the documented `static_html_table` semantic; agent
   never re-fetches the same aggregate page per-model.
4. **Source priority cascade** — Phase 3 walks publishers in deterministic
   order: `priority="primary"` → `secondary` → `tertiary` → WebSearch
   fallback. Whitelist `publishes[]` may be either a flat string list (legacy)
   or `[{key, priority}]` (P10.4); the agent reads both shapes via
   `idea_context.sourcesWhitelist` without normalization.
5. **Low-coverage priority queue** — when the skill ships `idea_context.priorityCells[]`
   (computed from MATRIX_SNAPSHOT), the agent resolves those cells FIRST in
   Phase 2/3 cascade. Mid-cycle interruption thus closes the most starved
   cells before less critical ones.
6. **Phase 1.5 broad WebSearch sweep** — concurrent with Phase 1 fetches, the
   agent issues `WebSearch("<bench> leaderboard 2026")` queries for each
   coreBenchKey. Snippets discover unknown leaderboards (auto-suggested via
   `whitelistAdditions[]`) and surface scores without waiting on Phase 3.
7. **Phase 0 fail-fast** — vendor URL 4xx/5xx → 1 retry with
   `_schema.contracts.FETCH_RETRY_COUNT` (default 1) backoff
   `_schema.contracts.FETCH_TIMEOUT_SEC` (default 10s) → vendor entry skipped
   for this cycle (recorded in `gaps[]` under `lineup:<vendor>: unreachable`).
   Never block on a stuck fetch.
8. **Deterministic output ordering** — `models[]` sorted by `id` ascending;
   each `models[i].updates.bench` keys ordered per `coreBenchKeys`; `gaps[]`
   sorted by `(modelId, benchKey)` lex; `sourcesAdded[]` mirror. Result:
   idempotent re-application, minimal git diff churn, faster review.
9. **Run metadata** — populate `runMetadata` with phase wallclock counters
   (`phase0Ms`, `phase1Ms`, `phase2Ms`, `phase3Ms`, `totalMs`). Skill compares
   to prior cycle and surfaces `⚠ phase-N regression` in CHANGELOG when a
   phase doubles.
10. **Health-check freshness TTL** — `_runtime.healthChecks[url].observedAt`
    is honored; entries fresher than `_schema.contracts.HEALTH_CHECK_TTL_DAYS`
    (default 7) skip the re-probe step (extraction still runs).

These directives never weaken completeness — they only shorten the wallclock.
The matrix invariant + gap chain rules above remain absolute.

## SUCCESS_CRITERIA

The agent cycle is **complete** when every cell the agent **attempted** is either
filled, gapped (with provenance), or marked N/A. The agent does NOT need to
attempt every cell — `partialReturn: true` is always set, and the orchestrator
gap-gen closes the matrix invariant for anything the agent did not attempt.

Quality rules (agent is responsible for these):
1. Every `gaps[]` entry the agent emits has `triedSources[]` ≥ 1 URL,
   `triedQueries[]` ≥ 2 queries, `triedFormats[]` ≥ 1 format.
2. Every leaderboard whose `publishes[]` intersects `coreBenchKeys` was visited
   (status 200 + extract attempted, OR documented unreachable + fallback exhausted,
   OR `_runtime.unhealthy` auto-skip).
3. Every vendor in `sourcesWhitelist.vendors[]` was attempted for Phase 0 lineup
   discovery.
4. Every `models[].notApplicable[]` entry cites a `rule` from
   `sourcesWhitelist._schema.notApplicableRules.rules[]` (no hardcoded model id).

The orchestrator (`scripts/merge.py`) HARD-BLOCKs via MX1 gate — satisfied by
the combined agent output + gap-gen supplement, not the agent alone.

## PARTIAL_RETURN_PROTOCOL

When `PRE_EMIT_SELF_AUDIT` runs:
1. Compute `coverageMatrix` for cells attempted this cycle only.
2. Set `partialReturn: true` in the artifact.
3. For each cell the agent attempted but could not fill:
   - If matching N/A rule exists → `models[].notApplicable[]` entry.
   - Otherwise → `gaps[]` entry with `triedSources[]`, `triedQueries[]`, `triedFormats[]`.
4. **Emit and exit.** Do NOT loop back. Do NOT retry missing cells.
   The orchestrator gap-gen step is mandatory and covers remaining cells.

Fabricating an N/A rule (citing a rule absent from `_schema.notApplicableRules`)
fails audit-data-coherence AC9 and rolls the merge back.

## INADEQUACY_SIGNALS (orchestrator-side)

The orchestrator triggers `COMPLETENESS_RETRY` (single retry) or surfaces a
loud CHANGELOG warning on any of:

- `coverageMatrix` missing or `totalCells == 0`.
- `filledCells + gapsRecorded + notApplicableCells != totalCells`.
- Model in `idea_context.currentIds` absent from BOTH `models[]` AND `gaps[]`
  AND `notApplicable[]`.
- `runtime.modelAudit[id] == "zero-delta-no-gap"` (skill matrix-snapshot
  delta detector — model received no updates and emitted no gaps; suspect
  silent omission).
- `gaps[]` entry with `triedSources[]` empty (stripped → silent omission).
- `notApplicable[].rule` not found in `_schema.notApplicableRules.rules[]`
  (fabricated N/A — caught by audit-data-coherence AC9).
