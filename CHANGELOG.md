
## [2026-04-29.c] — preset weight bug fix + bench taxonomy expansion

### Fixed
- `applyPreset` weight leak: prior `{...DEFAULT_WEIGHTS, ...preset}` spread leaked DEFAULT keys for every key the preset omitted, pushing runtime sums to 123–160 instead of 100. Switched to zero-base merge `Object.fromEntries(BENCH_KEYS.map(k => [k, preset[k] || 0]))`. Every preset now sums to exactly 100 at runtime.

### Added (3 new bench keys, 22 → 25)
- `nl2Repo` — Natural-language → full repository generation (multi-file, dependency resolution); 7/9 vendor adoption per recent flagship reports, complementary to SWE-bench.
- `tau3` — τ³-bench, longer-horizon multi-turn tool-calling successor to τ²-bench; 9/9 vendor adoption.
- `toolDec` — Tool-Decathlon, 10-task multi-tool agent benchmark; 9/9 vendor adoption, complements MCP-Atlas.

### Reweighted (all 5 presets — every preset still sums to 100)
- `balanced`: 16 → 19 keys (added nl2Repo:5, tau3:1, toolDec:1; trimmed swePro 20→18, tb2 13→12, lcb 13→12, sweV 10→9, mcpA 5→4, tau2 4→3)
- `swe-focused`: 8 → 9 keys (added nl2Repo:9; trimmed swePro 25→23, sweV 18→16, sweMulti 15→13, lcb 12→11, tb2 10→9, tbHard 10→9)
- `agentic-focused`: 9 → 11 keys (added tau3:8, toolDec:7; trimmed tb2 18→15, mcpA 15→13, tbHard 12→10, browseComp 12→10, aaAgentic 12→10, tau2 10→8, swePro 8→7, lcb 8→7)
- `reasoning-focused`: unchanged (no reasoning-domain additions)
- `benchmark-only`: 10 → 13 keys (added nl2Repo:5, tau3:3, toolDec:3; trimmed swePro 18→17, sweV 15→13, tb2 13→11, lcb 13→11, tbHard 10→9, cfElo 8→7, sweMulti 8→7, gpqa 7→6)

### Skipped (analyzed user-supplied bench table, rejected for project scope)
- `HLE w/Tools` — variant of `hle`; tool-augmented branch adds noise without distinct signal.
- `HMMT Nov 2025`, `HMMT Feb 2026`, `IMOAnswerBench` — math/Olympiad domain already covered by `aime26`; coding-tracker overweighting math is an anti-pattern.
- `Terminal-Bench 2.0 (best self-reported)` — same bench as `tb2`, vendor-favored harness is provenance noise.
- `CyberGym` — niche security domain, 5/9 vendor adoption.
- `BrowseComp w/Context Manage` — variant of `browseComp`; vendor-reported context-management addon, single source of truth maintained.
- `Vending Bench 2` — $-denominated agentic business simulation, scale incompatible with 0–100 normalization.

## [2026-04-29] — autonomous refresh-all [WARN: very low cumulative provenance coverage 41.0%] [WARN: coverageMatrix invariant violated — 824 cell(s) silently missing (filled=347 + gaps=17 ≠ total=1188)]

### Updated
- 27 models: `opus-4-7`, `gpt-5-4`, `gpt-5-5`, `grok-4-20`, `grok-3`, `grok-3-mini`, `gemini-3-1-pro`, `sonnet-4-6`, `claude-haiku-4-5`, `deepseek-v4-pro`, `deepseek-v4-flash`, `kimi-k2-6`, `glm-5-1`, `nemotron-3-super`, `gemma-4-31b`, `gemma-4-26b-moe`, `qwen3-235b`, `qwen3-coder-480b`, `qwen3-coder-next`, `devstral-2`, `devstral-small-2`, `devstral-medium`, `llama-4-maverick`, `mimo-v2-5-pro`, `mimo-v2-pro`, `mimo-v2-flash`, `qwen3-6-plus`

### Deprecated
- `devstral-medium` — vendor-marked deprecated
- `codestral-22b` — vendor-marked deprecated

### Renamed
- grok-4-3 -> grok-4-20

### Resolved (auto via trustScore)
- kimi-k2-6.swePro: winner={'value': 58.6, 'trustScore': 0.47, 'sourceUrl': 'https://huggingface.co/moonshotai/Kimi-K2.6', 'tier': 'S'} (severity=GREEN, Δ0)
- deepseek-v4-pro.sweV: winner={'value': 80.6, 'trustScore': 0.67, 'sourceUrl': 'https://artificialanalysis.ai/articles/deepseek-is-back-among-the-leading-open-weights-models-with-v4-pro-and-v4-flash', 'tier': 'I'} (severity=GREEN, Δ0)

### Gaps (17 entries — see data/known-gaps.json or next refresh)
- `gemini-3-1-flash.sweV`: Gemini 3.1 Flash SWE-bench Verified not reported; model is API-only preview
- `gemini-3-1-flash.tb2`: TB2 not reported for Gemini 3.1 Flash
- `grok-4-20.sweV`: Grok 4.20 sweV not independently confirmed; leaked scores are unverified
- `grok-4-20.swePro`: Grok 4.20 swePro: only leaked estimates found, not from Scale SEAL official list for this ID
- `grok-4-20.hle`: Grok 4.20 HLE: only leaked estimates (35-45%) not independently confirmed
- `gpt-5-5.sweV`: GPT-5.5 SWE-bench Verified not published; OpenAI only reported Pro=88.7 unverified
- `opus-4-7.lcb`: Opus 4.7 LiveCodeBench not reported by Anthropic; model not on LCB leaderboard
- `opus-4-7.aime26`: Opus 4.7 AIME 2026 not separately reported; only AIME 2025 scores available
- ... and 9 more

## [2026-04-29.b] — bench taxonomy refactor

### Removed
- `aider` (Aider Polyglot): leaderboard frozen 2025-08-25; no Opus 4.7, Gemini 3.1 Pro, GPT-5.5 entries; vendors stopped self-reporting. 13 historical scores dropped from data, 12 sources entries dropped.

### Renamed
- `lcbV6` → `lcb`: pinned v6 dataset frozen Apr 2025 (12-month contamination window); switched to rolling LiveCodeBench leaderboard (May 2023 → present). 49 sources entries renamed.

### Added (7 new bench keys)
- `tbHard` — Terminal-Bench Hard (44-task subset, AA Index v4 component)
- `cfElo` — Codeforces ELO (raw 1000-3500 scale; normalized in composite)
- `mmluPro` — MMLU-Pro (57-discipline reasoning)
- `simpleQa` — SimpleQA-Verified (factuality / hallucination resistance)
- `mrcr` — MRCR 1M (long-context multi-needle retrieval)
- `arcAgi2` — ARC-AGI-2 (the only frontier bench below human baseline)
- `browseComp` — BrowseComp (web research agent benchmark)

### Reweighted
- DEFAULT_WEIGHTS rebalanced (16 → 16 active keys; aider:10pp redistributed across new keys)
- All 5 PRESETS rewritten — `swe-focused` adds `tbHard`+`cfElo`; `agentic-focused` adds `tbHard`+`browseComp`; `reasoning-focused` adds `arcAgi2`+`mmluPro`+`simpleQa`+`mrcr`; `benchmark-only` adds `tbHard`+`cfElo`+`mmluPro`
- Each preset still sums to 100

### Fixed
- `grok-4-3` entry — merge.py left envelope (`updates`/`sourcesAdded`) un-flattened from previous refresh; fields hoisted to top-level
- `audit-data-coherence.py` — cfElo cell-value range relaxed to 0-3500 (raw ELO)

### Migrated
- `data/models.json` — 54 models updated (rename + drop + 7 nullable adds per model)
- `data/sources.json` — 12 aider provenance entries dropped, 49 lcbV6 keys renamed to lcb
- `i18n/{tr,en}.json` — bench label sets aligned to new taxonomy
- `auto/eval.py` BENCH_KEYS list aligned


## [2026-04-29] — autonomous refresh-all [WARN: cumulative provenance coverage 52.0% below 85% target] [WARN: coverageMatrix invariant violated — 428 cell(s) silently missing (filled=332 + gaps=8 ≠ total=768)]

### Added
- `grok-4-3` — new model from vendor lineup discovery

### Updated
- 5 models: `claude-haiku-4-5`, `mimo-v2-5`, `gpt-5-5`, `grok-4-20`, `mimo-v2-5-pro`

### Resolved (auto via trustScore)
- grok-4-20.pricing.api.in: winner={'value': 3, 'trustScore': 0.7, 'sourceUrl': 'https://docs.x.ai/developers/models', 'tier': 'S'} (severity=GREEN, Δ1)

### Gaps (8 entries — see data/known-gaps.json or next refresh)
- `gemma-3-27b.sweV`: Google does not officially publish SWE-bench Verified for Gemma 3 27B; swebench.com leaderboard has no entry; no independent evaluation found
- `mimo-v2-5.sweV`: MiMo-V2.5 base model (not Pro) sweV not separately published; only V2.5-Pro has confirmed 78.9 sweV; base model data conflated; emitting single-source C-tier estimate
- `claude-haiku-4-5.gpqa`: AA-sourced 67.2 not independently confirmed by second I-tier source; Anthropic model card does not publish Haiku GPQA separately; single-source I-tier
- `grok-4-20.sweMulti`: No published SWE-bench Multilingual score for Grok 4.20 found on any leaderboard or xAI blog
- `grok-4-20.mcpA`: No MCP-Atlas score for Grok 4.20 found in any indexed source
- `qwen-3-6-max.swePro`: Qwen3.6-Max-Preview claims #1 on SWE-bench Pro but independent numeric score not confirmed; existing 58.4 is from prior cycle; Qwen blog does not publish exact number with methodology disclosure
- `grok-4-3.bench.*`: Grok 4.3 Beta is SuperGrok-gated, no benchmarks published as of 2026-04-29
- `gpt-5-5.lcbV6`: GPT-5.5 LCB v6 score not published by OpenAI or found on any leaderboard; OpenAI uses internal coding indices instead


## [2026-04-29] — autonomous refresh-all [WARN: cumulative provenance coverage 52.0% below 85% target] [WARN: artifact missing coverageMatrix; agent skipped self-audit]

### Updated
- 13 models: `gpt-5-5`, `sonnet-4-6`, `claude-haiku-4-5`, `glm-5-1`, `gemma-4-31b`, `gemma-4-26b-moe`, `gemma-4-e2b`, `gemma-4-e4b`, `qwen-3-6-27b`, `qwen-3-6-max`, `devstral-small-2`, `grok-4-20`, `llama-4-maverick`

### Deprecated
- `gpt-4-1` — vendor-marked deprecated
- `o3` — vendor-marked deprecated
- `o4-mini` — vendor-marked deprecated

### Resolved (auto via trustScore)
- grok-4-20.sweV: winner={'value': 58.6, 'trustScore': 0.67, 'sourceUrl': 'https://tokenmix.ai/blog/swe-bench-2026-claude-opus-4-7-wins', 'tier': 'I'} (severity=RED, Δ18.1)
- gpt-5-5.sweV: winner={'value': 88.7, 'trustScore': 0.89, 'sourceUrl': 'https://artificialanalysis.ai/articles/openai-gpt5-5-is-the-new-leading-AI-model', 'tier': 'I'} (severity=YELLOW, Δ3.7)

### Gaps (9 entries — see data/known-gaps.json or next refresh)
- `grok-4-3.bench.*`: Grok 4.3 Beta launched April 17 2026; no official benchmarks published at launch; SuperGrok Heavy ($300/mo) only; no API pricing disclosed
- `gpt-5-5.lcbV6`: No lcbV6 score found in GPT-5.5 benchmark coverage; not a benchmark OpenAI prioritises in release notes
- `qwen-3-6-max.swePro`: Qwen3.6 Plus swePro not yet published on SWE-bench Pro public leaderboard; Alibaba reports sweV 78.8 only
- `mimo-v2-5.sweV`: No sweV score found for MiMo-V2.5 base model; only Pro variant has swePro
- `claude-haiku-4-5.gpqa`: No GPQA Diamond score found in Anthropic Haiku 4.5 release materials; benchmark not featured in release notes
- `gemma-3-27b.sweV`: Gemma 3 27B sweV not found; significantly lower capability vs Gemma 4; prior benchmarks show 29.1% lcbV6
- `qwen3-coder-next.swePro`: qwen3-coder-next swePro shows 44.3% from arxiv technical report (Feb 2026); sweV shows 70%+ with SWE-Agent; single source only
- `deepseek-v4-flash.swePro`: V4 Flash swePro not published; only V4 Pro has swePro data (55.4%)
- ... and 1 more


## [2026-04-28] — autonomous refresh-all [WARN: cumulative provenance coverage 54.0% below 85% target]

### Updated
- 29 models: `gpt-5-5`, `opus-4-7`, `sonnet-4-6`, `claude-haiku-4-5`, `grok-4-20`, `kimi-k2-6`, `glm-5-1`, `deepseek-v4-pro`, `deepseek-v4-flash`, `mimo-v2-5-pro`, `mimo-v2-5`, `mimo-v2-flash`, `minimax-m2-7`, `qwen3-coder-30b`, `qwen3-coder-next`, `qwen-3-6-27b`, `qwen3-6-35b-moe`, `qwen3-6-plus`, `qwen3-235b`, `gemma-3-27b`, `gemma-4-26b-moe`, `gemma-4-31b`, `gemma-4-e2b`, `gemma-4-e4b`, `devstral-small-2`, `codestral`, `nemotron-3-super`, `step-3-5-flash`, `devstral-2`

### Deprecated
- `gpt-4-1` — vendor-marked deprecated
- `o3` — vendor-marked deprecated
- `o4-mini` — vendor-marked deprecated
- `codestral-22b` — vendor-marked deprecated
- `devstral-2` — vendor-marked deprecated

### Renamed
- devstral-medium -> devstral-small-2

### Resolved (auto via trustScore)
- grok-4-20.swePro: winner={'value': 51.8, 'trustScore': 0.82, 'sourceUrl': 'https://benchlm.ai/models/grok-4-20-beta', 'tier': 'I'} (severity=RED, Δ5.9)
- deepseek-v4-pro.swePro: winner={'value': 55.4, 'trustScore': 0.85, 'sourceUrl': 'https://benchlm.ai/benchmarks/swePro', 'tier': 'I'} (severity=YELLOW, Δ3.3)
- glm-5-1.hle: winner={'value': 52.3, 'trustScore': 0.55, 'sourceUrl': 'https://lushbinary.com/blog/glm-5-1-benchmarks-breakdown-swe-bench-pro-nl2repo-cybergym/', 'tier': 'C'} (severity=RED, Δ21.3)

### Gaps (17 entries — see data/known-gaps.json or next refresh)
- `grok-4-20.tb2`: No public Terminal-Bench 2 score published for Grok 4.20; xAI docs bot-blocked, WebSearch returned no score
- `grok-4-20.aime26`: xAI did not publish AIME 2026 score; WebSearch returned only AIME 2025 data
- `grok-3.swePro`: Grok 3 not on Scale SEAL public leaderboard; xAI docs bot-blocked
- `qwen3-6-max.sweV`: Qwen3.6 Max is proprietary API; no public SWE-bench Verified score found in whitelist sources
- `qwen3-6-plus.sweV`: Qwen3.6 Plus is proprietary API; no public SWE-bench Verified score found
- `codestral.bench.*`: Codestral 2508 has no published benchmark scores on Scale SEAL, BenchLM, or whitelist leaderboards; model is code-complete specialized, scores not submitted
- `mimo-v2-flash.bench.*`: MiMo-V2-Flash (older open-source MoE) has no published scores on current leaderboards
- `deepseek-r1-14b.bench.*`: Local distilled model; not benchmarked on frontier leaderboards like Scale SEAL or BenchLM for coding tasks
- ... and 9 more


## [2026-04-28] — autonomous refresh-all [WARN: partial coverage 48.0%]

### Resolved (auto via trustScore)
- sonnet-4-6.sweV: winner={'value': 79.6, 'trustScore': 0.87, 'sourceUrl': 'https://www.marc0.dev/en/leaderboard', 'tier': 'I'} (severity=GREEN, Δ2.4)
- opus-4-7.swePro: winner={'value': 64.3, 'trustScore': 0.93, 'sourceUrl': 'https://labs.scale.com/leaderboard/swe_bench_pro_public', 'tier': 'I'} (severity=YELLOW, Δ3.1)
- deepseek-v4-pro.sweV: winner={'value': 80.6, 'trustScore': 0.8, 'sourceUrl': 'https://artificialanalysis.ai/articles/deepseek-is-back-among-the-leading-open-weights-models-with-v4-pro-and-v4-flash', 'tier': 'I'} (severity=GREEN, Δ0)


## [2026-04-27] — autonomous refresh-all [WARN: partial coverage 48.0%]

### Updated
- 5 models: `gpt-5-5`, `glm-5-1`, `minimax-m2-5`, `qwen3-32b`, `qwen3-6-plus`

### Resolved (auto via trustScore)
- sonnet-4-6.sweV: winner={'value': 79.6, 'trustScore': 0.87, 'sourceUrl': 'https://www.marc0.dev/en/leaderboard', 'tier': 'I'} (severity=GREEN, Δ2.4)
- opus-4-7.swePro: winner={'value': 64.3, 'trustScore': 0.93, 'sourceUrl': 'https://labs.scale.com/leaderboard/swe_bench_pro_public', 'tier': 'I'} (severity=YELLOW, Δ3.1)
- deepseek-v4-pro.sweV: winner={'value': 80.6, 'trustScore': 0.8, 'sourceUrl': 'https://artificialanalysis.ai/articles/deepseek-is-back-among-the-leading-open-weights-models-with-v4-pro-and-v4-flash', 'tier': 'I'} (severity=GREEN, Δ0)


## [2026-04-27] — autonomous refresh-all [WARN: partial coverage 42.0%]

### Updated
- 14 models: `gpt-5-5`, `claude-haiku-4-5`, `grok-4-20`, `gpt-4-1`, `codestral-22b`, `codestral`, `deepseek-r1-14b`, `qwen25-coder-7b`, `qwen3-coder-480b`, `qwen3-6-35b-moe`, `minimax-m2-5`, `mimo-v2-flash`, `mimo-v2-pro`, `mimo-v2-5-pro`

### Gaps (10 entries — see data/known-gaps.json or next refresh)
- `None`: No public sweV score for Codestral-22B; tried 5 sources; deprecated coder focused on FIM not SWE-bench agent tasks
- `None`: LCB v6 for 14B specifically not extracted from technical report images; 7B and 32B extracted
- `None`: SWE-bench Verified not reported for Lite 16B; main paper reports full 236B model only
- `None`: MiMo-V2.5 (base) sweV not confirmed separately from Pro/Flash variants
- `None`: sweV for MiMo-V2.5-Pro not explicitly stated; V2-Pro has 78% but V2.5-Pro upgrade unclear
- `None`: GPQA for step-3-5-flash not in search snippets; arXiv table shows samples but exact % not extracted
- `None`: HLE for Mistral Large 3 not found in any source
- `None`: HLE for GPT-4.1 not available; model released Apr 2025, HLE benchmark newer
- ... and 2 more


## [2026-04-27] — autonomous refresh-all

### Updated
- 14 models: `qwen25-coder-14b`, `qwen25-coder-7b`, `deepseek-coder-v2-16b`, `devstral-2`, `devstral-medium`, `mimo-v2-5`, `qwen-3-6-max`, `qwen3-32b`, `gpt-4-1`, `o3`, `qwen3-6-plus`, `gemma-4-e2b`, `gemma-4-e4b`, `devstral-small-2`

### Resolved (auto via trustScore)
- devstral-medium.sweV: winner={'value': 68, 'trustScore': 0.9, 'sourceUrl': 'https://designforonline.com/ai-models/mistral-devstral-medium/', 'tier': 'I'} (severity=GREEN, Δ0)

### Gaps (11 entries — see data/known-gaps.json or next refresh)
- `None`: Only 2024-era LCB v1-v4 score 23.4 found; LCB v6 not published for 14B
- `None`: LCB v6 not published for 7B
- `None`: Codestral 22B 2024-era; no v6 evaluation found
- `None`: Codestral is code-focused; GPQA not reported
- `None`: MiMo-V2.5 base sweV not independently published; Pro variant 77.2 unconfirmed for base
- `None`: MiMo-V2.5 base not on LCB v6
- `None`: AIME 2026 score for Qwen3.6-Max-Preview not in aggregator sources
- `None`: No official GPQA Diamond for Gemma 4 E2B; only 31B/26B have GPQA
- ... and 3 more


## [2026-04-27] — autonomous refresh-all

### Updated
- 26 models: `gpt-5-5`, `claude-haiku-4-5`, `grok-4-20`, `sonnet-4-6`, `gemini-3-1-pro`, `gemini-3-1-flash`, `kimi-k2-6`, `glm-5-1`, `devstral-2`, `devstral-medium`, `mimo-v2-5-pro`, `minimax-m2-5`, `minimax-m2-7`, `nemotron-3-super`, `qwen-3-6-27b`, `qwen3-6-plus`, `qwen3-coder-30b`, `qwen3-coder-480b`, `qwen3-coder-next`, `qwen3-235b`, `step-3-5-flash`, `gemma-4-26b-moe`, `gemma-3-27b`, `deepseek-r1-14b`, `codestral`, `deepseek-coder-v2-16b`

### Resolved (auto via trustScore)
- kimi-k2-6.lcbV6: winner={'value': 89.6, 'trustScore': 0.65, 'sourceUrl': 'https://www.latent.space/p/ainews-moonshot-kimi-k26-the-worlds', 'tier': 'C'} (severity=RED, Δ35.9)
- gpt-5-5.swePro: winner={'value': 58.6, 'trustScore': 0.65, 'sourceUrl': 'https://mindwiredai.com/2026/04/24/gpt-5-5-is-here-benchmarks-pricing-and-who-should-actually-upgrade-april-2026/', 'tier': 'C'} (severity=GREEN, Δ0.9)
- gemma-4-26b-moe.gpqa: winner={'value': 82.3, 'trustScore': 0.62, 'sourceUrl': 'https://tokenmix.ai/blog/gemma-4-review-open-source-benchmarks-2026', 'tier': 'C'} (severity=YELLOW, Δ3.1)

### Gaps (13 entries — see data/known-gaps.json or next refresh)
- `None`: Gemini 3.1 Flash model card not found separately from Flash-Lite; sweep data not in available search snippets
- `None`: No TB2 score found for Gemini 3.1 Flash specifically
- `None`: Grok 3 sweV not in available 2026 search results
- `None`: Grok 3 Mini sweV not found
- `None`: MiMo-V2-Flash sweV numeric score not surfaced, only qualitative #1 claim
- `None`: MiMo-V2-Pro sweV score not in available search snippets
- `None`: SWE-bench V score for 16B Lite variant not in official paper; full 236B model score only
- `None`: GPQA not reported for DeepSeek-Coder-V2 in official paper (code-focused)
- ... and 5 more


## [2026-04-27] — autonomous refresh-all [WARN: partial coverage 38.0%]

### Added
- `grok-4-20` — new model from vendor lineup discovery

### Updated
- 39 models: `opus-4-7`, `sonnet-4-6`, `claude-haiku-4-5`, `gpt-5-5`, `gpt-4-1`, `gpt-5-4`, `o3`, `o4-mini`, `gemini-3-1-pro`, `gemini-3-1-flash`, `grok-3`, `grok-3-mini`, `deepseek-v4-pro`, `deepseek-v4-flash`, `deepseek-v3-2`, `glm-5-1`, `kimi-k2-6`, `llama-4-maverick`, `llama-4-scout`, `minimax-m2-5`, `minimax-m2-7`, `nemotron-3-super`, `devstral-2`, `devstral-small-2`, `codestral-22b`, `codestral`, `devstral-medium`, `qwen3-235b`, `qwen3-6-35b-moe`, `qwen-3-6-27b`, `qwen-3-6-max`, `qwen3-coder-480b`, `qwen3-coder-30b`, `qwen3-coder-next`, `mimo-v2-flash`, `mimo-v2-pro`, `mimo-v2-5`, `mimo-v2-5-pro`, `step-3-5-flash`

### Deprecated
- `codestral-22b` — vendor-marked deprecated
- `devstral-small-2` — vendor-marked deprecated
- `o4-mini` — vendor-marked deprecated
- `gpt-4-1` — vendor-marked deprecated

### Resolved (auto via trustScore)
- gpt-5-5.swePro: winner={'value': 58.6, 'trustScore': 0.6, 'sourceUrl': 'https://mindwiredai.com/2026/04/24/gpt-5-5-is-here-benchmarks-pricing-and-who-should-actually-upgrade-april-2026/', 'tier': 'C'} (severity=GREEN, Δ0)

### Gaps (15 entries — see data/known-gaps.json or next refresh)
- `None`: No SWE-bench Verified data found for Gemini 3.1 Flash-Lite specifically
- `None`: No independent SWE-bench Verified score found; only SWE-bench Pro reported
- `None`: o3 deprecated from ChatGPT Feb 2026; no new bench data
- `None`: o4-mini deprecated from ChatGPT Feb 2026; no new bench data
- `None`: SWE-bench Verified not yet published for Grok 4.20; only community leak estimates
- `None`: Qwen3-Coder-Next benchmark data not yet publicly available
- `None`: MiMo-V2.5 (standard) bench data sparse; V2.5-Pro has data but base model unclear
- `None`: Legacy model; no 2026 bench refresh found
- ... and 7 more


## [2026-04-26] — autonomous refresh-all

### Updated
- 46 models: `opus-4-7`, `sonnet-4-6`, `claude-haiku-4-5`, `gpt-5-5`, `gpt-5-4`, `gemini-3-1-pro`, `deepseek-v4-pro`, `deepseek-v4-flash`, `deepseek-v3-2`, `kimi-k2-6`, `glm-5-1`, `minimax-m2-7`, `minimax-m2-5`, `mimo-v2-5-pro`, `mimo-v2-5`, `mimo-v2-pro`, `mimo-v2-flash`, `qwen3-235b`, `qwen3-coder-480b`, `qwen3-coder-30b`, `qwen3-coder-next`, `qwen-3-6-27b`, `qwen3-6-35b-moe`, `qwen3-6-plus`, `qwen-3-6-max`, `qwen3-32b`, `gemma-4-31b`, `gemma-4-26b-moe`, `gemma-4-e2b`, `gemma-4-e4b`, `gemma-3-27b`, `llama-4-maverick`, `llama-4-scout`, `nemotron-3-super`, `step-3-5-flash`, `mistral-large-3`, `devstral-medium`, `grok-3`, `grok-3-mini`, `o3`, `o4-mini`, `gpt-4-1`, `gemini-3-1-flash`, `codestral-22b`, `qwen25-coder-7b`, `qwen25-coder-32b`

### Resolved (auto via trustScore)
- kimi-k2-6.pricing.api.in: winner={'value': 0.57, 'trustScore': 0.85, 'sourceUrl': 'https://platform.kimi.com/docs', 'tier': 'S'} (severity=WARN, Δ0.38)
- llama-4-maverick.pricing.api.in: winner={'value': 0.2, 'trustScore': 0.82, 'sourceUrl': 'https://www.vellum.ai/llm-leaderboard', 'tier': 'I'} (severity=WARN, Δ0.1)
- llama-4-scout.pricing.api.in: winner={'value': 0.11, 'trustScore': 0.82, 'sourceUrl': 'https://www.vellum.ai/open-llm-leaderboard', 'tier': 'I'} (severity=WARN, Δ0.08)
- gemini-3-1-pro.bench.sweV: winner={'value': 80.6, 'trustScore': 0.85, 'sourceUrl': 'https://www.swebench.com/', 'tier': 'I'} (severity=WARN, Δ1.8)
- qwen3-coder-480b.bench.sweV: winner={'value': 69.6, 'trustScore': 0.65, 'sourceUrl': 'https://llm-stats.com/benchmarks/swe-bench-verified', 'tier': 'I'} (severity=WARN, Δ3.1)

### Gaps (21 entries — see data/known-gaps.json or next refresh)
- `None`: No SWE-bench Verified submission for Qwen3-32B dense standalone (Qwen3-Max 235B = 69.6%)
- `None`: Qwen3.6-Max-Preview API-hosted proprietary; too recent for independent eval (released 2026-04-20)
- `None`: SWE-bench Pro submission not found
- `None`: MiMo-V2.5 standard SWE-bench Verified score not published; V2.5-Pro available
- `None`: Not on Scale SEAL or BenchLM; vendor opt-out for Flash variant
- `None`: xAI vendor opt-out pattern; no submission to SWE-bench
- `None`: xAI vendor opt-out pattern
- `None`: Legacy 2024 model; not on current leaderboards
- ... and 13 more


## [2026-04-26] — autonomous refresh-all

### Updated
- 1 models: `gpt-5-4`

### Resolved (auto via trustScore)
- opus-4-7.swePro: winner=64.3 (severity=YELLOW, Δ3.1)

### Gaps (9 entries — see data/known-gaps.json or next refresh)
- `aaCoding.most`: AA Coding Index sub-page SPA-only across all whitelist sources after 3 cycles + 6 alternate URLs; will retry next cycle via WebSearch primary protocol now in agent.md
- `aaAgentic.all`: AA Agentic Index sub-page SPA-only; only GDPval-AA Elo found (which is a different metric, not a 0-100 index)
- `bfcl.most`: BFCL leaderboard SPA; awesomeagents aggregator only carries Qwen3-235B (74.9%); no GitHub raw mirror found
- `aime26.opus-4-7`: Anthropic did not publish AIME 2026 score for Opus 4.7
- `aime26.sonnet-4-6`: Anthropic Sonnet 4.6 announcement no AIME 2026
- `aime26.gpt-5-5`: GPT-5.5 launch did not publish AIME 2026
- `grok-3.swePro`: xAI vendor opt-out from SWE-bench (data confirmed via WebSearch — no Grok 3 SWE-bench score)
- `o3.swePro`: OpenAI does not publish o3 swePro
- ... and 1 more


## [2026-04-26] — autonomous refresh-all

### Added
- `gpt-5-5` — new model from vendor lineup discovery

### Updated
- 17 models: `gpt-5-4`, `devstral-medium`, `devstral-2`, `devstral-small-2`, `kimi-k2-6`, `minimax-m2-7`, `mimo-v2-5-pro`, `deepseek-v4-pro`, `deepseek-v4-flash`, `qwen3-6-35b-moe`, `qwen3-coder-480b`, `gemma-4-31b`, `gemma-4-26b-moe`, `opus-4-7`, `gemini-3-1-pro`, `glm-5-1`, `qwen3-235b`

### Deprecated
- `devstral-small-2` — vendor-marked deprecated

### Renamed
- devstral-medium -> devstral-2-123b

### Resolved (auto via trustScore)
- kimi-k2-6.bench.swePro: winner=58.6 (severity=RED, Δ30.93)
- kimi-k2-6.bench.sweV: winner=80.2 (severity=RED, Δ14.4)
- devstral-medium.bench.sweV: winner=72.2 (severity=RED, Δ10.6)
- minimax-m2-7.bench.sweV: winner=78 (severity=RED, Δ21.8)
- opus-4-7.bench.sweV: winner=87.6 (severity=RED, Δ5.6)

### Gaps (19 entries — see data/known-gaps.json or next refresh)
- `aaCoding.*`: AA coding leaderboard JS-SPA
- `aaAgentic.*`: AA agentic JS-SPA
- `bfcl.*`: BFCL Berkeley page not parseable
- `aaOmni.*`: AA omni leaderboard not fetched
- `mimo-v2-5.bench`: MiMo V2.5 standard bench not publicly published
- `qwen3-coder-next.sweV`: prior 58.7 unverified — needs triangulation
- `step-3-5-flash.swePro`: no swePro found
- `o3.swePro`: OpenAI does not publish o3 swePro
- ... and 11 more


## [2026-04-26] — autonomous refresh-all

### Updated
- 1 models: `grok-3`

### Gaps (3 entries — see data/known-gaps.json or next refresh)
- `grok-3.sweV`: S-tier value 63.8 found but custom-scaffold; needs I-tier corroboration; recheckAfter 2026-10-01
- `llama-4-maverick.sweV`: Confirmed permanent vendor-opt-out — Meta does not submit
- `mimo-v2-5.swePro`: Confirmed — only V2.5-Pro variant has SWE-Pro 57.2; base V2.5 has no public bench


## [2026-04-26] — autonomous refresh-all

### Updated
- 5 models: `gpt-5-4`, `gemini-3-1-pro`, `kimi-k2-6`, `minimax-m2-7`, `qwen3-coder-480b`

### Resolved (auto via trustScore)
- kimi-k2-6.lcbV6: winner=53.7 (severity=RED, Δ35.9)
- kimi-k2-6.sweV: winner=65.8 (severity=RED, Δ14.4)
- kimi-k2-6.tb2: winner=27.8 (severity=RED, Δ38.9)
- minimax-m2-7.swePro: winner=36.81 (severity=RED, Δ19.39)
- gemini-3-1-pro.hle: winner=51.4 (severity=RED, Δ7.0)
- gpt-5-4.swePro: winner=59.1 (severity=GREEN, Δ1.4)

### Gaps (8 entries — see data/known-gaps.json or next refresh)
- `claude-haiku-4-5.gpqa`: Anthropic page lacks GPQA in text (likely PNG); needs system card or image OCR
- `claude-haiku-4-5.tb2`: Same — bench in image
- `claude-haiku-4-5.tau2`: Same
- `claude-haiku-4-5.lcbV6`: Same
- `claude-haiku-4-5.hle`: Same
- `openai_403_block`: openai.com/index/* returned 403 — agent could not fetch o3/o4-mini/gpt-4-1/gpt-5-4 official pages this cycle
- `lcbV6_general`: LiveCodeBench leaderboard JS-rendered; many models without lcbV6 — needs GitHub releases JSON or alternate source
- `permanent_swePro_gaps`: Models not submitted to Scale SEAL public leaderboard — should move to known-gaps.json as vendor-opt-out


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
