
## [2026-05-10] — autonomous refresh-all [WARN: very low cumulative provenance coverage 32.5%] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 346 new fills; 832 cells auto-gapped by orchestrator; 97 explicit agent gaps preserved]

[fillRatio:0.33 cells:507/1560 contradictions:1 fetch:0.0min tools:None batches:None build:101c05d]

### Updated
- 60 models: `opus-4-7`, `sonnet-4-6`, `claude-haiku-4-5`, `deepseek-v3-2`, `deepseek-v4-flash`, `deepseek-v4-pro`, `deepseek-coder-v2-16b`, `deepseek-r1-14b`, `gemini-3-1-flash`, `gemini-3-1-pro`, `gemma-3-27b`, `gemma-4-26b-moe`, `gemma-4-31b`, `gemma-4-e2b`, `gemma-4-e4b`, `llama-4-maverick`, `llama-4-scout`, `minimax-m2-5`, `minimax-m2-7`, `minimax-m2-1`, `mistral-large-3`, `codestral-22b`, `devstral-2`, `devstral-medium`, `codestral`, `devstral-small-2`, `mistral-medium-3-5`, `kimi-k2-6`, `nemotron-3-super`, `gpt-5-5`, `gpt-5-4`, `gpt-4-1`, `o3`, `o4-mini`, `qwen-3-6-27b`, `qwen3-235b`, `qwen3-32b`, `qwen3-6-35b-moe`, `qwen-3-6-max`, `qwen3-6-plus`, `qwen3-coder-30b`, `qwen3-coder-480b`, `qwen3-coder-next`, `qwen25-coder-14b`, `qwen25-coder-32b`, `qwen25-coder-7b`, `qwen3-5-9b`, `step-3-5-flash`, `grok-4-3`, `grok-4-20`, `grok-3`, `grok-3-mini`, `grok-4-1-fast`, `mimo-v2-5-pro`, `mimo-v2-5`, `mimo-v2-flash`, `mimo-v2-pro`, `glm-5-1`, `glm-4-5-air`, `glm-4-7`

### Resolved (auto via trustScore)
- qwen-3-6-max.lcb: winner={'value': 77.5, 'trustScore': 0.667, 'sourceUrl': 'https://llm-stats.com/', 'tier': 'I'} (severity=RED, Δ5.4)

### Gaps (911 entries — agent:79 orchestrator:832 — see data/known-gaps.json or next refresh)
- `gemini-3-1-flash.tb2` *(agent)*: agent attempted but found no value
- `gemini-3-1-flash.aaCoding` *(agent)*: agent attempted but found no value
- `gemini-3-1-flash.aaAgentic` *(agent)*: agent attempted but found no value
- `gemini-3-1-pro.tbHard` *(agent)*: agent attempted but found no value
- `gemini-3-1-pro.aaCoding` *(agent)*: agent attempted but found no value
- `gemini-3-1-pro.aaAgentic` *(agent)*: agent attempted but found no value
- `claude-haiku-4-5.aaAgentic` *(orchestrator)*: not reached in agent survey cycle; AA Agentic data unavailable
- `claude-haiku-4-5.aaCoding` *(orchestrator)*: not reached in agent survey cycle; AA Coding data unavailable
- ... and 903 more


## [2026-05-09] — autonomous refresh-all [WARN: very low cumulative provenance coverage 30.4%] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 141 new fills; 940 cells auto-gapped by orchestrator; 11 explicit agent gaps preserved]

[fillRatio:0.30 cells:473/1560 contradictions:2 fetch:0.0min tools:None batches:None build:4b8098c]

### Updated
- 12 models: `gemini-3-1-flash`, `gemini-3-1-pro`, `gemma-3-27b`, `gemma-4-31b`, `llama-4-maverick`, `llama-4-scout`, `kimi-k2-6`, `glm-4-5-air`, `glm-4-7`, `qwen25-coder-32b`, `qwen25-coder-7b`, `qwen3-5-9b`

### Resolved (auto via trustScore)
- llama-4-maverick.gpqa: winner={'value': 69.8, 'trustScore': 0.6, 'sourceUrl': None, 'tier': 'S'} (severity=RED, Δ15.0)
- gemma-4-26b-moe.gpqa: winner={'value': 82.3, 'trustScore': 0.7, 'sourceUrl': 'https://blog.google', 'tier': 'S'} (severity=YELLOW, Δ3.1)

### Gaps (947 entries — agent:7 orchestrator:940 — see data/known-gaps.json or next refresh)
- `opus-4-7.lcb` *(agent)*: Not found in whitelist leaderboards for opus-4-7
- `opus-4-7.bfcl` *(agent)*: Not found in whitelist leaderboards
- `llama-4-scout.swePro` *(agent)*: Not on SWE-bench Pro leaderboard for open-weight scout model
- `devstral-small-2.swePro` *(agent)*: Deprecated model; not benchmarked post-deprecation
- `mistral-medium-3-5.swePro` *(agent)*: Fresh launch (2026-04-29); not yet on leaderboards
- `qwen25-coder-7b.sweV` *(agent)*: Released 2026-05-02; not yet on leaderboard snapshots
- `claude-haiku-4-5.aaAgentic` *(orchestrator)*: not reached in agent survey cycle; AA Agentic data unavailable
- `claude-haiku-4-5.aaCoding` *(orchestrator)*: not reached in agent survey cycle; AA Coding data unavailable
- ... and 939 more


## [2026-05-09] — autonomous refresh-all [WARN: very low cumulative provenance coverage 30.4%] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 141 new fills; 940 cells auto-gapped by orchestrator; 11 explicit agent gaps preserved]

[fillRatio:0.30 cells:473/1560 contradictions:2 fetch:0.0min tools:None batches:None build:4b8098c]

### Updated
- 12 models: `gemini-3-1-flash`, `gemini-3-1-pro`, `gemma-3-27b`, `gemma-4-31b`, `llama-4-maverick`, `llama-4-scout`, `kimi-k2-6`, `glm-4-5-air`, `glm-4-7`, `qwen25-coder-32b`, `qwen25-coder-7b`, `qwen3-5-9b`

### Resolved (auto via trustScore)
- llama-4-maverick.gpqa: winner={'value': 69.8, 'trustScore': 0.6, 'sourceUrl': None, 'tier': 'S'} (severity=RED, Δ15.0)
- gemma-4-26b-moe.gpqa: winner={'value': 82.3, 'trustScore': 0.7, 'sourceUrl': 'https://blog.google', 'tier': 'S'} (severity=YELLOW, Δ3.1)

### Gaps (947 entries — agent:7 orchestrator:940 — see data/known-gaps.json or next refresh)
- `opus-4-7.lcb` *(agent)*: Not found in whitelist leaderboards for opus-4-7
- `opus-4-7.bfcl` *(agent)*: Not found in whitelist leaderboards
- `llama-4-scout.swePro` *(agent)*: Not on SWE-bench Pro leaderboard for open-weight scout model
- `devstral-small-2.swePro` *(agent)*: Deprecated model; not benchmarked post-deprecation
- `mistral-medium-3-5.swePro` *(agent)*: Fresh launch (2026-04-29); not yet on leaderboards
- `qwen25-coder-7b.sweV` *(agent)*: Released 2026-05-02; not yet on leaderboard snapshots
- `claude-haiku-4-5.aaAgentic` *(orchestrator)*: not reached in agent survey cycle; AA Agentic data unavailable
- `claude-haiku-4-5.aaCoding` *(orchestrator)*: not reached in agent survey cycle; AA Coding data unavailable
- ... and 939 more


## [2026-05-09] — autonomous refresh-all [WARN: very low cumulative provenance coverage 29.4%] [MX2: coverage 29.4% < absolute floor 30%] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 423 new fills; 534 cells auto-gapped by orchestrator; 444 explicit agent gaps preserved]

[fillRatio:0.29 cells:458/1560 contradictions:29 fetch:0.0min tools:None batches:None build:868107d]

### Updated
- 55 models: `opus-4-7`, `claude-haiku-4-5`, `deepseek-v3-2`, `deepseek-v4-flash`, `deepseek-v4-pro`, `deepseek-coder-v2-16b`, `deepseek-r1-14b`, `gemini-3-1-flash`, `gemini-3-1-pro`, `gemma-3-27b`, `gemma-4-26b-moe`, `gemma-4-31b`, `gemma-4-e2b`, `gemma-4-e4b`, `llama-4-maverick`, `llama-4-scout`, `minimax-m2-1`, `minimax-m2-5`, `minimax-m2-7`, `mistral-large-3`, `codestral-22b`, `devstral-2`, `devstral-medium`, `codestral`, `devstral-small-2`, `mistral-medium-3-5`, `kimi-k2-6`, `nemotron-3-super`, `gpt-4-1`, `gpt-5-4`, `o3`, `o4-mini`, `gpt-5-5`, `qwen-3-6-27b`, `qwen-3-6-max`, `qwen3-235b`, `qwen3-32b`, `qwen3-6-35b-moe`, `qwen3-6-plus`, `qwen3-coder-480b`, `qwen3-coder-next`, `qwen25-coder-32b`, `qwen25-coder-7b`, `qwen3-5-9b`, `step-3-5-flash`, `grok-3`, `grok-4-20`, `grok-4-3`, `grok-4-1-fast`, `mimo-v2-5`, `mimo-v2-5-pro`, `mimo-v2-flash`, `glm-5-1`, `glm-4-7`, `glm-4-5-air`

### Resolved (auto via trustScore)
- deepseek-v3-2.sweV: winner={'value': 73, 'trustScore': 0.78, 'sourceUrl': 'https://benchlm.ai/models/deepseek-v3-2', 'tier': 'I'} (severity=YELLOW, Δ3.0)
- deepseek-coder-v2-16b.lcb: winner={'value': 24.3, 'trustScore': 0.63, 'sourceUrl': 'https://arxiv.org/html/2406.11931v1', 'tier': 'S'} (severity=RED, Δ19.1)
- gemini-3-1-flash.lcb: winner={'value': 72, 'trustScore': 0.67, 'sourceUrl': 'https://benchlm.ai/coding', 'tier': 'I'} (severity=RED, Δ19.7)
- gemma-4-26b-moe.gpqa: winner={'value': 82.3, 'trustScore': 0.62, 'sourceUrl': 'https://tech-insider.org/google-gemma-4-open-model-benchmarks-2026/', 'tier': 'C'} (severity=YELLOW, Δ3.1)
- gemma-4-e2b.aime26: winner={'value': 37.5, 'trustScore': 0.4, 'sourceUrl': 'https://aurigait.com/blog/gemma-4-features-benchmarks-guide/', 'tier': 'C'} (severity=RED, Δ5.0)
- gemma-4-e2b.ollamaSize: winner={'value': '7.2GB', 'trustScore': 0.67, 'sourceUrl': 'https://ollama.com/library/gemma4/tags', 'tier': 'I'} (severity=RED, ΔNone)
- gemma-4-e4b.ollamaSize: winner={'value': '9.6GB', 'trustScore': 0.67, 'sourceUrl': 'https://ollama.com/library/gemma4/tags', 'tier': 'I'} (severity=RED, ΔNone)
- llama-4-maverick.bench.gpqa: winner={'value': 69.8, 'trustScore': 0.62, 'sourceUrl': 'https://www.llama.com/models/llama-4/', 'tier': 'S'} (severity=RED, Δ17.8)
- llama-4-maverick.bench.sweV: winner={'value': None, 'trustScore': 0.55, 'sourceUrl': 'https://llm-stats.com/benchmarks/swe-bench-verified', 'tier': 'I'} (severity=RED, Δ76.8)
- llama-4-scout.bench.sweV: winner={'value': None, 'trustScore': 0.55, 'sourceUrl': 'https://llm-stats.com/benchmarks/swe-bench-verified', 'tier': 'I'} (severity=RED, Δ68)
- minimax-m2-5.aime26: winner={'value': 86.3, 'trustScore': 0.27, 'sourceUrl': 'https://onyx.app/insights/best-llms-2026', 'tier': 'C'} (severity=RED, Δ41.3)
- devstral-2.status: winner={'value': 'active', 'trustScore': 0.47, 'sourceUrl': 'https://openrouter.ai/mistralai/devstral-2512', 'tier': 'S'} (severity=GREEN, Δ0)
- devstral-medium.context: winner={'value': 131072, 'trustScore': 0.47, 'sourceUrl': 'https://openrouter.ai/mistralai/devstral-medium', 'tier': 'S'} (severity=RED, Δ131072)
- devstral-medium.sweV: winner={'value': 61.6, 'trustScore': 0.47, 'sourceUrl': 'https://mistral.ai/news/devstral-2507', 'tier': 'S'} (severity=YELLOW, Δ6.4)
- kimi-k2-6.pricing.api.in: winner={'value': 0.75, 'trustScore': 0.9, 'sourceUrl': 'https://openrouter.ai/moonshotai/kimi-k2.6', 'tier': 'I'} (severity=GREEN, Δ0.0052)
- nemotron-3-super.lcb: winner={'value': 78.7, 'trustScore': 0.55, 'sourceUrl': 'https://arxiv.org/html/2603.19220', 'tier': 'S'} (severity=GREEN, Δ2.5)
- nemotron-3-super.aime26: winner={'value': 89.8, 'trustScore': 0.55, 'sourceUrl': 'https://arxiv.org/html/2603.19220', 'tier': 'S'} (severity=GREEN, Δ0.41)
- nemotron-3-super.pricing.api.in: winner={'value': 0.1, 'trustScore': 0.83, 'sourceUrl': 'https://deepinfra.com/blog/nvidia-nemotron-api-pricing-guide-2026', 'tier': 'S'} (severity=GREEN, Δ0.1)
- gpt-5-5.sweV: winner={'value': 82.6, 'trustScore': 0.85, 'sourceUrl': 'https://www.vals.ai/benchmarks/swebench', 'tier': 'I'} (severity=RED, Δ6.1)
- gpt-5-4.context: winner={'value': 1048576, 'trustScore': 0.87, 'sourceUrl': 'https://openrouter.ai/openai/gpt-5.4', 'tier': 'I'} (severity=RED, Δ776576)
- gpt-5-4.pricing.api.in: winner={'value': 2.5, 'trustScore': 0.87, 'sourceUrl': 'https://openrouter.ai/openai/gpt-5.4', 'tier': 'I'} (severity=YELLOW, Δ1.25)
- qwen-3-6-max.pricing.api.in: winner={'value': 1.04, 'trustScore': 0.67, 'sourceUrl': 'https://openrouter.ai/qwen/qwen3.6-max-preview', 'tier': 'I'} (severity=GREEN, Δ0.78)
- qwen3-6-35b-moe.mcpA: winner={'value': 37.0, 'trustScore': 0.47, 'sourceUrl': 'https://qwen.ai/blog?id=qwen3.6-35b-a3b', 'tier': 'S'} (severity=RED, Δ25.8)
- qwen3-coder-30b.sweV: winner={'value': 51.6, 'trustScore': 0.93, 'sourceUrl': 'https://artificialanalysis.ai/models/qwen3-coder-30b-a3b-instruct', 'tier': 'I'} (severity=RED, Δ18.0)
- step-3-5-flash.gpqa: winner={'value': 83.5, 'trustScore': 0.75, 'sourceUrl': 'https://huggingface.co/stepfun-ai/Step-3.5-Flash', 'tier': 'S'} (severity=GREEN, Δ0.9)
- grok-4-20.pricing.api.in: winner={'value': 2.0, 'trustScore': 0.7, 'sourceUrl': 'https://docs.x.ai/developers/models', 'tier': 'S'} (severity=GREEN, Δ0.75)
- mimo-v2-flash.hle: winner={'value': 22.1, 'trustScore': 0.62, 'sourceUrl': 'https://arxiv.org/html/2601.02780v2', 'tier': 'S'} (severity=RED, Δ14.1)
- mimo-v2-5-pro.hle: winner={'value': 48, 'trustScore': 0.44, 'sourceUrl': 'https://mimo.xiaomi.com/mimo-v2-5-pro/', 'tier': 'S'} (severity=RED, Δ14.2)
- glm-4-7.pricing.api.in: winner={'value': 0.38, 'trustScore': 0.85, 'sourceUrl': 'https://openrouter.ai/z-ai/glm-4.7', 'tier': 'I'} (severity=GREEN, Δ0.22)

### Gaps (966 entries — agent:432 orchestrator:534 — see data/known-gaps.json or next refresh)
- `opus-4-7.lcb` *(agent)*: No LiveCodeBench pass@1 score found for Claude Opus 4.7; not in April 2026 release materials
- `opus-4-7.tbHard` *(agent)*: Terminal-Bench Hard sub-score not separately published for Opus 4.7; only TB2 aggregate reported
- `opus-4-7.cfElo` *(agent)*: Codeforces ELO not reported for Claude Opus 4.7; LCB Pro SPA format blocks direct fetch
- `opus-4-7.aime26` *(agent)*: AIME 2026 score not publicly reported for Claude Opus 4.7; Anthropic launch focused on coding/agentic benches
- `opus-4-7.bfcl` *(agent)*: BFCL score not found for Claude Opus 4.7; BFCL site is SPA with no static data
- `opus-4-7.simpleQa` *(agent)*: SimpleQA score not found for Claude Opus 4.7 in any source
- `codestral.aaAgentic` *(orchestrator)*: not reached in agent survey cycle; AA Agentic data unavailable
- `codestral.aaCoding` *(orchestrator)*: not reached in agent survey cycle; AA Coding data unavailable
- ... and 958 more


## [2026-05-08] — autonomous refresh-all [WARN: very low cumulative provenance coverage 27.3%] [MX2: coverage 27.3% < absolute floor 30%] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 51 new fills; 969 cells auto-gapped by orchestrator; 81 explicit agent gaps preserved]

[fillRatio:0.27 cells:426/1560 contradictions:8 fetch:0.0min tools:None batches:None build:868107d]

### Resolved (auto via trustScore)
- gpt-5-5.hle: winner={'value': 41.4, 'trustScore': 0.7, 'sourceUrl': 'https://openai.com/index/introducing-gpt-5-5/', 'tier': 'S'} (severity=RED, Δ10.8)
- sonnet-4-6.tau2: winner={'value': 87.5, 'trustScore': 0.67, 'sourceUrl': 'https://benchlm.ai/models/sonnet-4-6', 'tier': 'I'} (severity=RED, Δ7.3)
- deepseek-v3-2.sweV: winner={'value': 67.8, 'trustScore': 0.7, 'sourceUrl': 'https://github.com/deepseek-ai/DeepSeek-V3.2-Exp', 'tier': 'S'} (severity=GREEN, Δ2.2)
- deepseek-v3-2.lcb: winner={'value': 74.1, 'trustScore': 0.7, 'sourceUrl': 'https://github.com/deepseek-ai/DeepSeek-V3.2-Exp', 'tier': 'S'} (severity=RED, Δ9.2)
- deepseek-v3-2.gpqa: winner={'value': 79.9, 'trustScore': 0.7, 'sourceUrl': 'https://github.com/deepseek-ai/DeepSeek-V3.2-Exp', 'tier': 'S'} (severity=GREEN, Δ2.5)
- deepseek-v3-2.hle: winner={'value': 19.8, 'trustScore': 0.7, 'sourceUrl': 'https://github.com/deepseek-ai/DeepSeek-V3.2-Exp', 'tier': 'S'} (severity=RED, Δ21.0)
- kimi-k2-6.tb2: winner={'value': 66.7, 'trustScore': 0.7, 'sourceUrl': 'https://platform.moonshot.cn/docs', 'tier': 'S'} (severity=RED, Δ13.5)
- minimax-m2-5.swePro: winner={'value': 55.4, 'trustScore': 0.7, 'sourceUrl': 'https://platform.minimaxi.com/document', 'tier': 'S'} (severity=RED, Δ18.59)

### Gaps (1021 entries — agent:52 orchestrator:969 — see data/known-gaps.json or next refresh)
- `gpt-5-5.nl2Repo` *(agent)*: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `opus-4-7.nl2Repo` *(agent)*: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `sonnet-4-6.nl2Repo` *(agent)*: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `claude-haiku-4-5.nl2Repo` *(agent)*: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `grok-4-20.nl2Repo` *(agent)*: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `grok-4-3.nl2Repo` *(agent)*: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `claude-haiku-4-5.aaAgentic` *(orchestrator)*: not reached in agent survey cycle; AA Agentic data unavailable
- `claude-haiku-4-5.aaCoding` *(orchestrator)*: not reached in agent survey cycle; AA Coding data unavailable
- ... and 1013 more


## [2026-05-08] — autonomous refresh-all [WARN: very low cumulative provenance coverage 27.3%] [MX2: coverage 27.3% < absolute floor 30%] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 51 new fills; 969 cells auto-gapped by orchestrator; 81 explicit agent gaps preserved]

[fillRatio:0.27 cells:426/1560 contradictions:8 fetch:0.0min tools:None batches:None build:c512eaa]

### Resolved (auto via trustScore)
- gpt-5-5.hle: winner={'value': 41.4, 'trustScore': 0.7, 'sourceUrl': 'https://openai.com/index/introducing-gpt-5-5/', 'tier': 'S'} (severity=RED, Δ10.8)
- sonnet-4-6.tau2: winner={'value': 87.5, 'trustScore': 0.67, 'sourceUrl': 'https://benchlm.ai/models/sonnet-4-6', 'tier': 'I'} (severity=RED, Δ7.3)
- deepseek-v3-2.sweV: winner={'value': 67.8, 'trustScore': 0.7, 'sourceUrl': 'https://github.com/deepseek-ai/DeepSeek-V3.2-Exp', 'tier': 'S'} (severity=GREEN, Δ2.2)
- deepseek-v3-2.lcb: winner={'value': 74.1, 'trustScore': 0.7, 'sourceUrl': 'https://github.com/deepseek-ai/DeepSeek-V3.2-Exp', 'tier': 'S'} (severity=RED, Δ9.2)
- deepseek-v3-2.gpqa: winner={'value': 79.9, 'trustScore': 0.7, 'sourceUrl': 'https://github.com/deepseek-ai/DeepSeek-V3.2-Exp', 'tier': 'S'} (severity=GREEN, Δ2.5)
- deepseek-v3-2.hle: winner={'value': 19.8, 'trustScore': 0.7, 'sourceUrl': 'https://github.com/deepseek-ai/DeepSeek-V3.2-Exp', 'tier': 'S'} (severity=RED, Δ21.0)
- kimi-k2-6.tb2: winner={'value': 66.7, 'trustScore': 0.7, 'sourceUrl': 'https://platform.moonshot.cn/docs', 'tier': 'S'} (severity=RED, Δ13.5)
- minimax-m2-5.swePro: winner={'value': 55.4, 'trustScore': 0.7, 'sourceUrl': 'https://platform.minimaxi.com/document', 'tier': 'S'} (severity=RED, Δ18.59)

### Gaps (1021 entries — see data/known-gaps.json or next refresh)
- `gpt-5-5.nl2Repo`: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `opus-4-7.nl2Repo`: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `sonnet-4-6.nl2Repo`: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `claude-haiku-4-5.nl2Repo`: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `grok-4-20.nl2Repo`: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `grok-4-3.nl2Repo`: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `grok-4-1-fast.nl2Repo`: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `deepseek-v4-pro.nl2Repo`: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- ... and 1013 more


## [2026-05-07] — autonomous refresh-all [WARN: very low cumulative provenance coverage 27.3%] [MX2: coverage 27.3% < absolute floor 30%] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 51 new fills; 969 cells auto-gapped by orchestrator; 81 explicit agent gaps preserved]

[fillRatio:0.27 cells:426/1560 contradictions:8 fetch:0.0min tools:None batches:None build:951a10b]

### Updated
- 3 models: `deepseek-v3-2`, `qwen3-32b`, `minimax-m2-5`

### Resolved (auto via trustScore)
- gpt-5-5.hle: winner={'value': 41.4, 'trustScore': 0.7, 'sourceUrl': 'https://openai.com/index/introducing-gpt-5-5/', 'tier': 'S'} (severity=RED, Δ10.8)
- sonnet-4-6.tau2: winner={'value': 87.5, 'trustScore': 0.67, 'sourceUrl': 'https://benchlm.ai/models/sonnet-4-6', 'tier': 'I'} (severity=RED, Δ7.3)
- deepseek-v3-2.sweV: winner={'value': 67.8, 'trustScore': 0.7, 'sourceUrl': 'https://github.com/deepseek-ai/DeepSeek-V3.2-Exp', 'tier': 'S'} (severity=GREEN, Δ2.2)
- deepseek-v3-2.lcb: winner={'value': 74.1, 'trustScore': 0.7, 'sourceUrl': 'https://github.com/deepseek-ai/DeepSeek-V3.2-Exp', 'tier': 'S'} (severity=RED, Δ9.2)
- deepseek-v3-2.gpqa: winner={'value': 79.9, 'trustScore': 0.7, 'sourceUrl': 'https://github.com/deepseek-ai/DeepSeek-V3.2-Exp', 'tier': 'S'} (severity=GREEN, Δ2.5)
- deepseek-v3-2.hle: winner={'value': 19.8, 'trustScore': 0.7, 'sourceUrl': 'https://github.com/deepseek-ai/DeepSeek-V3.2-Exp', 'tier': 'S'} (severity=RED, Δ21.0)
- kimi-k2-6.tb2: winner={'value': 66.7, 'trustScore': 0.7, 'sourceUrl': 'https://platform.moonshot.cn/docs', 'tier': 'S'} (severity=RED, Δ13.5)
- minimax-m2-5.swePro: winner={'value': 55.4, 'trustScore': 0.7, 'sourceUrl': 'https://platform.minimaxi.com/document', 'tier': 'S'} (severity=RED, Δ18.59)

### Gaps (1021 entries — see data/known-gaps.json or next refresh)
- `gpt-5-5.nl2Repo`: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `opus-4-7.nl2Repo`: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `sonnet-4-6.nl2Repo`: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `claude-haiku-4-5.nl2Repo`: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `grok-4-20.nl2Repo`: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `grok-4-3.nl2Repo`: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `grok-4-1-fast.nl2Repo`: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- `deepseek-v4-pro.nl2Repo`: Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets
- ... and 1013 more


## [2026-05-06] — autonomous refresh-all [WARN: very low cumulative provenance coverage 28.4%] [MX2: coverage 27.3% < absolute floor 30%] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 182 new fills; 0 cells auto-gapped by orchestrator; 1031 explicit agent gaps preserved]

[fillRatio:0.27 cells:426/1560 contradictions:1 fetch:0.0min tools:None batches:None build:6688fa2]

### Updated
- 29 models: `opus-4-7`, `sonnet-4-6`, `gpt-5-5`, `gpt-5-4`, `o3`, `o4-mini`, `gemini-3-1-pro`, `gemini-3-1-flash`, `grok-4-20`, `grok-4-3`, `grok-4-1-fast`, `grok-3-mini`, `deepseek-v4-pro`, `deepseek-v4-flash`, `deepseek-v3-2`, `minimax-m2-5`, `minimax-m2-7`, `minimax-m2-1`, `qwen3-coder-480b`, `qwen3-coder-next`, `qwen3-5-9b`, `mistral-medium-3-5`, `mistral-large-3`, `gemma-4-26b-moe`, `mimo-v2-pro`, `mimo-v2-flash`, `glm-4-5-air`, `glm-4-7`, `glm-5-1`

### Resolved (auto via trustScore)
- gemini-3-1-flash.lcb: winner={'value': 91.7, 'trustScore': 0.87, 'sourceUrl': 'https://livecodebench.github.io/leaderboard.html', 'tier': 'I'} (severity=GREEN, Δ0.9)

### Gaps (1020 entries — see data/known-gaps.json or next refresh)
- `glm-4-5-air.sweV`: GLM-4.5 Air sweV not found on any leaderboard; model too recent/lightweight for SWE-bench listing
- `glm-4-5-air.swePro`: GLM-4.5 Air not listed on Scale SEAL SWE-bench Pro leaderboard
- `devstral-2.swePro`: Devstral 2 too newly released (2026-05-01); not yet indexed on Scale SEAL Pro leaderboard
- `mistral-medium-3-5.gpqa`: Mistral Medium 3.5 GPQA not published at launch per official blog
- `mistral-medium-3-5.lcb`: LiveCodeBench score for Mistral Medium 3.5 not published at launch
- `qwen3-5-9b.sweV`: Qwen3-5-9B sweV score not found on SWE-bench leaderboard; likely too recent
- `claude-haiku-4-5.aaAgentic`: not reached in agent survey cycle; AA Agentic data unavailable
- `claude-haiku-4-5.aaCoding`: not reached in agent survey cycle; AA Coding data unavailable
- ... and 1012 more

# Changelog

All notable changes to AICoderMap will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **Refresh-cycle entries** (autonomous `/aicodermap refresh-all` runs) are
> consolidated into the **Refresh log** table at the bottom of this file;
> per-cycle gap lists are not duplicated here — they live in
> `data/known-gaps.json` and remain recoverable from `git log -- data/`.
> Only structural / schema / pipeline changes get their own dated section.

---

## [Unreleased]

### Added — 2026-05-10 (FAZ 4.D — Python-side synth)

Sonnet synth agent hit Claude's 32K output token limit on full 60-model
OUTPUT_SCHEMA. Pivot to deterministic Python synth: trustScore arithmetic,
argmax winner picks, contradiction delta detection, N/A rule lookup,
lineup aggregation, pricing/ollama/unsloth merge — all mechanical work
that didn't need an LLM.

- New `scripts/lib/synth.py` — pure-Python pipeline; no LLM call.
- `gen_unified_artifact.py` prefers `.aicodermap-agent-out-synth.json` when
  present (FAZ 4.C); now Python writes it.
- Schema validation hardening: non-canonical bench keys filtered at synth;
  tier values clamped to canonical model-tier set; status values clamped;
  empty `triedSources` in rawGaps backfilled with bench primary URL.
- Cycle 2026-05-10-B measured (Python synth):
  | Metric          | Python | sonnet 05-09 | haiku-only 05-10 |
  |-----------------|--------|--------------|------------------|
  | NEW fills       | **34** | 32           | 15               |
  | UPDATED         | **73** | 20           | 11               |
  | Updated models  | **60** | 55           | 12               |
  | Coverage        | 32.5%  | 30.4%        | 30.4%            |
  | Cost            | ~%6    | baseline     | ~%50             |

Python synth dominates on every dimension — quality matches/exceeds
sonnet single-stage at ~6% of the cost.

### Changed — 2026-05-10 (FAZ 4.C.1 + 4.C.2 — hybrid hardening)

Cycle 2026-05-10 first hybrid run produced 14/18 weak-batch haiku gathers
(avg <3 observations/model) and ~%50 quality regression vs single-stage
sonnet baseline. Two-pronged fix:

**FAZ 4.C.1 — Stricter haiku gather prompt (`agent.md` GATHER_MODE):**
- Required minimum 3 observations per target_model on average.
- Mandatory snapshot enumeration: read EVERY snapshot. Multi-cell extraction.
- Multi-source per cell: one observation per source, not consolidated.
- Output schema discipline: EXACT `models[].observations[]` shape;
  no top-level `filled`/`gaps`/`na` keys.
- New `runtime.perModelObservations` for orchestrator-side weak-batch detection.

**FAZ 4.C.2 — Retry-on-empty escalation (`SKILL.md` Step 4 Stage A.5):**
- Post-Stage A scan: avg observations/target_model < 3 → sonnet retry.
- Retry uses `model:"sonnet"` + `mode:"gather"`. Sonnet artifact
  overwrites haiku artifact at same path.
- New `scripts/lib/constants.HAIKU_GATHER_MIN_AVG_OBS = 3`.

### Added — 2026-05-09 (FAZ 4.C — hybrid haiku gather + sonnet synth dispatch)

Two-phase dispatch architecture replaces single-stage 18× sonnet:

- **Stage A (gather):** 18 batches × **haiku** agent (mode="gather"). Pure
  data extraction — raw observations + naCandidates + lineupHints. NO
  contradiction analysis, NO trustScore math, NO autoResolveWinner, NO
  WRONG_ID detection. Cheap and fast.
- **Stage B (synth):** 1× **sonnet** agent (mode="synth"). Reads ALL gather
  artifacts, applies analytical work: trustScore + contradictions +
  autoResolveWinner + WRONG_ID + N/A rule citation. Emits unified
  OUTPUT_SCHEMA artifact at `.aicodermap-agent-out-synth.json`.

**Cost:** ~18× sonnet → 18× haiku + 1× sonnet ≈ 1/8 baseline.

**Quality:** edge cases (WRONG_ID, cross-model misattribution, contradiction
detection) concentrate in the single sonnet pass with full cross-batch view —
better than 18 scattered sonnet sub-agents that each see only their slice.

Files modified:
- `agent.md` — new DISPATCH_MODES section: GATHER (haiku, simplified output
  schema) + SYNTH (sonnet, consumes gather artifacts) + FULL (legacy
  single-stage). New `mode` and `synth_input_paths` parameters.
- `SKILL.md` — Step 4 rewritten as two-stage dispatch.
- `scripts/gen_unified_artifact.py` — prefers synth artifact when present
  (already in OUTPUT_SCHEMA shape, copied verbatim); falls back to batch
  union when synth absent.

### Changed — 2026-05-08 (FAZ 4.A — priorityCells AUTHORITATIVE → ADVISORY)

Reverts the FAZ 2.3 reform after the 2026-05-08 cycle measured its cost:
- 18 batches used 591/900 tool-calls (~33% — kapasitenin 1/3'ü boşta)
- 51 fills out of ~1300 reachable slice cells (~4% slice coverage)
- Bottleneck: top-200 priority queue ÷ 18 batches ≈ 11 cells/batch as the
  AUTHORITATIVE scope, while each agent's slice was 78-130 cells

**Reform:** `target_model_ids × coreBenchKeys` (full slice) is the agent's
target. `priorityCells[]` is ORDERING within the slice, not scope. Agent
resolves priorityCells FIRST, then sweeps the rest of `target_model_ids ×
coreBenchKeys` until budget/wallclock ceiling. Wallclock cap (FAZ 1.3) +
tool-call ceiling (FAZ 1) independently prevent runaway sweep — the
problem the FAZ 2.3 reform tried to fix is already solved by them.

- `agent.md` "Matrix awareness" — full re-write of the four MUST rules.
  New rule 3: "snapshot-first multi-cell extraction" — one Read should
  yield N×M cells across N models × M benches.
- `SKILL.md` `priorityCells` comment — narrative updated.
- `scripts/lib/matrix.priority_cells()` docstring — updated to match.

### Added — 2026-05-08 (FAZ 4.B — gap.source: 'agent' \| 'orchestrator' ayrımı)

Gap entries now carry `source` field so CHANGELOG, telemetry, and audit
can distinguish agent's "tried-and-failed" from orchestrator's auto-stubs.
Cycle 2026-05-08 had 1021 gaps; with this split: **52 agent gaps (signal),
969 orchestrator gaps (noise)** — previously indistinguishable.

- `.aicodermap-gap-gen.py` — auto-stubs get `source='orchestrator'` (in
  addition to legacy `autoGenerated: True`). `_normalize_existing_gap()`
  treats `autoGenerated: True` as authoritative, even if a stale `source`
  field disagrees.
- `agent.md` OUTPUT_SCHEMA gaps[] — added `source: 'agent'` field
  documentation.
- `scripts/merge.py` — CHANGELOG section now reads
  `### Gaps (N entries — agent:X orchestrator:Y)` with up to 6 agent
  gaps shown first (real research effort), then up to 2 orchestrator
  stubs.
- `scripts/lib/telemetry.py` — `aggregate_per_batch_telemetry()` adds
  `agentGaps` + `orchestratorGaps` to per-batch + cycle totals.



### Changed — 2026-05-07 (FAZ 3 — spec slim-down, pragmatic level)

Reduced spec sprawl in `agent.md` and `SKILL.md`. The aggressive original
targets (agent ~600, SKILL ~400) were de-scoped to "remove redundancy
without behavioural risk"; aggressive trimming deferred until next refresh
exercises the FAZ 1+2 reforms.

- `agent.md`: 1571 → 1418 lines (-153, -10%):
  - Removed 6 "Why this section exists" reform-narrative blocks that were
    historical justification, not active guidance (PHASE 0,
    WEBSEARCH_PRIMARY_DISCIPLINE, GAP_VALIDITY_GATE, SOURCE_FIRST_SWEEP,
    PER_MODEL_URL_EXPANSION, DATA_CONTRACT).
  - Folded PHASE 0b/0c into PHASE 0 sub-probes section.
  - Trimmed RESEARCH_PIPELINE_OPTIMIZATION P10 reform paragraph.
  - Trimmed FORMAT_DISPATCH inline FAZ comments to one-liners.
  - Trimmed PRE_EMIT_SELF_AUDIT pseudocode + emission rules.
  - Removed EXAMPLES section (was 3 boilerplate dispatch templates).
  - Trimmed UNCAPPED + BUDGET reform comments in INPUT_CONTRACT.
- `SKILL.md`: 972 → 841 lines (-131, -13%):
  - Replaced CONSTANTS block (~85 lines) with reference to new
    `scripts/lib/constants.py` + 4-bullet termination summary.
  - Trimmed F1 REFORM and FAZ 1.4/2.1/2.2 reform-narrative comments
    inside WORKFLOW Step 3 idea_context block.
  - Trimmed INVARIANTS section.
- New `scripts/lib/constants.py` (67 lines) — single source of truth for
  numeric thresholds, freshness contract, file paths. Runtime values still
  fetch from `_schema.contracts` via `whitelist.contracts()`; constants.py
  is the SAFE_DEFAULTS fallback.

Lint: ruff clean. Imports verified.

### Added — 2026-05-07 (FAZ 2.4 — wave telemetry + 0-fill auto-retry)

- `scripts/lib/telemetry.aggregate_per_batch_telemetry()` — walks per-batch
  artifacts; aggregates wallclock, tool-call counts, fills/gaps/na,
  partialReason; computes `zeroFillBatches[]` candidates and cycle totals
  (max + p95 wallclock, toolCallSum).
- `scripts/lib/telemetry.write_cycle_telemetry(date, data)` — writes
  `data/_telemetry/<YYYY-MM-DD>.json`. Idempotent on rerun (overwrites
  same-date file).
- `SKILL.md` Step 4 wave loop — single-retry on 0-fill batches with
  `cellsAttempted > 0`. Retry uses fresh agent context, same params,
  same wallclock deadline. Two consecutive 0-fills logged as CHANGELOG
  warn ("genuinely unreachable").
- `SKILL.md` new Step 11a `CYCLE_TELEMETRY` — runs aggregator + writer
  after merge, before commit. Output enables future auto-tuning of
  `dispatch.MAX_BATCH_MODELS` (opt-in; default just logs).

Cycle 2026-05-06 batch03-google_deepm 0-fill (2 models × 26 keys → 0 fills,
43 gaps) was the canonical target this protects against.

### Changed — 2026-05-07 (FAZ 2.3 — priorityCells is authoritative)

- `agent.md` "Matrix awareness" — `priorityCells[]` upgraded from
  "process FIRST" to "process EXCLUSIVELY". Agent walks the list
  top-down through Phase 2/3 cascade and SHALL NOT process cells
  outside the list. Pre-FAZ-2.3 sweep-the-rest behavior burned the
  budget on low-priority cells (cycle 2026-05-06 batch03 0-fill
  pattern); the reform makes priorityCells the only valid scope.
- `scripts/lib/matrix.priority_cells()` —
  `skip_confirmed_within_days` default 14→7 to align with FAZ 2.2
  `FRESHNESS_TTL_DAYS`. Two views of the same data: priorityCells
  says "actively work on this"; skipCells says "use cached value".
- `SKILL.md` `idea_context.priorityCells` — call signature now
  passes `verification_map` and `skip_confirmed_within_days=
  contracts.FRESHNESS_TTL_DAYS` so the work list excludes T2 cells.
- Cells not reached this cycle re-surface in next cycle's priority
  queue (no in-cycle auto-stub by the agent).

### Added — 2026-05-07 (FAZ 2.2 — freshness-tiered cell skip)

Partial retirement of the UNCAPPED+UNCACHED doctrine. Permanent skip lists
(known-gaps.json) remain banned; this reform only adds time-based,
confirmation-gated skip for cells with strong agreement.

- New `scripts/lib/freshness.py`:
  - `classify_cell(cell, today)` → returns tier (T1/T2) and skip flag.
  - `compute_skip_cells(map, today, active_ids, core_keys)` — walks every
    (modelId, benchKey) cell, returns `{<modelId>: {<benchKey>: {value,
    sources, lastChecked, ageDays, verifications}}}` for T2 cells.
  - CLI: `python scripts/lib/freshness.py` prints today's T1/T2 split.
- T1 (always re-fetch): `confirmed=false` OR `verifs<3` OR
  `age>FRESHNESS_TTL_DAYS` OR unresolved-contradiction OR cell missing.
- T2 (skip): `confirmed=true` AND `verifs≥3` AND `age≤7d` AND no
  contradiction. Default TTL 7d, configurable via
  `_schema.contracts.FRESHNESS_TTL_DAYS`.
- `SKILL.md` `idea_context.skipCells` injected to every batch dispatch.
- `agent.md` FORMAT_DISPATCH dispatch protocol — added FRESHNESS-TIER
  CELL SKIP gate BEFORE the WebFetch GATE: when target cell is in
  skipCells, agent emits cached value + cached provenance and skips
  the cell entirely. No fetch, no fallback chain.
- `agent.md` UNCAPPED reform comment — scope-clarified to distinguish
  policy-based skip (banned) from time-based skip (allowed for T2 only).
- Memory feedback `feedback_known_gaps_registry.md` updated to record
  the freshness-tier carve-out + the four T2 conditions.

**First-cycle measurement (2026-05-07):** all 168 verification-map cells
have `lastChecked=2026-04-28` (9 days old) → 0 cells eligible for T2.
After the next `refresh-all`, lastChecked shifts to today; on cycles 1–7
days later, ~10–15 % of confirmed cells skip; steady-state savings depend
on contradiction stability.

### Added — 2026-05-07 (FAZ 2.1 — leaderboard prefetch)

Orchestrator-side single-pass HTTP collapses ~666 duplicated WebFetches/cycle
(18 sub-agents × 37 leaderboards) into ONE prefetch run.

- New `scripts/prefetch-leaderboards.py` — stdlib-only `urllib`
  HTTP-GET pass over every healthy whitelist URL whose format is NOT
  in the FAZ 1.4 banned-list. 8-worker thread pool; per-URL HEAD/GET
  with 15s timeout; SHA8-named snapshots written to
  `data/.leaderboard-snapshots/<host>__<sha8>.{html,json}`.
- New `data/.leaderboard-snapshots/_index.json` — manifest mapping
  `url → { path, fetchedAt, etag, contentLength, contentType, format,
  category }`. Loaded by skill orchestrator into
  `idea_context.leaderboardSnapshots` for every batch dispatch.
- TTL gating: snapshots stay fresh for 24h. Re-runs within TTL no-op.
  `--force` flag bypasses TTL when whitelist URLs change.
- `.gitignore` — `data/.leaderboard-snapshots/` excluded (~40MB,
  regeneratable).
- `SKILL.md` — new `PRELIM-B. LEADERBOARD_PREFETCH` step between
  source-health-check and Phase 0; new SILENT_FAIL_PREVENTION row
  `0c Leaderboard prefetch` (non-fatal, falls back to WebFetch).
- `agent.md` FORMAT_DISPATCH dispatch protocol — added SNAPSHOT-FIRST
  branch: when `entry.url ∈ leaderboardSnapshots`, use `Read(snapshot.path)`
  instead of WebFetch. Same extractor cascade applies. Saves ~1.5
  tool-calls + 5–30s per leaderboard per agent.

**First cycle measurements (2026-05-07):** 81 targets, 73 fetched
successfully, 8 failed (SSL/DNS/404), 15.5s total wallclock, 39MB on
disk. TTL re-run: `fresh: 73, to-fetch: 8` — only failed URLs retried.

### Added — 2026-05-07 (FAZ 1 — wave dispatch hardening)

Four reforms targeting the 2026-05-06 wave-0 wallclock blowout
(refresh-all observed 30–90min, only 5/18 batches completed before
partial-commit). All reforms are spec-only or constants-only — no
behavioural change without the next refresh-all cycle exercising them.

**1.1 Wave dispatch state machine (`SKILL.md` Step 4):**
- `wave_state = {pending, completed}` tracked across the wave loop;
  Step 5 may NOT advance until `len(completed) == len(plan.waves)`.
- HARD GUARD `halt_workflow()` after the loop — blocks gap-gen from
  silently masking missing-wave cells as auto-gaps. SOLE non-push
  halt path in the workflow.
- New SILENT_FAIL_PREVENTION row `4d Wave dispatch completeness`.

**1.2 MAX_PARALLEL 5→10 (`scripts/lib/dispatch.py`):**
- `MAX_PARALLEL = 10` (Claude Code single-message ceiling).
- 18 batches now dispatch in 2 waves (10+8) instead of 4 waves
  (5+5+5+3). Each wave's wallclock is bounded by its slowest batch,
  so fewer waves = less total wallclock.
- Verified via `python scripts/lib/dispatch.py`: totalWaves=2.

**1.3 Hard wallclock per-batch (`SKILL.md` + `agent.md`):**
- New constants `BATCH_WALLCLOCK_SEC=600` and
  `BATCH_WALLCLOCK_SOFT_STOP_SEC=30`.
- Agent INPUT_CONTRACT gets `wallclock_deadline_unix` parameter;
  agent self-stops at `deadline-30s` (Phase boundary checks).
- Orchestrator wraps each Agent call with `subprocess.run(timeout=…)`
  → SIGKILL on overrun; partial Write survives, `partialReason:
  {code:'timeout'}` recorded.
- New SILENT_FAIL_PREVENTION row `4w Wallclock cap`.
- UNCAPPED RESEARCH DOCTRINE clarified: applies to RESEARCH QUALITY
  (sources, fallbacks, gap fabrication) — NOT to per-dispatch resource
  budgets. Tool-call ceiling and wallclock ceiling are EQUAL authority.

**1.4 SPA fetch banned-list mekanik enforcement:**
- `data/sources-whitelist.json` `_schema.formatTaxonomy.{spa_full,
  image_embedded, bot_blocked}.skipWebFetch=true`.
- New `scripts/lib/whitelist.banned_fetch_patterns(whitelist)` —
  derives regex patterns from whitelist entries whose format has
  `skipWebFetch=true` OR `_runtime.unhealthy=true` OR per-entry
  `skipWebFetch=true` override. Tested: 6 banned URLs derived
  (livecodebench, livebench, gorilla BFCL, matharena, epoch.ai,
  HF Chatbot Arena).
- `SKILL.md` `idea_context.bannedFetchPatterns` injected to every
  agent dispatch.
- `agent.md` FORMAT_DISPATCH dispatch protocol — added HARD WebFetch
  GATE: three signals (skipWebFetch, primaryTool=='skip',
  bannedFetchPatterns match) → skip primary, jump to fallback chain.
  Repeated WebFetch on a banned pattern is a contract violation.

### Added — 2026-05-06 (FAZ G — agent budget reform + HuggingFace coverage)

Two reforms in one commit. Together they solve the dominant failure mode
of the prior cycle (97 % of gaps were `autoGenerated: true` stubs because
a single sonnet agent hit Claude Code's tool-call ceiling at 11 % filled).

**Budget reform (root cause fix):**
- `scripts/lib/dispatch.py` (new) — adaptive multi-batch planner.
  Constants: `AGENT_BUDGET_BUFFER=50` tool calls, `CELLS_PER_TOOL_CALL=3`,
  `MAX_BATCH_CELLS=150`. For 60 × 26 universe → 5 models per batch
  (130 cells, well under buffer) → 18 batches arranged into 4 waves of
  {5, 5, 5, 3} parallel sub-agents. **No agent ever exceeds its
  tool-call ceiling.**
- `SKILL.md` Step 4 — replaced the single-shot Agent dispatch with a
  wave-by-wave plan loop:
    plan = compute_dispatch_plan(active, coreKeys)
    for wave in plan.waves:
      results += parallel([Agent(batch) for batch in wave])
    artifact = merge_batch_artifacts(results)
  Each sub-agent emits `.aicodermap-agent-out-<batchId>.json`; gen_unified_artifact.py
  unions the disjoint slices.
- `agent.md` INPUT_CONTRACT — added `agent_budget_buffer` and `batch_id`
  parameters; explicit BUDGET REFORM block: "if approaching the buffer,
  finish the current cell + emit final JSON, do not start another
  cascade". Sub-agents see only their slice; `target_model_ids` is now
  always a strict subset (typically ≤8 models).

**HuggingFace coverage:**
- Refreshed `lastVerifiedDate` on HF Open LLM Leaderboard v2 and
  BigCodeBench HF Space (were null → 2026-05-06). AC9_live stale dropped
  17 → 13.
- New leaderboard: **LMSYS Chatbot Arena (HF mirror)**
  (`huggingface.co/spaces/lmsys/chatbot-arena-leaderboard`) — second
  live publisher for `webDevElo`, closing the AC8 SPOF (grace count
  1 → 0).
- New `_schema.huggingfaceExtraction` block — Phase 2 PER_MODEL_URL_EXPANSION
  protocol: hfApi (`/api/models/<org>/<slug>` JSON modelIndex) → hfReadme
  (`raw/main/README.md` markdown) → hfModelCard (HTML fallback). Eight
  benchmark table regex patterns documented.
- Vendor URL templates added for 9 vendors with HF mirrors (mistralai,
  deepseek-ai, Qwen, moonshotai, zai-org, XiaomiMiMo, MiniMaxAI,
  meta-llama, google, nvidia, stepfun-ai, all-hands). Three new URL
  fields per vendor: `hfModelCard`, `hfReadme`, `hfApi`.
- `agent.md` Phase 3 cascade Step 1 — extended to include the HF chain
  AFTER vendor-own primary sources but BEFORE generic WebSearch (HF API
  returns structured JSON, lower fetch cost than scraping marketing pages).

### Added — 2026-05-06 (FAZ E — source enrichment)

- `data/sources-whitelist.json` — Berkeley BFCL marked live with
  `lastVerifiedDate=2026-05-06` (was null, kept it out of the live
  publisher index so AC8 flagged bfcl as a single-publisher SPOF).
  bfcl now has 2 live publishers (Berkeley + BenchLM); AC8 grace count
  dropped from 2 → 1 (only `webDevElo` still SPOF).
- New I-tier publisher: **OpenRouter Rankings**
  (`https://openrouter.ai/rankings`) — multi-provider adoption + price
  signal aggregator; publishes `aaIdx` proxy. `lastVerifiedDate` +
  `format_lastVerified` set to today so AC6 sees it as live.
- New `_schema.notApplicableRules` entry **`spa-blocked-bench-without-alt`**:
  when the canonical publisher is `spa_full` AND no alt publisher
  exists, the bench is structurally unfillable; agent records affected
  cells under `notApplicable[]` citing this rule. `excludeBenchKeys[]`
  starts empty — populated dynamically as the cycle's health-check
  surfaces persistently-broken extraction paths.
- AC9_live stale-leaderboard count dropped 17 → 16 (Berkeley fresh).

### Added — 2026-05-06 (FAZ D — observability + cycle telemetry)

- `scripts/lib/telemetry.py` (new) — pure-stdlib helper that composes the
  cycle snapshot, writes `data/_meta.json`, and appends a row to
  `data/refresh-history.json` (ring-buffer, last 30 cycles).
- `data/_meta.json` (new canonical artifact) — single-row snapshot per
  refresh: `schemaVersion`, `updatedAt`, `buildSha`, `cycleId`,
  `modelCount`, `benchKeyCount`, `totalCells`, `filledCells`, `gapCells`,
  `naCells`, `fillRatio`, `contradictionsResolved`,
  `lastCycle{ToolCallCount,FetchAttemptCount,BatchCount,ElapsedMs}`,
  `prevPushEtag`. Consumers: `freshness.js`, `verify-deploy.py`, the
  footer chip in the UI.
- `data/refresh-history.json` (new ring-buffer) — last 30 cycles' worth
  of telemetry. Human-review fodder; not consumed by the UI today.
- `merge.py` — telemetry write happens after MX1/MX2/SSOT/AC6/AC7 gates
  pass (writes only on a clean merge). CHANGELOG entry header now carries
  a one-line metadata row right under the title:
  `[fillRatio:0.27 cells:421/1560 contradictions:4 fetch:5.2min tools:62 batches:5 build:abc1234]`.
- `assets/js/data.js` — `loadData()` fetches `_meta.json` best-effort
  (404 silent for legacy deploys). Populates `State.meta`.
- `assets/js/core.js` — `State.meta` slot.
- `assets/js/render-controls.js` — footer chip extended:
  `Deployed: 2026-05-06 · build abc1234 · 27% · 421/1560`. Tooltip
  carries cycle-id + tool-call + batch-count diagnostics.

### Added — 2026-05-06 (FAZ C — research pipeline telemetry)

- `agent.md OUTPUT_SCHEMA.runMetadata` — promoted from optional to MANDATORY,
  with three new fields the orchestrator records per cycle to detect
  research-pipeline degradation early:
  - `toolCallCount` — total agent tool invocations (≥80 = priority-cascade
    starvation alarm; CHANGELOG WARN on next cycle prelude).
  - `fetchAttemptCount` — subset of toolCallCount that hit the network
    (sizes IN-CYCLE PROMOTION budget; spots cycles that thrashed local
    Reads instead of fetching evidence).
  - `batchCount` — number of sub-agents the orchestrator dispatched. The
    P10.1 multi-agent fan-out target is 5; batchCount=1 surfaces a WARN
    that fan-out collapsed and per-cell coverage will be lower.
- `merge.py` — new soft-gate `runMetadata` audit. Missing fields surface
  `[WARN: runMetadata missing fields …]` in the CHANGELOG entry; tool/batch
  alarms surface inline (`[WARN: toolCallCount=85 near agent ceiling — priority cascade likely starved]`).
  Merge is NOT rolled back (legacy artifacts predate this contract). Once
  one full refresh-all lands with the new fields, a future commit can
  promote this to MX6 hard-block.

### Added — 2026-05-06 (FAZ B — silent-failure hardening + post-push verify)

- `scripts/verify-deploy.py` (new) — post-push GitHub Pages deploy
  verification. Three nested checks (commits-API SHA / Pages ETag rotation
  / `_meta.json` parity) wrapped in one binary; 60s CDN warm-up + 3×30s
  retry budget; exit code semantics 0/1/2 documented for skill Step 14.
- `merge.py` MX2 absolute coverage floor — promoted from WARN-only to
  HARD BLOCK by default; opt-out via `AICODERMAP_MX2_WARN_ONLY=1` env or
  `--bypass-floor-check` CLI flag for transition periods. The breach
  triggers the same `.bak` rollback + non-zero exit chain MX1 already
  uses, so cycles that regress below the 30 % cumulative-provenance
  floor are blocked at merge time, never reach `git push`.
- `merge.py` MX1 — retired the `--warn-only-invariant` migration path
  from docstrings + error message; the matrix invariant has no warn-only
  override. Operators must fix the artifact (gaps[] / notApplicable[] /
  bench cells) instead of bypassing.
- `audit-bench-source-mapping.py` AC8 — promoted from pure WARN to
  CONDITIONAL BLOCK behind `AICODERMAP_AC8_BLOCK=1` env-flag (opt-in
  until FAZ E lands missing publishers). Within the 14-day grace window
  (`firstSeen` ≤ 14 days), single-publisher status stays a warn so a
  freshly-added coreBenchKey isn't rejected immediately.
- `scripts/hooks/pre-push` — every successful run stamps
  `.audit/last-pre-push.iso` + `.audit/last-pre-push.sha`. Acts as audit
  trail anchor: a downstream check can detect a stale stamp (proxy for
  `git push --no-verify` bypass) without polluting the commit history.
- `.claude/skills/aicodermap/SKILL.md` Step 14 — now invokes
  `verify-deploy.py` (was a single `curl`). Exit-code policy explicit:
  0 = ✓ verified, 1 = log failure to CHANGELOG, 2 = tooling unavailable.
  Cycle is not "complete" until verify-deploy returns 0 or 2.
- `.gitignore` — `.audit/` directory ignored except `.audit/.gitkeep`
  preserves the directory in fresh clones so hooks have a write target.

### Added — 2026-05-06 (M4 polish gate)

- `sitemap.xml` + `robots.txt` at repo root — TR / EN / x-default hreflang
  alternates, weekly changefreq.
- `index.html` — JSON-LD `@graph` (WebSite + Person + Dataset + SoftwareApplication),
  canonical link, full Open Graph (og:url, og:image, og:locale + locale:alternate,
  site_name, image dimensions), Twitter `summary_large_image`,
  `<meta name="referrer">` strict-origin, `Permissions-Policy` (interest-cohort,
  browsing-topics, geolocation, camera, microphone, payment all denied),
  CSP `script-src` explicit with html2canvas SHA-256.
- `assets/og-image.svg` — 1200×630 social card (vendored, no external CDN).
- Skip-to-content link (`#filters`) — header bypass for keyboard / screen-reader
  users; `:focus-visible` outline scoped to brand accent.
- `i18n/{tr,en}.json` — `ui.a11y.skipToContent` key (TR + EN parity preserved,
  323 / 323 keys, 0 drift).
- `.gitignore` — root-level `__pycache__/` glob (was only `scripts/__pycache__/`),
  `*.pyc` / `*.pyo`, generated Lighthouse audit reports.

### Changed — 2026-05-06 (documentation drift sweep)

- `CLAUDE.md` — module list updated 11 → 14 (added `freshness.js`, `sources.js`,
  `render-privacy.js` after Apr-29 refactor).
- `docs/TECHSPEC.md` §3 — schema example regenerated against the live shape:
  25-key bench universe, multi-provider pricing array (was object), `notApplicableBenchKeys`
  + `benchQuarantine` + per-cell `benchUpdated` map.
- `docs/IMPLGUIDE.md` §8 — `DEFAULT_WEIGHTS` (19 keys, integer 0-100, sums 100)
  + 5 presets (added `reasoning-focused`); supersedes the old 12-key decimal table.
- `docs/TEST_PLAN.md` — model count 53 → 55, AC table extended with privacy table /
  freshness banner / pricing baseline scenarios; Lighthouse runbook section.
- `docs/WORKFLOW.md` §1 — `/ledger-tracker-update` → `/aicodermap` (skill rename
  was reflected in code but not in this doc).
- `docs/PRD.md` — "35-model" → "55+ model" reference updated; `aaCoding` /
  `aaIdx` taxonomy aligned with `data/sources-whitelist.json._schema.coreBenchKeys`.
- `docs/TASKS.md` — T24 (mobile card-stack) marked done; T25 (custom preset
  save/load) explicitly deferred to Phase 2.
- `README.md` — roadmap blurb clarified: M3 13-feature UI complete; bench
  cross-source coverage tracked separately and continues to climb each refresh.

### Added — 2026-05-06 (ProgramBench + hardware preset shortcuts)

- New coreBenchKey **`programBench`** — cleanroom program reconstruction
  benchmark from arXiv:2605.03546 (Meta + Stanford + Harvard, 2026-05-05).
  200 tasks, 248K+ behavioral tests; agents must rebuild a working
  implementation from documentation + a hidden test harness, sandboxed,
  no internet. Tracks frontier breakthrough rather than discriminate at
  current capability tier (no public model has fully resolved any task).
  - `data/sources-whitelist.json`: `_schema.coreBenchKeys` 25→26;
    `_schema.benchAliases.programBench`; coding category gains the key;
    two new I-tier publishers (`programbench.com` official +
    `benchlm.ai/benchmarks/programBench` aggregator) with
    `lastVerifiedDate` set so AC6/AC7 pass.
  - `assets/js/core.js`: `BENCH_KEYS` 25→26, `BENCH_CATEGORIES.coding`
    gains `programBench`; `DEFAULT_WEIGHTS` adds `programBench:1`. Net
    rebalance fixed a pre-existing 99-instead-of-100 sum on the balanced
    preset (no behavioural change for any user, but the smoke harness now
    reports clean).
  - `i18n/{tr,en}.json`: `benchmarks.programBench.{short,name,desc}`.
  - `data/models.json`: every model's `bench` initialised with
    `programBench: null`; next `/aicodermap refresh-all` cycle fills.
  - `scripts/add-programbench.py`: one-shot helper kept for traceability.
- New `data/gpu-database.json.featuredPresets[]` — eight curated
  hardware tiers (RTX 3070/4060/4070/4080/4090/5090, M3 Max 64GB,
  M4 Max 128GB) shown as a `⭐ Popular hardware` optgroup at the top of
  the GPU dropdown, ahead of the full 100+ vendor list.
  - `assets/js/gpu.js populateGpuSelect()` honours the `featuredPresets`
    array; ids resolve to canonical `vendor.entry` records — the URL
    state codec (`gpu=nvidia.rtx-4090`) works unchanged.
  - `i18n/{tr,en}.json`: `ui.filter.gpuPopular` ("Popüler donanım" /
    "Popular hardware").

### Added — 2026-05-06 (URL state codec + lineup expansion)

- `assets/js/url-state.js` — URL ⇄ State codec. Every visible filter,
  weight set, sort, language, theme, GPU, and VRAM choice is reflected in
  the address bar with named query parameters. Precedence at first load:
  URL > localStorage > defaults. `pushUrlState()` is debounced 250 ms;
  `buildShareUrl()` returns a paste-ready link.
- `index.html` — **Copy share link** button in the Export section
  (clipboard + `navigator.share` fallback chain).
- `i18n/{tr,en}.json` — `ui.share.{tooltip, button, copied, failed}` keys
  (337 / 337, 0 drift).
- `assets/test/smoke.html` — three new url-state assertions
  (preset=balanced, custom-weights serialize, filter encoding).
- `docs/TECHSPEC.md` §4.5 — URL state contract (12-key codec, stability
  pinned to `acm.v1.*` localStorage version).
- `README.md` — "Shareable deep-links" + "Programmatic Access" sections
  with curl + jq examples for CLI / agent consumers.
- `data/models.json` — 5 new lineup-stub entries from the 2026-05-06
  user-supplied table (`glm-4-5-air`, `glm-4-7`, `mistral-medium-3-5`,
  `qwen3-5-9b`, `minimax-m2-1`). Bench cells are null and will be filled
  by the next `/aicodermap refresh-all` cycle. i18n strengths /
  weaknesses populated for both locales to keep parity audits green.
  Model count 55 → 60.
- `scripts/add-lineup-stubs.py` — one-shot helper that wrote the stubs;
  kept in repo for traceability.

### Notes — localStorage namespace

The runtime canonical prefix is `acm.v1.*` (see `assets/js/core.js:STORAGE`).
Older docs referenced `cmt.v1.*` from a pre-rename draft — that key was never
shipped to users; kept here so future readers don't grep for a ghost.

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

## [2026-04-25.a] — M1 + M2 + M3 first integration

### Added (M1 Foundation)

- `data/models.json` — schema + initial seed entries (2 frontier + 1 OpenAI + 2 open-tier1/local).
- `data/sources.json` — provenance for 10 Opus 4.7 bench scores; demo YELLOW contradiction on `swePro` (Δ 3.1pp).
- `data/gpu-database.json` — NVIDIA RTX 50/40/30/20/16 + Apple M1–M4 + AMD RX 7000/6000 + Intel Arc + `webgpuVendorMap`.
- `i18n/tr.json` + `i18n/en.json` — nested key structure (ui / models / benchmarks / verdicts).

### Added (M2 Core)

- `index.html` — semantic HTML5, sticky nav, tooltip slot, OG meta, hreflang.
- `assets/app.css` — 3-breakpoint responsive (mobile <640 / tablet 641–1024 / desktop >1024), CSS variables, dark + light theme, export-mode rules.
- `assets/app.js` — vanilla render core: schema validation, composite score, model card builder, no-innerHTML XSS defense.

### Added (M3 Integration)

- Weights editor — 19 number inputs, 100% total constraint, 5 presets (balanced / swe-focused / agentic-focused / reasoning-focused / benchmark-only), reset, `acm.v1.weights` persist.
- i18n TR/EN runtime switch — `acm.v1.language` persist, `<html lang>` + page-wide `data-i18n-key` walk.
- Contradiction flag UI — 3pp YELLOW / 5pp RED, hover/focus tooltip with source breakdown (value, source URL, tier S/I/C, date).
- PNG export — vendored `html2canvas@1.4.1` (SHA256 `e87e5507…ab8cb`), per-section + full-page buttons, export-mode CSS hides nav/actions.
- GPU VRAM detect — WebGPU `navigator.gpu` auto + manual GPU select (NVIDIA/Apple/AMD/Intel optgroups) + manual VRAM override + per-model compatibility badge (fits / offload / too-large) + Unsloth UD recommend + filter checkbox + `acm.v1.{gpu,vram}` persist.
- Filters — tier select, open-only checkbox, GPU-fit-only checkbox, all persisted via `acm.v1.filters`.

## [0.0.1] — 2026-04-25

### Added

- Initial repo bootstrap.
- 6 documentation files in `docs/` (PRD, TechSpec, ImplGuide, Tasks, Workflow, Pitch).
- README + CHANGELOG + `.gitignore`.
- Folder structure: `assets/`, `data/`, `i18n/`, `docs/`.
- `CLAUDE.md` project instructions.

### Status

- Pre-implementation — Project Kickstart complete, M1 Foundation starting.

---

## Refresh log — autonomous `refresh-all` cycles (compacted)

> Each cycle lands as a single-line summary. Detailed gap lists live in
> `data/known-gaps.json`; per-cell historical observations live in
> `.aicodermap-verification-map.json` (gitignored, regenerable via
> `scripts/verification-map.py bootstrap`).

| Date       | Updated | Lineup Δ              | Resolved | Gaps  | Coverage | Note                                                                                  |
|------------|--------:|-----------------------|---------:|------:|---------:|---------------------------------------------------------------------------------------|
| 2026-04-30 | 47      | —                     | 4        | 971   | 29.4%    | partial completeness loop; agent self-audit skipped (covMatrix missing in artifact)   |
| 2026-04-30 | 21      | —                     | 8        | 1003  | 27.1%    | gap-gen supplement (+51 fills); LMArena WebDev Arena SPA-blocked across frontier set  |
| 2026-04-30 | 3       | —                     | 1        | 1044  | 24.1%    | targeted Grok 4.x batch; AIME 2026 not yet published for Grok 4.1 Fast / GPT-5.5      |
| 2026-04-29 | 52      | —                     | —        | 1107  | 22.6%    | completeness loop hit 87 tool calls; gap-gen accounted for all 1430 cells             |
| 2026-04-29 | 11      | +1 (`grok-4-1-fast`)  | 3        | 3     | 42.0%    | matrix invariant violated (1105 silent) — motivated reform [.d]                       |
| 2026-04-29 | 2       | 1 deprecated          | 0        | 48    | 38.0%    | webDevElo SPA-gated across frontier set                                                |
| 2026-04-29 | 27      | 2 deprecated, 1 renamed | 2      | 17    | 41.0%    | matrix invariant violated (824 cells silent) — motivated reform [.d]                  |
| 2026-04-29 | 23      | —                     | 1        | 8     | 52.0%    | invariant violated (428 cells silent)                                                  |
| 2026-04-28 | 29      | 4 deprecated          | —        | —     | 54.0%    | first refresh after dynamic whitelist mutation                                         |
| 2026-04-28 | —       | —                     | —        | —     | 48.0%    | (lineup-sync only)                                                                     |
| 2026-04-27 (×5) | various | various          | various  | various | 38–48% | SOURCE_FIRST_SWEEP path live; per-model URL expansion; vendor-conditional slug map    |
| 2026-04-26 (×9) | various | various          | various  | various | ~41%   | UNCAPPED reform live; 9 cycles ran in one day during research-pipeline tuning         |
| 2026-04-25 | 51      | —                     | 6        | 14    | 17–18%  | first full sweep; independent-source canonical rule established                       |

**Anti-Aider-stale watermark:** longest gap between any two consecutive refreshes
to date is **6 days** (2026-04-30 → 2026-05-06 *as of writing*). M5 target
≤ 14 days unmet only by R3 (solo burnout) recovery sprint contingency.
