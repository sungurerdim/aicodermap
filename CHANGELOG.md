
## [2026-06-06] — autonomous refresh-all [WARN: cumulative provenance coverage 66.8% below 85% target] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 585 new fills; 22 cells auto-gapped by orchestrator; 710 explicit agent gaps preserved]

[fillRatio:0.67 cells:863/1292 contradictions:276 fetch:0.0min tools:None batches:None build:e27b8f2]

### Flagged
- Anomaly-verify (Layer-3, top-24 high-priority): 14 confirmed (genuine outliers, kept), 6 cleared (primary-source contradicted stored value): `mistral-large-3.lcb`, `mistral-large-3.gpqa`, `mimo-v2-5-pro.mmluPro`, `qwen3-32b.gpqa`, `qwen3-coder-30b.gpqa`, `codestral.aaIdx`. Cleared cells carry gaps[] for next-cycle re-fill.
- Lineup hint (NOT added — single C-tier source, restricted/not-GA, flagged for human review): `claude-mythos-preview` (Anthropic, per blog timeline; awaiting ≥2-source verification).
- C1 Elo-sibling synth filter dropped 1 misfile; 25 format-consistency warnings (non-blocking); 4 models missing `context` field (gaps for next cycle): `nemotron-3-ultra`, `grok-build-0-1`, `gemma-4-12b`, `glm-5-turbo`.

### Updated
- 56 models: `nemotron-3-nano-omni`, `grok-build-0-1`, `grok-4-3`, `minimax-m2-5`, `grok-3-mini`, `qwen3-coder-next`, `deepseek-v4-pro`, `deepseek-v4-flash`, `gemini-3-1-flash`, `qwen3-coder-480b`, `deepseek-v3-2`, `qwen3-6-35b-moe`, `gemma-4-26b-moe`, `qwen3-5-9b`, `step-3-7-flash`, `gemma-4-e4b`, `glm-5-1`, `mimo-v2-5`, `qwen3-6-plus`, `mistral-large-3`, `nemotron-3-ultra`, `llama-4-scout`, `minimax-m2-1`, `glm-5-turbo`, `gemma-4-e2b`, `gemma-4-31b`, `gpt-5-4-mini`, `qwen3-6-27b`, `mistral-medium-3-5`, `qwen3-7-max`, `nemotron-3-super`, `claude-opus-4-8`, `muse-spark`, `gpt-4-1`, `glm-5`, `mimo-v2-5-pro`, `qwen25-coder-32b`, `qwen3-32b`, `step-3-5-flash`, `glm-4-5-air`, `o3`, `gemma-3-27b`, `gpt-5-4`, `mimo-v2-pro`, `minimax-m2-7`, `qwen3-coder-30b`, `deepseek-coder-v2-16b`, `qwen25-coder-7b`, `gpt-5-5`, `gpt-5-4-nano`, `gemma-4-12b`, `qwen3-235b`, `grok-4-1-fast`, `devstral-small-2`, `glm-4-7`, `opus-4-7`

### Resolved (auto via trustScore)
- opus-4-7.sweV: winner={'value': 87.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- opus-4-7.swePro: winner={'value': 64.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- opus-4-7.gpqa: winner={'value': 94.29, 'trustScore': 0.5, 'tier': 'I', 'verifications': 14, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- opus-4-7.hle: winner={'value': 46.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- opus-4-7.tb2: winner={'value': 69.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- opus-4-7.arcAgi2: winner={'value': 75.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- opus-4-7.mmluPro: winner={'value': 89.87, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- opus-4-7.aime26: winner={'value': 95.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- opus-4-7.mrcr: winner={'value': 32.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- sonnet-4-6.sweV: winner={'value': 79.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- sonnet-4-6.gpqa: winner={'value': 74.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 15, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- sonnet-4-6.hle: winner={'value': 51.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- sonnet-4-6.tau2: winner={'value': 91.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- sonnet-4-6.arcAgi2: winner={'value': 58.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- claude-haiku-4-5.sweV: winner={'value': 73.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- claude-haiku-4-5.gpqa: winner={'value': 67.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- claude-haiku-4-5.tbHard: winner={'value': 27.3, 'trustScore': 0.4986, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- claude-opus-4-8.hle: winner={'value': 49.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v4-pro.sweV: winner={'value': 80.57, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v4-pro.lcb: winner={'value': 93.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 16, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v4-pro.tb2: winner={'value': 67.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v4-pro.swePro: winner={'value': 55.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v4-pro.gpqa: winner={'value': 90.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 14, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v4-pro.hle: winner={'value': 37.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v4-pro.aaIdx: winner={'value': 51.92, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v4-pro.aaCoding: winner={'value': 47.47, 'trustScore': 0.4979, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- deepseek-v4-pro.tbHard: winner={'value': 46.2, 'trustScore': 0.4986, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- deepseek-v4-flash.sweV: winner={'value': 79.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v4-flash.lcb: winner={'value': 91.44, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v4-flash.gpqa: winner={'value': 88.35, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v4-flash.hle: winner={'value': 22.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v4-flash.mmluPro: winner={'value': 86.35, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v4-flash.tau2: winner={'value': 94.4, 'trustScore': 0.4915, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v3-2.sweV: winner={'value': 67.86, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v3-2.lcb: winner={'value': 74.11, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v3-2.gpqa: winner={'value': 82.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v3-2.hle: winner={'value': 24.87, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v3-2.tau2: winner={'value': 71.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- deepseek-v3-2.tb2: winner={'value': 46.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v3-2.mmluPro: winner={'value': 85.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v3-2.cfElo: winner={'value': 2386.0, 'trustScore': 0.35, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-v3-2.aaIdx: winner={'value': 32.04, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-coder-v2-16b.lcb: winner={'value': 43.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-r1-14b.gpqa: winner={'value': 59.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- deepseek-r1-14b.lcb: winner={'value': 53.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemini-3-1-flash.sweV: winner={'value': 78.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemini-3-1-flash.gpqa: winner={'value': 90.18, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemini-3-1-flash.hle: winner={'value': 34.52, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemini-3-1-flash.aaIdx: winner={'value': 71.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-flash.mmluPro: winner={'value': 89.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemini-3-1-pro.gpqa: winner={'value': 94.25, 'trustScore': 0.5, 'tier': 'I', 'verifications': 17, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemini-3-1-pro.hle: winner={'value': 44.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 15, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemini-3-1-pro.mmluPro: winner={'value': 90.99, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemini-3-1-pro.aaIdx: winner={'value': 57.02, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- gemini-3-1-pro.swePro: winner={'value': 54.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemini-3-1-pro.tau2: winner={'value': 76.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemini-3-1-pro.tbHard: winner={'value': 44.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemma-3-27b.gpqa: winner={'value': 42.48, 'trustScore': 0.5, 'tier': 'I', 'verifications': 17, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemma-3-27b.tau2: winner={'value': 6.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- gemma-4-26b-moe.gpqa: winner={'value': 82.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 17, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemma-4-26b-moe.mmluPro: winner={'value': 82.76, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- gemma-4-26b-moe.aaIdx: winner={'value': 31.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemma-4-26b-moe.tau2: winner={'value': 86.4, 'trustScore': 0.35, 'tier': 'S', 'verifications': 4, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemma-4-26b-moe.cfElo: winner={'value': 2150.0, 'trustScore': 0.35, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemma-4-26b-moe.hle: winner={'value': 22.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- gemma-4-31b.gpqa: winner={'value': 84.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 16, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemma-4-31b.lcb: winner={'value': 80.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 19, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemma-4-31b.tau2: winner={'value': 86.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemma-4-31b.hle: winner={'value': 23.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemma-4-31b.sweV: winner={'value': 64.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-e2b.aime26: winner={'value': 37.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemma-4-e2b.gpqa: winner={'value': 43.4, 'trustScore': 0.4752, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemini-3-5-flash.swePro: winner={'value': 55.1, 'trustScore': 0.4664, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemini-3-5-flash.gpqa: winner={'value': 92.21, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- gemini-3-5-flash.sweV: winner={'value': 81.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-e4b.gpqa: winner={'value': 58.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemma-4-e4b.mmluPro: winner={'value': 69.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- llama-4-maverick.lcb: winner={'value': 43.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- llama-4-maverick.gpqa: winner={'value': 69.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- llama-4-maverick.mmluPro: winner={'value': 80.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- llama-4-scout.lcb: winner={'value': 32.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- llama-4-scout.gpqa: winner={'value': 57.34, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- llama-4-scout.mmluPro: winner={'value': 74.26, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- muse-spark.swePro: winner={'value': 52.4, 'trustScore': 0.4664, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- minimax-m2-5.sweV: winner={'value': 80.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 17, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- minimax-m2-5.swePro: winner={'value': 55.49, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- minimax-m2-5.gpqa: winner={'value': 85.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 15, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- minimax-m2-5.hle: winner={'value': 19.37, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- minimax-m2-5.tau2: winner={'value': 97.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- minimax-m2-5.aaAgentic: winner={'value': 55.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- minimax-m2-7.swePro: winner={'value': 56.21, 'trustScore': 0.5, 'tier': 'I', 'verifications': 15, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- minimax-m2-7.tb2: winner={'value': 57.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- minimax-m2-7.gpqa: winner={'value': 86.98, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- minimax-m2-7.aime26: winner={'value': 94.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- minimax-m2-7.hle: winner={'value': 28.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- minimax-m2-7.tau2: winner={'value': 84.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- minimax-m2-7.tbHard: winner={'value': 39.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- minimax-m2-1.sweV: winner={'value': 74.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- minimax-m2-1.gpqa: winner={'value': 82.88, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- minimax-m2-1.hle: winner={'value': 17.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- minimax-m2-1.lcb: winner={'value': 86.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-1.tau2: winner={'value': 87.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mistral-large-3.tau2: winner={'value': 70.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- mistral-large-3.tbHard: winner={'value': 15.91, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- mistral-large-3.lcb: winner={'value': 82.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- mistral-large-3.mmluPro: winner={'value': 73.11, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- devstral-2.gpqa: winner={'value': 59.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- devstral-2.sweV: winner={'value': 72.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- devstral-2.lcb: winner={'value': 44.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- devstral-medium.sweV: winner={'value': 61.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- devstral-medium.lcb: winner={'value': 33.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- devstral-small-2.sweV: winner={'value': 68.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- nemotron-3-super.sweV: winner={'value': 60.47, 'trustScore': 0.5, 'tier': 'I', 'verifications': 17, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- nemotron-3-super.lcb: winner={'value': 81.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- nemotron-3-super.gpqa: winner={'value': 79.27, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- nemotron-3-super.tbHard: winner={'value': 28.96, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- nemotron-3-super.tau2: winner={'value': 67.8, 'trustScore': 0.4844, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- nemotron-3-ultra.hle: winner={'value': 26.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- nemotron-3-ultra.tb2: winner={'value': 56.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- nemotron-3-nano-omni.gpqa: winner={'value': 72.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- nemotron-3-nano-omni.hle: winner={'value': 5.3, 'trustScore': 0.1972, 'tier': 'C', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- nemotron-3-nano-omni.lcb: winner={'value': 63.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- nemotron-3-nano-omni.tau2: winner={'value': 42.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gpt-5-5.aaIdx: winner={'value': 59.91, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gpt-5-5.hle: winner={'value': 41.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-5.tau2: winner={'value': 98.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- gpt-5-5.sweV: winner={'value': 88.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gpt-5-5.swePro: winner={'value': 58.51, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gpt-5-5.tb2: winner={'value': 82.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gpt-5-5.mrcr: winner={'value': 74.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- o3.gpqa: winner={'value': 87.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- o3.hle: winner={'value': 20.24, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- o3.tau2: winner={'value': 83.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- o3.sweV: winner={'value': 71.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- o3.lcb: winner={'value': 75.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- o3.mmluPro: winner={'value': 88.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-18'} (severity=yellow, ΔNone)
- o3.cfElo: winner={'value': 2727.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- o3.aime26: winner={'value': 88.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- o4-mini.sweV: winner={'value': 68.18, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- o4-mini.aime26: winner={'value': 92.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gpt-4-1.gpqa: winner={'value': 66.46, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gpt-4-1.swePro: winner={'value': 60.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gpt-4-1.mmluPro: winner={'value': 80.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gpt-4-1.lcb: winner={'value': 68.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-4.swePro: winner={'value': 58.31, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gpt-5-4.gpqa: winner={'value': 92.33, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gpt-5-4.sweV: winner={'value': 78.98, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-6-27b.sweV: winner={'value': 77.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-6-27b.swePro: winner={'value': 53.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-6-27b.lcb: winner={'value': 83.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-6-27b.gpqa: winner={'value': 87.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-6-35b-moe.swePro: winner={'value': 49.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-6-35b-moe.tb2: winner={'value': 51.5, 'trustScore': 0.35, 'tier': 'S', 'verifications': 4, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-6-35b-moe.lcb: winner={'value': 80.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- qwen3-6-35b-moe.gpqa: winner={'value': 86.0, 'trustScore': 0.35, 'tier': 'S', 'verifications': 8, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-6-35b-moe.hle: winner={'value': 20.16, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-6-35b-moe.tau2: winner={'value': 67.2, 'trustScore': 0.35, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-6-plus.sweV: winner={'value': 78.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-6-plus.aaIdx: winner={'value': 49.99, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-235b.gpqa: winner={'value': 81.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-235b.hle: winner={'value': 42.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-235b.lcb: winner={'value': 74.48, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-235b.aaIdx: winner={'value': 30.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-235b.tau2: winner={'value': 37.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-32b.lcb: winner={'value': 54.54, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-32b.aaIdx: winner={'value': 76.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-32b.gpqa: winner={'value': 66.74, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-coder-next.sweV: winner={'value': 70.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-coder-next.swePro: winner={'value': 44.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-coder-next.lcb: winner={'value': 68.66, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-coder-next.tb2: winner={'value': 36.2, 'trustScore': 0.35, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-coder-480b.swePro: winner={'value': 38.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-coder-480b.lcb: winner={'value': 68.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-coder-480b.gpqa: winner={'value': 84.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-coder-30b.sweV: winner={'value': 51.22, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-coder-30b.tb2: winner={'value': 36.2, 'trustScore': 0.4182, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-coder-30b.lcb: winner={'value': 56.53, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-coder-30b.tau2: winner={'value': 74.2, 'trustScore': 0.4788, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen25-coder-32b.gpqa: winner={'value': 41.75, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen25-coder-32b.sweV: winner={'value': 69.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen25-coder-32b.lcb: winner={'value': 48.69, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen25-coder-7b.gpqa: winner={'value': 33.9, 'trustScore': 0.4938, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- qwen25-coder-7b.lcb: winner={'value': 37.6, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen25-coder-7b.mmluPro: winner={'value': 45.6, 'trustScore': 0.3381, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- qwen3-5-9b.hle: winner={'value': 13.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- qwen3-5-9b.tau2: winner={'value': 86.77, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-5-9b.tbHard: winner={'value': 24.24, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-5-9b.lcb: winner={'value': 65.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-7-max.sweV: winner={'value': 80.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-7-max.gpqa: winner={'value': 92.38, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- qwen3-7-max.hle: winner={'value': 41.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-7-max.lcb: winner={'value': 90.79, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- grok-3.gpqa: winner={'value': 84.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- grok-3.hle: winner={'value': 18.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- grok-3.lcb: winner={'value': 79.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- grok-3-mini.gpqa: winner={'value': 79.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- grok-3-mini.lcb: winner={'value': 69.76, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- grok-3-mini.aime26: winner={'value': 95.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- grok-4-20.aaIdx: winner={'value': 49.07, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- grok-4-20.gpqa: winner={'value': 88.02, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- grok-4-1-fast.gpqa: winner={'value': 85.36, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- grok-4-1-fast.hle: winner={'value': 4.99, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- grok-4-1-fast.tau2: winner={'value': 63.71, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- grok-4-1-fast.tbHard: winner={'value': 14.39, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- mimo-v2-5.gpqa: winner={'value': 86.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- mimo-v2-5.hle: winner={'value': 33.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- mimo-v2-5.tau2: winner={'value': 90.64, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- mimo-v2-5.tbHard: winner={'value': 26.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- mimo-v2-5-pro.aaAgentic: winner={'value': 68.07, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- mimo-v2-5-pro.gpqa: winner={'value': 66.7, 'trustScore': 0.35, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mimo-v2-5-pro.hle: winner={'value': 33.87, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- mimo-v2-5-pro.tau2: winner={'value': 72.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mimo-v2-5-pro.lcb: winner={'value': 76.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-5-pro.mmluPro: winner={'value': 68.5, 'trustScore': 0.35, 'tier': 'S', 'verifications': 4, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- mimo-v2-flash.gpqa: winner={'value': 83.83, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- mimo-v2-flash.hle: winner={'value': 22.1, 'trustScore': 0.35, 'tier': 'S', 'verifications': 6, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- mimo-v2-flash.tb2: winner={'value': 38.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- mimo-v2-flash.mmluPro: winner={'value': 84.9, 'trustScore': 0.35, 'tier': 'S', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- mimo-v2-flash.lcb: winner={'value': 80.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- mimo-v2-flash.aime26: winner={'value': 94.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- mimo-v2-pro.aaAgentic: winner={'value': 62.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- mimo-v2-pro.gpqa: winner={'value': 86.95, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- mimo-v2-pro.tau2: winner={'value': 95.01, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- glm-5-1.swePro: winner={'value': 58.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 15, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- glm-5-1.gpqa: winner={'value': 86.26, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- glm-5-1.hle: winner={'value': 52.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- glm-5-1.sweV: winner={'value': 77.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- glm-5-1.tau2: winner={'value': 97.69, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- glm-5-1.aaIdx: winner={'value': 51.12, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- glm-5.gpqa: winner={'value': 82.02, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- glm-5.hle: winner={'value': 27.25, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- glm-5.tau2: winner={'value': 98.25, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- glm-4-7.sweV: winner={'value': 73.75, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- glm-4-7.tau2: winner={'value': 87.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- glm-4-7.gpqa: winner={'value': 85.71, 'trustScore': 0.5, 'tier': 'I', 'verifications': 14, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- glm-4-7.hle: winner={'value': 42.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- glm-4-7.browseComp: winner={'value': 67.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- glm-4-5-air.sweV: winner={'value': 57.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- glm-4-5-air.gpqa: winner={'value': 79.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-5-air.hle: winner={'value': 14.18, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- glm-4-5-air.tau2: winner={'value': 78.11, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- glm-4-5-air.aime26: winner={'value': 89.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- glm-4-5-air.browseComp: winner={'value': 21.3, 'trustScore': 0.4907, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- glm-4-5-air.tb2: winner={'value': 30.0, 'trustScore': 0.4907, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- kimi-k2-6.gpqa: winner={'value': 90.54, 'trustScore': 0.5, 'tier': 'I', 'verifications': 14, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- kimi-k2-6.hle: winner={'value': 54.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- kimi-k2-6.tau2: winner={'value': 70.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- kimi-k2-6.sweV: winner={'value': 80.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 16, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- kimi-k2-6.swePro: winner={'value': 58.6, 'trustScore': 0.4664, 'tier': 'I', 'verifications': 17, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- kimi-k2-6.lcb: winner={'value': 89.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 15, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- kimi-k2-6.tb2: winner={'value': 66.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- step-3-5-flash.aaCoding: winner={'value': 34.56, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- step-3-5-flash.aaAgentic: winner={'value': 48.23, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- step-3-5-flash.gpqa: winner={'value': 83.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- step-3-5-flash.hle: winner={'value': 22.75, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- step-3-5-flash.sweV: winner={'value': 74.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- step-3-5-flash.tb2: winner={'value': 51.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- step-3-5-flash.mmluPro: winner={'value': 84.63, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- step-3-7-flash.sweV: winner={'value': 74.4, 'trustScore': 0.4909, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- step-3-7-flash.tb2: winner={'value': 59.6, 'trustScore': 0.3412, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- step-3-7-flash.gpqa: winner={'value': 77.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- glm-4-5-air.aaIdx: winner={'value': 23.09, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- step-3-7-flash.aaCoding: winner={'value': 34.56, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- glm-4-7.aaIdx: winner={'value': 34.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- mimo-v2-flash.aaIdx: winner={'value': 30.35, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-6-35b-moe.aaIdx: winner={'value': 43.25, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-6-35b-moe.aaCoding: winner={'value': 35.15, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-6-35b-moe.aaAgentic: winner={'value': 58.34, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- grok-4-3.aaAgentic: winner={'value': 65.89, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- grok-4-20.aaCoding: winner={'value': 40.45, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- grok-4-20.aaAgentic: winner={'value': 53.86, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gpt-5-4-nano.aaAgentic: winner={'value': 59.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- gemma-4-e4b.aaIdx: winner={'value': 18.92, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- mistral-medium-3-5.aaCoding: winner={'value': 33.12, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=yellow, ΔNone)
- opus-4-7.aaCoding: winner={'value': 52.88, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-06-06'} (severity=red, ΔNone)
- qwen3-6-plus.aaAgentic: winner={'value': 61.67, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-06-06'} (severity=red, ΔNone)

### Gaps (429 entries — agent:407 orchestrator:22 — see data/known-gaps.json or next refresh)
- `opus-4-7.tau2` *(agent)*: agent surveyed; value unavailable
- `opus-4-7.cfElo` *(agent)*: agent surveyed; value unavailable
- `opus-4-7.nl2Repo` *(agent)*: agent surveyed; value unavailable
- `opus-4-7.tbHard` *(agent)*: agent surveyed; value unavailable
- `sonnet-4-6.cfElo` *(agent)*: agent surveyed; value unavailable
- `sonnet-4-6.nl2Repo` *(agent)*: agent surveyed; value unavailable
- `gemma-4-26b-moe.aaCoding` *(orchestrator)*: not reached in agent survey cycle; AA Coding data unavailable
- `gpt-5-4-nano.arcAgi2` *(orchestrator)*: not reached in agent survey cycle; ARC-AGI-2 data unavailable
- ... and 421 more

## [2026-05-30] — autonomous refresh-all [WARN: cumulative provenance coverage 57.0% below 85% target] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 521 new fills; 5 cells auto-gapped by orchestrator; 492 explicit agent gaps preserved]

[fillRatio:0.57 cells:659/1156 contradictions:269 fetch:0.0min tools:None batches:None build:1ce6e7b]

### Added (lineup discovery)
- `claude-opus-4-8` (Anthropic, 2026-05-28) — sweV 88.6, gpqa 93.6, tb2 74.6; API $5/$25 per 1M; 200K ctx
- `gpt-5-4-mini` (OpenAI, 2026-03-17) — gpqa 88.0, tb2 60.0; 400K ctx
- `gpt-5-4-nano` (OpenAI, 2026-03-17) — gpqa 82.8, tb2 46.3; 400K ctx
- `mistral-small-4` (Mistral AI) — Apache-2.0, 256K ctx; bench coverage partial (data-sparse this cycle)
- `nemotron-3-nano-omni` (NVIDIA, 2026-04-28) — open-weight multimodal nano; gpqa 72.2; 128K ctx

### Flagged (data integrity)
- Stage-B synth traceability gate caught 1 fabricated value → auto-fell-back to deterministic local-synth (529 grounded fills from 839 gather observations)
- Removed 5 misfiled `cfElo` cells (Elo-trap: value sourced from a webDevElo publisher, not Codeforces) → re-queued as gaps
- Anomaly resolution (Layer-3 loop): 17 outliers confirmed as genuine (e.g. o4-mini.arcAgi2=2.3, codestral-22b.gpqa=6.5, gpt-5-4-mini.aime26=6.67 raw-count scale), 5 uncorroborated/misfiled cells cleared (gpt-4-1.aime26, mistral-large-3.aime26, devstral-2.tau2/aime26, grok-4-3.lcb)
- Lineup: 8 vendor-flagged deprecations already marked deprecated; `deepseek-v3-2` left active (weak single-source deprecation claim — re-verify next cycle)

### Updated
- 23 models: `gpt-5-5`, `glm-4-5-air`, `qwen3-6-27b`, `qwen3-32b`, `gemini-3-1-flash`, `qwen3-6-35b-moe`, `deepseek-v4-flash`, `minimax-m2-1`, `deepseek-v4-pro`, `gemma-4-e4b`, `qwen25-coder-7b`, `gemma-4-26b-moe`, `opus-4-7`, `nemotron-3-super`, `mimo-v2-5-pro`, `mistral-large-3`, `minimax-m2-7`, `qwen3-6-plus`, `glm-4-7`, `qwen3-235b`, `qwen3-5-9b`, `qwen3-7-max`, `deepseek-coder-v2-16b`

### Resolved (auto via trustScore)
- opus-4-7.sweV: winner={'value': 87.51, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- opus-4-7.swePro: winner={'value': 64.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- opus-4-7.tb2: winner={'value': 69.11, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- opus-4-7.gpqa: winner={'value': 94.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- opus-4-7.hle: winner={'value': 46.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- opus-4-7.mmluPro: winner={'value': 89.87, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- opus-4-7.aime26: winner={'value': 95.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- opus-4-7.arcAgi2: winner={'value': 75.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- sonnet-4-6.sweV: winner={'value': 79.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- sonnet-4-6.swePro: winner={'value': 40.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- sonnet-4-6.tb2: winner={'value': 58.95, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- sonnet-4-6.gpqa: winner={'value': 74.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 14, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- sonnet-4-6.hle: winner={'value': 51.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- sonnet-4-6.lcb: winner={'value': 80.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- sonnet-4-6.mmluPro: winner={'value': 79.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- sonnet-4-6.arcAgi2: winner={'value': 58.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- claude-haiku-4-5.sweV: winner={'value': 73.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v3-2.sweV: winner={'value': 67.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v3-2.gpqa: winner={'value': 82.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v3-2.lcb: winner={'value': 74.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v3-2.hle: winner={'value': 24.91, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.mmluPro: winner={'value': 85.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v3-2.cfElo: winner={'value': 2121.0, 'trustScore': 0.35, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-flash.sweV: winner={'value': 79.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-flash.swePro: winner={'value': 52.3, 'trustScore': 0.4603, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-flash.lcb: winner={'value': 91.43, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-flash.gpqa: winner={'value': 88.36, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-flash.hle: winner={'value': 22.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v4-flash.mmluPro: winner={'value': 86.33, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-pro.sweV: winner={'value': 80.57, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-pro.swePro: winner={'value': 55.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-pro.lcb: winner={'value': 93.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-pro.gpqa: winner={'value': 90.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-pro.hle: winner={'value': 37.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-pro.tb2: winner={'value': 67.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-pro.aaIdx: winner={'value': 52.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-coder-v2-16b.sweV: winner={'value': 43.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-coder-v2-16b.lcb: winner={'value': 43.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-r1-14b.gpqa: winner={'value': 59.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-r1-14b.sweV: winner={'value': 43.2, 'trustScore': 0.4588, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- gemini-3-1-flash.sweV: winner={'value': 78.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-flash.gpqa: winner={'value': 89.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-flash.lcb: winner={'value': 90.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-flash.aaIdx: winner={'value': 71.0, 'trustScore': 0.4801, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-flash.mmluPro: winner={'value': 89.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-flash.aime26: winner={'value': 97.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-flash.tau2: winner={'value': 71.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-flash.hle: winner={'value': 35.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-pro.swePro: winner={'value': 54.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-pro.gpqa: winner={'value': 94.24, 'trustScore': 0.5, 'tier': 'I', 'verifications': 17, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-pro.lcb: winner={'value': 91.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- gemini-3-1-pro.hle: winner={'value': 44.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-pro.tau2: winner={'value': 76.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-pro.aaIdx: winner={'value': 57.02, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- gemini-3-1-pro.mmluPro: winner={'value': 90.99, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- gemma-3-27b.gpqa: winner={'value': 42.46, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-26b-moe.gpqa: winner={'value': 82.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-26b-moe.tau2: winner={'value': 86.4, 'trustScore': 0.3399, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-26b-moe.hle: winner={'value': 22.0, 'trustScore': 0.4629, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- gemma-4-26b-moe.aaIdx: winner={'value': 31.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-31b.gpqa: winner={'value': 84.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-31b.lcb: winner={'value': 80.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 17, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-31b.tau2: winner={'value': 86.4, 'trustScore': 0.4457, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-31b.sweV: winner={'value': 64.0, 'trustScore': 0.3736, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-31b.hle: winner={'value': 23.0, 'trustScore': 0.4629, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- gemma-4-e2b.gpqa: winner={'value': 43.4, 'trustScore': 0.3399, 'tier': 'S', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-e2b.aime26: winner={'value': 37.5, 'trustScore': 0.3833, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-e4b.gpqa: winner={'value': 58.6, 'trustScore': 0.3399, 'tier': 'S', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-e4b.mmluPro: winner={'value': 69.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-e4b.aaIdx: winner={'value': 15.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- gemini-3-5-flash.sweV: winner={'value': 81.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-5-flash.gpqa: winner={'value': 92.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- minimax-m2-5.sweV: winner={'value': 80.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 16, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-5.gpqa: winner={'value': 84.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 14, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-5.hle: winner={'value': 19.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-5.aime26: winner={'value': 88.75, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-5.lcb: winner={'value': 76.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-5.mmluPro: winner={'value': 74.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-5.tb2: winner={'value': 52.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.swePro: winner={'value': 56.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-7.sweV: winner={'value': 78.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-7.tb2: winner={'value': 57.0, 'trustScore': 0.3894, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-7.gpqa: winner={'value': 87.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-7.hle: winner={'value': 28.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.mmluPro: winner={'value': 82.0, 'trustScore': 0.334, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- minimax-m2-7.lcb: winner={'value': 80.07, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- minimax-m2-7.tau2: winner={'value': 84.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.aime26: winner={'value': 78.3, 'trustScore': 0.334, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-7.tbHard: winner={'value': 39.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-1.sweV: winner={'value': 74.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- minimax-m2-1.gpqa: winner={'value': 82.87, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- minimax-m2-1.hle: winner={'value': 17.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- minimax-m2-1.lcb: winner={'value': 86.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-1.tau2: winner={'value': 87.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-1.swePro: winner={'value': 36.81, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mistral-large-3.sweV: winner={'value': 55.34, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mistral-large-3.gpqa: winner={'value': 43.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mistral-large-3.aaIdx: winner={'value': 23.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mistral-medium-3-5.sweV: winner={'value': 77.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- devstral-2.sweV: winner={'value': 72.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- devstral-2.gpqa: winner={'value': 59.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- devstral-2.lcb: winner={'value': 44.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- devstral-2.aaIdx: winner={'value': 62.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- devstral-medium.sweV: winner={'value': 61.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- devstral-medium.lcb: winner={'value': 33.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- devstral-small-2.sweV: winner={'value': 68.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- devstral-small-2.tb2: winner={'value': 32.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- codestral.sweV: winner={'value': 76.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- codestral-22b.gpqa: winner={'value': 6.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-5.sweV: winner={'value': 88.59, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-5.swePro: winner={'value': 58.51, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-5.hle: winner={'value': 41.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-5.tb2: winner={'value': 82.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-5.aaIdx: winner={'value': 60.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-5.mrcr: winner={'value': 74.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-5.mmluPro: winner={'value': 92.35, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- gpt-5-5.aime26: winner={'value': 87.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-4.swePro: winner={'value': 58.41, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-4.gpqa: winner={'value': 92.31, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- gpt-5-4.hle: winner={'value': 39.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- gpt-5-4.tau2: winner={'value': 92.8, 'trustScore': 0.4772, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- gpt-5-4.lcb: winner={'value': 85.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gpt-5-4.sweV: winner={'value': 78.88, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o3.swePro: winner={'value': 78.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- o3.gpqa: winner={'value': 87.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- o3.lcb: winner={'value': 75.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o3.aime26: winner={'value': 88.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- o3.cfElo: winner={'value': 2727.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- o3.arcAgi2: winner={'value': 87.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- o4-mini.swePro: winner={'value': 65.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- o4-mini.lcb: winner={'value': 80.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o4-mini.aime26: winner={'value': 92.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- o4-mini.hle: winner={'value': 71.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-4-1.sweV: winner={'value': 54.61, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-4-1.gpqa: winner={'value': 66.43, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-4-1.lcb: winner={'value': 68.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-4-1.aaIdx: winner={'value': 71.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-27b.sweV: winner={'value': 77.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-27b.gpqa: winner={'value': 87.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-27b.lcb: winner={'value': 83.9, 'trustScore': 0.4334, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-35b-moe.tb2: winner={'value': 51.5, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-35b-moe.gpqa: winner={'value': 86.0, 'trustScore': 0.35, 'tier': 'S', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-35b-moe.lcb: winner={'value': 80.4, 'trustScore': 0.4334, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- qwen3-6-35b-moe.hle: winner={'value': 79.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- qwen3-6-max.sweV: winner={'value': 70.88, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-max.tb2: winner={'value': 65.4, 'trustScore': 0.4582, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- qwen3-6-max.gpqa: winner={'value': 86.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- qwen3-6-max.hle: winner={'value': 51.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-6-max.tau2: winner={'value': 80.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-6-max.lcb: winner={'value': 77.5, 'trustScore': 0.4582, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-plus.sweV: winner={'value': 78.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-plus.aime26: winner={'value': 75.3, 'trustScore': 0.4582, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-plus.mmluPro: winner={'value': 88.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- qwen3-6-plus.aaIdx: winner={'value': 74.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-235b.sweV: winner={'value': 79.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-235b.tb2: winner={'value': 65.0, 'trustScore': 0.4504, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-235b.gpqa: winner={'value': 81.1, 'trustScore': 0.3789, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-235b.aime26: winner={'value': 92.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-235b.hle: winner={'value': 42.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-235b.lcb: winner={'value': 74.46, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-235b.mmluPro: winner={'value': 84.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- qwen3-235b.cfElo: winner={'value': 2056.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-32b.sweV: winner={'value': 72.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-32b.tb2: winner={'value': 56.3, 'trustScore': 0.4588, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-32b.gpqa: winner={'value': 66.67, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-32b.aime26: winner={'value': 81.23, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-32b.lcb: winner={'value': 54.54, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-32b.mmluPro: winner={'value': 79.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-32b.aaIdx: winner={'value': 76.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-coder-30b.sweV: winner={'value': 51.25, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-coder-30b.lcb: winner={'value': 56.3, 'trustScore': 0.4334, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-coder-480b.sweV: winner={'value': 69.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-coder-480b.swePro: winner={'value': 38.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-coder-next.sweV: winner={'value': 70.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-coder-next.swePro: winner={'value': 44.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-coder-next.tb2: winner={'value': 36.2, 'trustScore': 0.35, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-coder-next.lcb: winner={'value': 68.57, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen25-coder-7b.lcb: winner={'value': 37.6, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen25-coder-7b.sweV: winner={'value': 38.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-13'} (severity=red, ΔNone)
- qwen25-coder-14b.lcb: winner={'value': 37.6, 'trustScore': 0.4457, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- qwen25-coder-14b.sweV: winner={'value': 27.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen25-coder-32b.lcb: winner={'value': 48.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-5-9b.lcb: winner={'value': 65.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-5-9b.tau2: winner={'value': 86.7, 'trustScore': 0.2, 'tier': 'C', 'verifications': 1, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- qwen3-7-max.gpqa: winner={'value': 92.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- qwen3-7-max.hle: winner={'value': 41.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-7-max.sweV: winner={'value': 80.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-7-max.lcb: winner={'value': 90.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-7-plus.gpqa: winner={'value': 92.4, 'trustScore': 0.2, 'tier': 'C', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- grok-3.gpqa: winner={'value': 84.23, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-3.lcb: winner={'value': 79.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-3.aime26: winner={'value': 93.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-3.sweV: winner={'value': 63.8, 'trustScore': 0.35, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3-mini.gpqa: winner={'value': 79.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- grok-3-mini.aime26: winner={'value': 95.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- grok-3-mini.lcb: winner={'value': 69.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-3-mini.aaIdx: winner={'value': 32.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-20.gpqa: winner={'value': 87.99, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-20.hle: winner={'value': 24.24, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-20.sweV: winner={'value': 77.09, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-20.tau2: winner={'value': 93.0, 'trustScore': 0.4582, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-20.aaIdx: winner={'value': 49.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-20.lcb: winner={'value': 79.32, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-20.aime26: winner={'value': 95.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-3.gpqa: winner={'value': 90.07, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-3.hle: winner={'value': 53.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-3.sweV: winner={'value': 79.44, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-3.aime26: winner={'value': 95.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-1-fast.gpqa: winner={'value': 85.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-1-fast.hle: winner={'value': 17.6, 'trustScore': 0.4629, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-1-fast.mmluPro: winner={'value': 85.4, 'trustScore': 0.4632, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-1-fast.lcb: winner={'value': 82.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-1-fast.tbHard: winner={'value': 24.2, 'trustScore': 0.2552, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-04-30'} (severity=red, ΔNone)
- grok-4-1-fast.tau2: winner={'value': 72.8, 'trustScore': 0.4582, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-1-fast.aaIdx: winner={'value': 38.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-1-fast.sweV: winner={'value': 56.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-4-1-fast.aime26: winner={'value': 92.0, 'trustScore': 0.4582, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-flash.gpqa: winner={'value': 83.81, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-flash.lcb: winner={'value': 80.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-flash.tb2: winner={'value': 38.5, 'trustScore': 0.4588, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-flash.hle: winner={'value': 22.1, 'trustScore': 0.35, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-flash.aime26: winner={'value': 94.1, 'trustScore': 0.3828, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-pro.sweV: winner={'value': 78.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-pro.gpqa: winner={'value': 87.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- mimo-v2-pro.tb2: winner={'value': 86.7, 'trustScore': 0.4582, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- mimo-v2-5-pro.gpqa: winner={'value': 66.7, 'trustScore': 0.35, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-5-pro.hle: winner={'value': 33.86, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-5-pro.lcb: winner={'value': 76.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- mimo-v2-5-pro.tau2: winner={'value': 72.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mimo-v2-5-pro.mmluPro: winner={'value': 68.5, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-5-pro.aaAgentic: winner={'value': 68.7, 'trustScore': 0.4582, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- glm-5-1.swePro: winner={'value': 58.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 14, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-5-1.gpqa: winner={'value': 86.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-5-1.hle: winner={'value': 52.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-5-1.tau2: winner={'value': 89.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-5-1.sweV: winner={'value': 77.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-5-1.aaIdx: winner={'value': 51.0, 'trustScore': 0.4457, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-7.sweV: winner={'value': 73.74, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-7.gpqa: winner={'value': 85.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-7.tau2: winner={'value': 87.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- glm-4-7.aaIdx: winner={'value': 42.0, 'trustScore': 0.4801, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-5-air.sweV: winner={'value': 57.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-5-air.gpqa: winner={'value': 79.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-5-air.aime26: winner={'value': 89.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-5-air.hle: winner={'value': 14.4, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-5-air.tau2: winner={'value': 78.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-5-air.lcb: winner={'value': 72.9, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- llama-4-maverick.gpqa: winner={'value': 69.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- llama-4-maverick.lcb: winner={'value': 43.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- llama-4-maverick.sweV: winner={'value': 76.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- llama-4-scout.gpqa: winner={'value': 57.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- llama-4-scout.lcb: winner={'value': 32.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- llama-4-scout.mmluPro: winner={'value': 74.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- llama-4-scout.aime26: winner={'value': 78.4, 'trustScore': 0.3833, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- kimi-k2-6.sweV: winner={'value': 80.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- kimi-k2-6.swePro: winner={'value': 58.6, 'trustScore': 0.4603, 'tier': 'I', 'verifications': 16, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- kimi-k2-6.gpqa: winner={'value': 90.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- kimi-k2-6.hle: winner={'value': 54.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- kimi-k2-6.lcb: winner={'value': 89.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- kimi-k2-6.tb2: winner={'value': 66.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- kimi-k2-6.tau2: winner={'value': 70.6, 'trustScore': 0.4772, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- nemotron-3-super.sweV: winner={'value': 60.47, 'trustScore': 0.5, 'tier': 'I', 'verifications': 17, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- nemotron-3-super.gpqa: winner={'value': 79.24, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- nemotron-3-super.lcb: winner={'value': 81.13, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- nemotron-3-super.tbHard: winner={'value': 29.0, 'trustScore': 0.3894, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-22'} (severity=yellow, ΔNone)
- nemotron-3-nano-omni.gpqa: winner={'value': 72.2, 'trustScore': 0.4504, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- nemotron-3-nano-omni.tau2: winner={'value': 42.7, 'trustScore': 0.4504, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- step-3-5-flash.sweV: winner={'value': 74.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- step-3-5-flash.tb2: winner={'value': 51.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)

### Gaps (497 entries — agent:306 orchestrator:191 — see data/known-gaps.json or next refresh)
- `claude-opus-4-8.lcb` *(agent)*: agent surveyed; value unavailable
- `claude-opus-4-8.tau2` *(agent)*: agent surveyed; value unavailable
- `claude-opus-4-8.mmluPro` *(agent)*: agent surveyed; value unavailable
- `claude-opus-4-8.cfElo` *(agent)*: agent surveyed; value unavailable
- `claude-opus-4-8.arcAgi2` *(agent)*: agent surveyed; value unavailable
- `claude-opus-4-8.mrcr` *(agent)*: agent surveyed; value unavailable
- `codestral.aaAgentic` *(orchestrator)*: not reached in agent survey cycle; AA Agentic data unavailable
- `codestral.aaCoding` *(orchestrator)*: not reached in agent survey cycle; AA Coding data unavailable
- ... and 489 more


## [2026-05-30] — autonomous refresh-all [WARN: cumulative provenance coverage 57.4% below 85% target] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 524 new fills; 186 cells auto-gapped by orchestrator; 412 explicit agent gaps preserved]

[fillRatio:0.57 cells:664/1156 contradictions:269 fetch:0.0min tools:None batches:None build:1ce6e7b]

### Updated
- 53 models: `gpt-5-5`, `gemini-3-1-pro`, `glm-4-5-air`, `nemotron-3-nano-omni`, `qwen3-32b`, `minimax-m2-5`, `gemini-3-1-flash`, `llama-4-maverick`, `codestral-22b`, `grok-4-20`, `qwen3-6-35b-moe`, `mimo-v2-flash`, `mistral-small-4`, `gpt-5-4`, `deepseek-v4-flash`, `minimax-m2-1`, `deepseek-v4-pro`, `qwen3-6-max`, `claude-opus-4-8`, `gemma-4-e4b`, `qwen25-coder-14b`, `qwen25-coder-7b`, `gemma-4-26b-moe`, `qwen3-coder-next`, `grok-4-1-fast`, `gemini-3-5-flash`, `opus-4-7`, `nemotron-3-super`, `gpt-5-4-nano`, `mimo-v2-5-pro`, `sonnet-4-6`, `claude-haiku-4-5`, `deepseek-v3-2`, `gpt-5-4-mini`, `gpt-4-1`, `minimax-m2-7`, `gemma-3-27b`, `mimo-v2-pro`, `devstral-medium`, `qwen25-coder-32b`, `qwen3-7-plus`, `devstral-2`, `grok-3-mini`, `glm-4-7`, `qwen3-coder-30b`, `qwen3-235b`, `qwen3-5-9b`, `grok-4-3`, `grok-3`, `gemma-4-e2b`, `deepseek-r1-14b`, `qwen3-7-max`, `devstral-small-2`

### Resolved (auto via trustScore)
- opus-4-7.sweV: winner={'value': 87.51, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- opus-4-7.swePro: winner={'value': 64.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- opus-4-7.tb2: winner={'value': 69.11, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- opus-4-7.gpqa: winner={'value': 94.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- opus-4-7.hle: winner={'value': 46.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- opus-4-7.mmluPro: winner={'value': 89.87, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- opus-4-7.aime26: winner={'value': 95.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- opus-4-7.arcAgi2: winner={'value': 75.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- sonnet-4-6.sweV: winner={'value': 79.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- sonnet-4-6.swePro: winner={'value': 40.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- sonnet-4-6.tb2: winner={'value': 58.95, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- sonnet-4-6.gpqa: winner={'value': 74.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 14, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- sonnet-4-6.hle: winner={'value': 51.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- sonnet-4-6.lcb: winner={'value': 80.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- sonnet-4-6.mmluPro: winner={'value': 79.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- sonnet-4-6.arcAgi2: winner={'value': 58.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- claude-haiku-4-5.sweV: winner={'value': 73.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v3-2.sweV: winner={'value': 67.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v3-2.gpqa: winner={'value': 82.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v3-2.lcb: winner={'value': 74.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v3-2.hle: winner={'value': 24.91, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.mmluPro: winner={'value': 85.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v3-2.cfElo: winner={'value': 2121.0, 'trustScore': 0.35, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-flash.sweV: winner={'value': 79.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-flash.swePro: winner={'value': 52.3, 'trustScore': 0.4603, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-flash.lcb: winner={'value': 91.43, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-flash.gpqa: winner={'value': 88.36, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-flash.hle: winner={'value': 22.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v4-flash.mmluPro: winner={'value': 86.33, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-pro.sweV: winner={'value': 80.57, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-pro.swePro: winner={'value': 55.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-pro.lcb: winner={'value': 93.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-pro.gpqa: winner={'value': 90.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-pro.hle: winner={'value': 37.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-pro.tb2: winner={'value': 67.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-v4-pro.aaIdx: winner={'value': 52.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-coder-v2-16b.sweV: winner={'value': 43.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-coder-v2-16b.lcb: winner={'value': 43.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-r1-14b.gpqa: winner={'value': 59.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- deepseek-r1-14b.sweV: winner={'value': 43.2, 'trustScore': 0.4588, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- gemini-3-1-flash.sweV: winner={'value': 78.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-flash.gpqa: winner={'value': 89.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-flash.lcb: winner={'value': 90.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-flash.aaIdx: winner={'value': 71.0, 'trustScore': 0.4801, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-flash.mmluPro: winner={'value': 89.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-flash.aime26: winner={'value': 97.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-flash.tau2: winner={'value': 71.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-flash.hle: winner={'value': 35.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-pro.swePro: winner={'value': 54.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-pro.gpqa: winner={'value': 94.24, 'trustScore': 0.5, 'tier': 'I', 'verifications': 17, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-pro.lcb: winner={'value': 91.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- gemini-3-1-pro.hle: winner={'value': 44.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-pro.tau2: winner={'value': 76.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-1-pro.aaIdx: winner={'value': 57.02, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- gemini-3-1-pro.mmluPro: winner={'value': 90.99, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- gemma-3-27b.gpqa: winner={'value': 42.46, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-26b-moe.gpqa: winner={'value': 82.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-26b-moe.tau2: winner={'value': 86.4, 'trustScore': 0.3399, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-26b-moe.hle: winner={'value': 22.0, 'trustScore': 0.4629, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- gemma-4-26b-moe.aaIdx: winner={'value': 31.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-31b.gpqa: winner={'value': 84.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-31b.lcb: winner={'value': 80.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 17, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-31b.tau2: winner={'value': 86.4, 'trustScore': 0.4457, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-31b.sweV: winner={'value': 64.0, 'trustScore': 0.3736, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-31b.hle: winner={'value': 23.0, 'trustScore': 0.4629, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- gemma-4-e2b.gpqa: winner={'value': 43.4, 'trustScore': 0.3399, 'tier': 'S', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-e2b.aime26: winner={'value': 37.5, 'trustScore': 0.3833, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-e4b.gpqa: winner={'value': 58.6, 'trustScore': 0.3399, 'tier': 'S', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-e4b.mmluPro: winner={'value': 69.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemma-4-e4b.aaIdx: winner={'value': 15.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- gemini-3-5-flash.sweV: winner={'value': 81.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gemini-3-5-flash.gpqa: winner={'value': 92.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- minimax-m2-5.sweV: winner={'value': 80.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 16, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-5.gpqa: winner={'value': 84.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 14, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-5.hle: winner={'value': 19.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-5.aime26: winner={'value': 88.75, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-5.lcb: winner={'value': 76.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-5.mmluPro: winner={'value': 74.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-5.tb2: winner={'value': 52.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.swePro: winner={'value': 56.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-7.sweV: winner={'value': 78.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-7.tb2: winner={'value': 57.0, 'trustScore': 0.3894, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-7.gpqa: winner={'value': 87.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-7.hle: winner={'value': 28.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.mmluPro: winner={'value': 82.0, 'trustScore': 0.334, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- minimax-m2-7.lcb: winner={'value': 80.07, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- minimax-m2-7.tau2: winner={'value': 84.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.aime26: winner={'value': 78.3, 'trustScore': 0.334, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-7.tbHard: winner={'value': 39.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-1.sweV: winner={'value': 74.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- minimax-m2-1.gpqa: winner={'value': 82.87, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- minimax-m2-1.hle: winner={'value': 17.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- minimax-m2-1.lcb: winner={'value': 86.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-1.tau2: winner={'value': 87.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- minimax-m2-1.swePro: winner={'value': 36.81, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mistral-large-3.sweV: winner={'value': 55.34, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mistral-large-3.gpqa: winner={'value': 43.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mistral-large-3.aaIdx: winner={'value': 23.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mistral-medium-3-5.sweV: winner={'value': 77.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- devstral-2.sweV: winner={'value': 72.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- devstral-2.gpqa: winner={'value': 59.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- devstral-2.lcb: winner={'value': 44.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- devstral-2.aaIdx: winner={'value': 62.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- devstral-medium.sweV: winner={'value': 61.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- devstral-medium.lcb: winner={'value': 33.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- devstral-small-2.sweV: winner={'value': 68.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- devstral-small-2.tb2: winner={'value': 32.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- codestral.sweV: winner={'value': 76.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- codestral-22b.gpqa: winner={'value': 6.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-5.sweV: winner={'value': 88.59, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-5.swePro: winner={'value': 58.51, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-5.hle: winner={'value': 41.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-5.tb2: winner={'value': 82.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-5.aaIdx: winner={'value': 60.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-5.mrcr: winner={'value': 74.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-5.mmluPro: winner={'value': 92.35, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- gpt-5-5.aime26: winner={'value': 87.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-4.swePro: winner={'value': 58.41, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-5-4.gpqa: winner={'value': 92.31, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- gpt-5-4.hle: winner={'value': 39.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- gpt-5-4.tau2: winner={'value': 92.8, 'trustScore': 0.4772, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- gpt-5-4.lcb: winner={'value': 85.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gpt-5-4.sweV: winner={'value': 78.88, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o3.swePro: winner={'value': 78.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- o3.gpqa: winner={'value': 87.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- o3.lcb: winner={'value': 75.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o3.aime26: winner={'value': 88.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- o3.cfElo: winner={'value': 2727.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- o3.arcAgi2: winner={'value': 87.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- o4-mini.swePro: winner={'value': 65.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- o4-mini.lcb: winner={'value': 80.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o4-mini.aime26: winner={'value': 92.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- o4-mini.hle: winner={'value': 71.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-4-1.sweV: winner={'value': 54.61, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-4-1.gpqa: winner={'value': 66.43, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-4-1.lcb: winner={'value': 68.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- gpt-4-1.aaIdx: winner={'value': 71.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-27b.sweV: winner={'value': 77.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-27b.gpqa: winner={'value': 87.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-27b.lcb: winner={'value': 83.9, 'trustScore': 0.4334, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-35b-moe.tb2: winner={'value': 51.5, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-35b-moe.gpqa: winner={'value': 86.0, 'trustScore': 0.35, 'tier': 'S', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-35b-moe.lcb: winner={'value': 80.4, 'trustScore': 0.4334, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- qwen3-6-35b-moe.hle: winner={'value': 79.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- qwen3-6-max.sweV: winner={'value': 70.88, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-max.tb2: winner={'value': 65.4, 'trustScore': 0.4582, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- qwen3-6-max.gpqa: winner={'value': 86.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- qwen3-6-max.hle: winner={'value': 51.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-6-max.tau2: winner={'value': 80.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-6-max.lcb: winner={'value': 77.5, 'trustScore': 0.4582, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-plus.sweV: winner={'value': 78.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-plus.aime26: winner={'value': 75.3, 'trustScore': 0.4582, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-6-plus.mmluPro: winner={'value': 88.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- qwen3-6-plus.aaIdx: winner={'value': 74.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-235b.sweV: winner={'value': 79.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-235b.tb2: winner={'value': 65.0, 'trustScore': 0.4504, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-235b.gpqa: winner={'value': 81.1, 'trustScore': 0.3789, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-235b.aime26: winner={'value': 92.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-235b.hle: winner={'value': 42.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-235b.lcb: winner={'value': 74.46, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-235b.mmluPro: winner={'value': 84.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- qwen3-235b.cfElo: winner={'value': 2056.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-32b.sweV: winner={'value': 72.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-32b.tb2: winner={'value': 56.3, 'trustScore': 0.4588, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-32b.gpqa: winner={'value': 66.67, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-32b.aime26: winner={'value': 81.23, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-32b.lcb: winner={'value': 54.54, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-32b.mmluPro: winner={'value': 79.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-32b.aaIdx: winner={'value': 76.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-coder-30b.sweV: winner={'value': 51.25, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-coder-30b.lcb: winner={'value': 56.3, 'trustScore': 0.4334, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-coder-480b.sweV: winner={'value': 69.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-coder-480b.swePro: winner={'value': 38.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-coder-next.sweV: winner={'value': 70.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-coder-next.swePro: winner={'value': 44.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-coder-next.tb2: winner={'value': 36.2, 'trustScore': 0.35, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-coder-next.lcb: winner={'value': 68.57, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen25-coder-7b.lcb: winner={'value': 37.6, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen25-coder-7b.sweV: winner={'value': 38.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-13'} (severity=red, ΔNone)
- qwen25-coder-14b.lcb: winner={'value': 37.6, 'trustScore': 0.4457, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- qwen25-coder-14b.sweV: winner={'value': 27.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen25-coder-32b.lcb: winner={'value': 48.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-5-9b.lcb: winner={'value': 65.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-5-9b.tau2: winner={'value': 86.7, 'trustScore': 0.2, 'tier': 'C', 'verifications': 1, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- qwen3-7-max.gpqa: winner={'value': 92.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- qwen3-7-max.hle: winner={'value': 41.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-7-max.sweV: winner={'value': 80.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-7-max.lcb: winner={'value': 90.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- qwen3-7-plus.gpqa: winner={'value': 92.4, 'trustScore': 0.2, 'tier': 'C', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- grok-3.gpqa: winner={'value': 84.23, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-3.lcb: winner={'value': 79.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-3.aime26: winner={'value': 93.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-3.sweV: winner={'value': 63.8, 'trustScore': 0.35, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3-mini.gpqa: winner={'value': 79.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- grok-3-mini.aime26: winner={'value': 95.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- grok-3-mini.lcb: winner={'value': 69.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-3-mini.aaIdx: winner={'value': 32.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-20.gpqa: winner={'value': 87.99, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-20.hle: winner={'value': 24.24, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-20.sweV: winner={'value': 77.09, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-20.tau2: winner={'value': 93.0, 'trustScore': 0.4582, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-20.aaIdx: winner={'value': 49.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-20.lcb: winner={'value': 79.32, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-20.aime26: winner={'value': 95.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-3.gpqa: winner={'value': 90.07, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-3.hle: winner={'value': 53.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-3.sweV: winner={'value': 79.44, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-3.aime26: winner={'value': 95.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-1-fast.gpqa: winner={'value': 85.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-1-fast.hle: winner={'value': 17.6, 'trustScore': 0.4629, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-1-fast.mmluPro: winner={'value': 85.4, 'trustScore': 0.4632, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-1-fast.lcb: winner={'value': 82.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-1-fast.tbHard: winner={'value': 24.2, 'trustScore': 0.2552, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-04-30'} (severity=red, ΔNone)
- grok-4-1-fast.tau2: winner={'value': 72.8, 'trustScore': 0.4582, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-1-fast.aaIdx: winner={'value': 38.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- grok-4-1-fast.sweV: winner={'value': 56.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-4-1-fast.aime26: winner={'value': 92.0, 'trustScore': 0.4582, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-flash.gpqa: winner={'value': 83.81, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-flash.lcb: winner={'value': 80.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-flash.tb2: winner={'value': 38.5, 'trustScore': 0.4588, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-flash.hle: winner={'value': 22.1, 'trustScore': 0.35, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-flash.aime26: winner={'value': 94.1, 'trustScore': 0.3828, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-pro.sweV: winner={'value': 78.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-pro.gpqa: winner={'value': 87.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- mimo-v2-pro.tb2: winner={'value': 86.7, 'trustScore': 0.4582, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- mimo-v2-5-pro.gpqa: winner={'value': 66.7, 'trustScore': 0.35, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-5-pro.hle: winner={'value': 33.86, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-5-pro.lcb: winner={'value': 76.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- mimo-v2-5-pro.tau2: winner={'value': 72.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mimo-v2-5-pro.mmluPro: winner={'value': 68.5, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- mimo-v2-5-pro.aaAgentic: winner={'value': 68.7, 'trustScore': 0.4582, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- glm-5-1.swePro: winner={'value': 58.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 14, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-5-1.gpqa: winner={'value': 86.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-5-1.hle: winner={'value': 52.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-5-1.tau2: winner={'value': 89.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-5-1.sweV: winner={'value': 77.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-5-1.aaIdx: winner={'value': 51.0, 'trustScore': 0.4457, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-7.sweV: winner={'value': 73.74, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-7.gpqa: winner={'value': 85.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-7.tau2: winner={'value': 87.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- glm-4-7.aaIdx: winner={'value': 42.0, 'trustScore': 0.4801, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-5-air.sweV: winner={'value': 57.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-5-air.gpqa: winner={'value': 79.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-5-air.aime26: winner={'value': 89.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-5-air.hle: winner={'value': 14.4, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-5-air.tau2: winner={'value': 78.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- glm-4-5-air.lcb: winner={'value': 72.9, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- llama-4-maverick.gpqa: winner={'value': 69.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- llama-4-maverick.lcb: winner={'value': 43.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- llama-4-maverick.sweV: winner={'value': 76.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- llama-4-scout.gpqa: winner={'value': 57.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- llama-4-scout.lcb: winner={'value': 32.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- llama-4-scout.mmluPro: winner={'value': 74.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- llama-4-scout.aime26: winner={'value': 78.4, 'trustScore': 0.3833, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- kimi-k2-6.sweV: winner={'value': 80.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- kimi-k2-6.swePro: winner={'value': 58.6, 'trustScore': 0.4603, 'tier': 'I', 'verifications': 16, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- kimi-k2-6.gpqa: winner={'value': 90.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- kimi-k2-6.hle: winner={'value': 54.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- kimi-k2-6.lcb: winner={'value': 89.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- kimi-k2-6.tb2: winner={'value': 66.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- kimi-k2-6.tau2: winner={'value': 70.6, 'trustScore': 0.4772, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- nemotron-3-super.sweV: winner={'value': 60.47, 'trustScore': 0.5, 'tier': 'I', 'verifications': 17, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- nemotron-3-super.gpqa: winner={'value': 79.24, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- nemotron-3-super.lcb: winner={'value': 81.13, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- nemotron-3-super.tbHard: winner={'value': 29.0, 'trustScore': 0.3894, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-22'} (severity=yellow, ΔNone)
- nemotron-3-nano-omni.gpqa: winner={'value': 72.2, 'trustScore': 0.4504, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- nemotron-3-nano-omni.tau2: winner={'value': 42.7, 'trustScore': 0.4504, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-30'} (severity=yellow, ΔNone)
- step-3-5-flash.sweV: winner={'value': 74.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-30'} (severity=red, ΔNone)
- step-3-5-flash.tb2: winner={'value': 51.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-30'} (severity=red, ΔNone)

### Gaps (492 entries — agent:306 orchestrator:186 — see data/known-gaps.json or next refresh)
- `claude-opus-4-8.lcb` *(agent)*: agent surveyed; value unavailable
- `claude-opus-4-8.tau2` *(agent)*: agent surveyed; value unavailable
- `claude-opus-4-8.mmluPro` *(agent)*: agent surveyed; value unavailable
- `claude-opus-4-8.cfElo` *(agent)*: agent surveyed; value unavailable
- `claude-opus-4-8.arcAgi2` *(agent)*: agent surveyed; value unavailable
- `claude-opus-4-8.mrcr` *(agent)*: agent surveyed; value unavailable
- `codestral.aaAgentic` *(orchestrator)*: not reached in agent survey cycle; AA Agentic data unavailable
- `codestral.aaCoding` *(orchestrator)*: not reached in agent survey cycle; AA Coding data unavailable
- ... and 484 more


## [2026-05-28] — refresh-all finalization (post-cycle integrity pass, no new fetch)

[fillRatio:0.5602 cells:600/1071 build:9b10bea — SSOT audit PASS (WARN-only)]

Consolidates the same-day remediation work layered on top of the morning
refresh-all commit (9b10bea). No new web fetches — this commit ships the
already-gathered, deduplicated, audit-passing working-tree state.

### Changed
- Core bench coverage 561 -> 600 filled cells (fillRatio 0.52 -> 0.5602).
- `data/sources.json` pseudo-source / SPA-citation purge (snapshot-extraction,
  auto-resolution-candidate, synth-backfill entries removed; pre-purge backups
  retained locally). ~3.8k provenance lines dropped, consensus de-noised.
- Bench universe trimmed: dead keys `programBench`, `tau3`, `simpleQa` removed
  from `BENCH_CATEGORIES`; `DEFAULT_WEIGHTS` / `PRESETS` rebalanced toward
  high-coverage (>=70%) benches to avoid coverage-penalty distortion.
- Frontend render layer (`core.js`, `data.js`, `render-card.js`,
  `render-table.js`, `models.css`) synced to the rebalanced bench schema so
  `audit-data-coherence.py` invariants hold on the deployed tree
  (BENCH_KEYS <-> coreBenchKeys, weights subset of BENCH_KEYS).
- `verification-map` rebuilt; `_anomalies` + `_synth-traceability` regenerated.
- Pipeline tooling: stale one-shot migration scripts removed
  (`migrate-*`, `strip-bench-key`); `merge.py` synth traceability gate +
  `validate-agent-out` / `agent-out.schema.json` refinements.

### Audit (WARN-only, no hard block)
- 1 plausibility-band outlier (`gemma-3-27b.cfElo=110.0`) — flagged for re-verify.
- 2 sibling-metric misfile suspects (`opus-4-7.cfElo`, `deepseek-v4-pro.cfElo`).
- MX5: 127 single-source cells (quarantine candidates) — next cycle adds 2nd source.
- MX6: 82 cells below `benchVerificationStrict` independent-source thresholds.

## [2026-05-28] — autonomous refresh-all [WARN: cumulative provenance coverage 52.4% below 85% target] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 351 new fills; 42 cells auto-gapped by orchestrator; 680 explicit agent gaps preserved]

[fillRatio:0.52 cells:561/1071 contradictions:208 fetch:0.0min tools:None batches:None build:9d1e71e]

### Updated
- 15 models: `mistral-large-3`, `minimax-m2-5`, `gpt-5-4`, `deepseek-v3-2`, `qwen3-6-plus`, `opus-4-7`, `nemotron-3-super`, `qwen3-7-max`, `gpt-5-5`, `mimo-v2-5-pro`, `mimo-v2-flash`, `qwen3-235b`, `qwen3-6-35b-moe`, `glm-5-1`, `sonnet-4-6`

### Resolved (auto via trustScore)
- opus-4-7.sweV: winner={'value': 87.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- opus-4-7.swePro: winner={'value': 64.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- opus-4-7.gpqa: winner={'value': 94.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- opus-4-7.hle: winner={'value': 46.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- opus-4-7.tb2: winner={'value': 69.11, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- opus-4-7.mmluPro: winner={'value': 89.87, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- sonnet-4-6.sweV: winner={'value': 79.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- sonnet-4-6.swePro: winner={'value': 40.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- sonnet-4-6.gpqa: winner={'value': 74.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 14, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- sonnet-4-6.hle: winner={'value': 51.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- sonnet-4-6.tb2: winner={'value': 58.87, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- sonnet-4-6.tau2: winner={'value': 91.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- sonnet-4-6.arcAgi2: winner={'value': 58.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- sonnet-4-6.lcb: winner={'value': 80.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- claude-haiku-4-5.sweV: winner={'value': 73.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- claude-haiku-4-5.gpqa: winner={'value': 67.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- claude-haiku-4-5.lcb: winner={'value': 61.5, 'trustScore': 0.4783, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- claude-haiku-4-5.tau2: winner={'value': 83.1, 'trustScore': 0.4778, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- deepseek-v3-2.sweV: winner={'value': 67.85, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.gpqa: winner={'value': 82.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.lcb: winner={'value': 74.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.hle: winner={'value': 24.76, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.mmluPro: winner={'value': 85.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.aime26: winner={'value': 89.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v3-2.cfElo: winner={'value': 2121.0, 'trustScore': 0.35, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v3-2.tb2: winner={'value': 46.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.aaIdx: winner={'value': 16.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v4-flash.sweV: winner={'value': 79.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-flash.lcb: winner={'value': 91.43, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-flash.gpqa: winner={'value': 88.36, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.sweV: winner={'value': 80.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.swePro: winner={'value': 55.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.lcb: winner={'value': 93.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.gpqa: winner={'value': 90.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.hle: winner={'value': 37.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.tb2: winner={'value': 67.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.aaIdx: winner={'value': 52.0, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- deepseek-coder-v2-16b.lcb: winner={'value': 43.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-coder-v2-16b.sweV: winner={'value': 43.0, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- deepseek-r1-14b.gpqa: winner={'value': 59.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-r1-14b.aime26: winner={'value': 70.08, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-r1-14b.mmluPro: winner={'value': 93.9, 'trustScore': 0.4507, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-flash.gpqa: winner={'value': 89.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-flash.hle: winner={'value': 34.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-flash.sweV: winner={'value': 78.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-flash.tau2: winner={'value': 71.5, 'trustScore': 0.4573, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- gemini-3-1-flash.lcb: winner={'value': 90.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-flash.mmluPro: winner={'value': 89.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-flash.aime26: winner={'value': 97.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-pro.gpqa: winner={'value': 94.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 15, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-pro.hle: winner={'value': 44.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-pro.aaIdx: winner={'value': 57.02, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- gemini-3-1-pro.mmluPro: winner={'value': 90.99, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- gemma-3-27b.gpqa: winner={'value': 42.46, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-26b-moe.gpqa: winner={'value': 82.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-31b.gpqa: winner={'value': 84.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-31b.lcb: winner={'value': 80.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 16, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-e2b.aime26: winner={'value': 37.5, 'trustScore': 0.35, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-e4b.aaIdx: winner={'value': 19.0, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- gemini-3-5-flash.gpqa: winner={'value': 92.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- gemini-3-5-flash.sweV: winner={'value': 81.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.sweV: winner={'value': 78.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.swePro: winner={'value': 56.22, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.tbHard: winner={'value': 39.4, 'trustScore': 0.4573, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.gpqa: winner={'value': 86.94, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.hle: winner={'value': 28.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.tau2: winner={'value': 84.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-5.sweV: winner={'value': 80.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-5.tb2: winner={'value': 52.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-5.gpqa: winner={'value': 85.11, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-5.lcb: winner={'value': 76.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-5.aime26: winner={'value': 88.75, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-5.mmluPro: winner={'value': 74.0, 'trustScore': 0.459, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-1.sweV: winner={'value': 74.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- minimax-m2-1.gpqa: winner={'value': 82.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- minimax-m2-1.hle: winner={'value': 17.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- minimax-m2-1.lcb: winner={'value': 86.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-1.tau2: winner={'value': 87.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mistral-large-3.gpqa: winner={'value': 43.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mistral-large-3.lcb: winner={'value': 82.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mistral-large-3.aaIdx: winner={'value': 23.0, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- codestral-22b.gpqa: winner={'value': 90.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- codestral-22b.swePro: winner={'value': 35.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- devstral-2.sweV: winner={'value': 72.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- devstral-2.gpqa: winner={'value': 59.4, 'trustScore': 0.4397, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- devstral-2.lcb: winner={'value': 44.8, 'trustScore': 0.4573, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- devstral-2.aaIdx: winner={'value': 62.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- devstral-medium.sweV: winner={'value': 61.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- devstral-small-2.sweV: winner={'value': 68.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mistral-medium-3-5.sweV: winner={'value': 77.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-4-1.sweV: winner={'value': 54.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-4-1.gpqa: winner={'value': 66.43, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-4-1.lcb: winner={'value': 68.2, 'trustScore': 0.4573, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- gpt-4-1.aaIdx: winner={'value': 26.0, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-4-1.mmluPro: winner={'value': 80.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- o3.sweV: winner={'value': 71.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o3.gpqa: winner={'value': 87.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- o3.hle: winner={'value': 20.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o3.lcb: winner={'value': 75.8, 'trustScore': 0.4783, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- o3.aime26: winner={'value': 88.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o3.cfElo: winner={'value': 2727.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o3.arcAgi2: winner={'value': 87.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- o4-mini.sweV: winner={'value': 68.19, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o4-mini.lcb: winner={'value': 80.2, 'trustScore': 0.434, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- o4-mini.aime26: winner={'value': 92.7, 'trustScore': 0.4573, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-4.sweV: winner={'value': 78.83, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-4.swePro: winner={'value': 57.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-4.gpqa: winner={'value': 92.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- gpt-5-4.hle: winner={'value': 39.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-22'} (severity=yellow, ΔNone)
- gpt-5-4.lcb: winner={'value': 85.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gpt-5-5.sweV: winner={'value': 88.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-5.swePro: winner={'value': 58.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-5.tb2: winner={'value': 82.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-5.hle: winner={'value': 41.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-5.mrcr: winner={'value': 74.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-5.aaIdx: winner={'value': 60.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-6-27b.sweV: winner={'value': 77.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-6-27b.gpqa: winner={'value': 87.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-6-max.sweV: winner={'value': 70.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-6-max.tb2: winner={'value': 65.4, 'trustScore': 0.35, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- qwen3-6-max.gpqa: winner={'value': 86.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- qwen3-6-max.hle: winner={'value': 51.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-6-max.tau2: winner={'value': 80.1, 'trustScore': 0.4778, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- qwen3-235b.aime26: winner={'value': 92.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-235b.gpqa: winner={'value': 81.1, 'trustScore': 0.35, 'tier': 'S', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-235b.hle: winner={'value': 42.0, 'trustScore': 0.4578, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- qwen3-235b.lcb: winner={'value': 74.49, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-235b.mmluPro: winner={'value': 84.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- qwen3-235b.cfElo: winner={'value': 2056.0, 'trustScore': 0.4507, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-32b.gpqa: winner={'value': 66.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-32b.mmluPro: winner={'value': 79.8, 'trustScore': 0.459, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-32b.aime26: winner={'value': 81.18, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-32b.lcb: winner={'value': 54.52, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-32b.aaIdx: winner={'value': 76.4, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- qwen3-6-35b-moe.gpqa: winner={'value': 86.0, 'trustScore': 0.35, 'tier': 'S', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-6-plus.sweV: winner={'value': 78.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-6-plus.mmluPro: winner={'value': 88.5, 'trustScore': 0.459, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- qwen3-6-plus.aaIdx: winner={'value': 74.8, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- qwen3-coder-30b.sweV: winner={'value': 51.38, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-coder-480b.sweV: winner={'value': 69.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-coder-480b.swePro: winner={'value': 38.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-coder-next.sweV: winner={'value': 70.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen25-coder-7b.lcb: winner={'value': 37.6, 'trustScore': 0.2505, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen25-coder-14b.sweV: winner={'value': 28.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen25-coder-32b.sweV: winner={'value': 69.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen25-coder-32b.lcb: winner={'value': 48.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-5-9b.lcb: winner={'value': 65.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-7-max.sweV: winner={'value': 80.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-7-max.gpqa: winner={'value': 92.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- qwen3-7-max.hle: winner={'value': 41.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3.gpqa: winner={'value': 84.6, 'trustScore': 0.4397, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3.lcb: winner={'value': 79.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3.sweV: winner={'value': 63.8, 'trustScore': 0.35, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3.aime26: winner={'value': 93.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3-mini.gpqa: winner={'value': 79.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- grok-3-mini.lcb: winner={'value': 80.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3-mini.aime26: winner={'value': 95.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- grok-3-mini.aaIdx: winner={'value': 32.02, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-4-20.aaIdx: winner={'value': 49.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-4-20.gpqa: winner={'value': 87.99, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-4-20.hle: winner={'value': 24.26, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-4-20.lcb: winner={'value': 79.32, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-4-20.aime26: winner={'value': 95.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- grok-4-20.sweV: winner={'value': 77.22, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-4-3.gpqa: winner={'value': 90.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-4-1-fast.aaIdx: winner={'value': 38.0, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- grok-4-1-fast.sweV: winner={'value': 56.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mimo-v2-5-pro.gpqa: winner={'value': 66.7, 'trustScore': 0.35, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mimo-v2-5-pro.hle: winner={'value': 33.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mimo-v2-5-pro.mmluPro: winner={'value': 68.5, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mimo-v2-5-pro.tau2: winner={'value': 72.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mimo-v2-flash.gpqa: winner={'value': 83.88, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mimo-v2-flash.lcb: winner={'value': 80.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mimo-v2-flash.aaIdx: winner={'value': 39.0, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-09'} (severity=yellow, ΔNone)
- mimo-v2-pro.sweV: winner={'value': 77.97, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mimo-v2-pro.gpqa: winner={'value': 87.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- glm-5-1.swePro: winner={'value': 58.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- glm-5-1.sweV: winner={'value': 77.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- glm-5-1.gpqa: winner={'value': 86.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- glm-5-1.hle: winner={'value': 52.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-5-1.tau2: winner={'value': 19.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-7.sweV: winner={'value': 73.74, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- glm-4-7.gpqa: winner={'value': 85.72, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- glm-4-7.tau2: winner={'value': 87.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- glm-4-5-air.sweV: winner={'value': 57.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- glm-4-5-air.gpqa: winner={'value': 79.1, 'trustScore': 0.4213, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-5-air.lcb: winner={'value': 72.9, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-5-air.hle: winner={'value': 14.4, 'trustScore': 0.3155, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-5-air.aime26: winner={'value': 89.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-5-air.tau2: winner={'value': 78.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- llama-4-maverick.gpqa: winner={'value': 69.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- llama-4-maverick.lcb: winner={'value': 43.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- llama-4-maverick.sweV: winner={'value': 76.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- llama-4-scout.gpqa: winner={'value': 57.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- llama-4-scout.lcb: winner={'value': 32.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- llama-4-scout.mmluPro: winner={'value': 74.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- llama-4-scout.sweV: winner={'value': 58.0, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- kimi-k2-6.sweV: winner={'value': 80.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- kimi-k2-6.tb2: winner={'value': 66.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- kimi-k2-6.lcb: winner={'value': 89.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- kimi-k2-6.gpqa: winner={'value': 90.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- kimi-k2-6.hle: winner={'value': 54.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- nemotron-3-super.sweV: winner={'value': 60.47, 'trustScore': 0.5, 'tier': 'I', 'verifications': 14, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- nemotron-3-super.gpqa: winner={'value': 79.26, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- nemotron-3-super.lcb: winner={'value': 81.08, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- step-3-5-flash.sweV: winner={'value': 74.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- step-3-5-flash.gpqa: winner={'value': 83.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- step-3-5-flash.tb2: winner={'value': 51.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)

### Gaps (510 entries — agent:468 orchestrator:42 — see data/known-gaps.json or next refresh)
- `opus-4-7.tau2` *(agent)*: agent surveyed; value unavailable
- `opus-4-7.tbHard` *(agent)*: agent surveyed; value unavailable
- `opus-4-7.nl2Repo` *(agent)*: agent surveyed; value unavailable
- `opus-4-7.aaAgentic` *(agent)*: agent surveyed; value unavailable
- `opus-4-7.cfElo` *(agent)*: agent surveyed; value unavailable
- `sonnet-4-6.tbHard` *(agent)*: agent surveyed; value unavailable
- `codestral.arcAgi2` *(orchestrator)*: not reached in agent survey cycle; ARC-AGI-2 data unavailable
- `codestral.cfElo` *(orchestrator)*: not reached in agent survey cycle; Codeforces ELO data unavailable
- ... and 502 more


## [2026-05-28] — autonomous refresh-all [WARN: cumulative provenance coverage 52.4% below 85% target] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 351 new fills; 42 cells auto-gapped by orchestrator; 680 explicit agent gaps preserved]

[fillRatio:0.52 cells:561/1071 contradictions:208 fetch:0.0min tools:None batches:None build:9d1e71e]

### Updated
- 15 models: `mistral-large-3`, `minimax-m2-5`, `gpt-5-4`, `deepseek-v3-2`, `qwen3-6-plus`, `opus-4-7`, `nemotron-3-super`, `qwen3-7-max`, `gpt-5-5`, `mimo-v2-5-pro`, `mimo-v2-flash`, `qwen3-235b`, `qwen3-6-35b-moe`, `glm-5-1`, `sonnet-4-6`

### Resolved (auto via trustScore)
- opus-4-7.sweV: winner={'value': 87.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- opus-4-7.swePro: winner={'value': 64.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- opus-4-7.gpqa: winner={'value': 94.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- opus-4-7.hle: winner={'value': 46.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- opus-4-7.tb2: winner={'value': 69.11, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- opus-4-7.mmluPro: winner={'value': 89.87, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- sonnet-4-6.sweV: winner={'value': 79.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- sonnet-4-6.swePro: winner={'value': 40.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- sonnet-4-6.gpqa: winner={'value': 74.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 14, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- sonnet-4-6.hle: winner={'value': 51.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- sonnet-4-6.tb2: winner={'value': 58.87, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- sonnet-4-6.tau2: winner={'value': 91.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- sonnet-4-6.arcAgi2: winner={'value': 58.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- sonnet-4-6.lcb: winner={'value': 80.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- claude-haiku-4-5.sweV: winner={'value': 73.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- claude-haiku-4-5.gpqa: winner={'value': 67.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- claude-haiku-4-5.lcb: winner={'value': 61.5, 'trustScore': 0.4783, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- claude-haiku-4-5.tau2: winner={'value': 83.1, 'trustScore': 0.4778, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- deepseek-v3-2.sweV: winner={'value': 67.85, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.gpqa: winner={'value': 82.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.lcb: winner={'value': 74.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.hle: winner={'value': 24.76, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.mmluPro: winner={'value': 85.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.aime26: winner={'value': 89.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v3-2.cfElo: winner={'value': 2121.0, 'trustScore': 0.35, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v3-2.tb2: winner={'value': 46.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.aaIdx: winner={'value': 16.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v4-flash.sweV: winner={'value': 79.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-flash.lcb: winner={'value': 91.43, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-flash.gpqa: winner={'value': 88.36, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.sweV: winner={'value': 80.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.swePro: winner={'value': 55.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.lcb: winner={'value': 93.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.gpqa: winner={'value': 90.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.hle: winner={'value': 37.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.tb2: winner={'value': 67.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.aaIdx: winner={'value': 52.0, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- deepseek-coder-v2-16b.lcb: winner={'value': 43.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-coder-v2-16b.sweV: winner={'value': 43.0, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- deepseek-r1-14b.gpqa: winner={'value': 59.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-r1-14b.aime26: winner={'value': 70.08, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-r1-14b.mmluPro: winner={'value': 93.9, 'trustScore': 0.4507, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-flash.gpqa: winner={'value': 89.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-flash.hle: winner={'value': 34.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-flash.sweV: winner={'value': 78.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-flash.tau2: winner={'value': 71.5, 'trustScore': 0.4573, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- gemini-3-1-flash.lcb: winner={'value': 90.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-flash.mmluPro: winner={'value': 89.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-flash.aime26: winner={'value': 97.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-pro.gpqa: winner={'value': 94.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 15, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-pro.hle: winner={'value': 44.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-pro.aaIdx: winner={'value': 57.02, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- gemini-3-1-pro.mmluPro: winner={'value': 90.99, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- gemma-3-27b.gpqa: winner={'value': 42.46, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-26b-moe.gpqa: winner={'value': 82.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-31b.gpqa: winner={'value': 84.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-31b.lcb: winner={'value': 80.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 16, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-e2b.aime26: winner={'value': 37.5, 'trustScore': 0.35, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-e4b.aaIdx: winner={'value': 19.0, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- gemini-3-5-flash.gpqa: winner={'value': 92.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- gemini-3-5-flash.sweV: winner={'value': 81.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.sweV: winner={'value': 78.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.swePro: winner={'value': 56.22, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.tbHard: winner={'value': 39.4, 'trustScore': 0.4573, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.gpqa: winner={'value': 86.94, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.hle: winner={'value': 28.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.tau2: winner={'value': 84.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-5.sweV: winner={'value': 80.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-5.tb2: winner={'value': 52.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-5.gpqa: winner={'value': 85.11, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-5.lcb: winner={'value': 76.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-5.aime26: winner={'value': 88.75, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-5.mmluPro: winner={'value': 74.0, 'trustScore': 0.459, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-1.sweV: winner={'value': 74.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- minimax-m2-1.gpqa: winner={'value': 82.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- minimax-m2-1.hle: winner={'value': 17.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- minimax-m2-1.lcb: winner={'value': 86.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-1.tau2: winner={'value': 87.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mistral-large-3.gpqa: winner={'value': 43.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mistral-large-3.lcb: winner={'value': 82.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mistral-large-3.aaIdx: winner={'value': 23.0, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- codestral-22b.gpqa: winner={'value': 90.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- codestral-22b.swePro: winner={'value': 35.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- devstral-2.sweV: winner={'value': 72.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- devstral-2.gpqa: winner={'value': 59.4, 'trustScore': 0.4397, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- devstral-2.lcb: winner={'value': 44.8, 'trustScore': 0.4573, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- devstral-2.aaIdx: winner={'value': 62.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- devstral-medium.sweV: winner={'value': 61.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- devstral-small-2.sweV: winner={'value': 68.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mistral-medium-3-5.sweV: winner={'value': 77.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-4-1.sweV: winner={'value': 54.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-4-1.gpqa: winner={'value': 66.43, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-4-1.lcb: winner={'value': 68.2, 'trustScore': 0.4573, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- gpt-4-1.aaIdx: winner={'value': 26.0, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-4-1.mmluPro: winner={'value': 80.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- o3.sweV: winner={'value': 71.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o3.gpqa: winner={'value': 87.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- o3.hle: winner={'value': 20.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o3.lcb: winner={'value': 75.8, 'trustScore': 0.4783, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- o3.aime26: winner={'value': 88.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o3.cfElo: winner={'value': 2727.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o3.arcAgi2: winner={'value': 87.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- o4-mini.sweV: winner={'value': 68.19, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o4-mini.lcb: winner={'value': 80.2, 'trustScore': 0.434, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- o4-mini.aime26: winner={'value': 92.7, 'trustScore': 0.4573, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-4.sweV: winner={'value': 78.83, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-4.swePro: winner={'value': 57.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-4.gpqa: winner={'value': 92.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- gpt-5-4.hle: winner={'value': 39.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-22'} (severity=yellow, ΔNone)
- gpt-5-4.lcb: winner={'value': 85.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gpt-5-5.sweV: winner={'value': 88.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-5.swePro: winner={'value': 58.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-5.tb2: winner={'value': 82.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-5.hle: winner={'value': 41.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-5.mrcr: winner={'value': 74.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-5.aaIdx: winner={'value': 60.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-6-27b.sweV: winner={'value': 77.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-6-27b.gpqa: winner={'value': 87.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-6-max.sweV: winner={'value': 70.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-6-max.tb2: winner={'value': 65.4, 'trustScore': 0.35, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- qwen3-6-max.gpqa: winner={'value': 86.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- qwen3-6-max.hle: winner={'value': 51.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-6-max.tau2: winner={'value': 80.1, 'trustScore': 0.4778, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- qwen3-235b.aime26: winner={'value': 92.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-235b.gpqa: winner={'value': 81.1, 'trustScore': 0.35, 'tier': 'S', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-235b.hle: winner={'value': 42.0, 'trustScore': 0.4578, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- qwen3-235b.lcb: winner={'value': 74.49, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-235b.mmluPro: winner={'value': 84.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- qwen3-235b.cfElo: winner={'value': 2056.0, 'trustScore': 0.4507, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-32b.gpqa: winner={'value': 66.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-32b.mmluPro: winner={'value': 79.8, 'trustScore': 0.459, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-32b.aime26: winner={'value': 81.18, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-32b.lcb: winner={'value': 54.52, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-32b.aaIdx: winner={'value': 76.4, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- qwen3-6-35b-moe.gpqa: winner={'value': 86.0, 'trustScore': 0.35, 'tier': 'S', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-6-plus.sweV: winner={'value': 78.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-6-plus.mmluPro: winner={'value': 88.5, 'trustScore': 0.459, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- qwen3-6-plus.aaIdx: winner={'value': 74.8, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- qwen3-coder-30b.sweV: winner={'value': 51.38, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-coder-480b.sweV: winner={'value': 69.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-coder-480b.swePro: winner={'value': 38.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-coder-next.sweV: winner={'value': 70.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen25-coder-7b.lcb: winner={'value': 37.6, 'trustScore': 0.2505, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen25-coder-14b.sweV: winner={'value': 28.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen25-coder-32b.sweV: winner={'value': 69.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen25-coder-32b.lcb: winner={'value': 48.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-5-9b.lcb: winner={'value': 65.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-7-max.sweV: winner={'value': 80.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-7-max.gpqa: winner={'value': 92.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- qwen3-7-max.hle: winner={'value': 41.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3.gpqa: winner={'value': 84.6, 'trustScore': 0.4397, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3.lcb: winner={'value': 79.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3.sweV: winner={'value': 63.8, 'trustScore': 0.35, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3.aime26: winner={'value': 93.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3-mini.gpqa: winner={'value': 79.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- grok-3-mini.lcb: winner={'value': 80.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3-mini.aime26: winner={'value': 95.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- grok-3-mini.aaIdx: winner={'value': 32.02, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-4-20.aaIdx: winner={'value': 49.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-4-20.gpqa: winner={'value': 87.99, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-4-20.hle: winner={'value': 24.26, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-4-20.lcb: winner={'value': 79.32, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-4-20.aime26: winner={'value': 95.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- grok-4-20.sweV: winner={'value': 77.22, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-4-3.gpqa: winner={'value': 90.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-4-1-fast.aaIdx: winner={'value': 38.0, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- grok-4-1-fast.sweV: winner={'value': 56.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mimo-v2-5-pro.gpqa: winner={'value': 66.7, 'trustScore': 0.35, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mimo-v2-5-pro.hle: winner={'value': 33.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mimo-v2-5-pro.mmluPro: winner={'value': 68.5, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mimo-v2-5-pro.tau2: winner={'value': 72.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mimo-v2-flash.gpqa: winner={'value': 83.88, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mimo-v2-flash.lcb: winner={'value': 80.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mimo-v2-flash.aaIdx: winner={'value': 39.0, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-09'} (severity=yellow, ΔNone)
- mimo-v2-pro.sweV: winner={'value': 77.97, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mimo-v2-pro.gpqa: winner={'value': 87.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- glm-5-1.swePro: winner={'value': 58.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- glm-5-1.sweV: winner={'value': 77.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- glm-5-1.gpqa: winner={'value': 86.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- glm-5-1.hle: winner={'value': 52.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-5-1.tau2: winner={'value': 19.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-7.sweV: winner={'value': 73.74, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- glm-4-7.gpqa: winner={'value': 85.72, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- glm-4-7.tau2: winner={'value': 87.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- glm-4-5-air.sweV: winner={'value': 57.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- glm-4-5-air.gpqa: winner={'value': 79.1, 'trustScore': 0.4213, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-5-air.lcb: winner={'value': 72.9, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-5-air.hle: winner={'value': 14.4, 'trustScore': 0.3155, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-5-air.aime26: winner={'value': 89.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-5-air.tau2: winner={'value': 78.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- llama-4-maverick.gpqa: winner={'value': 69.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- llama-4-maverick.lcb: winner={'value': 43.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- llama-4-maverick.sweV: winner={'value': 76.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- llama-4-scout.gpqa: winner={'value': 57.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- llama-4-scout.lcb: winner={'value': 32.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- llama-4-scout.mmluPro: winner={'value': 74.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- llama-4-scout.sweV: winner={'value': 58.0, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- kimi-k2-6.sweV: winner={'value': 80.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- kimi-k2-6.tb2: winner={'value': 66.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- kimi-k2-6.lcb: winner={'value': 89.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- kimi-k2-6.gpqa: winner={'value': 90.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- kimi-k2-6.hle: winner={'value': 54.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- nemotron-3-super.sweV: winner={'value': 60.47, 'trustScore': 0.5, 'tier': 'I', 'verifications': 14, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- nemotron-3-super.gpqa: winner={'value': 79.26, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- nemotron-3-super.lcb: winner={'value': 81.08, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- step-3-5-flash.sweV: winner={'value': 74.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- step-3-5-flash.gpqa: winner={'value': 83.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- step-3-5-flash.tb2: winner={'value': 51.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)

### Gaps (510 entries — agent:468 orchestrator:42 — see data/known-gaps.json or next refresh)
- `opus-4-7.tau2` *(agent)*: agent surveyed; value unavailable
- `opus-4-7.tbHard` *(agent)*: agent surveyed; value unavailable
- `opus-4-7.nl2Repo` *(agent)*: agent surveyed; value unavailable
- `opus-4-7.aaAgentic` *(agent)*: agent surveyed; value unavailable
- `opus-4-7.cfElo` *(agent)*: agent surveyed; value unavailable
- `sonnet-4-6.tbHard` *(agent)*: agent surveyed; value unavailable
- `codestral.arcAgi2` *(orchestrator)*: not reached in agent survey cycle; ARC-AGI-2 data unavailable
- `codestral.cfElo` *(orchestrator)*: not reached in agent survey cycle; Codeforces ELO data unavailable
- ... and 502 more


## [2026-05-28] — autonomous refresh-all [WARN: cumulative provenance coverage 52.4% below 85% target] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 351 new fills; 42 cells auto-gapped by orchestrator; 680 explicit agent gaps preserved]

[fillRatio:0.52 cells:561/1071 contradictions:208 fetch:0.0min tools:None batches:None build:9d1e71e]

### Updated
- 48 models: `mistral-large-3`, `qwen3-6-max`, `minimax-m2-7`, `minimax-m2-5`, `devstral-2`, `glm-4-7`, `gpt-5-4`, `qwen3-32b`, `deepseek-v3-2`, `glm-4-5-air`, `gemini-3-5-flash`, `grok-3-mini`, `qwen3-6-plus`, `claude-haiku-4-5`, `qwen3-5-9b`, `grok-4-20`, `opus-4-7`, `grok-4-1-fast`, `devstral-small-2`, `deepseek-v4-flash`, `mimo-v2-pro`, `gemma-4-26b-moe`, `qwen25-coder-32b`, `deepseek-r1-14b`, `gpt-4-1`, `gemini-3-1-pro`, `o3`, `deepseek-v4-pro`, `qwen25-coder-7b`, `qwen3-7-plus`, `gemini-3-1-flash`, `nemotron-3-super`, `step-3-5-flash`, `llama-4-scout`, `qwen3-7-max`, `devstral-medium`, `gemma-3-27b`, `gpt-5-5`, `mimo-v2-5`, `mimo-v2-5-pro`, `mimo-v2-flash`, `qwen3-235b`, `qwen3-6-35b-moe`, `gemma-4-e4b`, `glm-5-1`, `sonnet-4-6`, `qwen3-coder-30b`, `o4-mini`

### Resolved (auto via trustScore)
- opus-4-7.sweV: winner={'value': 87.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- opus-4-7.swePro: winner={'value': 64.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- opus-4-7.gpqa: winner={'value': 94.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- opus-4-7.hle: winner={'value': 46.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- opus-4-7.tb2: winner={'value': 69.11, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- opus-4-7.mmluPro: winner={'value': 89.87, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- sonnet-4-6.sweV: winner={'value': 79.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- sonnet-4-6.swePro: winner={'value': 40.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- sonnet-4-6.gpqa: winner={'value': 74.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 14, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- sonnet-4-6.hle: winner={'value': 51.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- sonnet-4-6.tb2: winner={'value': 58.87, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- sonnet-4-6.tau2: winner={'value': 91.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- sonnet-4-6.arcAgi2: winner={'value': 58.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- sonnet-4-6.lcb: winner={'value': 80.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- claude-haiku-4-5.sweV: winner={'value': 73.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- claude-haiku-4-5.gpqa: winner={'value': 67.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- claude-haiku-4-5.lcb: winner={'value': 61.5, 'trustScore': 0.4783, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- claude-haiku-4-5.tau2: winner={'value': 83.1, 'trustScore': 0.4778, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- deepseek-v3-2.sweV: winner={'value': 67.85, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.gpqa: winner={'value': 82.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.lcb: winner={'value': 74.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.hle: winner={'value': 24.76, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.mmluPro: winner={'value': 85.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.aime26: winner={'value': 89.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v3-2.cfElo: winner={'value': 2121.0, 'trustScore': 0.35, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v3-2.tb2: winner={'value': 46.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v3-2.aaIdx: winner={'value': 16.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v4-flash.sweV: winner={'value': 79.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-flash.lcb: winner={'value': 91.43, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-flash.gpqa: winner={'value': 88.36, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.sweV: winner={'value': 80.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.swePro: winner={'value': 55.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.lcb: winner={'value': 93.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.gpqa: winner={'value': 90.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.hle: winner={'value': 37.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.tb2: winner={'value': 67.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-v4-pro.aaIdx: winner={'value': 52.0, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- deepseek-coder-v2-16b.lcb: winner={'value': 43.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-coder-v2-16b.sweV: winner={'value': 43.0, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- deepseek-r1-14b.gpqa: winner={'value': 59.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-r1-14b.aime26: winner={'value': 70.08, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- deepseek-r1-14b.mmluPro: winner={'value': 93.9, 'trustScore': 0.4507, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-flash.gpqa: winner={'value': 89.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-flash.hle: winner={'value': 34.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-flash.sweV: winner={'value': 78.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-flash.tau2: winner={'value': 71.5, 'trustScore': 0.4573, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- gemini-3-1-flash.lcb: winner={'value': 90.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-flash.mmluPro: winner={'value': 89.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-flash.aime26: winner={'value': 97.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-pro.gpqa: winner={'value': 94.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 15, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-pro.hle: winner={'value': 44.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemini-3-1-pro.aaIdx: winner={'value': 57.02, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- gemini-3-1-pro.mmluPro: winner={'value': 90.99, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- gemma-3-27b.gpqa: winner={'value': 42.46, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-26b-moe.gpqa: winner={'value': 82.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-31b.gpqa: winner={'value': 84.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-31b.lcb: winner={'value': 80.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 16, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-e2b.aime26: winner={'value': 37.5, 'trustScore': 0.35, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gemma-4-e4b.aaIdx: winner={'value': 19.0, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- gemini-3-5-flash.gpqa: winner={'value': 92.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- gemini-3-5-flash.sweV: winner={'value': 81.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.sweV: winner={'value': 78.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.swePro: winner={'value': 56.22, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.tbHard: winner={'value': 39.4, 'trustScore': 0.4573, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.gpqa: winner={'value': 86.94, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.hle: winner={'value': 28.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-7.tau2: winner={'value': 84.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-5.sweV: winner={'value': 80.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-5.tb2: winner={'value': 52.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-5.gpqa: winner={'value': 85.11, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- minimax-m2-5.lcb: winner={'value': 76.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-5.aime26: winner={'value': 88.75, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-5.mmluPro: winner={'value': 74.0, 'trustScore': 0.459, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-1.sweV: winner={'value': 74.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- minimax-m2-1.gpqa: winner={'value': 82.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- minimax-m2-1.hle: winner={'value': 17.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- minimax-m2-1.lcb: winner={'value': 86.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-1.tau2: winner={'value': 87.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mistral-large-3.gpqa: winner={'value': 43.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mistral-large-3.lcb: winner={'value': 82.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mistral-large-3.aaIdx: winner={'value': 23.0, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- codestral-22b.gpqa: winner={'value': 90.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- codestral-22b.swePro: winner={'value': 35.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- devstral-2.sweV: winner={'value': 72.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- devstral-2.gpqa: winner={'value': 59.4, 'trustScore': 0.4397, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- devstral-2.lcb: winner={'value': 44.8, 'trustScore': 0.4573, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- devstral-2.aaIdx: winner={'value': 62.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- devstral-medium.sweV: winner={'value': 61.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- devstral-small-2.sweV: winner={'value': 68.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mistral-medium-3-5.sweV: winner={'value': 77.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-4-1.sweV: winner={'value': 54.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-4-1.gpqa: winner={'value': 66.43, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-4-1.lcb: winner={'value': 68.2, 'trustScore': 0.4573, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- gpt-4-1.aaIdx: winner={'value': 26.0, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-4-1.mmluPro: winner={'value': 80.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- o3.sweV: winner={'value': 71.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o3.gpqa: winner={'value': 87.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- o3.hle: winner={'value': 20.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o3.lcb: winner={'value': 75.8, 'trustScore': 0.4783, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- o3.aime26: winner={'value': 88.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o3.cfElo: winner={'value': 2727.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o3.arcAgi2: winner={'value': 87.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- o4-mini.sweV: winner={'value': 68.19, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- o4-mini.lcb: winner={'value': 80.2, 'trustScore': 0.434, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- o4-mini.aime26: winner={'value': 92.7, 'trustScore': 0.4573, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-4.sweV: winner={'value': 78.83, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-4.swePro: winner={'value': 57.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-4.gpqa: winner={'value': 92.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- gpt-5-4.hle: winner={'value': 39.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-22'} (severity=yellow, ΔNone)
- gpt-5-4.lcb: winner={'value': 85.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gpt-5-5.sweV: winner={'value': 88.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-5.swePro: winner={'value': 58.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-5.tb2: winner={'value': 82.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-5.hle: winner={'value': 41.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-5.mrcr: winner={'value': 74.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- gpt-5-5.aaIdx: winner={'value': 60.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-6-27b.sweV: winner={'value': 77.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-6-27b.gpqa: winner={'value': 87.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-6-max.sweV: winner={'value': 70.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-6-max.tb2: winner={'value': 65.4, 'trustScore': 0.35, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- qwen3-6-max.gpqa: winner={'value': 86.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- qwen3-6-max.hle: winner={'value': 51.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-6-max.tau2: winner={'value': 80.1, 'trustScore': 0.4778, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- qwen3-235b.aime26: winner={'value': 92.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-235b.gpqa: winner={'value': 81.1, 'trustScore': 0.35, 'tier': 'S', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-235b.hle: winner={'value': 42.0, 'trustScore': 0.4578, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- qwen3-235b.lcb: winner={'value': 74.49, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-235b.mmluPro: winner={'value': 84.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- qwen3-235b.cfElo: winner={'value': 2056.0, 'trustScore': 0.4507, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-32b.gpqa: winner={'value': 66.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-32b.mmluPro: winner={'value': 79.8, 'trustScore': 0.459, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-32b.aime26: winner={'value': 81.18, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-32b.lcb: winner={'value': 54.52, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-32b.aaIdx: winner={'value': 76.4, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- qwen3-6-35b-moe.gpqa: winner={'value': 86.0, 'trustScore': 0.35, 'tier': 'S', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-6-plus.sweV: winner={'value': 78.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-6-plus.mmluPro: winner={'value': 88.5, 'trustScore': 0.459, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- qwen3-6-plus.aaIdx: winner={'value': 74.8, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- qwen3-coder-30b.sweV: winner={'value': 51.38, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-coder-480b.sweV: winner={'value': 69.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-coder-480b.swePro: winner={'value': 38.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-coder-next.sweV: winner={'value': 70.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen25-coder-7b.lcb: winner={'value': 37.6, 'trustScore': 0.2505, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen25-coder-14b.sweV: winner={'value': 28.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen25-coder-32b.sweV: winner={'value': 69.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen25-coder-32b.lcb: winner={'value': 48.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-5-9b.lcb: winner={'value': 65.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-7-max.sweV: winner={'value': 80.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- qwen3-7-max.gpqa: winner={'value': 92.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- qwen3-7-max.hle: winner={'value': 41.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3.gpqa: winner={'value': 84.6, 'trustScore': 0.4397, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3.lcb: winner={'value': 79.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3.sweV: winner={'value': 63.8, 'trustScore': 0.35, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3.aime26: winner={'value': 93.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3-mini.gpqa: winner={'value': 79.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- grok-3-mini.lcb: winner={'value': 80.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-3-mini.aime26: winner={'value': 95.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- grok-3-mini.aaIdx: winner={'value': 32.02, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-4-20.aaIdx: winner={'value': 49.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-4-20.gpqa: winner={'value': 87.99, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-4-20.hle: winner={'value': 24.26, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-4-20.lcb: winner={'value': 79.32, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-4-20.aime26: winner={'value': 95.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- grok-4-20.sweV: winner={'value': 77.22, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-4-3.gpqa: winner={'value': 90.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- grok-4-1-fast.aaIdx: winner={'value': 38.0, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- grok-4-1-fast.sweV: winner={'value': 56.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mimo-v2-5-pro.gpqa: winner={'value': 66.7, 'trustScore': 0.35, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mimo-v2-5-pro.hle: winner={'value': 33.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mimo-v2-5-pro.mmluPro: winner={'value': 68.5, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mimo-v2-5-pro.tau2: winner={'value': 72.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mimo-v2-flash.gpqa: winner={'value': 83.88, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mimo-v2-flash.lcb: winner={'value': 80.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mimo-v2-flash.aaIdx: winner={'value': 39.0, 'trustScore': 0.4807, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-09'} (severity=yellow, ΔNone)
- mimo-v2-pro.sweV: winner={'value': 77.97, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- mimo-v2-pro.gpqa: winner={'value': 87.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- glm-5-1.swePro: winner={'value': 58.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- glm-5-1.sweV: winner={'value': 77.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- glm-5-1.gpqa: winner={'value': 86.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- glm-5-1.hle: winner={'value': 52.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-5-1.tau2: winner={'value': 19.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-7.sweV: winner={'value': 73.74, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- glm-4-7.gpqa: winner={'value': 85.72, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- glm-4-7.tau2: winner={'value': 87.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- glm-4-5-air.sweV: winner={'value': 57.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- glm-4-5-air.gpqa: winner={'value': 79.1, 'trustScore': 0.4213, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-5-air.lcb: winner={'value': 72.9, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-5-air.hle: winner={'value': 14.4, 'trustScore': 0.3155, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-5-air.aime26: winner={'value': 89.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-5-air.tau2: winner={'value': 78.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- llama-4-maverick.gpqa: winner={'value': 69.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- llama-4-maverick.lcb: winner={'value': 43.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- llama-4-maverick.sweV: winner={'value': 76.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- llama-4-scout.gpqa: winner={'value': 57.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- llama-4-scout.lcb: winner={'value': 32.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- llama-4-scout.mmluPro: winner={'value': 74.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- llama-4-scout.sweV: winner={'value': 58.0, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- kimi-k2-6.sweV: winner={'value': 80.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- kimi-k2-6.tb2: winner={'value': 66.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- kimi-k2-6.lcb: winner={'value': 89.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- kimi-k2-6.gpqa: winner={'value': 90.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- kimi-k2-6.hle: winner={'value': 54.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- nemotron-3-super.sweV: winner={'value': 60.47, 'trustScore': 0.5, 'tier': 'I', 'verifications': 14, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- nemotron-3-super.gpqa: winner={'value': 79.26, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- nemotron-3-super.lcb: winner={'value': 81.08, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-28'} (severity=yellow, ΔNone)
- step-3-5-flash.sweV: winner={'value': 74.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- step-3-5-flash.gpqa: winner={'value': 83.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-28'} (severity=red, ΔNone)
- step-3-5-flash.tb2: winner={'value': 51.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-28'} (severity=red, ΔNone)

### Gaps (510 entries — agent:468 orchestrator:42 — see data/known-gaps.json or next refresh)
- `opus-4-7.tau2` *(agent)*: agent surveyed; value unavailable
- `opus-4-7.tbHard` *(agent)*: agent surveyed; value unavailable
- `opus-4-7.nl2Repo` *(agent)*: agent surveyed; value unavailable
- `opus-4-7.aaAgentic` *(agent)*: agent surveyed; value unavailable
- `opus-4-7.cfElo` *(agent)*: agent surveyed; value unavailable
- `sonnet-4-6.tbHard` *(agent)*: agent surveyed; value unavailable
- `codestral.arcAgi2` *(orchestrator)*: not reached in agent survey cycle; ARC-AGI-2 data unavailable
- `codestral.cfElo` *(orchestrator)*: not reached in agent survey cycle; Codeforces ELO data unavailable
- ... and 502 more


## [2026-05-28] — synth-layer integrity: fabrication gate + fresh-divergence surfacing

A `refresh-all` cycle exposed two synthesis-layer defects (the gather stage was
sound — 530 source-traced observations). This entry ships the TOOLING fix that
prevents recurrence; the cycle's contested benchmark values were NOT committed.

### Fixed
- **Stage-B synth fabrication.** The FAZ 4.C sonnet synth invented ~25–68 bench
  values absent from every gather observation, attributed to real URLs and
  contradicting the gathered evidence (e.g. `opus-4-7.hle=11.6` when the
  observation was 54.7; `devstral-2.sweV=66.4` against 3 sources at 72.2;
  `grok-4-20.sweV=90.1` with no observation). Such an artifact would corrupt the
  live decision data.

### Added
- **Synth traceability gate (`scripts/validate-synth-traceability.py`).** Every
  non-null `updates.bench[k]` is checked against its cell's EVIDENCE ENVELOPE
  (this cycle's fresh gather observations ∪ historical `sources.json` values).
  A value outside `[min,max]` of its candidates — or with zero evidence — is a
  FABRICATION. Scale-agnostic (uses the cell's own candidate range, so
  cfElo/webDevElo/0-100 all validate). `--auto-fallback` regenerates the
  artifact via the deterministic `local-synth.py` (which can only pick
  trust-winners from real observations, never hallucinate) and re-validates.
  Verified: flags 68 fabricated values on the bad artifact, 0 on local-synth
  output, recovers cleanly on fallback.
- **Orchestration wiring (SKILL.md + agent.md).** New Stage-B gate step between
  synth dispatch and `gen_unified_artifact`, plus a `4s` row in
  SILENT_FAIL_PREVENTION. agent.md synth mode gains HARD RULE 0 — GROUNDING /
  NO FABRICATION: every emitted value must be a verbatim gather-observed
  trust-winner; no observation → gap, never a value.
- **`fresh-divergence` anomaly class (`scripts/detect-anomalies.py`).** Ingests
  the gate's advisory `divergences[]` (grounded values that disagree with THIS
  cycle's fresh observations by > CONTRADICTION_WARN_PP) into
  `data/_anomalies.json`, so a conservative historical-consensus winner that
  overrode a correct fresh correction surfaces for the Step 7.7 anomaly→research
  loop (e.g. `o3.arcAgi2` stored 87.5 [mislabeled ARC-AGI-1] vs fresh 2.9).
  Local-synth's conservative resolution policy is unchanged — flag, don't reject.

## [2026-05-27] — data-integrity hardening: 3 systematic layers

Defense-in-depth so benchmark values land in the right cell with the right
metric, and anomalies are investigated rather than silently accepted or rejected.
Honest scope: this is layered prevention + flag-and-verify, not a 100% guarantee.

### Added
- **Layer 1 — source-authorization audit (`audit-data-coherence.py`):** builds
  domain→published-benches from the whitelist `publishes[]` + known Arena Elo
  publishers; flags a filled cell when a source publishes a confusable SIBLING
  metric but not this bench (scoped to the Elo family, where scales differ and
  the signal is reliable). Advisory WARN.
- **Layer 2 — per-bench plausibility bands (`_schema.benchRanges` + audit):**
  data-driven hard bounds (scale-corruption guard → HARD BLOCK) + soft bounds
  (unusual-but-possible → advisory WARN, re-verify, never reject). Replaces the
  hardcoded `_bench_max`. e.g. gemma-3-27b cfElo=110 now flags for verification
  (stays — it is a genuine below-Newbie rating).
- **Layer 3 — anomaly verification queue (`scripts/detect-anomalies.py` →
  `data/_anomalies.json`):** detects source-mismatch / out-of-band / single-source
  / peer-outlier (robust MAD vs same-tier peers) cells; the orchestrator (SKILL
  PRELIM-F) slices the queue into each gather batch's `idea_context.anomalies`,
  and the agent (agent.md rule 9) resolves them FIRST — confirm / reclassify /
  flag, never auto-dismiss. Wired through `write-batch-ctx.py`. (172 cells flagged
  on current data, e.g. gpt-5-4.aaIdx=26 vs tier-median 51.)

## [2026-05-27] — data integrity: cfElo metric disambiguation + misclassification guards

Triggered by a real bug (deepseek-v4-pro's correct Codeforces rating 3206 was
quarantined while GPT models showed LMArena chat Elo ~1484 misfiled into the
Codeforces cell). Targeted research (DeepSeek HF card, Qwen3 report, OpenAI
o3/o4-mini, Codeforces blog) resolved every flagged cfElo cell.

### Fixed
- **cfElo metric mis-classification** (`scripts/migrate-cfelo-metric.py`, mechanical
  + research-sourced). Cleared misfiled values: gpt-5-4 (1484), gpt-5-5 (1488),
  grok-4-20 (1491) = LMArena chat Elo; grok-4-3 (1500) = GDPval-AA Elo;
  qwen3-coder-480b (2056) = qwen3-235b's value wrong-attributed. Un-quarantined
  deepseek-v4-pro cfElo=3206 (confirmed real by primary source; field 2800-3200).
  Dropped o4-mini's mis-attributed 2070 (a DeepSeek figure), kept 2719 (OpenAI).
  Kept confirmed-real: qwen3-235b (2056), gemma-3-27b (110, genuinely below-Newbie),
  o3 (2727), gemini-3-1-pro (3052).

### Added (recurrence prevention)
- **agent.md BENCH METRIC INTEGRITY rule:** record a value into cell X only when
  the source names benchmark X; never coerce by scale/name similarity. Disambiguates
  confusable families — Elo (cfElo=Codeforces vs lmArenaElo=chat vs webDevElo),
  SWE (sweV/swePro/sweMulti), Terminal (tb2/tbHard), tau2/tau3, etc. Outliers
  trigger investigation, never silent rejection (a breakthrough IS an outlier).
- **audit-data-coherence.py Elo-family guard (advisory):** flags any cfElo cell
  sourced only from Arena-family domains as a likely misfiled LMArena Elo, for
  re-verification (never blocks — a genuine low Codeforces rating stays).

## [2026-05-27] — scoring integrity: quarantine-aware composite + CI-overlap rank bands

Fairness/objectivity hardening of the ranking, model-agnostic (every current +
future model).

### Fixed
- **Imputed composite now respects benchQuarantine.** `compositeScoreImputed`
  (the active scoring path) used quarantined cells at full weight, while
  `compositeScore` excluded them — so a model whose high scores were all
  quarantined (single-source / dispersed hype-blog values) could outrank clean
  independent-leaderboard data (qwen3-7-max #3 over opus-4-7 #4 in swe-focused).
  Quarantined cells are now treated as missing → peer-tier imputation (reduced
  weight, capped) or excluded. `impute` also skips the model's own quarantined
  value and excludes peers' quarantined values from the median pool.

### Added
- **CI-overlap rank bands (AA / LMArena-inspired).** The composite now carries an
  EPISTEMIC uncertainty (±σ) propagated from per-cell evidence quality
  (cellConfidence + contradiction spread + coverage + imputation share).
  `rankBands()` keeps a granular ordinal rank (1..N by score) — discriminating
  and familiar — while a `cluster` id increments only at a SIGNIFICANCE BREAK
  (where a model's band no longer overlaps the cluster leader's). The table
  shows the ordinal rank + score ±σ + a thin divider at each break (composite
  sort), so users see both who is ahead AND where the gaps are statistically
  real, without opaque tier numbers. Card shows the uncertainty range too.
  Labelled "uncertainty range" (not a 95% CI); single-source cells flagged.
  Constants are schema-driven (`_schema.composite.uncertainty`). Atomic-only (no
  double-count of vendor composites); does not touch weights or the coverage
  exponent. Verified on real data: top-5 frontier models form one cluster (truly
  close), with clear breaks below — e.g. balanced yields 6 clusters across 53
  ranked models.

## [2026-05-27] — autonomous refresh-all [WARN: cumulative provenance coverage 50.7% below 85% target] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 352 new fills; 19 cells auto-gapped by orchestrator; 710 explicit agent gaps preserved]

[fillRatio:0.51 cells:543/1071 contradictions:204 fetch:0.0min tools:None batches:None build:9f80e29]

### Updated
- 42 models: `devstral-2`, `sonnet-4-6`, `qwen3-6-max`, `codestral`, `gpt-5-4`, `deepseek-v4-flash`, `glm-4-7`, `glm-5-1`, `codestral-22b`, `grok-3`, `gpt-4-1`, `qwen3-235b`, `gemini-3-1-flash`, `gemma-4-e2b`, `gemma-4-e4b`, `deepseek-v4-pro`, `mimo-v2-5-pro`, `qwen3-coder-480b`, `grok-3-mini`, `gemma-3-27b`, `qwen25-coder-32b`, `deepseek-v3-2`, `grok-4-3`, `grok-4-20`, `nemotron-3-super`, `gemini-3-5-flash`, `minimax-m2-7`, `grok-4-1-fast`, `qwen3-5-9b`, `devstral-medium`, `gemma-4-26b-moe`, `gemma-4-31b`, `llama-4-maverick`, `qwen3-6-35b-moe`, `qwen3-coder-30b`, `qwen3-7-max`, `minimax-m2-1`, `claude-haiku-4-5`, `gpt-5-5`, `gemini-3-1-pro`, `glm-4-5-air`, `o3`

### Resolved (auto via trustScore)
- opus-4-7.sweV: winner={'value': 87.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- opus-4-7.swePro: winner={'value': 64.3, 'trustScore': 0.464, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- opus-4-7.gpqa: winner={'value': 94.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- opus-4-7.tb2: winner={'value': 68.54, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- opus-4-7.hle: winner={'value': 46.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- opus-4-7.aaCoding: winner={'value': 53.0, 'trustScore': 0.4549, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- opus-4-7.mrcr: winner={'value': 32.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- sonnet-4-6.sweV: winner={'value': 79.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- sonnet-4-6.swePro: winner={'value': 40.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-13'} (severity=red, ΔNone)
- sonnet-4-6.gpqa: winner={'value': 74.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- sonnet-4-6.tb2: winner={'value': 59.1, 'trustScore': 0.462, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- sonnet-4-6.hle: winner={'value': 51.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- sonnet-4-6.lcb: winner={'value': 80.0, 'trustScore': 0.434, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- sonnet-4-6.tau2: winner={'value': 87.5, 'trustScore': 0.4768, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- sonnet-4-6.arcAgi2: winner={'value': 58.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- sonnet-4-6.mmluPro: winner={'value': 79.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- claude-haiku-4-5.sweV: winner={'value': 73.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v3-2.sweV: winner={'value': 67.8, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v3-2.gpqa: winner={'value': 82.4, 'trustScore': 0.4397, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- deepseek-v3-2.lcb: winner={'value': 74.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v3-2.aaIdx: winner={'value': 16.0, 'trustScore': 0.4748, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- deepseek-v3-2.tb2: winner={'value': 46.4, 'trustScore': 0.462, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v3-2.hle: winner={'value': 25.1, 'trustScore': 0.4639, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v3-2.swePro: winner={'value': 15.56, 'trustScore': 0.443, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-09T15:04:38Z'} (severity=red, ΔNone)
- deepseek-v3-2.mmluPro: winner={'value': 85.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v3-2.aime26: winner={'value': 89.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v3-2.cfElo: winner={'value': 2121.0, 'trustScore': 0.3338, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-04-30'} (severity=red, ΔNone)
- deepseek-v4-flash.sweV: winner={'value': 79.0, 'trustScore': 0.4658, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v4-flash.lcb: winner={'value': 91.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v4-flash.gpqa: winner={'value': 88.1, 'trustScore': 0.443, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v4-flash.mmluPro: winner={'value': 86.4, 'trustScore': 0.4549, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v4-flash.hle: winner={'value': 22.1, 'trustScore': 0.4639, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- deepseek-v4-pro.sweV: winner={'value': 80.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v4-pro.gpqa: winner={'value': 90.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v4-pro.lcb: winner={'value': 93.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v4-pro.tb2: winner={'value': 67.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v4-pro.hle: winner={'value': 37.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-v4-pro.swePro: winner={'value': 55.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-coder-v2-16b.lcb: winner={'value': 43.4, 'trustScore': 0.4783, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-r1-14b.gpqa: winner={'value': 59.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- deepseek-r1-14b.aime26: winner={'value': 69.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- gemini-3-1-flash.sweV: winner={'value': 78.0, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gemini-3-1-flash.gpqa: winner={'value': 90.4, 'trustScore': 0.4397, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gemini-3-1-flash.hle: winner={'value': 35.0, 'trustScore': 0.4639, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gemini-3-1-flash.mmluPro: winner={'value': 89.0, 'trustScore': 0.4549, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- gemini-3-1-flash.lcb: winner={'value': 90.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-19'} (severity=red, ΔNone)
- gemini-3-1-pro.gpqa: winner={'value': 94.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 15, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gemini-3-1-pro.hle: winner={'value': 44.4, 'trustScore': 0.4731, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gemini-3-1-pro.mmluPro: winner={'value': 90.99, 'trustScore': 0.4562, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-18'} (severity=yellow, ΔNone)
- gemini-3-1-pro.tau2: winner={'value': 76.5, 'trustScore': 0.4562, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- gemini-3-1-pro.swePro: winner={'value': 54.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gemini-3-1-pro.aaIdx: winner={'value': 57.0, 'trustScore': 0.4748, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- gemma-3-27b.gpqa: winner={'value': 42.4, 'trustScore': 0.443, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gemma-4-26b-moe.gpqa: winner={'value': 82.3, 'trustScore': 0.4397, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gemma-4-26b-moe.aaIdx: winner={'value': 31.0, 'trustScore': 0.4748, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gemma-4-31b.gpqa: winner={'value': 84.3, 'trustScore': 0.443, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gemma-4-31b.lcb: winner={'value': 80.0, 'trustScore': 0.4783, 'tier': 'I', 'verifications': 15, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gemma-4-31b.sweV: winner={'value': 64.0, 'trustScore': 0.35, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- gemma-4-e2b.aime26: winner={'value': 37.5, 'trustScore': 0.3393, 'tier': 'S', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gemma-4-e4b.mmluPro: winner={'value': 69.4, 'trustScore': 0.4549, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gemini-3-5-flash.sweV: winner={'value': 81.0, 'trustScore': 0.4562, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- minimax-m2-5.sweV: winner={'value': 80.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-5.swePro: winner={'value': 55.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-5.gpqa: winner={'value': 85.2, 'trustScore': 0.443, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-5.hle: winner={'value': 19.4, 'trustScore': 0.4731, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- minimax-m2-5.lcb: winner={'value': 76.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-5.tb2: winner={'value': 52.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-5.aime26: winner={'value': 88.75, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-5.aaAgentic: winner={'value': 56.0, 'trustScore': 0.4549, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- minimax-m2-7.sweV: winner={'value': 78.0, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-7.swePro: winner={'value': 56.22, 'trustScore': 0.5, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-7.gpqa: winner={'value': 87.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-7.hle: winner={'value': 28.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-7.lcb: winner={'value': 79.93, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-7.tau2: winner={'value': 84.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-1.sweV: winner={'value': 74.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- minimax-m2-1.swePro: winner={'value': 36.81, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-1.gpqa: winner={'value': 82.3, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-1.hle: winner={'value': 17.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- minimax-m2-1.lcb: winner={'value': 86.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- minimax-m2-1.tau2: winner={'value': 87.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- devstral-2.sweV: winner={'value': 72.2, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- devstral-2.aaIdx: winner={'value': 62.1, 'trustScore': 0.4748, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- devstral-small-2.sweV: winner={'value': 68.0, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- devstral-medium.sweV: winner={'value': 67.5, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- devstral-medium.aaIdx: winner={'value': 54.6, 'trustScore': 0.4748, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- devstral-medium.gpqa: winner={'value': 49.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- devstral-medium.lcb: winner={'value': 33.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mistral-large-3.gpqa: winner={'value': 43.9, 'trustScore': 0.443, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mistral-large-3.lcb: winner={'value': 82.8, 'trustScore': 0.443, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mistral-medium-3-5.sweV: winner={'value': 77.6, 'trustScore': 0.4768, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- codestral-22b.gpqa: winner={'value': 90.1, 'trustScore': 0.443, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- codestral-22b.lcb: winner={'value': 62.7, 'trustScore': 0.4783, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- codestral.gpqa: winner={'value': 78.6, 'trustScore': 0.443, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- gpt-5-5.sweV: winner={'value': 88.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gpt-5-5.swePro: winner={'value': 58.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gpt-5-5.hle: winner={'value': 41.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gpt-5-5.tb2: winner={'value': 82.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gpt-5-5.mrcr: winner={'value': 74.0, 'trustScore': 0.4562, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gpt-5-5.mmluPro: winner={'value': 92.3, 'trustScore': 0.4562, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- gpt-5-5.lcb: winner={'value': 88.6, 'trustScore': 0.4783, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- gpt-5-5.aaIdx: winner={'value': 60.0, 'trustScore': 0.4748, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-08'} (severity=red, ΔNone)
- gpt-5-4.sweV: winner={'value': 79.2, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gpt-5-4.gpqa: winner={'value': 92.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- gpt-5-4.swePro: winner={'value': 59.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gpt-5-4.lcb: winner={'value': 85.3, 'trustScore': 0.4783, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- o3.sweV: winner={'value': 71.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- o3.gpqa: winner={'value': 87.7, 'trustScore': 0.443, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- o3.aime26: winner={'value': 88.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- o3.cfElo: winner={'value': 2727.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- o4-mini.sweV: winner={'value': 68.1, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gpt-4-1.sweV: winner={'value': 54.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gpt-4-1.gpqa: winner={'value': 66.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- gpt-4-1.mmluPro: winner={'value': 80.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- qwen3-6-27b.sweV: winner={'value': 77.2, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-6-27b.gpqa: winner={'value': 87.8, 'trustScore': 0.4189, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-6-max.sweV: winner={'value': 70.8, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- qwen3-6-max.gpqa: winner={'value': 86.0, 'trustScore': 0.4397, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- qwen3-6-max.hle: winner={'value': 51.0, 'trustScore': 0.4639, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-235b.gpqa: winner={'value': 81.1, 'trustScore': 0.3135, 'tier': 'S', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-235b.aime26: winner={'value': 92.3, 'trustScore': 0.4479, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- qwen3-235b.lcb: winner={'value': 74.1, 'trustScore': 0.434, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-235b.mmluPro: winner={'value': 84.4, 'trustScore': 0.4562, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- qwen3-235b.sweV: winner={'value': 79.0, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- qwen3-32b.lcb: winner={'value': 54.6, 'trustScore': 0.4549, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- qwen3-32b.aime26: winner={'value': 81.5, 'trustScore': 0.3839, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- qwen3-32b.gpqa: winner={'value': 66.8, 'trustScore': 0.4479, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-19'} (severity=red, ΔNone)
- qwen3-32b.sweV: winner={'value': 72.0, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- qwen3-6-35b-moe.gpqa: winner={'value': 86.0, 'trustScore': 0.35, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-6-plus.sweV: winner={'value': 78.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-coder-30b.sweV: winner={'value': 51.6, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-coder-480b.sweV: winner={'value': 69.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- qwen3-coder-480b.swePro: winner={'value': 38.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-coder-next.sweV: winner={'value': 70.6, 'trustScore': 0.5, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-coder-next.lcb: winner={'value': 68.9, 'trustScore': 0.434, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-coder-next.tb2: winner={'value': 36.2, 'trustScore': 0.3135, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- qwen25-coder-32b.sweV: winner={'value': 69.6, 'trustScore': 0.4562, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen25-coder-32b.lcb: winner={'value': 48.2, 'trustScore': 0.434, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-5-9b.lcb: winner={'value': 82.7, 'trustScore': 0.4783, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- qwen3-7-max.sweV: winner={'value': 80.4, 'trustScore': 0.3743, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-7-max.lcb: winner={'value': 90.5, 'trustScore': 0.434, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-7-max.gpqa: winner={'value': 92.4, 'trustScore': 0.443, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- qwen3-7-max.hle: winner={'value': 41.4, 'trustScore': 0.4731, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- qwen3-7-max.aime26: winner={'value': 90.5, 'trustScore': 0.3839, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-3.sweV: winner={'value': 63.8, 'trustScore': 0.2984, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-3.lcb: winner={'value': 79.4, 'trustScore': 0.4783, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-3.aime26: winner={'value': 93.3, 'trustScore': 0.4549, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-3-mini.gpqa: winner={'value': 79.1, 'trustScore': 0.4397, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- grok-3-mini.lcb: winner={'value': 69.6, 'trustScore': 0.4549, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-3-mini.aime26: winner={'value': 95.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- grok-3-mini.aaIdx: winner={'value': 32.1, 'trustScore': 0.4748, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-4-20.sweV: winner={'value': 76.7, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- grok-4-20.swePro: winner={'value': 51.8, 'trustScore': 0.4549, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- grok-4-20.lcb: winner={'value': 79.4, 'trustScore': 0.4549, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- grok-4-20.gpqa: winner={'value': 88.0, 'trustScore': 0.4397, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- grok-4-20.hle: winner={'value': 24.2, 'trustScore': 0.4639, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-4-20.aaIdx: winner={'value': 49.0, 'trustScore': 0.4748, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- grok-4-3.sweV: winner={'value': 79.6, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- grok-4-3.lcb: winner={'value': 46.63, 'trustScore': 0.3015, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-4-3.gpqa: winner={'value': 93.2, 'trustScore': 0.443, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- grok-4-3.hle: winner={'value': 53.0, 'trustScore': 0.4639, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- grok-4-3.aime26: winner={'value': 95.6, 'trustScore': 0.3839, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- grok-4-1-fast.sweV: winner={'value': 56.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-4-1-fast.gpqa: winner={'value': 85.3, 'trustScore': 0.4397, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- grok-4-1-fast.lcb: winner={'value': 82.2, 'trustScore': 0.4549, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- mimo-v2-flash.lcb: winner={'value': 80.6, 'trustScore': 0.4783, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mimo-v2-flash.gpqa: winner={'value': 83.7, 'trustScore': 0.4397, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mimo-v2-flash.hle: winner={'value': 22.1, 'trustScore': 0.3338, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mimo-v2-flash.aime26: winner={'value': 94.1, 'trustScore': 0.3338, 'tier': 'S', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mimo-v2-pro.sweV: winner={'value': 78.0, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mimo-v2-pro.gpqa: winner={'value': 87.0, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- mimo-v2-5.sweV: winner={'value': 78.9, 'trustScore': 0.3041, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mimo-v2-5-pro.gpqa: winner={'value': 66.7, 'trustScore': 0.2744, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mimo-v2-5-pro.hle: winner={'value': 33.8, 'trustScore': 0.4639, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- mimo-v2-5-pro.mmluPro: winner={'value': 68.5, 'trustScore': 0.35, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- mimo-v2-5-pro.tau2: winner={'value': 72.9, 'trustScore': 0.4549, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-5-1.swePro: winner={'value': 58.4, 'trustScore': 0.5, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-5-1.gpqa: winner={'value': 86.2, 'trustScore': 0.443, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-5-1.hle: winner={'value': 52.3, 'trustScore': 0.4731, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- glm-5-1.tau2: winner={'value': 19.9, 'trustScore': 0.4768, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- glm-5-1.sweV: winner={'value': 77.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-7.sweV: winner={'value': 73.8, 'trustScore': 0.4562, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-7.gpqa: winner={'value': 85.7, 'trustScore': 0.4189, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-7.tau2: winner={'value': 87.4, 'trustScore': 0.4562, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- glm-4-5-air.sweV: winner={'value': 57.6, 'trustScore': 0.4562, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- glm-4-5-air.lcb: winner={'value': 72.9, 'trustScore': 0.2505, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- glm-4-5-air.aime26: winner={'value': 89.4, 'trustScore': 0.3839, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-22'} (severity=yellow, ΔNone)
- glm-4-5-air.tau2: winner={'value': 77.9, 'trustScore': 0.5, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- llama-4-maverick.sweV: winner={'value': 76.8, 'trustScore': 0.5, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-18'} (severity=red, ΔNone)
- llama-4-maverick.gpqa: winner={'value': 69.8, 'trustScore': 0.4397, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- llama-4-maverick.lcb: winner={'value': 43.4, 'trustScore': 0.4783, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- llama-4-scout.gpqa: winner={'value': 57.2, 'trustScore': 0.4397, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- llama-4-scout.lcb: winner={'value': 32.8, 'trustScore': 0.434, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- llama-4-scout.mmluPro: winner={'value': 74.3, 'trustScore': 0.4562, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-22'} (severity=red, ΔNone)
- kimi-k2-6.sweV: winner={'value': 80.2, 'trustScore': 0.4658, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- kimi-k2-6.gpqa: winner={'value': 90.5, 'trustScore': 0.443, 'tier': 'I', 'verifications': 12, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- kimi-k2-6.lcb: winner={'value': 89.6, 'trustScore': 0.443, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- kimi-k2-6.tb2: winner={'value': 66.7, 'trustScore': 0.4562, 'tier': 'I', 'verifications': 10, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- kimi-k2-6.hle: winner={'value': 54.0, 'trustScore': 0.4639, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- nemotron-3-super.sweV: winner={'value': 60.47, 'trustScore': 0.4728, 'tier': 'I', 'verifications': 13, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- nemotron-3-super.gpqa: winner={'value': 79.23, 'trustScore': 0.4397, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- nemotron-3-super.lcb: winner={'value': 81.19, 'trustScore': 0.4783, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-27'} (severity=yellow, ΔNone)
- step-3-5-flash.sweV: winner={'value': 74.4, 'trustScore': 0.4562, 'tier': 'I', 'verifications': 11, 'latestDate': '2026-05-27'} (severity=red, ΔNone)
- step-3-5-flash.tb2: winner={'value': 51.0, 'trustScore': 0.443, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-27'} (severity=red, ΔNone)

### Gaps (528 entries — agent:509 orchestrator:19 — see data/known-gaps.json or next refresh)
- `opus-4-7.tbHard` *(agent)*: agent surveyed; value unavailable
- `opus-4-7.cfElo` *(agent)*: agent surveyed; value unavailable
- `opus-4-7.nl2Repo` *(agent)*: agent surveyed; value unavailable
- `opus-4-7.tau2` *(agent)*: agent surveyed; value unavailable
- `sonnet-4-6.tbHard` *(agent)*: agent surveyed; value unavailable
- `sonnet-4-6.cfElo` *(agent)*: agent surveyed; value unavailable
- `claude-haiku-4-5.aaAgentic` *(orchestrator)*: not reached in agent survey cycle; AA Agentic data unavailable
- `codestral.aaAgentic` *(orchestrator)*: not reached in agent survey cycle; AA Agentic data unavailable
- ... and 520 more


## [2026-05-26] — N/A permanent-skip retired + model-agnostic naming canonicalization

Manual pipeline + data change (no refresh). Two model-agnostic fixes.

### Changed
- **N/A retired end-to-end.** The `notApplicableBenchKeys` permanent-skip is gone —
  every (model, bench) cell is now FILLED or GAP. Unmeasured cells become gaps and
  are re-researched every cycle; the ONLY skip is the freshness tier (confirmed +
  ≥3 verifs + ≤7d). Cleared the field from all 63 models (589 previously-skipped
  cells freed for research), emptied `_schema.notApplicableRules`, and removed N/A
  generation/accounting from matrix.py, gap_gen.py, merge.py, local-synth.py,
  render-card.js, and the agent + skill contracts. Matrix invariant is now
  `filled + gaps == totalCells`. (Fixes frontier models like `gpt-5-5` whose
  fetchable benches — e.g. `lcb` — were wrongly N/A-skipped, masking real coverage.)
- **Model-agnostic display-name canonicalization.** Version minors now use a dot,
  not a space: `Qwen3 7 Max` → `Qwen3.7 Max`, `Qwen3 7 Plus` → `Qwen3.7 Plus`.
  Applied via `lib.util.canonical_display_name` in merge.py (self-corrects every
  refresh) and enforced by new audit AC12. Param sizes (`Gemma 3 27B`) and dotted
  versions (`Qwen 3.5 9B`) are intentionally untouched.
- **ID slug consistency:** `qwen-3-6-27b` → `qwen3-6-27b`, `qwen-3-6-max` →
  `qwen3-6-max` across models.json, sources.json, sources-whitelist.json, i18n, docs.

### Audit
- AC9 repurposed → blocks any `notApplicableBenchKeys`/`notApplicable` (N/A retired).
- AC12 added → model name version-format must be canonical.

## [2026-05-22] — autonomous refresh-all [WARN: very low cumulative provenance coverage 47.1%] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 236 new fills; 449 cells auto-gapped by orchestrator; 6 explicit agent gaps preserved]

[fillRatio:0.45 cells:482/1071 contradictions:20 fetch:0.0min tools:None batches:None build:4bbf149]

### Updated
- 55 models: `opus-4-7`, `sonnet-4-6`, `claude-haiku-4-5`, `deepseek-v3-2`, `deepseek-v4-flash`, `deepseek-v4-pro`, `deepseek-coder-v2-16b`, `deepseek-r1-14b`, `gemini-3-5-flash`, `gemini-3-1-pro`, `gemini-3-1-flash`, `gemma-3-27b`, `gemma-4-26b-moe`, `gemma-4-31b`, `gemma-4-e2b`, `gemma-4-e4b`, `minimax-m2-5`, `minimax-m2-7`, `minimax-m2-1`, `mistral-large-3`, `mistral-medium-3-5`, `devstral-2`, `devstral-medium`, `devstral-small-2`, `codestral-22b`, `codestral`, `gpt-5-5`, `gpt-5-4`, `gpt-4-1`, `o3`, `o4-mini`, `qwen-3-6-27b`, `qwen3-235b`, `qwen3-32b`, `qwen3-6-35b-moe`, `qwen3-6-plus`, `qwen3-coder-30b`, `qwen3-coder-480b`, `qwen3-7-max`, `qwen3-7-plus`, `grok-4-3`, `grok-4-20`, `grok-3-mini`, `mimo-v2-flash`, `mimo-v2-pro`, `mimo-v2-5`, `mimo-v2-5-pro`, `glm-5-1`, `glm-4-7`, `glm-4-5-air`, `llama-4-maverick`, `llama-4-scout`, `kimi-k2-6`, `nemotron-3-super`, `step-3-5-flash`

### Resolved (auto via trustScore)
- claude-haiku-4-5.sweV: winner={'value': 73.3, 'trustScore': 0.8, 'sourceUrl': 'https://benchlm.ai/models/claude-haiku-4-5', 'tier': 'I'} (severity=RED, Δ14.7)
- opus-4-7.hle: winner={'value': 54.7, 'trustScore': 0.7, 'sourceUrl': 'https://llm-stats.com/blog/research/claude-opus-4-7-launch', 'tier': 'I'} (severity=RED, Δ7.8)
- deepseek-v4-pro.sweV: winner={'value': 80.6, 'trustScore': 0.8, 'sourceUrl': 'https://deepseek.com/blog/deepseek-v4-pro', 'tier': 'S'} (severity=RED, Δ14.6)
- deepseek-v4-flash.sweV: winner={'value': 62.5, 'trustScore': 0.7, 'sourceUrl': 'https://benchlm.ai/models/deepseek-v4-flash', 'tier': 'I'} (severity=RED, Δ16.5)
- minimax-m2-5.gpqa: winner={'value': 47.0, 'trustScore': 0.7, 'sourceUrl': 'https://artificialanalysis.ai/models/minimax-m2-5', 'tier': 'I'} (severity=RED, Δ38.2)
- minimax-m2-5.hle: winner={'value': 32.0, 'trustScore': 0.7, 'sourceUrl': 'https://artificialanalysis.ai/models/minimax-m2-5', 'tier': 'I'} (severity=RED, Δ12.6)
- gemma-4-31b.gpqa: winner={'value': 84.3, 'trustScore': 0.87, 'sourceUrl': 'https://huggingface.co/google/gemma-4-31b', 'tier': 'I'} (severity=RED, Δ8.0)
- gemma-4-26b-moe.gpqa: winner={'value': 82.3, 'trustScore': 0.87, 'sourceUrl': 'https://huggingface.co/google/gemma-4-26b-moe', 'tier': 'I'} (severity=YELLOW, Δ3.1)
- qwen3-6-plus.aime26: winner={'value': 95.3, 'trustScore': 0.7, 'sourceUrl': 'https://llm-stats.com/benchmarks/aime', 'tier': 'I'} (severity=RED, Δ20.0)
- qwen3-235b.lcb: winner={'value': 62.2, 'trustScore': 0.7, 'sourceUrl': 'https://livecodebench.github.io/leaderboard.html', 'tier': 'I'} (severity=RED, Δ8.5)
- qwen3-coder-30b.sweV: winner={'value': 54.2, 'trustScore': 0.7, 'sourceUrl': 'https://arxiv.org/abs/2505.12345', 'tier': 'I'} (severity=RED, Δ13.8)
- grok-4-3.gpqa: winner={'value': 90.1, 'trustScore': 0.7, 'sourceUrl': 'https://artificialanalysis.ai/models/grok-4-3', 'tier': 'I'} (severity=YELLOW, Δ3.1)
- grok-4-1-fast.sweV: winner={'value': 64.0, 'trustScore': 0.7, 'sourceUrl': 'https://llm-stats.com/benchmarks/swe-bench-verified', 'tier': 'I'} (severity=RED, Δ8.0)
- mimo-v2-5-pro.gpqa: winner={'value': 86.6, 'trustScore': 0.7, 'sourceUrl': 'https://artificialanalysis.ai/models/mimo-v2-5-pro', 'tier': 'I'} (severity=RED, Δ19.9)
- llama-4-maverick.lcb: winner={'value': 43.4, 'trustScore': 0.7, 'sourceUrl': 'https://ai.meta.com/blog/llama-4-multimodal-intelligence/', 'tier': 'S'} (severity=RED, Δ33.7)
- o3.cfElo: winner={'value': 2706, 'trustScore': 0.7, 'sourceUrl': 'https://artificialanalysis.ai/models/o3', 'tier': 'I'} (severity=GREEN, Δ21)
- glm-4-7.tau2: winner={'value': 87.4, 'trustScore': 0.7, 'sourceUrl': 'https://llm-stats.com/benchmarks/tau-bench', 'tier': 'I'} (severity=YELLOW, Δ2.7)
- gpt-5-5.hle: winner={'value': 52.2, 'trustScore': 0.7, 'sourceUrl': 'https://openai.com/blog/gpt-5-5', 'tier': 'S'} (severity=RED, Δ10.8)
- gpt-5-5.mrcr: winner={'value': 74.0, 'trustScore': 0.7, 'sourceUrl': 'https://llm-stats.com/benchmarks/mrcr', 'tier': 'I'} (severity=RED, Δ13.5)
- o4-mini.cfElo: winner={'value': 2719, 'trustScore': 0.7, 'sourceUrl': 'https://benchlm.ai/benchmarks/codeforces-elo', 'tier': 'I'} (severity=RED, Δ649)

### Gaps (450 entries — agent:1 orchestrator:449 — see data/known-gaps.json or next refresh)
- `step-3-5-flash.swePro` *(agent)*: no SWE-bench Pro coverage found for StepFun models
- `claude-haiku-4-5.aaAgentic` *(orchestrator)*: not reached in agent survey cycle; AA Agentic data unavailable
- `claude-haiku-4-5.aaCoding` *(orchestrator)*: not reached in agent survey cycle; AA Coding data unavailable
- ... and 447 more


## [2026-05-19] — autonomous refresh-all [WARN: very low cumulative provenance coverage 45.2%] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 0 new fills; 430 cells auto-gapped by orchestrator; 0 explicit agent gaps preserved]

[fillRatio:0.45 cells:461/1020 contradictions:0 fetch:0.0min tools:None batches:None build:07d866a]

### Updated
- 36 models: `claude-haiku-4-5`, `codestral`, `codestral-22b`, `deepseek-v3-2`, `deepseek-v4-flash`, `deepseek-v4-pro`, `devstral-2`, `devstral-medium`, `devstral-small-2`, `gemini-3-1-flash`, `gemini-3-1-pro`, `glm-4-5-air`, `glm-4-7`, `glm-5-1`, `gpt-4-1`, `gpt-5-4`, `gpt-5-5`, `grok-3`, `grok-3-mini`, `grok-4-1-fast`, `grok-4-20`, `grok-4-3`, `kimi-k2-6`, `llama-4-maverick`, `llama-4-scout`, `minimax-m2-1`, `minimax-m2-5`, `minimax-m2-7`, `mistral-large-3`, `mistral-medium-3-5`, `nemotron-3-super`, `o3`, `o4-mini`, `opus-4-7`, `sonnet-4-6`, `step-3-5-flash`

### Gaps (430 entries — agent:0 orchestrator:430 — see data/known-gaps.json or next refresh)
- `claude-haiku-4-5.aaAgentic` *(orchestrator)*: not reached in agent survey cycle; AA Agentic data unavailable
- `claude-haiku-4-5.aaCoding` *(orchestrator)*: not reached in agent survey cycle; AA Coding data unavailable
- ... and 428 more


## [2026-05-19] — autonomous refresh-all [WARN: very low cumulative provenance coverage 45.3%] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 138 new fills; 429 cells auto-gapped by orchestrator; 1 explicit agent gaps preserved]

[fillRatio:0.45 cells:461/1020 contradictions:10 fetch:0.0min tools:None batches:None build:fb2f730]

### Updated
- 34 models: `opus-4-7`, `sonnet-4-6`, `claude-haiku-4-5`, `deepseek-v3-2`, `deepseek-r1-14b`, `gemma-3-27b`, `gemma-4-26b-moe`, `minimax-m2-5`, `minimax-m2-7`, `minimax-m2-1`, `mistral-large-3`, `mistral-medium-3-5`, `devstral-2`, `devstral-small-2`, `gpt-4-1`, `o3`, `o4-mini`, `qwen3-235b`, `qwen3-32b`, `qwen3-coder-480b`, `qwen-3-6-27b`, `qwen3-6-35b-moe`, `qwen3-6-plus`, `qwen-3-6-max`, `qwen3-coder-next`, `qwen3-5-9b`, `grok-3`, `grok-3-mini`, `glm-4-5-air`, `glm-4-7`, `qwen25-coder-7b`, `qwen25-coder-14b`, `qwen25-coder-32b`, `deepseek-coder-v2-16b`

### Resolved (auto via trustScore)
- qwen3-235b.gpqa: winner={'value': 70.0, 'trustScore': 0.9, 'sourceUrl': 'https://artificialanalysis.ai/models/qwen3-235b', 'tier': 'I'} (severity=RED, Δ11.1)
- qwen3-235b.lcb: winner={'value': 74.1, 'trustScore': 0.85, 'sourceUrl': 'https://llm-stats.com/benchmarks/livecodebench', 'tier': 'I'} (severity=AMBER, Δ3.4)
- o4-mini.aime26: winner={'value': 99.5, 'trustScore': 0.85, 'sourceUrl': 'https://openai.com/index/o4-mini', 'tier': 'S'} (severity=RED, Δ6.8)
- gpt-5-5.sweV: winner={'value': 88.7, 'trustScore': 0.85, 'sourceUrl': 'https://openai.com/index/gpt-5-5', 'tier': 'S'} (severity=RED, Δ6.1)
- llama-4-scout.gpqa: winner={'value': 57.2, 'trustScore': 0.85, 'sourceUrl': 'https://ai.meta.com/blog/llama-4-scout', 'tier': 'S'} (severity=RED, Δ17.1)
- qwen3-coder-next.lcb: winner={'value': 68.4, 'trustScore': 0.75, 'sourceUrl': 'https://arxiv.org/abs/2506.09964', 'tier': 'S'} (severity=RED, Δ14.7)
- deepseek-v3-2.sweV: winner={'value': 67.8, 'trustScore': 0.85, 'sourceUrl': 'https://artificialanalysis.ai/models/deepseek-v3-2', 'tier': 'I'} (severity=AMBER, Δ4.2)
- grok-4-3.gpqa: winner={'value': 90.1, 'trustScore': 0.85, 'sourceUrl': 'https://artificialanalysis.ai/models/grok-4-3', 'tier': 'I'} (severity=GREEN, Δ2.1)
- mimo-v2-flash.gpqa: winner={'value': 83.7, 'trustScore': 0.7, 'sourceUrl': 'https://github.com/XiaomiMiMo/MiMo', 'tier': 'S'} (severity=GREEN, Δ0.6)
- opus-4-7.tb2: winner={'value': 69.4, 'trustScore': 0.8, 'sourceUrl': 'https://www.anthropic.com/news/claude-opus-4-7', 'tier': 'S'} (severity=GREEN, Δ0.86)

### Gaps (430 entries — agent:1 orchestrator:429 — see data/known-gaps.json or next refresh)
- `opus-4-7.tau2` *(agent)*: Not published on any surveyed leaderboard for this model
- `claude-haiku-4-5.aaAgentic` *(orchestrator)*: not reached in agent survey cycle; AA Agentic data unavailable
- `claude-haiku-4-5.aaCoding` *(orchestrator)*: not reached in agent survey cycle; AA Coding data unavailable
- ... and 427 more


## [2026-05-18] — autonomous refresh-all [WARN: very low cumulative provenance coverage 47.6%] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 214 new fills; 377 cells auto-gapped by orchestrator; 6 explicit agent gaps preserved]

[fillRatio:0.47 cells:452/960 contradictions:12 fetch:0.0min tools:None batches:None build:8a1e0a0]

### Updated
- 34 models: `opus-4-7`, `sonnet-4-6`, `claude-haiku-4-5`, `deepseek-v3-2`, `gemini-3-1-flash`, `gemini-3-1-pro`, `gemma-3-27b`, `gemma-4-26b-moe`, `gemma-4-31b`, `gemma-4-e4b`, `minimax-m2-5`, `mistral-large-3`, `devstral-2`, `codestral-22b`, `devstral-small-2`, `gpt-4-1`, `o3`, `o4-mini`, `qwen-3-6-27b`, `qwen-3-6-max`, `qwen3-6-35b-moe`, `qwen3-6-plus`, `qwen3-coder-30b`, `qwen3-coder-480b`, `qwen3-coder-next`, `qwen25-coder-32b`, `qwen3-5-9b`, `grok-3`, `grok-3-mini`, `grok-4-20`, `grok-4-1-fast`, `glm-4-7`, `glm-4-5-air`, `nemotron-3-super`

### Resolved (auto via trustScore)
- qwen-3-6-27b.gpqa: winner={'value': 87.8, 'trustScore': 1.0, 'sourceUrl': 'https://llm-stats.com', 'tier': 'I'} (severity=RED, Δ15.4)
- qwen3-coder-480b.sweV: winner={'value': 66.5, 'trustScore': 0.7, 'sourceUrl': 'https://qwenlm.github.io/blog/qwen3-coder', 'tier': 'S'} (severity=RED, Δ16.5)
- qwen3-coder-480b.swePro: winner={'value': 38.7, 'trustScore': 1.0, 'sourceUrl': 'https://scale.com/leaderboard', 'tier': 'I'} (severity=RED, Δ27.3)
- devstral-2.aaIdx: winner={'value': 22.0, 'trustScore': 1.0, 'sourceUrl': 'https://artificialanalysis.ai/models/devstral-2', 'tier': 'I'} (severity=RED, Δ40.1)
- qwen25-coder-32b.sweV: winner={'value': 38.0, 'trustScore': 1.0, 'sourceUrl': 'https://arxiv.org/abs/2501.12599', 'tier': 'I'} (severity=RED, Δ31.6)
- minimax-m2-5.tb2: winner={'value': 52.0, 'trustScore': 1.0, 'sourceUrl': 'https://terminal-bench.com', 'tier': 'I'} (severity=RED, Δ5.0)
- glm-4-7.tau2: winner={'value': 84.7, 'trustScore': 0.7, 'sourceUrl': 'https://zhipuai.cn/news/glm-4-7', 'tier': 'S'} (severity=YELLOW, Δ2.7)
- nemotron-3-super.gpqa: winner={'value': 82.7, 'trustScore': 1.0, 'sourceUrl': 'https://llm-stats.com', 'tier': 'I'} (severity=YELLOW, Δ3.47)
- deepseek-v4-flash.gpqa: winner={'value': 89.4, 'trustScore': 1.0, 'sourceUrl': 'https://llm-stats.com', 'tier': 'I'} (severity=GREEN, Δ1.3)
- grok-3.gpqa: winner={'value': 84.0, 'trustScore': 0.7, 'sourceUrl': 'https://x.ai/news/grok-3', 'tier': 'S'} (severity=GREEN, Δ0.6)
- mimo-v2-flash.gpqa: winner={'value': 84.3, 'trustScore': 1.0, 'sourceUrl': 'https://llm-stats.com', 'tier': 'I'} (severity=GREEN, Δ0.6)
- llama-4-maverick.sweV: winner={'value': 76.8, 'trustScore': 1.0, 'sourceUrl': 'https://swebench.com', 'tier': 'I'} (severity=YELLOW, Δ2.6)

### Gaps (380 entries — agent:3 orchestrator:377 — see data/known-gaps.json or next refresh)
- `grok-3.swePro` *(agent)*: No SWE-bench Pro result found for Grok 3
- `grok-3.tb2` *(agent)*: No Terminal-Bench 2 result found for Grok 3
- `deepseek-v3-2.aider` *(agent)*: Aider Polyglot leaderboard frozen 2025-08; no 2026 entries
- `claude-haiku-4-5.aaAgentic` *(orchestrator)*: not reached in agent survey cycle; AA Agentic data unavailable
- `claude-haiku-4-5.aaCoding` *(orchestrator)*: not reached in agent survey cycle; AA Coding data unavailable
- ... and 375 more


## [2026-05-18] — refactor(composite): F1+F2 data-driven schema + atomic-only composite + vendor consensus

### Added
- `data/sources-whitelist.json _schema` gains 6 new blocks (single source of truth for what was previously hardcoded in `assets/js/core.js`):
  - **`normalization`** — per-bench `[0, 100]` mapping (cfElo piecewise, webDevElo linear, aaOmni invert). New ELO/inverted bench keys = data PR only, no code change.
  - **`confidence`** — `cellConfidence()` parameters (`verifDivisor`, contradiction penalties, `confidenceFloor`/`Ceiling`, `fallbackTrust`, `pseudoSources`).
  - **`benchKind`** — explicit `atomic` (22 keys) vs `vendorComposite` (4 keys: `aaIdx`, `aaCoding`, `aaAgentic`, `aaOmni`) split.
  - **`vendorComposites`** — metadata for each vendor aggregate (label, publisher, domain, `componentBenches`). Drives the new UI cross-validation panel.
  - **`composite`** — policy (`coverageShrinkageExponent` configurable; `imputation` block scaffolded but `enabled=false` by default).
  - **`presets`** — data-driven preset definitions (`atomicWeights` + `vendorCompositeView` + tiered `requiredBenches` / `criticalBenches` / `imputableBenches`). New **`consensus`** preset (kind=`vendorConsensus`) added alongside the 5 existing editorial presets.
- `assets/js/core.js` accessor helpers: `getPresets()`, `getDefaultWeights()`, `getContradictionThresholds()`, `getBenchKind()`, `isAtomicBench()`, `isVendorComposite()`, `getVendorCompositeMeta()`, `getCompositePolicy()`, `getPresetTiers()`. All prefer schema, fall back to hardcoded literals — no behavior change when whitelist not fetched.
- `assets/js/data.js` new functions: `effectiveScore()` (score dispatcher), `vendorComposites()`, `vendorConsensusScore()`, `crossValidationAgreement()`, `presetTiersFor()`.
- UI: vendor composite badge row + agreement indicator (🟢 consensus / 🟡 mild / 🔴 controversy) + tiered "limited data" / "limited coverage" warning rozetler on every model card.

### Changed
- `compositeScore()` now skips vendor composite benches (atomic-only aggregation) — prevents double-counting their `componentBenches`. Vendor composites surface in the new cross-validation panel instead.
- `coverageOf()` matches the new atomic-only contract.
- `normalizeBenchScore()` consults `_schema.normalization[key]` first; hardcoded piecewise/linear/invert logic is now the fallback only.
- `cellConfidence()` reads thresholds + pseudo-source set from `_schema.confidence` with literal fallback.
- `contradictionFor()` + `disputedCount()` use `getContradictionThresholds()` (data-driven via `_schema.contracts.CONTRADICTION_WARN_PP/BLOCK_PP`).
- `data.js:loadData()` now also fetches `sources-whitelist.json` (best-effort; 404 → fallback to all hardcoded values).
- Preset selector in `index.html` gains the new "Vendor Consensus" option.
- `applyPreset()` sets `State.scoreFn` based on preset kind so render layer dispatches to the right scoring path.

### Methodology note (top-10 ranking will shift)
Existing presets previously included vendor composites with non-zero weights (e.g., balanced had `aaCoding=4, aaAgentic=4, aaIdx=3, aaOmni=3` totaling 14 pts). Those weights are now zero in the data-driven schema; the same signal is shown separately in the vendor panel. Net: AICM composite scores drop slightly for models with strong vendor composite values, but ranking is more honest (no signal double-counting). Cross-validation panel surfaces agreement/disagreement with vendor consensus for every model.

[build:after-0673f36]

## [2026-05-18] — autonomous refresh-all [WARN: very low cumulative provenance coverage 48.3%] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 274 new fills; 32 cells auto-gapped by orchestrator; 355 explicit agent gaps preserved]

[fillRatio:0.46 cells:445/960 contradictions:11 fetch:0.0min tools:None batches:None build:a98aee1]

### Updated
- 54 models: `opus-4-7`, `sonnet-4-6`, `claude-haiku-4-5`, `gemini-3-1-flash`, `gemma-3-27b`, `gemma-4-31b`, `gemma-4-26b-moe`, `gemma-4-e2b`, `gemma-4-e4b`, `deepseek-v3-2`, `deepseek-v4-flash`, `deepseek-v4-pro`, `deepseek-coder-v2-16b`, `deepseek-r1-14b`, `minimax-m2-5`, `minimax-m2-7`, `minimax-m2-1`, `mistral-large-3`, `devstral-2`, `devstral-medium`, `devstral-small-2`, `mistral-medium-3-5`, `codestral`, `codestral-22b`, `o3`, `o4-mini`, `grok-3-mini`, `grok-4-20`, `grok-4-3`, `grok-4-1-fast`, `qwen-3-6-27b`, `qwen-3-6-max`, `qwen3-235b`, `qwen3-32b`, `qwen3-6-35b-moe`, `qwen3-6-plus`, `qwen3-coder-30b`, `qwen3-coder-480b`, `qwen3-coder-next`, `qwen3-5-9b`, `qwen25-coder-14b`, `qwen25-coder-32b`, `qwen25-coder-7b`, `mimo-v2-5`, `mimo-v2-5-pro`, `mimo-v2-flash`, `mimo-v2-pro`, `glm-4-7`, `glm-4-5-air`, `llama-4-maverick`, `llama-4-scout`, `kimi-k2-6`, `nemotron-3-super`, `step-3-5-flash`

### Resolved (auto via trustScore)
- deepseek-v3-2.sweV: winner={'value': 74.2, 'trustScore': 1.0, 'sourceUrl': 'https://artificialanalysis.ai/models/deepseek-v3', 'tier': 'I'} (severity=RED, Δ6.4)
- gemini-3-1-flash.gpqa: winner={'value': 86.9, 'trustScore': 1.0, 'sourceUrl': 'https://artificialanalysis.ai/models/gemini-3-1-flash', 'tier': 'I'} (severity=YELLOW, Δ3.5)
- mistral-large-3.sweV: winner={'value': 48.5, 'trustScore': 0.93, 'sourceUrl': 'https://artificialanalysis.ai/models/mistral-large-3', 'tier': 'I'} (severity=RED, Δ13.2)
- minimax-m2-1.swePro: winner={'value': 44.1, 'trustScore': 0.93, 'sourceUrl': 'https://benchlm.ai/models/minimax-m2-1', 'tier': 'I'} (severity=RED, Δ7.29)
- minimax-m2-1.tau2: winner={'value': 87.0, 'trustScore': 0.93, 'sourceUrl': 'https://artificialanalysis.ai/models/minimax-m2-1', 'tier': 'I'} (severity=YELLOW, Δ4.0)
- minimax-m2-1.lcb: winner={'value': 86.0, 'trustScore': 0.93, 'sourceUrl': 'https://benchlm.ai/models/minimax-m2-1', 'tier': 'I'} (severity=RED, Δ5.0)
- gpt-5-5.aaOmni: winner={'value': 43.0, 'trustScore': 0.93, 'sourceUrl': 'https://benchlm.ai/models/gpt-5-5', 'tier': 'I'} (severity=RED, Δ14.0)
- grok-4-1-fast.lcb: winner={'value': 39.9, 'trustScore': 0.93, 'sourceUrl': 'https://artificialanalysis.ai/models/grok-4-1-fast', 'tier': 'I'} (severity=RED, Δ42.3)
- qwen3-6-35b-moe.gpqa: winner={'value': 82.3, 'trustScore': 0.93, 'sourceUrl': 'https://artificialanalysis.ai/models/qwen3-6-35b-moe', 'tier': 'I'} (severity=YELLOW, Δ3.7)
- qwen3-5-9b.lcb: winner={'value': 65.6, 'trustScore': 0.93, 'sourceUrl': 'https://artificialanalysis.ai/models/qwen3-5-9b', 'tier': 'I'} (severity=RED, Δ17.1)
- mimo-v2-5-pro.gpqa: winner={'value': 86.6, 'trustScore': 0.93, 'sourceUrl': 'https://artificialanalysis.ai/models/mimo-v2-5-pro', 'tier': 'I'} (severity=RED, Δ19.9)

### Gaps (387 entries — agent:0 orchestrator:387 — see data/known-gaps.json or next refresh)
- `claude-haiku-4-5.aaAgentic` *(orchestrator)*: not reached in agent survey cycle; AA Agentic data unavailable
- `claude-haiku-4-5.aaCoding` *(orchestrator)*: not reached in agent survey cycle; AA Coding data unavailable
- ... and 385 more


## [2026-05-18] — autonomous refresh-all [WARN: very low cumulative provenance coverage 47.7%] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 46 new fills; 0 cells auto-gapped by orchestrator; 454 explicit agent gaps preserved]

[fillRatio:0.48 cells:457/960 contradictions:11 fetch:0.0min tools:None batches:None build:a1b9577]

### Updated
- 13 models: `opus-4-7`, `sonnet-4-6`, `claude-haiku-4-5`, `deepseek-v3-2`, `gemini-3-1-flash`, `gemini-3-1-pro`, `gemma-3-27b`, `gpt-4-1`, `o3`, `o4-mini`, `qwen3-235b`, `llama-4-maverick`, `llama-4-scout`

### Resolved (auto via trustScore)
- opus-4-7.hle: winner={'value': 46.9, 'trustScore': 0.555, 'sourceUrl': 'https://www.anthropic.com/news/claude-opus-4-7', 'tier': 'S'} (severity=RED, Δ7.8)
- deepseek-v3-2.sweV: winner={'value': 74.2, 'trustScore': 0.5, 'sourceUrl': 'https://www.swebench.com', 'tier': 'I'} (severity=RED, Δ6.4)
- deepseek-v3-2.tb2: winner={'value': 46.4, 'trustScore': 0.5, 'sourceUrl': 'https://terminal-bench.com', 'tier': 'I'} (severity=RED, Δ11.2)
- deepseek-v3-2.gpqa: winner={'value': 78.5, 'trustScore': 0.5, 'sourceUrl': 'https://artificialanalysis.ai/models/deepseek-v3-2', 'tier': 'I'} (severity=RED, Δ7.2)
- deepseek-v3-2.lcb: winner={'value': 60.3, 'trustScore': 0.5, 'sourceUrl': 'https://livecodebench.github.io/leaderboard.html', 'tier': 'I'} (severity=RED, Δ13.8)
- o4-mini.aime26: winner={'value': 99.5, 'trustScore': 0.35, 'sourceUrl': 'https://openai.com/index/o4-mini', 'tier': 'S'} (severity=RED, Δ6.8)
- qwen3-235b.gpqa: winner={'value': 70.0, 'trustScore': 0.5, 'sourceUrl': 'https://artificialanalysis.ai/models/qwen3-235b', 'tier': 'I'} (severity=RED, Δ14.4)
- qwen3-235b.lcb: winner={'value': 62.2, 'trustScore': 0.5, 'sourceUrl': 'https://livecodebench.github.io/leaderboard.html', 'tier': 'I'} (severity=RED, Δ8.5)
- glm-4-7.gpqa: winner={'value': 85.7, 'trustScore': 0.5, 'sourceUrl': 'https://docs.z.ai/models/glm-4-7', 'tier': 'S'} (severity=RED, Δ43.7)
- minimax-m2-5.lcb: winner={'value': 69.5, 'trustScore': 0.35, 'sourceUrl': 'https://api.minimax.io/news/minimax-m2', 'tier': 'S'} (severity=YELLOW, Δ4.5)
- o3.gpqa: winner={'value': 87.7, 'trustScore': 0.555, 'sourceUrl': 'https://openai.com/index/o3', 'tier': 'S'} (severity=YELLOW, Δ4.4)

### Gaps (398 entries — agent:1 orchestrator:397 — see data/known-gaps.json or next refresh)
- `deepseek-v3-2.tau2` *(agent)*: No independent source found
- `claude-haiku-4-5.aaAgentic` *(orchestrator)*: not reached in agent survey cycle; AA Agentic data unavailable
- `claude-haiku-4-5.aaCoding` *(orchestrator)*: not reached in agent survey cycle; AA Coding data unavailable
- ... and 395 more


## [2026-05-18] — autonomous refresh-all [WARN: very low cumulative provenance coverage 47.7%] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 46 new fills; 0 cells auto-gapped by orchestrator; 454 explicit agent gaps preserved]

[fillRatio:0.48 cells:457/960 contradictions:11 fetch:0.0min tools:None batches:None build:a1b9577]

### Updated
- 7 models: `opus-4-7`, `sonnet-4-6`, `claude-haiku-4-5`, `deepseek-v3-2`, `gpt-4-1`, `o3`, `o4-mini`

### Resolved (auto via trustScore)
- opus-4-7.hle: winner={'value': 46.9, 'trustScore': 0.555, 'sourceUrl': 'https://www.anthropic.com/news/claude-opus-4-7', 'tier': 'S'} (severity=RED, Δ7.8)
- deepseek-v3-2.sweV: winner={'value': 74.2, 'trustScore': 0.5, 'sourceUrl': 'https://www.swebench.com', 'tier': 'I'} (severity=RED, Δ6.4)
- deepseek-v3-2.tb2: winner={'value': 46.4, 'trustScore': 0.5, 'sourceUrl': 'https://terminal-bench.com', 'tier': 'I'} (severity=RED, Δ11.2)
- deepseek-v3-2.gpqa: winner={'value': 78.5, 'trustScore': 0.5, 'sourceUrl': 'https://artificialanalysis.ai/models/deepseek-v3-2', 'tier': 'I'} (severity=RED, Δ7.2)
- deepseek-v3-2.lcb: winner={'value': 60.3, 'trustScore': 0.5, 'sourceUrl': 'https://livecodebench.github.io/leaderboard.html', 'tier': 'I'} (severity=RED, Δ13.8)
- o4-mini.aime26: winner={'value': 99.5, 'trustScore': 0.35, 'sourceUrl': 'https://openai.com/index/o4-mini', 'tier': 'S'} (severity=RED, Δ6.8)
- qwen3-235b.gpqa: winner={'value': 70.0, 'trustScore': 0.5, 'sourceUrl': 'https://artificialanalysis.ai/models/qwen3-235b', 'tier': 'I'} (severity=RED, Δ14.4)
- qwen3-235b.lcb: winner={'value': 62.2, 'trustScore': 0.5, 'sourceUrl': 'https://livecodebench.github.io/leaderboard.html', 'tier': 'I'} (severity=RED, Δ8.5)
- glm-4-7.gpqa: winner={'value': 85.7, 'trustScore': 0.5, 'sourceUrl': 'https://docs.z.ai/models/glm-4-7', 'tier': 'S'} (severity=RED, Δ43.7)
- minimax-m2-5.lcb: winner={'value': 69.5, 'trustScore': 0.35, 'sourceUrl': 'https://api.minimax.io/news/minimax-m2', 'tier': 'S'} (severity=YELLOW, Δ4.5)
- o3.gpqa: winner={'value': 87.7, 'trustScore': 0.555, 'sourceUrl': 'https://openai.com/index/o3', 'tier': 'S'} (severity=YELLOW, Δ4.4)

### Gaps (398 entries — agent:1 orchestrator:397 — see data/known-gaps.json or next refresh)
- `deepseek-v3-2.tau2` *(agent)*: No independent source found
- `claude-haiku-4-5.aaAgentic` *(orchestrator)*: not reached in agent survey cycle; AA Agentic data unavailable
- `claude-haiku-4-5.aaCoding` *(orchestrator)*: not reached in agent survey cycle; AA Coding data unavailable
- ... and 395 more


## [2026-05-18] — autonomous refresh-all [WARN: very low cumulative provenance coverage 47.7%] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 46 new fills; 0 cells auto-gapped by orchestrator; 454 explicit agent gaps preserved]

[fillRatio:0.48 cells:457/960 contradictions:11 fetch:0.0min tools:None batches:None build:3246226]

### Updated
- 20 models: `opus-4-7`, `sonnet-4-6`, `claude-haiku-4-5`, `deepseek-v3-2`, `gemini-3-1-flash`, `gemini-3-1-pro`, `gemma-3-27b`, `gpt-4-1`, `o3`, `o4-mini`, `qwen3-235b`, `qwen3-coder-30b`, `grok-3`, `grok-3-mini`, `glm-4-7`, `llama-4-maverick`, `llama-4-scout`, `mistral-large-3`, `codestral-22b`, `devstral-medium`

### Resolved (auto via trustScore)
- opus-4-7.hle: winner={'value': 46.9, 'trustScore': 0.555, 'sourceUrl': 'https://www.anthropic.com/news/claude-opus-4-7', 'tier': 'S'} (severity=RED, Δ7.8)
- deepseek-v3-2.sweV: winner={'value': 74.2, 'trustScore': 0.5, 'sourceUrl': 'https://www.swebench.com', 'tier': 'I'} (severity=RED, Δ6.4)
- deepseek-v3-2.tb2: winner={'value': 46.4, 'trustScore': 0.5, 'sourceUrl': 'https://terminal-bench.com', 'tier': 'I'} (severity=RED, Δ11.2)
- deepseek-v3-2.gpqa: winner={'value': 78.5, 'trustScore': 0.5, 'sourceUrl': 'https://artificialanalysis.ai/models/deepseek-v3-2', 'tier': 'I'} (severity=RED, Δ7.2)
- deepseek-v3-2.lcb: winner={'value': 60.3, 'trustScore': 0.5, 'sourceUrl': 'https://livecodebench.github.io/leaderboard.html', 'tier': 'I'} (severity=RED, Δ13.8)
- o4-mini.aime26: winner={'value': 99.5, 'trustScore': 0.35, 'sourceUrl': 'https://openai.com/index/o4-mini', 'tier': 'S'} (severity=RED, Δ6.8)
- qwen3-235b.gpqa: winner={'value': 70.0, 'trustScore': 0.5, 'sourceUrl': 'https://artificialanalysis.ai/models/qwen3-235b', 'tier': 'I'} (severity=RED, Δ14.4)
- qwen3-235b.lcb: winner={'value': 62.2, 'trustScore': 0.5, 'sourceUrl': 'https://livecodebench.github.io/leaderboard.html', 'tier': 'I'} (severity=RED, Δ8.5)
- glm-4-7.gpqa: winner={'value': 85.7, 'trustScore': 0.5, 'sourceUrl': 'https://docs.z.ai/models/glm-4-7', 'tier': 'S'} (severity=RED, Δ43.7)
- minimax-m2-5.lcb: winner={'value': 69.5, 'trustScore': 0.35, 'sourceUrl': 'https://api.minimax.io/news/minimax-m2', 'tier': 'S'} (severity=YELLOW, Δ4.5)
- o3.gpqa: winner={'value': 87.7, 'trustScore': 0.555, 'sourceUrl': 'https://openai.com/index/o3', 'tier': 'S'} (severity=YELLOW, Δ4.4)

### Gaps (398 entries — agent:1 orchestrator:397 — see data/known-gaps.json or next refresh)
- `deepseek-v3-2.tau2` *(agent)*: No independent source found
- `claude-haiku-4-5.aaAgentic` *(orchestrator)*: not reached in agent survey cycle; AA Agentic data unavailable
- `claude-haiku-4-5.aaCoding` *(orchestrator)*: not reached in agent survey cycle; AA Coding data unavailable
- ... and 395 more


## [2026-05-18] — phase 3a: purge pseudo-source contamination

Removed 1281 pseudo-source entries from `data/sources.json` (33.2% of total):
- `snapshot-extraction` (871)
- `auto-resolution candidate` (361)
- `synth-backfill` (49)

These entries lacked verifiable URLs and contributed zero real evidence
while inflating verification counts and trustScore weights in composite
calculations.

568 orphan cells (pseudo-only, no backing models.json value) dropped
entirely. 12 cells rescued (sole-evidence pseudo entries re-tagged
`rescued: true` for re-fetch in next refresh cycle). Total cell count
`1549 → 981`. Backup at `data/sources.json.bak3`.


## [2026-05-18] — autonomous refresh-all [WARN: cumulative provenance coverage 70.8% below 85% target] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 117 new fills; 3 cells auto-gapped by orchestrator; 87 explicit agent gaps preserved]

[fillRatio:0.70 cells:421/600 contradictions:7 fetch:0.0min tools:None batches:None build:7c7fe54]

### Updated
- 29 models: `opus-4-7`, `sonnet-4-6`, `claude-haiku-4-5`, `deepseek-v3-2`, `deepseek-r1-14b`, `deepseek-coder-v2-16b`, `deepseek-v4-flash`, `deepseek-v4-pro`, `gemini-3-1-pro`, `gemini-3-1-flash`, `minimax-m2-5`, `minimax-m2-1`, `mistral-medium-3-5`, `devstral-2`, `mistral-large-3`, `gpt-5-5`, `gpt-5-4`, `qwen3-235b`, `qwen3-32b`, `qwen3-6-35b-moe`, `qwen3-coder-next`, `grok-4-20`, `grok-4-3`, `mimo-v2-5`, `mimo-v2-5-pro`, `glm-5-1`, `glm-4-7`, `llama-4-maverick`, `llama-4-scout`

### Resolved (auto via trustScore)
- deepseek-v3-2.sweV: winner={'value': 74.2, 'trustScore': 0.67, 'sourceUrl': 'https://marc0.dev/leaderboard', 'tier': 'I'} (severity=RED, Δ15.5)
- grok-4-20.sweV: winner={'value': 76.7, 'trustScore': 0.67, 'sourceUrl': 'https://marc0.dev/leaderboard', 'tier': 'I'} (severity=RED, Δ18.1)
- llama-4-maverick.sweV: winner={'value': 76.8, 'trustScore': 0.67, 'sourceUrl': 'https://www.vellum.ai/open-llm-leaderboard', 'tier': 'I'} (severity=RED, Δ18.2)
- minimax-m2-5.swePro: winner={'value': 55.4, 'trustScore': 0.7, 'sourceUrl': 'https://platform.minimaxi.com', 'tier': 'S'} (severity=RED, Δ24.8)
- mimo-v2-5-pro.gpqa: winner={'value': 86.6, 'trustScore': 0.67, 'sourceUrl': 'https://artificialanalysis.ai/models/mimo-v2-5-pro', 'tier': 'I'} (severity=RED, Δ19.9)
- minimax-m2-1.gpqa: winner={'value': 80.5, 'trustScore': 0.7, 'sourceUrl': 'https://platform.minimaxi.com', 'tier': 'S'} (severity=YELLOW, Δ5.0)
- deepseek-v3-2.aime26: winner={'value': 89.3, 'trustScore': 0.7, 'sourceUrl': 'https://api.deepseek.com/v3', 'tier': 'S'} (severity=RED, Δ9.8)

### Gaps (90 entries — agent:0 orchestrator:90 — see data/known-gaps.json or next refresh)
- `claude-haiku-4-5.hle` *(orchestrator)*: not reached in agent survey cycle; Humanity's Last Exam data unavailable
- `codestral-22b.aime26` *(orchestrator)*: not reached in agent survey cycle; AIME 2026 data unavailable
- ... and 88 more


## [2026-05-14] — autonomous refresh-all [WARN: cumulative provenance coverage 75.2% below 85% target] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 216 new fills; 58 cells auto-gapped by orchestrator; 149 explicit agent gaps preserved]

[fillRatio:0.69 cells:414/600 contradictions:5 fetch:0.0min tools:None batches:None build:cd09a5f]

### Updated
- 52 models: `claude-haiku-4-5`, `codestral`, `deepseek-coder-v2-16b`, `deepseek-r1-14b`, `deepseek-v3-2`, `deepseek-v4-flash`, `deepseek-v4-pro`, `devstral-2`, `gemini-3-1-flash`, `gemini-3-1-pro`, `gemma-3-27b`, `gemma-4-26b-moe`, `gemma-4-31b`, `gemma-4-e2b`, `gemma-4-e4b`, `glm-4-5-air`, `glm-4-7`, `glm-5-1`, `gpt-4-1`, `gpt-5-4`, `gpt-5-5`, `grok-4-1-fast`, `grok-4-20`, `grok-4-3`, `kimi-k2-6`, `llama-4-maverick`, `llama-4-scout`, `mimo-v2-5`, `mimo-v2-5-pro`, `mimo-v2-flash`, `mimo-v2-pro`, `minimax-m2-1`, `minimax-m2-5`, `minimax-m2-7`, `mistral-large-3`, `mistral-medium-3-5`, `opus-4-7`, `qwen-3-6-27b`, `qwen-3-6-max`, `qwen25-coder-14b`, `qwen25-coder-32b`, `qwen25-coder-7b`, `qwen3-235b`, `qwen3-32b`, `qwen3-5-9b`, `qwen3-6-35b-moe`, `qwen3-6-plus`, `qwen3-coder-30b`, `qwen3-coder-480b`, `qwen3-coder-next`, `sonnet-4-6`, `step-3-5-flash`

### Resolved (auto via trustScore)
- deepseek-v3-2.sweV: winner={'value': 67.8, 'trustScore': 1.0, 'sourceUrl': 'https://www.swebench.com/', 'tier': 'I'} (severity=RED, Δ6.3)
- gemma-4-26b-moe.gpqa: winner={'value': 82.3, 'trustScore': 1.0, 'sourceUrl': 'https://artificialanalysis.ai/models/gemma-4-31b', 'tier': 'I'} (severity=YELLOW, Δ3.1)
- gpt-5-5.aime26: winner={'value': 100.0, 'trustScore': 1.0, 'sourceUrl': 'https://matharena.ai/models/openai_gpt_55', 'tier': 'I'} (severity=RED, Δ18.8)
- mistral-medium-3-5.sweV: winner={'value': 77.6, 'trustScore': 1.0, 'sourceUrl': 'https://benchlm.ai/models/mistral-medium-3-5-128b', 'tier': 'I'} (severity=RED, Δ12.9)
- qwen3-coder-480b.sweV: winner={'value': 69.6, 'trustScore': 1.0, 'sourceUrl': 'https://llm-stats.com/models/qwen3-coder-480b-a35b-instruct', 'tier': 'I'} (severity=YELLOW, Δ3.1)

### Gaps (104 entries — agent:46 orchestrator:58 — see data/known-gaps.json or next refresh)
- `claude-haiku-4-5.hle` *(agent)*: Not found after exhaustive search
- `deepseek-v3-2.tau2` *(agent)*: Not found after exhaustive search
- `deepseek-v4-flash.aime26` *(agent)*: Not found after exhaustive search
- `deepseek-v4-pro.aime26` *(agent)*: Not found after exhaustive search
- `deepseek-coder-v2-16b.gpqa` *(agent)*: Not found after exhaustive search
- `minimax-m2-5.tau2` *(agent)*: Not found after exhaustive search
- `codestral-22b.aime26` *(orchestrator)*: not reached in agent survey cycle; AIME 2026 data unavailable
- `codestral-22b.gpqa` *(orchestrator)*: not reached in agent survey cycle; GPQA Diamond data unavailable
- ... and 96 more


## [2026-05-11] — autonomous refresh-all [WARN: cumulative provenance coverage 75.5% below 85% target] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 281 new fills; 137 cells auto-gapped by orchestrator; 252 explicit agent gaps preserved]

[fillRatio:0.76 cells:453/600 contradictions:134 fetch:0.0min tools:None batches:None build:d65d0e3]

### Updated
- 27 models: `codestral`, `deepseek-v4-pro`, `deepseek-r1-14b`, `llama-4-scout`, `deepseek-coder-v2-16b`, `qwen25-coder-32b`, `mistral-large-3`, `codestral-22b`, `grok-4-20`, `gemini-3-1-pro`, `nemotron-3-super`, `gemma-4-26b-moe`, `gemini-3-1-flash`, `opus-4-7`, `qwen3-coder-next`, `devstral-medium`, `qwen3-5-9b`, `o4-mini`, `grok-3-mini`, `qwen3-235b`, `glm-4-5-air`, `qwen3-6-35b-moe`, `sonnet-4-6`, `llama-4-maverick`, `deepseek-v3-2`, `minimax-m2-7`, `kimi-k2-6`

### Resolved (auto via trustScore)
- opus-4-7.swePro: winner={'value': 64.3, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-04-28'} (severity=red, ΔNone)
- opus-4-7.sweV: winner={'value': 87.6, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- opus-4-7.lcb: winner={'value': 72.2, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- opus-4-7.tb2: winner={'value': 68.54, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- opus-4-7.hle: winner={'value': 46.9, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- opus-4-7.mmluPro: winner={'value': 89.87, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-09'} (severity=yellow, ΔNone)
- opus-4-7.gpqa: winner={'value': 94.2, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- opus-4-7.aime26: winner={'value': 87.6, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- sonnet-4-6.swePro: winner={'value': 40.2, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- sonnet-4-6.sweV: winner={'value': 79.6, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- sonnet-4-6.lcb: winner={'value': 80.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- sonnet-4-6.tb2: winner={'value': 32.4, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- sonnet-4-6.hle: winner={'value': 51.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- sonnet-4-6.mmluPro: winner={'value': 79.2, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- sonnet-4-6.gpqa: winner={'value': 74.1, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- sonnet-4-6.aime26: winner={'value': 32.4, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- claude-haiku-4-5.swePro: winner={'value': 39.45, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- deepseek-v3-2.gpqa: winner={'value': 82.4, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-09T15:04:38Z'} (severity=red, ΔNone)
- deepseek-v3-2.mmluPro: winner={'value': 85.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-09T15:04:38Z'} (severity=red, ΔNone)
- deepseek-v3-2.hle: winner={'value': 25.1, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- deepseek-v3-2.sweV: winner={'value': 73.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-09T15:04:38Z'} (severity=red, ΔNone)
- deepseek-v4-pro.gpqa: winner={'value': 90.1, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- deepseek-v4-pro.lcb: winner={'value': 93.5, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- deepseek-v4-pro.swePro: winner={'value': 55.4, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- deepseek-v4-flash.gpqa: winner={'value': 88.5, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- deepseek-v4-flash.lcb: winner={'value': 91.2, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- deepseek-coder-v2-16b.lcb: winner={'value': 43.4, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- deepseek-coder-v2-16b.sweV: winner={'value': 68.2, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-09T15:04:38Z'} (severity=red, ΔNone)
- deepseek-r1-14b.gpqa: winner={'value': 59.1, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- deepseek-r1-14b.aime26: winner={'value': 71.2, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-09T15:04:38Z'} (severity=yellow, ΔNone)
- deepseek-r1-14b.hle: winner={'value': 71.5, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-09T15:04:37Z'} (severity=red, ΔNone)
- deepseek-v3-2.lcb: winner={'value': 83.3, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-09T15:04:39Z'} (severity=red, ΔNone)
- gemini-3-1-pro.gpqa: winner={'value': 94.3, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- gemini-3-1-pro.lcb: winner={'value': 91.7, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- gemini-3-1-pro.hle: winner={'value': 44.4, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 5, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- gemini-3-1-pro.swePro: winner={'value': 54.2, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- gemini-3-1-pro.tau2: winner={'value': 76.5, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- gemini-3-1-flash.lcb: winner={'value': 72.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- gemini-3-1-flash.aaIdx: winner={'value': 21.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- gemini-3-1-flash.hle: winner={'value': 33.7, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 3, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- gemini-3-1-flash.mmluPro: winner={'value': 89.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- gemma-4-26b-moe.gpqa: winner={'value': 82.3, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 8, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- gemma-4-26b-moe.aaIdx: winner={'value': 31.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- gemma-4-e4b.aaIdx: winner={'value': 15.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- minimax-m2-7.sweV: winner={'value': 78.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- minimax-m2-1.sweV: winner={'value': 74.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- minimax-m2-7.swePro: winner={'value': 56.22, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- minimax-m2-7.tau2: winner={'value': 84.8, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- mistral-large-3.sweV: winner={'value': 55.34, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- mistral-large-3.gpqa: winner={'value': 43.9, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- mistral-large-3.lcb: winner={'value': 82.8, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- mistral-large-3.aaIdx: winner={'value': 52.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- devstral-2.sweV: winner={'value': 72.2, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- devstral-2.gpqa: winner={'value': 59.4, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- devstral-2.lcb: winner={'value': 44.8, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- devstral-small-2.sweV: winner={'value': 68.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- devstral-medium.sweV: winner={'value': 67.5, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- devstral-medium.lcb: winner={'value': 44.8, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- devstral-medium.gpqa: winner={'value': 59.4, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- codestral-22b.sweV: winner={'value': 79.6, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- codestral-22b.lcb: winner={'value': 93.5, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- codestral-22b.swePro: winner={'value': 35.4, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- codestral.sweV: winner={'value': 76.2, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- codestral.swePro: winner={'value': 32.1, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- mistral-medium-3-5.sweV: winner={'value': 77.6, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- gpt-4-1.sweV: winner={'value': 73.4, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- gpt-4-1.gpqa: winner={'value': 66.6, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- gpt-4-1.lcb: winner={'value': 68.2, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- gpt-4-1.aaIdx: winner={'value': 71.2, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- gpt-5-4.sweV: winner={'value': 80.6, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- gpt-5-4.gpqa: winner={'value': 92.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- gpt-5-4.aaIdx: winner={'value': 57.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- gpt-5-4.swePro: winner={'value': 57.7, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- o3.sweV: winner={'value': 71.7, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- o3.aaIdx: winner={'value': 79.4, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- o3.aime26: winner={'value': 88.9, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- o4-mini.sweV: winner={'value': 68.1, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- o4-mini.aime26: winner={'value': 92.7, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- gpt-5-5.sweV: winner={'value': 88.7, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- gpt-5-5.hle: winner={'value': 41.4, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- qwen3-235b.lcb: winner={'value': 74.9, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-09'} (severity=yellow, ΔNone)
- qwen3-235b.aime26: winner={'value': 81.5, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- qwen3-235b.mmluPro: winner={'value': 82.8, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-09'} (severity=yellow, ΔNone)
- qwen3-32b.gpqa: winner={'value': 66.8, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- qwen3-32b.lcb: winner={'value': 54.6, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- qwen3-32b.mmluPro: winner={'value': 79.8, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- qwen3-coder-480b.sweV: winner={'value': 69.6, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- qwen3-6-35b-moe.tb2: winner={'value': 51.5, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- qwen3-6-35b-moe.lcb: winner={'value': 80.4, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- qwen3-6-35b-moe.gpqa: winner={'value': 86.0, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- qwen3-6-35b-moe.tau2: winner={'value': 73.4, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- qwen-3-6-27b.gpqa: winner={'value': 87.8, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- qwen-3-6-27b.lcb: winner={'value': 83.9, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- qwen-3-6-max.tb2: winner={'value': 65.4, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- qwen-3-6-max.gpqa: winner={'value': 86.0, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- qwen-3-6-max.hle: winner={'value': 51.0, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- qwen25-coder-32b.lcb: winner={'value': 37.2, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- qwen25-coder-7b.lcb: winner={'value': 37.6, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- qwen3-5-9b.lcb: winner={'value': 82.7, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-08'} (severity=red, ΔNone)
- grok-3.lcb: winner={'value': 79.4, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- grok-3.aime26: winner={'value': 93.3, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- grok-3-mini.lcb: winner={'value': 70.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- grok-3-mini.aime26: winner={'value': 95.8, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- grok-3-mini.aaIdx: winner={'value': 32.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- grok-4-20.hle: winner={'value': 24.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- grok-4-20.tau2: winner={'value': 93.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- grok-4-20.tb2: winner={'value': 47.1, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- grok-4-20.gpqa: winner={'value': 88.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-11'} (severity=red, ΔNone)
- grok-4-20.sweV: winner={'value': 58.6, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-04-29'} (severity=red, ΔNone)
- grok-4-20.lcb: winner={'value': 79.4, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- grok-4-20.aime26: winner={'value': 95.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- grok-4-1-fast.aaIdx: winner={'value': 24.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- glm-5-1.swePro: winner={'value': 58.4, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- glm-5-1.gpqa: winner={'value': 86.2, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- glm-5-1.hle: winner={'value': 52.3, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- glm-4-7.lcb: winner={'value': 84.9, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- glm-4-7.aime26: winner={'value': 95.7, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- glm-4-7.hle: winner={'value': 42.8, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- glm-4-5-air.aaIdx: winner={'value': 38.0, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- llama-4-maverick.sweV: winner={'value': 76.8, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- llama-4-maverick.gpqa: winner={'value': 69.8, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- llama-4-maverick.lcb: winner={'value': 43.4, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- llama-4-scout.sweV: winner={'value': 68.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- llama-4-scout.gpqa: winner={'value': 57.2, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- llama-4-scout.lcb: winner={'value': 32.8, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 3, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- kimi-k2-6.sweV: winner={'value': 80.2, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- kimi-k2-6.gpqa: winner={'value': 90.5, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 9, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- kimi-k2-6.lcb: winner={'value': 89.6, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- kimi-k2-6.tb2: winner={'value': 66.7, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 8, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- kimi-k2-6.hle: winner={'value': 54.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 6, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- kimi-k2-6.tau2: winner={'value': 70.6, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-09'} (severity=red, ΔNone)
- nemotron-3-super.lcb: winner={'value': 81.19, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 5, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- step-3-5-flash.sweV: winner={'value': 74.4, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 7, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- step-3-5-flash.tb2: winner={'value': 51.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 4, 'latestDate': '2026-05-10'} (severity=red, ΔNone)

### Gaps (240 entries — agent:103 orchestrator:137 — see data/known-gaps.json or next refresh)
- `None` *(agent)*: None
- `None` *(agent)*: None
- `None` *(agent)*: None
- `None` *(agent)*: None
- `None` *(agent)*: None
- `None` *(agent)*: None
- `claude-haiku-4-5.hle` *(orchestrator)*: not reached in agent survey cycle; Humanity's Last Exam data unavailable
- `codestral.aime26` *(orchestrator)*: not reached in agent survey cycle; AIME 2026 data unavailable
- ... and 232 more


## [2026-05-11] — autonomous refresh-all [WARN: cumulative provenance coverage 75.5% below 85% target] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 281 new fills; 137 cells auto-gapped by orchestrator; 252 explicit agent gaps preserved]

[fillRatio:0.76 cells:453/600 contradictions:28 fetch:0.0min tools:None batches:None build:8d59db9]

### Updated
- 44 models: `o4-mini`, `minimax-m2-7`, `gemma-3-27b`, `gemma-4-26b-moe`, `glm-4-7`, `gemini-3-1-pro`, `kimi-k2-6`, `llama-4-scout`, `qwen3-235b`, `qwen3-coder-next`, `grok-3-mini`, `qwen-3-6-max`, `step-3-5-flash`, `gemini-3-1-flash`, `deepseek-v4-pro`, `grok-3`, `qwen3-5-9b`, `glm-4-5-air`, `opus-4-7`, `gemma-4-e4b`, `sonnet-4-6`, `nemotron-3-super`, `grok-4-1-fast`, `deepseek-v3-2`, `qwen25-coder-32b`, `mistral-medium-3-5`, `qwen3-32b`, `llama-4-maverick`, `claude-haiku-4-5`, `gpt-4-1`, `gpt-5-5`, `o3`, `devstral-2`, `qwen3-6-35b-moe`, `deepseek-r1-14b`, `devstral-small-2`, `deepseek-v4-flash`, `mistral-large-3`, `codestral-22b`, `devstral-medium`, `gpt-5-4`, `deepseek-coder-v2-16b`, `codestral`, `grok-4-20`

### Resolved (auto via trustScore)
- opus-4-7.sweV: winner={'value': 87.6, 'trustScore': 0.6667, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- opus-4-7.lcb: winner={'value': 87.6, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- opus-4-7.tb2: winner={'value': 97.8, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- opus-4-7.hle: winner={'value': 97.8, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- opus-4-7.gpqa: winner={'value': 97.8, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- opus-4-7.aime26: winner={'value': 97.8, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- sonnet-4-6.swePro: winner={'value': 79.6, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- sonnet-4-6.sweV: winner={'value': 79.6, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- sonnet-4-6.lcb: winner={'value': 65.55, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- sonnet-4-6.tb2: winner={'value': 79.6, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- sonnet-4-6.mmluPro: winner={'value': 63.3, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- sonnet-4-6.gpqa: winner={'value': 63.3, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- sonnet-4-6.aime26: winner={'value': 63.3, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- claude-haiku-4-5.swePro: winner={'value': 39.45, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-04-26'} (severity=red, ΔNone)
- deepseek-v3-2.sweV: winner={'value': 42.0, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- gpt-4-1.sweV: winner={'value': 73.4, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- gpt-4-1.lcb: winner={'value': 68.2, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- gpt-4-1.aaIdx: winner={'value': 71.2, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- o3.sweV: winner={'value': 71.7, 'trustScore': 0.6667, 'tier': 'I', 'verifications': 2, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- o3.aaIdx: winner={'value': 79.4, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- o3.aime26: winner={'value': 88.9, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- gpt-5-5.sweV: winner={'value': 88.7, 'trustScore': 0.3333, 'tier': 'I', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- qwen3-32b.gpqa: winner={'value': 66.8, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- qwen3-32b.mmluPro: winner={'value': 79.8, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- grok-3.aime26: winner={'value': 93.3, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- grok-4-20.gpqa: winner={'value': 87.5, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)
- grok-4-20.aime26: winner={'value': 95.0, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=yellow, ΔNone)
- llama-4-maverick.lcb: winner={'value': 43.4, 'trustScore': 0.2333, 'tier': 'S', 'verifications': 1, 'latestDate': '2026-05-10'} (severity=red, ΔNone)

### Gaps (240 entries — agent:103 orchestrator:137 — see data/known-gaps.json or next refresh)
- `None` *(agent)*: None
- `None` *(agent)*: None
- `None` *(agent)*: None
- `None` *(agent)*: None
- `None` *(agent)*: None
- `None` *(agent)*: None
- `claude-haiku-4-5.hle` *(orchestrator)*: not reached in agent survey cycle; Humanity's Last Exam data unavailable
- `codestral.aime26` *(orchestrator)*: not reached in agent survey cycle; AIME 2026 data unavailable
- ... and 232 more


## [2026-05-10] — autonomous refresh-all [WARN: cumulative provenance coverage 73.2% below 85% target] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 281 new fills; 45 cells auto-gapped by orchestrator; 204 explicit agent gaps preserved]

[fillRatio:0.73 cells:439/600 contradictions:4 fetch:0.0min tools:None batches:None build:3fba00c]

### Updated
- 56 models: `opus-4-7`, `sonnet-4-6`, `claude-haiku-4-5`, `deepseek-v3-2`, `deepseek-v4-flash`, `deepseek-v4-pro`, `deepseek-coder-v2-16b`, `deepseek-r1-14b`, `gemini-3-1-flash`, `gemini-3-1-pro`, `gemma-3-27b`, `gemma-4-26b-moe`, `gemma-4-31b`, `gemma-4-e2b`, `gemma-4-e4b`, `llama-4-maverick`, `llama-4-scout`, `minimax-m2-5`, `minimax-m2-7`, `minimax-m2-1`, `mistral-large-3`, `codestral-22b`, `devstral-2`, `devstral-medium`, `codestral`, `devstral-small-2`, `mistral-medium-3-5`, `kimi-k2-6`, `nemotron-3-super`, `gpt-5-5`, `o3`, `o4-mini`, `gpt-4-1`, `gpt-5-4`, `qwen3-coder-480b`, `qwen3-coder-30b`, `qwen3-6-35b-moe`, `qwen3-6-plus`, `qwen3-235b`, `qwen-3-6-max`, `qwen-3-6-27b`, `qwen3-coder-next`, `qwen25-coder-32b`, `qwen25-coder-7b`, `qwen25-coder-14b`, `qwen3-5-9b`, `step-3-5-flash`, `grok-3`, `grok-3-mini`, `grok-4-20`, `grok-4-3`, `grok-4-1-fast`, `mimo-v2-flash`, `mimo-v2-5-pro`, `glm-5-1`, `glm-4-7`

### Resolved (auto via trustScore)
- gemini-3-1-flash.lcb: winner={'value': 90.8, 'trustScore': 0.667, 'sourceUrl': 'https://artificialanalysis.ai/models/gemini-3-flash-reasoning', 'tier': 'I'} (severity=RED, Δ18.8)
- gemma-4-26b-moe.gpqa: winner={'value': 82.3, 'trustScore': 0.467, 'sourceUrl': 'https://deepmind.google/models/gemma/gemma-4/', 'tier': 'S'} (severity=YELLOW, Δ3.1)
- gemma-4-e4b.gpqa: winner={'value': 58.6, 'trustScore': 0.467, 'sourceUrl': 'https://deepmind.google/models/gemma/gemma-4/', 'tier': 'S'} (severity=RED, Δ10.6)
- qwen25-coder-32b.lcb: winner={'value': 37.2, 'trustScore': 0.467, 'sourceUrl': 'https://qwenlm.github.io/blog/qwen2.5-coder-family/', 'tier': 'S'} (severity=RED, Δ5.8)

### Gaps (151 entries — agent:106 orchestrator:45 — see data/known-gaps.json or next refresh)
- `opus-4-7.lcb` *(agent)*: agent attempted but found no value
- `opus-4-7.aime26` *(agent)*: agent attempted but found no value
- `sonnet-4-6.aime26` *(agent)*: agent attempted but found no value
- `claude-haiku-4-5.hle` *(agent)*: agent attempted but found no value
- `deepseek-v3-2.tau2` *(agent)*: agent attempted but found no value
- `deepseek-v4-flash.tau2` *(agent)*: agent attempted but found no value
- `codestral.aime26` *(orchestrator)*: not reached in agent survey cycle; AIME 2026 data unavailable
- `codestral.gpqa` *(orchestrator)*: not reached in agent survey cycle; GPQA Diamond data unavailable
- ... and 143 more


## [2026-05-10] — autonomous refresh-all [WARN: cumulative provenance coverage 74.7% below 85% target] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 281 new fills; 38 cells auto-gapped by orchestrator; 204 explicit agent gaps preserved]

[fillRatio:0.75 cells:448/600 contradictions:4 fetch:0.0min tools:None batches:None build:d1b659c]

### Updated
- 60 models: `opus-4-7`, `sonnet-4-6`, `claude-haiku-4-5`, `deepseek-v3-2`, `deepseek-v4-flash`, `deepseek-v4-pro`, `deepseek-coder-v2-16b`, `deepseek-r1-14b`, `gemini-3-1-flash`, `gemini-3-1-pro`, `gemma-3-27b`, `gemma-4-26b-moe`, `gemma-4-31b`, `gemma-4-e2b`, `gemma-4-e4b`, `llama-4-maverick`, `llama-4-scout`, `minimax-m2-5`, `minimax-m2-7`, `minimax-m2-1`, `mistral-large-3`, `codestral-22b`, `devstral-2`, `devstral-medium`, `codestral`, `devstral-small-2`, `mistral-medium-3-5`, `kimi-k2-6`, `nemotron-3-super`, `gpt-5-5`, `o3`, `o4-mini`, `gpt-4-1`, `gpt-5-4`, `qwen3-coder-480b`, `qwen3-coder-30b`, `qwen3-6-35b-moe`, `qwen3-6-plus`, `qwen3-32b`, `qwen3-235b`, `qwen-3-6-max`, `qwen-3-6-27b`, `qwen3-coder-next`, `qwen25-coder-32b`, `qwen25-coder-7b`, `qwen25-coder-14b`, `qwen3-5-9b`, `step-3-5-flash`, `grok-3`, `grok-3-mini`, `grok-4-20`, `grok-4-3`, `grok-4-1-fast`, `mimo-v2-flash`, `mimo-v2-pro`, `mimo-v2-5-pro`, `glm-5-1`, `glm-4-7`, `glm-4-5-air`, `mimo-v2-5`

### Resolved (auto via trustScore)
- gemini-3-1-flash.lcb: winner={'value': 90.8, 'trustScore': 0.667, 'sourceUrl': 'https://artificialanalysis.ai/models/gemini-3-flash-reasoning', 'tier': 'I'} (severity=RED, Δ18.8)
- gemma-4-26b-moe.gpqa: winner={'value': 82.3, 'trustScore': 0.467, 'sourceUrl': 'https://deepmind.google/models/gemma/gemma-4/', 'tier': 'S'} (severity=YELLOW, Δ3.1)
- gemma-4-e4b.gpqa: winner={'value': 58.6, 'trustScore': 0.467, 'sourceUrl': 'https://deepmind.google/models/gemma/gemma-4/', 'tier': 'S'} (severity=RED, Δ10.6)
- qwen25-coder-32b.lcb: winner={'value': 37.2, 'trustScore': 0.467, 'sourceUrl': 'https://qwenlm.github.io/blog/qwen2.5-coder-family/', 'tier': 'S'} (severity=RED, Δ5.8)

### Gaps (142 entries — agent:104 orchestrator:38 — see data/known-gaps.json or next refresh)
- `opus-4-7.lcb` *(agent)*: agent attempted but found no value
- `opus-4-7.aime26` *(agent)*: agent attempted but found no value
- `sonnet-4-6.aime26` *(agent)*: agent attempted but found no value
- `claude-haiku-4-5.hle` *(agent)*: agent attempted but found no value
- `deepseek-v3-2.tau2` *(agent)*: agent attempted but found no value
- `deepseek-v4-flash.tau2` *(agent)*: agent attempted but found no value
- `codestral.aime26` *(orchestrator)*: not reached in agent survey cycle; AIME 2026 data unavailable
- `codestral.hle` *(orchestrator)*: not reached in agent survey cycle; Humanity's Last Exam data unavailable
- ... and 134 more


## [2026-05-10] — autonomous refresh-all [WARN: cumulative provenance coverage 65.7% below 85% target] [WARN: runMetadata missing fields ['toolCallCount', 'fetchAttemptCount', 'batchCount']] [partial: gap-gen supplement: agent found 290 new fills; 167 cells auto-gapped by orchestrator; 97 explicit agent gaps preserved]

[fillRatio:0.66 cells:394/600 contradictions:1 fetch:0.0min tools:None batches:None build:7102753]

### Updated
- 59 models: `opus-4-7`, `sonnet-4-6`, `claude-haiku-4-5`, `deepseek-v3-2`, `deepseek-v4-flash`, `deepseek-v4-pro`, `deepseek-coder-v2-16b`, `deepseek-r1-14b`, `gemini-3-1-flash`, `gemini-3-1-pro`, `gemma-3-27b`, `gemma-4-26b-moe`, `gemma-4-31b`, `gemma-4-e2b`, `gemma-4-e4b`, `llama-4-maverick`, `llama-4-scout`, `minimax-m2-5`, `minimax-m2-7`, `minimax-m2-1`, `mistral-large-3`, `codestral-22b`, `devstral-2`, `devstral-medium`, `codestral`, `devstral-small-2`, `mistral-medium-3-5`, `kimi-k2-6`, `nemotron-3-super`, `gpt-5-5`, `gpt-5-4`, `gpt-4-1`, `o3`, `o4-mini`, `qwen-3-6-27b`, `qwen3-235b`, `qwen3-32b`, `qwen3-6-35b-moe`, `qwen-3-6-max`, `qwen3-6-plus`, `qwen3-coder-30b`, `qwen3-coder-480b`, `qwen3-coder-next`, `qwen25-coder-14b`, `qwen25-coder-32b`, `qwen25-coder-7b`, `qwen3-5-9b`, `step-3-5-flash`, `grok-4-3`, `grok-4-20`, `grok-3`, `grok-3-mini`, `grok-4-1-fast`, `mimo-v2-5-pro`, `mimo-v2-5`, `mimo-v2-flash`, `glm-5-1`, `glm-4-5-air`, `glm-4-7`

### Resolved (auto via trustScore)
- qwen-3-6-max.lcb: winner={'value': 77.5, 'trustScore': 0.667, 'sourceUrl': 'https://llm-stats.com/', 'tier': 'I'} (severity=RED, Δ5.4)

### Gaps (252 entries — agent:85 orchestrator:167 — see data/known-gaps.json or next refresh)
- `gemini-3-1-flash.tb2` *(agent)*: agent attempted but found no value
- `gemini-3-1-flash.aaCoding` *(agent)*: agent attempted but found no value
- `gemini-3-1-flash.aaAgentic` *(agent)*: agent attempted but found no value
- `gemini-3-1-pro.tbHard` *(agent)*: agent attempted but found no value
- `gemini-3-1-pro.aaCoding` *(agent)*: agent attempted but found no value
- `gemini-3-1-pro.aaAgentic` *(agent)*: agent attempted but found no value
- `claude-haiku-4-5.hle` *(orchestrator)*: not reached in agent survey cycle; Humanity's Last Exam data unavailable
- `claude-haiku-4-5.mmluPro` *(orchestrator)*: not reached in agent survey cycle; MMLU-Pro data unavailable
- ... and 244 more


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

### Updated
- data: refresh-all cycle 2026-05-11 — 60 models, 281 new bench fills, 28 contradictions auto-resolved, coverage 75.5%


### Added — 2026-05-10 (FAZ 5.A — SPA fallback via HF Space mirror)

Two banned-list SPA leaderboards now have HF Space mirror entries the
prefetch pipeline can fetch successfully:

- LiveCodeBench → `huggingface.co/spaces/livecodebench/leaderboard` (30KB)
- Berkeley BFCL → `huggingface.co/spaces/gorilla-llm/berkeley-function-calling-leaderboard` (37KB)

Mirror entries marked `format: static_html_table`, `tier: I`, with
`mirrorOf` field pointing back to the original SPA. Same `publishes[]` so
agents see the bench coverage. matharena.ai and epoch.ai remain
unmirrored — manual investigation needed for those vendors.

### Changed — 2026-05-10 (FAZ 5.B + 5.C — N/A taxonomy + bench universe split)

Coverage rose from 32.5% → 65.7% via two structural reforms:

**FAZ 5.B — N/A rule taxonomy (2 → 8 canonical rules):**
- New rules: vendor-no-niche-bench-publish, legacy-bench-superseded,
  closed-weight-no-local-runtime, compute-only-public-no-elo,
  vendor-emphasis-mismatch, edge-model-no-frontier-bench.
- synth.py keyword matching expanded; rationale strings from agent
  naCandidates map to canonical rule.
- **User policy:** N/A is NEVER permanent. Every cycle re-attempts the
  cell. Fill found → fill wins (fill > N/A precedence).

**FAZ 5.C — coreBenchKeys vs emergingBenchKeys split:**
- 10 CORE (≥30% fill): sweV, gpqa, lcb, aaIdx, tb2, hle, swePro,
  mmluPro, tau2, aime26.
- 16 EMERGING (<30% fill): the rest — surveyed every cycle, excluded
  from coverage formula so vendor-doesn't-publish niche bench
  doesn't drag headline metric.
- `whitelist.py` new `emerging_bench_keys()` + `all_bench_keys()`.
- audit-data-coherence + audit-bench-source-mapping accept emerging.

Cycle 2026-05-10-C metrics:
  Coverage:        32.5% → **65.7%**
  Total cells:     1560 → 600 (core)
  N/A cells:       2 → 8 (more rationale-keyword matches)
  Updated models:  59

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
