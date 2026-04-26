
## [2026-04-26] — autonomous refresh-all

### Updated
- 18 models: `claude-haiku-4-5`, `gpt-4-1`, `gpt-5-4`, `gemini-3-1-flash`, `gemini-3-1-pro`, `o3`, `o4-mini`, `mistral-large-3`, `minimax-m2-5`, `mimo-v2-pro`, `mimo-v2-5-pro`, `mimo-v2-5`, `mimo-v2-flash`, `step-3-5-flash`, `nemotron-3-super`, `deepseek-v3-2`, `qwen3-coder-480b`, `glm-5-1`

### Resolved (auto via trustScore)
- gemini-3-1-pro.gpqa: winner=94.3 (severity=GREEN, Δ2.4)
- gpt-5-4.swePro: winner=57.7 (severity=GREEN, Δ1.4)

### Gaps (8 entries — see data/known-gaps.json or next refresh)
- `claude-haiku-4-5.swePro`: Not on SEAL board
- `claude-haiku-4-5.lcbV6`: No LCB v6 score for Haiku 4.5
- `gpt-4-1.swePro`: Non-reasoning model; no SWE-bench Pro published
- `o3.swePro`: o3 predates SWE-bench Pro
- `o4-mini.swePro`: No SWE-bench Pro for o4-mini
- `mistral-large-3.swePro`: No SEAL submission for Mistral Large 3
- `qwen3-coder-30b.bench`: Only 480B variant has published bench
- `minimax-m2-5.pricing`: M2.5 pricing not in standard per-1M format


## [2026-04-26] — autonomous refresh-all

### Updated
- 7 models: `claude-haiku-4-5`, `gemini-3-1-flash`, `nemotron-3-super`, `minimax-m2-7`, `mimo-v2-pro`, `step-3-5-flash`, `qwen3-coder-480b`

### Gaps (11 entries — see data/known-gaps.json or next refresh)
- `claude-haiku-4-5.gpqa`: No standalone GPQA Diamond score; benchmark image not machine-readable
- `claude-haiku-4-5.tau2`: Not in visible rows on tau2-bench AA leaderboard
- `claude-haiku-4-5.aaCoding`: AA only exposes composite Intelligence Index per model page
- `claude-haiku-4-5.aaAgentic`: AA only exposes composite Intelligence Index
- `gemini-3-1-flash.aaCoding`: Coding sub-index not separately published
- `gemini-3-1-flash.aaAgentic`: Agentic sub-index not separately published
- `nemotron-3-super.aaCoding`: AA bundles into composite index only
- `nemotron-3-super.aaAgentic`: AA bundles into composite index only
- ... and 3 more


## [2026-04-26] — autonomous refresh-all [WARN: partial coverage 41.0%]

### Updated
- 22 models: `opus-4-7`, `gpt-5-4`, `grok-3`, `deepseek-v4-pro`, `deepseek-v4-flash`, `devstral-medium`, `devstral-2`, `kimi-k2-6`, `qwen3-235b`, `qwen3-32b`, `qwen3-6-35b-moe`, `gemma-4-26b-moe`, `gemma-4-31b`, `gemma-4-e2b`, `gemma-4-e4b`, `deepseek-r1-14b`, `qwen25-coder-32b`, `qwen25-coder-14b`, `qwen25-coder-7b`, `codestral-22b`, `llama-4-maverick`, `llama-4-scout`

### Resolved (auto via trustScore)
- opus-4-7.sweV: winner=87.6 (severity=GREEN, Δ1.2)
- opus-4-7.gpqa: winner=95.4 (severity=GREEN, Δ1.2)
- sonnet-4-6.sweV: winner=82 (severity=YELLOW, Δ4.9)

### Gaps (11 entries — see data/known-gaps.json or next refresh)
- `claude-haiku-4-5.swePro`: No SEAL submission
- `claude-haiku-4-5.sweV`: Not on bench leaderboards
- `minimax-m2-7.all`: MiniMax platform unreachable
- `minimax-m2-5.all`: MiniMax platform unreachable
- `mimo-v2-pro.all`: Xiaomi MiMo fetch failed
- `mimo-v2-5-pro.all`: Xiaomi MiMo fetch failed
- `step-3-5-flash.all`: StepFun login wall
- `nemotron-3-super.all`: Nvidia NIM timeout
- ... and 3 more


## [2026-04-26] — autonomous refresh-all [WARN: partial coverage 41.0%]

### Added
- `claude-haiku-4-5` — new model from vendor lineup discovery

### Updated
- 26 models: `opus-4-7`, `sonnet-4-6`, `gemini-3-1-pro`, `gpt-5-4`, `grok-3`, `deepseek-v4-pro`, `deepseek-v4-flash`, `deepseek-v3-2`, `devstral-medium`, `devstral-2`, `kimi-k2-6`, `glm-5-1`, `qwen3-235b`, `qwen3-32b`, `qwen3-6-35b-moe`, `gemma-4-26b-moe`, `gemma-4-31b`, `gemma-4-e2b`, `gemma-4-e4b`, `deepseek-r1-14b`, `qwen25-coder-32b`, `qwen25-coder-14b`, `qwen25-coder-7b`, `codestral-22b`, `llama-4-maverick`, `llama-4-scout`

### Resolved (auto via trustScore)
- opus-4-7.sweV: winner=87.6 (severity=GREEN, Δ1.2)
- opus-4-7.gpqa: winner=95.4 (severity=GREEN, Δ1.2)
- sonnet-4-6.sweV: winner=82 (severity=YELLOW, Δ4.9)

### Gaps (11 entries — see data/known-gaps.json or next refresh)
- `claude-haiku-4-5.swePro`: No SEAL submission
- `claude-haiku-4-5.sweV`: Not on bench leaderboards
- `minimax-m2-7.all`: MiniMax platform unreachable
- `minimax-m2-5.all`: MiniMax platform unreachable
- `mimo-v2-pro.all`: Xiaomi MiMo fetch failed
- `mimo-v2-5-pro.all`: Xiaomi MiMo fetch failed
- `step-3-5-flash.all`: StepFun login wall
- `nemotron-3-super.all`: Nvidia NIM timeout
- ... and 3 more

# Changelog

All notable changes to AICoderMap will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

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
