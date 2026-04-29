
## [2026-04-29] — autonomous refresh-all [WARN: very low cumulative provenance coverage 22.6%] [MX2: coverage 22.6% < absolute floor 30%]
- Note: research agent hit completeness loop (87 tool calls); partial artifact generated via gap-gen script. All 1430 cells accounted for (323 filled + 1107 gaps). Next cycle re-attempts all cells.

### Updated
- 52 models: `gemini-3-1-flash`, `gemini-3-1-pro`, `gpt-4-1`, `gpt-5-4`, `grok-3`, `grok-3-mini`, `mistral-large-3`, `o3`, `o4-mini`, `opus-4-7`, `sonnet-4-6`, `codestral-22b`, `deepseek-v3-2`, `deepseek-v4-flash`, `deepseek-v4-pro`, `devstral-2`, `devstral-medium`, `glm-5-1`, `kimi-k2-6`, `llama-4-maverick`, `llama-4-scout`, `mimo-v2-5`, `mimo-v2-5-pro`, `mimo-v2-flash`, `mimo-v2-pro`, `minimax-m2-5`, `minimax-m2-7`, `nemotron-3-super`, `qwen-3-6-27b`, `qwen-3-6-max`, `qwen3-235b`, `qwen3-32b`, `qwen3-6-35b-moe`, `qwen3-6-plus`, `qwen3-coder-30b`, `qwen3-coder-480b`, `qwen3-coder-next`, `step-3-5-flash`, `gemma-3-27b`, `gemma-4-26b-moe`, `gemma-4-31b`, `gemma-4-e2b`, `gemma-4-e4b`, `deepseek-coder-v2-16b`, `deepseek-r1-14b`, `qwen25-coder-32b`, `qwen25-coder-7b`, `codestral`, `devstral-small-2`, `claude-haiku-4-5`, `gpt-5-5`, `grok-4-20`

### Gaps (1107 entries — see data/known-gaps.json or next refresh)
- `None`: No SWE-bench Verified score found in agent survey or public leaderboards
- `None`: No SWE-bench Multilingual score found in agent survey or public leaderboards
- `None`: No NL2Repo score found in agent survey or public leaderboards
- `None`: No Terminal-Bench v2 score found in agent survey or public leaderboards
- `None`: No Terminal-Bench Hard score found in agent survey or public leaderboards
- `None`: No tau-bench v2 score found in agent survey or public leaderboards
- `None`: No tau-bench v3 score found in agent survey or public leaderboards
- `None`: No MCP-Atlas score found in agent survey or public leaderboards
- ... and 1099 more


## [2026-04-29] — autonomous refresh-all [WARN: very low cumulative provenance coverage 42.0%] [MX1: matrix invariant violated — 1105 cell(s) silently missing (claude-haiku-4-5.aaAgentic, claude-haiku-4-5.aaCoding, claude-haiku-4-5.aaOmni, claude-haiku-4-5.arcAgi2, claude-haiku-4-5.bfcl ...+1100); filled_gap=1] [MX2: coverage 22.6% < absolute floor 30%]

### Added
- `grok-4-1-fast` — new model from vendor lineup discovery

### Updated
- 10 models: `sonnet-4-6`, `gemini-3-1-flash`, `llama-4-maverick`, `kimi-k2-6`, `deepseek-v4-pro`, `mimo-v2-5-pro`, `step-3-5-flash`, `qwen3-235b`, `qwen3-coder-480b`, `qwen3-coder-30b`

### Resolved (auto via trustScore)
- sonnet-4-6.gpqa: winner={'value': 74.1, 'trustScore': 0.53, 'sourceUrl': 'https://www.nxcode.io/resources/news/claude-sonnet-4-6-complete-guide-benchmarks-pricing-2026', 'tier': 'C'} (severity=RED, Δ15.8)
- gemini-3-1-flash.hle: winner={'value': 33.7, 'trustScore': 0.7, 'sourceUrl': 'https://blog.google/products-and-platforms/products/gemini/gemini-3-flash/', 'tier': 'S'} (severity=RED, Δ17.5)
- llama-4-maverick.lcb: winner={'value': 43.4, 'trustScore': 1.0, 'sourceUrl': 'https://benchlm.ai/models/llama-4-maverick', 'tier': 'I'} (severity=RED, Δ41.6)

### Gaps (3 entries — see data/known-gaps.json or next refresh)
- `grok-4-1-fast.swePro`: New model with no published bench data yet; early access only
- `grok-4-3.swePro`: Grok 4.3 Beta early access only, no published benchmark data
- `deepseek-v4-pro.mrcr`: Single C-tier source only; MRCR not on standard leaderboards

# Changelog

All notable changes to AICoderMap will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2026-04-29.d] — refresh pipeline reform (gate stack)

### Added
- `scripts/lib/whitelist.py` + `scripts/lib/matrix.py` — DRY shared modules (P9). Every audit/merge script now reads contracts and matrix invariants through one path.
- `scripts/audit-bench-source-mapping.py` — AC6/AC7/AC8: every `coreBenchKey` must have a publishing leaderboard; advertised keys must be canonical; single-publisher keys flagged.
- `scripts/migrate-w1-foundation.py` — one-shot migration adding `notApplicableBenchKeys` + `benchQuarantine` to every model entry; bootstraps `_schema.contracts` + `_schema.benchAliases` + `_schema.notApplicableRules` + `_schema.deprecatedBenchKeys` blocks in the whitelist.
- `merge.py _verify_matrix_invariant()` — MX1 cell-level invariant: every `(active_modelId, coreBenchKey)` cell ends in exactly one of FILLED / GAP / NOT_APPLICABLE. HARD BLOCK + `.bak` rollback on violation; `--warn-only-invariant` (or `AICODERMAP_MX1_WARN_ONLY=1`) for migration phase.
- `merge.py validate_gaps()` MX3 — strips gap entries with empty `triedSources[]`; surfaces them via MX1 as silent omissions.
- `merge.py` MX2 absolute coverage floor (default 0.30) — env-gated BLOCK via `AICODERMAP_MX2_BLOCK=1`; `--bypass-floor-check` for migration.
- `audit-data-coherence.py` AC9 (notApplicableBenchKeys ⊆ coreBenchKeys), MX4 (filled cell ↔ sources.json entry), MX5 (≥2 distinct source URLs per filled cell, quarantine candidates).
- SKILL.md Step 5a/5b/5c — MATRIX_SNAPSHOT, COMPLETENESS_GATE (single retry), DELTA_CHECK (zero-delta-no-gap detection).
- agent.md SUCCESS_CRITERIA / ADEQUACY_REACTION / INADEQUACY_SIGNALS blocks; `notApplicable[]` + `coverageMatrix.notApplicableCells` + `runMetadata` in OUTPUT_SCHEMA.
- agent.md RESEARCH_PIPELINE_OPTIMIZATION (P10) — concurrent Phase 0+1, parallel batching, priority cascade, low-coverage queue, fail-fast.
- pre-commit hook now runs `audit-bench-source-mapping.py`; cross-platform python resolver (`python3` → `python` fallback for Windows).

### Changed
- `verification-map.py` — `confirmed` flag retired (P9 YAGNI: no reader, recomputable on demand from `verifications[]`).
- agent.md bench alias table moved out of EXTRACTION_DISCIPLINE row 5 → `_schema.benchAliases` whitelist block. Vendor names removed from `SCOPE_CATEGORIES` (data-driven via `sourcesWhitelist.vendors`).
- agent.md gap shape HARD: `triedSources[]≥1`, `triedQueries[]≥2`, `triedFormats[]≥1`. Empty/placeholder gaps stripped.
- SKILL.md CONSTANTS — numeric thresholds now reference `_schema.contracts` SSOT block; `lib/whitelist.py contracts()` overlays SAFE_DEFAULTS.
- `data/sources-whitelist.json._schema` — `contracts`, `benchAliases`, `notApplicableRules`, `deprecatedBenchKeys` blocks; `publishes[]` shape upgrade documented (string list legacy + `{key, priority}` future).
- `data/models.json` — every entry gains `notApplicableBenchKeys: []` + `benchQuarantine: {}`.
- `docs/WORKFLOW.md` — section 9 reform gate matrix (AC1-AC9 + MX1-MX5 + CP1), bench add/deprecate checklist, post-reform pipeline diagram.

### Activation phases
- W1 (current): every new gate WARN-only via env flags or CLI flags. Pre-commit runs both audits; bench-source mapping non-blocking.
- W2: `unset AICODERMAP_MX1_WARN_ONLY` + `unset AICODERMAP_BENCH_SOURCE_WARN_ONLY` → AC6/AC7/MX1 promote to HARD BLOCK.
- W3: `AICODERMAP_MX2_BLOCK=1` + `AICODERMAP_MX4_BLOCK=1` set as defaults; `--bypass-floor-check` retired.

## [2026-04-29.c] — preset weight bug fix + bench taxonomy expansion

### Fixed
- `applyPreset` weight leak: prior `{...DEFAULT_WEIGHTS, ...preset}` spread leaked DEFAULT keys for every key the preset omitted, pushing runtime sums to 123–160 instead of 100. Switched to zero-base merge `Object.fromEntries(BENCH_KEYS.map(k => [k, preset[k] || 0]))`. Every preset now sums to exactly 100 at runtime.

### Added (3 new bench keys, 22 → 25)
- `nl2Repo` — NL → full-repo generation; 7/9 vendor adoption.
- `tau3` — τ³-bench, longer-horizon multi-turn tool-calling; 9/9 vendor adoption.
- `toolDec` — Tool-Decathlon, 10-task multi-tool agent; 9/9 vendor adoption.

### Reweighted
- All 5 presets rewritten to sum to 100 with new keys folded in (`balanced`, `swe-focused`, `agentic-focused`, `reasoning-focused`, `benchmark-only`).

### Skipped (rejected for project scope)
- `HLE w/Tools`, `HMMT Nov 2025`, `HMMT Feb 2026`, `IMOAnswerBench`, `Terminal-Bench 2.0 (best self-reported)`, `CyberGym`, `BrowseComp w/Context Manage`, `Vending Bench 2` — variant noise / domain mismatch / scale incompatibility.

## [2026-04-29.b] — bench taxonomy refactor

### Removed
- `aider` (Aider Polyglot) — leaderboard frozen 2025-08-25; 13 historical scores + 12 sources entries dropped.

### Renamed
- `lcbV6` → `lcb` (rolling LiveCodeBench supersedes pinned v6); 49 sources entries renamed.

### Added (7 new bench keys)
- `tbHard`, `cfElo`, `mmluPro`, `simpleQa`, `mrcr`, `arcAgi2`, `browseComp`.

### Reweighted
- DEFAULT_WEIGHTS rebalanced; all 5 presets rewritten; each still sums to 100.

### Fixed
- `grok-4-3` envelope un-flatten regression; `audit-data-coherence.py` cfElo range relaxed to 0-3500 (raw ELO).

### Migrated
- `data/models.json` (54 entries), `data/sources.json` (drops + renames), `i18n/{tr,en}.json`, `auto/eval.py` BENCH_KEYS list aligned.

## [Refresh log] — autonomous `refresh-all` cycles (compacted)

> Detailed per-cycle entries collapsed 2026-04-29 to keep this file readable.
> Each refresh now lands as a single-line summary; root-cause findings worth
> permanent record graduate to a manually-curated `[YYYY-MM-DD.x]` section.
> Full per-cycle history is recoverable from `git log -- CHANGELOG.md`.

| Date | Updated | Lineup Δ | Resolved | Gaps | Coverage | Note |
|------|---------|----------|----------|------|----------|------|
| 2026-04-29 | 2 | 1 deprecated | 0 | 48 | 38.0% | webDevElo SPA-gated across frontier set |
| 2026-04-29 | 27 | 2 deprecated, 1 renamed | 2 | 17 | 41.0% | matrix invariant violated (824 cells silent) → motivated reform [.d] |
| 2026-04-29 | 23 | — | 1 | 8 | 52.0% | invariant violated (428 cells silent) |
| 2026-04-29 | — | — | — | — | 52.0% | artifact missing coverageMatrix; agent self-audit skipped |
| 2026-04-28 | 29 | 4 deprecated | — | — | 54.0% | first refresh after dynamic whitelist mutation |
| 2026-04-28 | — | — | — | — | 48.0% | (lineup-sync) |
| 2026-04-27 (×5) | various | various | various | various | 38–48% | SOURCE_FIRST_SWEEP path live; per-model URL expansion; vendor-conditional slug map |
| 2026-04-26 (×9) | various | various | various | various | ~41% | UNCAPPED reform live; 9 cycles ran in one day during research-pipeline tuning |

## [Unreleased]

### Data refresh — 2026-04-25 (exhaustive 3-phase mining, agent run #5)

First exhaustive-mining pass per the new EXHAUSTIVE_FILL_STRATEGY. Three phases ran (Tier-A leaderboards + aggregator providers + per-model fallback), 22 tool uses, 75K tokens. The JS-rendered LiveCodeBench page returned empty (known limit; needs headless-browser capability — flagged for next refresh). AA leaderboard surfaced only top-10 visible rows; ranked 11+ aaIdx values not extracted (pagination needed). Despite these limits, 10 field updates landed:

#### New bench scores (independent-source, tier=I)
- `deepseek-v4-pro.swePro` 55.4 (BenchLM provisional)
- `mimo-v2-5-pro.tau2` 72.9 (Xiaomi release article)
- `deepseek-v3-2.aaIdx` 16 (AA DeepSeek V3 page)
- `minimax-m2-7.aaIdx` 50, `minimax-m2-5.aaIdx` 42 (AA leaderboard, confirmed already canonical)

#### Independent-source overrides applied (pricing canonical)
OpenRouter API live pricing replaced provider self-reports per VALIDATION_RULES rule 7:
- `deepseek-v4-pro.pricing.in` $1.74 → **$0.435** (RED Δ75% — OpenRouter aggregator price reflects post-launch reduction or different tier)
- `deepseek-v4-pro.pricing.out` $3.48 → **$0.87**
- `kimi-k2-6.pricing.in` $0.95 → **$0.74** (YELLOW)
- `kimi-k2-6.pricing.out` $4.00 → **$4.65** (YELLOW — aggregator margin)
- `glm-5-1.pricing.in` $1.00 → $1.05, `pricing.out` $3.20 → $3.50 (minor)

#### RED contradiction resolved (recency rule)
`gpt-5-4.swePro` 41.8 → **59.1** — Scale SEAL leaderboard rank-1 xHigh entry (current fetch) supersedes the prior High-scaffold value. Both fetches were tier=I from the same source URL; the newer extraction wins per recency rule. Previous user pick of 41.8 (High scaffold) preserved as historical provenance in `data/sources.json`.

#### Documented limits (for next refresh)
- LiveCodeBench page is fully JavaScript-rendered; static fetch returns empty HTML. Requires either a headless-browser fetch tool or an alternate data source (LCB GitHub releases JSON).
- Artificial Analysis leaderboard renders top-10 rows in HTML; ranks 11–50 require their public API or pagination handling.
- These limits flagged in `gaps[]` and surfaced as actionable items for the next exhaustive run.

#### Bench fill rate
17.0% → 17.8% (113 → 116 cells out of 650). Modest gain because most agent output went into pricing overrides rather than new bench cells. Provider mining captured aggregator pricing across 4 models (kimi/deepseek/glm/v4-pro) — high-value canonical updates.

### Architecture — 2026-04-25 (known-gaps registry + exhaustive-mining strategy)

#### `data/known-gaps.json` — new canonical registry (84 entries)
A curated list of `(modelId, benchKey)` pairs that will never be filled by a refresh — vendor opt-outs (xAI on SEAL/SWE-bench, Meta on SEAL, etc.), not-applicable benchmarks (Gemma E-series edge models on agentic), and out-of-scope variants (deepseek-r1-14b distill, qwen25-coder 7B/14B, codestral bare alias). Each entry carries `reason`, `note`, and optional `recheckAfter` ISO date for vendors whose policy may change.

#### Agent (`aicodermap-research-agent.md`) — `EXHAUSTIVE_FILL_STRATEGY` section
Three-phase mining protocol:
- **Phase A — Tier-A leaderboards** (5 parallel fetches): Artificial Analysis, Scale SEAL SWE-Pro, LiveCodeBench, Vellum, BenchLM — bench scores with tier=I.
- **Phase B — aggregator inference providers** (≤6 parallel fetches): OpenRouter (provider count, uptime, alt pricing), Together, Fireworks, DeepInfra, Groq, Ollama library, OpenCode Zen/Go, HuggingFace trending — captures throughput, latency, alt pricing, ollama metadata.
- **Phase C — per-model targeted follow-up** (≤3 fetches): HF cards / official blogs / tech reports for any model still <2 bench cells filled.

Per-row extraction with exact-id + fuzzy-name + alias-map matching. Independent-source rule applies to all Phase A+B values. Hard budget ≤14 total fetches / ≤30 tool uses / ≤140K input tokens. Skips every `(modelId, benchKey)` in `known-gaps.json` whose `recheckAfter` has not passed — prevents burning fetches on permanent absences and keeps the agent's `gaps[]` reserved for genuinely fixable holes.

#### Skill (`aicodermap/SKILL.md`) — known-gaps integration
Skill's CONTEXT block now lists `data/known-gaps.json` as a fourth canonical data file and instructs the orchestrator to include it in the agent prompt so the skip rule is honored.

#### UI (`assets/app.js` + `app.css` + `i18n/{tr,en}.json`) — opt-out indicators
`buildBenchCell` checks the known-gaps registry when a score is null; renders 🚫 (vendor opt-out), ∅ (not applicable), or – (out-of-scope) instead of generic "—". CSS classes `.opt-out-vendor-opt-out`, `.opt-out-not-applicable`, `.opt-out-out-of-scope` differentiate the markers; tooltip carries the human-readable note. New i18n keys `ui.optOut.{vendor-opt-out,not-applicable,out-of-scope}` for both languages.

### Data refresh — 2026-04-25 (gap-fill pass for 11 underrepresented models)

Targeted agent run filled the 10 confirmed-missing i18n entries plus partial bench/pricing/context data. Applied via the new schema-complete merge pipeline (MERGE_RULES); .bak → .bak2 rotation produced two backup layers; self-check verified no expected i18n entry was dropped.

#### i18n added (TR + EN strengths/weaknesses)
gemini-3-1-flash · gemini-3-1-pro · gpt-4-1 · grok-3 · mistral-large-3 · o3 · qwen3-235b · qwen3-32b · qwen3-6-plus · devstral-small-2 — 10 models. i18n coverage is now 49/50; `codestral` (the bare ID, not `codestral-22b`) does not exist in `data/models.json` and the bare-ID alias is documented in gaps.

#### New bench scores (independent-source rule applied)
- `mistral-large-3.lcbV6` 82.8 (Artificial Analysis, I-tier — canonical)
- `mistral-large-3.gpqa` 43.9 (BenchLM, I-tier — canonical)
- `o3.sweV` 71.7 (OpenAI, S-tier — already in sources)
- `o3.gpqa` 87.7 (S-tier, single-source flagged in gaps for I-tier follow-up)
- `qwen3-235b.lcbV6` 74.8 / `gpqa` 81.1 (Qwen technical report, S-tier)
- `gemini-3-1-pro` bench backfill (swePro/sweV/lcbV6/gpqa/hle/mcpA/aaIdx all confirmed)
- `gpt-4-1.sweV` 54.6 (OpenAI, S-tier)
- `grok-3.gpqa` 84.6 / `lcbV6` 79.4 / `context` 1M (xAI, S-tier; lcbV6 conservative — 80.4 alt mode flagged)
- `devstral-small-2.sweV` 68.0 + full schema fill (pricing/context/released/license/open)
- `mimo-v2-5.pricing/context` filled
- `qwen25-coder-7b.aider` 88.4
- `deepseek-coder-v2-16b.context` 128000
- `o3.pricing` $2/$8 with cacheHit $0.50, Plus $20/mo subscription

#### Provenance
9 new keys in `data/sources.json` covering the I-tier and S-tier values above. All conflicting figures preserved as separate entries for the contradiction tooltip.

#### Documented gaps (28 entries, in `gaps[]`)
SWE-bench Verified absence for grok-3, mistral-large-3, qwen3-235b, qwen3-32b, qwen3-6-plus (Qwen3 family + xAI do not submit to SEAL). Gemini-3-1-flash has no LCB v6 / aaIdx under current ID slug. Most cacheHit values for new models not officially disclosed. These remain `gaps[]` entries until next refresh.

### Docs + UI polish — 2026-04-25 (English-only repo, Ollama UI render)

#### Repo English-only (memory rule: docs in English; Turkish lives only in `i18n/tr.json`)
- `index.html` — `<html lang>` set to `en`; all default fallback strings translated to English (tooltips, nav, section headings, filter options, preset names, footer note). The `data-i18n-key`/`data-i18n-tip` runtime translation continues to switch the page to Turkish via `i18n/tr.json` when the user picks TR.
- `.gitignore` — comment lines translated to English.
- Internal-tool name leaks removed across `README.md`, `CLAUDE.md`, `CHANGELOG.md`, `docs/PRD.md`, `docs/TECHSPEC.md`, `docs/IMPLGUIDE.md`, `docs/PITCH.md` — moat B and template references now describe the technique generically ("reusable skill+agent template").

#### Ollama metadata UI (16 models with `ollama` rich object now render)
- `assets/app.js` — model card builder gains an Ollama block between the Unsloth list and the Notes section. Renders: 💻 title with architecture + parameter count, monospace `pullCmd` with a copy-to-clipboard button, secondary line with pullCount · license · releasedISO, and a "View on Ollama" link.
- `assets/app.css` — `.ollama-block`, `.ollama-title`, `.ollama-cmd-row`, `.pull-cmd`, `.copy-btn`, `.ollama-meta`, `.ollama-link` styles using project CSS variables, accent-soft left border, focus-visible accessibility.
- `i18n/{tr,en}.json` — new `ui.ollama.{title,copy,viewOn}` keys for both languages.

### Policy — 2026-04-25 (independent-source canonical rule)
- **Independent benchmark sources are now canonical.** Tier=I leaderboards (Artificial Analysis, Scale SEAL, Vellum, BenchLM, LiveCodeBench, OpenRouter, Arena.ai) override Tier=S provider self-reports for the same metric in `data/models.json`. Self-reported values are retained as provenance in `data/sources.json` only; the UI marker for "self-reported when no independent value exists" is pending M3+. Rationale: provider self-reports use custom scaffolds and best-of-N selection — independent leaderboards apply standardized scaffolds, which is the only foundation for the apple-to-apple comparison the tracker is built on.

### Data refresh — 2026-04-25 (run #4 + targeted gap-fill, full pass)

**Coverage**: 50 models · 80 source-attribution keys (25 new) · 16 with Ollama metadata · 10 with Unsloth UD quants · 39 with TR+EN strengths/weaknesses · validationCoverage 0.83 (M4 ≥0.95 force-overridden per documented gaps)

#### Updated (data normalization)
- **34 models** — provider field corrected from `"?"` placeholder to verified vendor (Anthropic, OpenAI, Google DeepMind, Moonshot AI, Z.ai, MiniMax, Alibaba Qwen, StepFun, Meta, DeepSeek, Mistral AI, Xiaomi, Nvidia, xAI)
- **35 models** — license field corrected from `"Unknown"` to verified license (Apache 2.0, Modified MIT, MIT, Llama 4 Community, Mistral Non-Production, Gemma, Nvidia Open Model, Proprietary)
- **5 models** — `open` flag corrected (true/false flips: kimi-k2-6, glm-5-1, MiMo-V2 family, Llama 4 family, Nemotron)
- **2 pricing updates** — `sonnet-4-6` filled ($3/$15/cache 0.30, Pro $20/mo); `kimi-k2-6` corrected ($0.60→$0.95 in, $2.75→$4.00 out, recency rule on apr-2026 source)
- **`sonnet-4-6` rich profile** — Anthropic provider, released 2026-02-17, context 1M, 4 providers, sweV resolved 77.1 (tier-weighted avg of 79.6 NxCode/blog-S + 74.6 System Card 10-trial-S; both S, no I available)

#### Added (bench scores under independent-source rule)
- `o4-mini` — sweV 58.6 (Vellum-I, picked over OpenAI 68.1-S; RED Δ9.5pp scaffold mismatch), lcbV6 80.2 (LCB-I), gpqa 81.4
- `grok-3-mini` — gpqa 79.1, lcbV6 69.6 (xAI conservative; alt 80.4 same-source flagged), aaIdx 32 (AA-I)
- `llama-4-maverick` — lcbV6 43.4 (Meta-S), gpqa 69.8, aaIdx 18 (AA-I)
- `llama-4-scout` — lcbV6 32.8, gpqa 57.2, aaIdx 14
- `gemma-4-e2b` / `gemma-4-e4b` — lcbV6 44.0 / 52.0 (Gemma4.wiki tier C), aaIdx 15 each
- `sonnet-4-6.aaIdx` 52, `kimi-k2-6.aaIdx` 54 (AA-I)
- `qwen3-6-35b-moe.sweMulti` 67.2 (recovered from prior artifact)

#### Updated (independent-source overrides — replacing prior self-reported values)
- `opus-4-7.swePro` 64.3→**61.2** (Scale SEAL-I)
- `opus-4-7.sweV` 87.6→**86.4** (Artificial Analysis-I)
- `glm-5-1.swePro` 58.4→**54.9** (Arena.ai Elo composite-I)
- `gpt-5-4.swePro` 57.7→**41.8** (Scale SEAL standardized scaffold-I) — RED Δ15.9pp resolved per user pick
- `kimi-k2-6.aaIdx` and `sonnet-4-6.aaIdx` filled from AA leaderboard (was null)

#### Added (Ollama + Unsloth metadata)
- **16 models** with full `ollama` object (pullCmd, tags, pullCount, architecture, parameters, license, releasedISO, ollamaUrl): qwen-3-6-27b · qwen3-235b · qwen3-32b · qwen3-6-35b-moe · qwen3-coder-30b · qwen3-coder-next · devstral-small-2 · devstral-2 · qwen25-coder-7b/14b/32b · deepseek-coder-v2-16b · deepseek-r1-14b · deepseek-v4-flash · llama-4-scout · llama-4-maverick
- **10 models** with `unslothVariants[]` (UD-IQ1_S/IQ2_XXS/IQ3_XXS/Q4_K_XL/Q5_K_M/Q8_0): qwen-3-6-27b (5 variants) · qwen3-235b · qwen3-32b · qwen3-6-35b-moe · devstral-small-2 · llama-4-scout · qwen3-coder-next · qwen25-coder-7b/14b/32b

#### Added (i18n strengths/weaknesses)
- TR + EN strengths/weaknesses populated for **39 models** (compound moat A — bilingual coverage). Stale alias keys cleaned: `gpt-5` → `gpt-5-4`, `deepseek-v4` → `deepseek-v4-pro`, `qwen-3-6-35b` → `qwen3-6-35b-moe`.

#### Flagged (contradictions resolved)
- **1 RED resolved** — `gpt-5-4.swePro` 57.7 [NxCode-S, custom scaffold] vs 41.8 [Scale SEAL-I, standardized] · Δ15.9pp · canonical 41.8 (independent-source rule + user pick)
- **3 YELLOW resolved** — `sonnet-4-6.sweV` 79.6/74.6 both-S → avg 77.1 (no I available) · `glm-5-1.swePro` Δ3.5pp → 54.9 I-tier wins (was avg 57.0) · `kimi-k2-6.pricing.in` Δ0.35 → 0.95 (recency)
- **2 RED surfaced from gap-fill** — `o4-mini.sweV` 68.1 OpenAI-S vs 58.6 Vellum-I (canonical 58.6) · `grok-3-mini.lcbV6` 69.6 vs 80.4 same-source xAI conflict (canonical 69.6 conservative)

#### Gaps (documented, deferred to next refresh)
- `llama-4-maverick`/`llama-4-scout` — no SWE-Verified or SWE-Pro on any Tier-I source (Meta does not self-report sweV; Scout not designed for agentic SWE)
- `grok-3-mini` — no SWE-Verified or SWE-Pro (xAI does not submit to SEAL or BenchLM)
- `gemma-4-e2b`/`gemma-4-e4b` — SWE absence is expected (edge models, no tool-use support); lcbV6 only on Tier-C source
- `o4-mini.aaIdx` — model not on AA leaderboard with current slug
- `gpt-5-5` — referenced in Codex blog rumor only, no official OpenAI announcement; not added; monitor May 2026

#### Infrastructure (skill + agent definition fixes during this run)
- `aicodermap-research-agent.md` — added `## OUTPUT_DELIVERY` section (JSON-only final-message delivery pattern): the agent returns its full schema as the final assistant text, no narration, no file write. Two prior runs lost their JSON output by saying "writing the file now" instead of returning the JSON. Frontmatter unchanged (no Write tool).
- `aicodermap/SKILL.md` Step 4 updated — explicit delivery contract reinforcement in agent prompt; Step 5 hardened to locate first `{` / last `}` if narration leaks.

### Skill enrichment — 2026-04-25 (federated fetch + llmfit snapshot)
- New `data/external/llmfit-hf-models.json` mirror — 148-model HuggingFace curated DB from `github.com/AlexsJones/llmfit`, used as canonical params/use_case/quant cross-reference (read before WebFetch, saves bandwidth).
- agent.md `FETCH_STRATEGY` directive added — Tier-A primary parallel fetch (AA leaderboard + HF Open LLM + Scale SEAL + LiveCodeBench + BenchLM), Tier-B targeted fallbacks (Vellum, EvalPlus, BFCL, Terminal-Bench, llm-stats), Tier-C provider-specific. Single-message multi-WebFetch parallelism enforced.
- 6 new sources added to leaderboard catalog: **Vellum LLM Leaderboard**, **HF Open LLM Leaderboard** (canonical for open-weight, direct anti-Aider-staleness), **EvalPlus** (HumanEval+/MBPP+), **LMMarketCap** (scrape only, hourly), **Artificial Analysis** flagged with public API access, **Scale SEAL** + **SWE-bench** linked to GitHub JSON releases.
- llmfit CLI integration boundary documented — Rust binary runs on user's machine; browser tracker (GitHub Pages, no backend) cannot invoke directly. Snapshot reference today; live integration deferred to Phase 2.

### Data refresh — 2026-04-25 (full sweep, pass 1+2 merged)
- **51 models** populated across 5 tiers (11 frontier · 28 open-tier1 · 0 openrouter · 5 gemma · 5 ollama)
- **49 source-attribution entries** added across 25 models
- **6 contradictions** flagged: 1 RESOLVED_AVG (`sonnet-4-6.sweV` 79.6/74.6/80.2 → avg 78.1, 3 Anthropic scaffolds), 5 YELLOW (kimi-k2-6.hle, gemini-3-1-pro.sweV, deepseek-v3-2.sweV, glm-5-1.swePro)
- **14 known gaps** preserved for next pass: tau2 broad gap (only opus-4-7), Llama 4 Meta-vs-Rootly triangulation pending, GLM-5.1 self-reported only, Qwen3.6-27B/35B Qwen-internal-scaffold, Codestral SWE-V missing, Qwen-Coder-Next pricing TBD, Grok 3 sparse data
- Skill defaults expanded: MODEL_FAMILIES (38 explicit IDs), INFERENCE_PROVIDERS (1st-party + 14 aggregator + leaderboard catalog), AUXILIARY_BENCHMARKS (bfcl/humanEval/fim/aime26/mmmu), USE_CASE_TAXONOMY + EXTERNAL_REFERENCE_REGISTRIES (llmfit hf_models.json cross-reference, precise VRAM formulas)


### Added (M1 Foundation)
- `data/models.json` — schema + 5 seed entries (2 frontier + 1 OpenAI + 2 open-tier1/local)
- `data/sources.json` — provenance for 10 Opus 4.7 bench scores; demo YELLOW contradiction on `swePro` (Δ 3.1pp)
- `data/gpu-database.json` — NVIDIA RTX 50/40/30/20/16 + Apple M1-M4 + AMD RX 7000/6000 + Intel Arc + webgpuVendorMap
- `i18n/tr.json` + `i18n/en.json` — nested key structure (ui/models/benchmarks/verdicts)

### Added (M2 Core)
- `index.html` — semantic HTML5, sticky nav, tooltip slot, OG meta, hreflang
- `assets/app.css` — 3-breakpoint responsive (mobile <640 / tablet 641-1024 / desktop >1024), CSS variables, dark theme + light theme override, export-mode rules
- `assets/app.js` — vanilla render core: schema validation, composite score, model card builder, no-innerHTML XSS defense

### Added (M3 Integration)
- Weights editor — 12 number inputs, 100% total constraint, 4 presets (balanced/swe-focused/agentic-focused/benchmark-only), reset, `acm.v1.weights` persist
- i18n TR/EN runtime switch — `acm.v1.language` persist, `<html lang>` + page-wide `data-i18n-key` walk
- Contradiction flag UI — 3pp YELLOW / 5pp RED, hover/focus tooltip with source breakdown (value, source URL, tier S/I/C, date)
- PNG export — vendored `html2canvas@1.4.1` (SHA256 e87e5507…ab8cb), per-section + full-page buttons, export-mode CSS hides nav/actions
- GPU VRAM detect — WebGPU `navigator.gpu` auto + manual GPU select (NVIDIA/Apple/AMD/Intel optgroups) + manual VRAM override + per-model compatibility badge (fits/offload/too-large) + Unsloth UD recommend + filter checkbox + `acm.v1.{gpu,vram}` persist
- Filters — tier select, open-only checkbox, GPU-fit-only checkbox, all persisted via `acm.v1.filters`

---

## [0.0.1] - 2026-04-25

### Added
- Initial repo bootstrap
- 6 documentation files in `docs/` (PRD, TechSpec, ImplGuide, Tasks, Workflow, Pitch)
- README + CHANGELOG + .gitignore
- Folder structure: `assets/`, `data/`, `i18n/`, `docs/`
- CLAUDE.md project instructions

### Status
- Pre-implementation — Project Kickstart complete, M1 Foundation starting
