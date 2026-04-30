#!/usr/bin/env python3
"""Generate unified .aicodermap-agent-out.json from 5-bucket agent findings.
Run once, then gap-gen + merge.py proceed normally.
"""

import json, datetime, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / ".aicodermap-agent-out.json"

TODAY = "2026-04-30"

# ── All confirmed fills from 5 bucket agents ─────────────────────────────────
UPDATES = {
    "gpt-5-4": {
        "tau2": 92.8,
        "arcAgi2": 73.3,
        "mmluPro": 78.0,
        "cfElo": 1484,
        "aaOmni": 43,
    },
    "gpt-5-5": {"cfElo": 1488, "aaOmni": 57},
    "sonnet-4-6": {"tau2": 87.5, "mcpA": 61.3, "sweMulti": 75.9, "browseComp": 74.0},
    "gemini-3-1-flash": {"mmluPro": 89.0},
    "gemma-3-27b": {"mmluPro": 67.5},
    "gemma-4-26b-moe": {"mmluPro": 82.6},
    "deepseek-v3-2": {
        "sweV": 67.8,
        "lcb": 74.1,
        "gpqa": 79.9,
        "hle": 19.8,
        "mmluPro": 85.0,
        "browseComp": 40.1,
        "simpleQa": 97.1,
        "cfElo": 2121,
        "tb2": 37.7,
        "sweMulti": 57.9,
    },
    "devstral-2": {"mmluPro": 76.2},
    "qwen3-32b": {"mmluPro": 65.5},
    "qwen3-6-35b-moe": {"mmluPro": 85.2, "tau3": 67.2, "nl2Repo": 29.4},
    "qwen-3-6-27b": {"mmluPro": 86.2, "nl2Repo": 36.2},
    "qwen-3-6-max": {"simpleQa": 52.0, "nl2Repo": 42.9},
    "qwen25-coder-14b": {"lcb": 37.6},
    "qwen3-235b": {"sweV": 34.4},
    "glm-5-1": {"nl2Repo": 42.7},
    "kimi-k2-6": {
        "browseComp": 83.2,
        "mcpA": 66.6,
        "mmluPro": 84.6,
        "simpleQa": 43,
        "tb2": 66.7,
    },
    "step-3-5-flash": {"mmluPro": 84.4, "gpqa": 83.5, "hle": 23.1},
    "nemotron-3-super": {"mmluPro": 83.7, "tbHard": 29},
    "minimax-m2-5": {"swePro": 55.4, "sweMulti": 51.3, "browseComp": 76.3},
    "minimax-m2-7": {"tau2": 84.8},
    "mimo-v2-flash": {"browseComp": 45.4},
}

# ── Sources provenance ────────────────────────────────────────────────────────
SOURCES = {
    "gpt-5-4.tau2": {
        "source": "OpenAI GPT-5.5 launch blog (GPT-5.4 baseline)",
        "url": "https://openai.com/index/introducing-gpt-5-5/",
        "tier": "S",
        "trustScore": 0.7,
    },
    "gpt-5-4.arcAgi2": {
        "source": "OpenAI GPT-5.5 launch blog (GPT-5.4 baseline)",
        "url": "https://openai.com/index/introducing-gpt-5-5/",
        "tier": "S",
        "trustScore": 0.7,
    },
    "gpt-5-4.mmluPro": {
        "source": "TokenMix MMLU leaderboard",
        "url": "https://tokenmix.ai/blog/mmlu-benchmark-leaderboard",
        "tier": "C",
        "trustScore": 0.27,
    },
    "gpt-5-4.cfElo": {
        "source": "LMArena Apr-2026 report",
        "url": "https://aidevdayindia.org/blogs/lmsys-chatbot-arena-current-rankings/gpt-5-1-high-elo-lmarena-performance.html",
        "tier": "C",
        "trustScore": 0.27,
    },
    "gpt-5-4.aaOmni": {
        "source": "Artificial Analysis GPT-5.5 article (derived: GPT-5.5=57% +14pp over GPT-5.4)",
        "url": "https://artificialanalysis.ai/articles/openai-gpt5-5-is-the-new-leading-AI-model",
        "tier": "I",
        "trustScore": 0.67,
    },
    "gpt-5-5.cfElo": {
        "source": "LMArena Leaderboard Changelog Apr-27-2026",
        "url": "https://arena.ai/blog/leaderboard-changelog/",
        "tier": "I",
        "trustScore": 0.67,
    },
    "gpt-5-5.aaOmni": {
        "source": "Artificial Analysis GPT-5.5 article",
        "url": "https://artificialanalysis.ai/articles/openai-gpt5-5-is-the-new-leading-AI-model",
        "tier": "I",
        "trustScore": 0.67,
    },
    "sonnet-4-6.tau2": {
        "source": "BenchLM Sonnet-4.6 model page (I-tier)",
        "url": "https://benchlm.ai/models/sonnet-4-6",
        "tier": "I",
        "trustScore": 0.67,
    },
    "sonnet-4-6.mcpA": {
        "source": "Anthropic Claude Sonnet-4.6 system card",
        "url": "https://www.anthropic.com/news/claude-sonnet-4-6",
        "tier": "S",
        "trustScore": 0.7,
    },
    "sonnet-4-6.sweMulti": {
        "source": "Anthropic Claude Sonnet-4.6 system card",
        "url": "https://www.anthropic.com/news/claude-sonnet-4-6",
        "tier": "S",
        "trustScore": 0.7,
    },
    "sonnet-4-6.browseComp": {
        "source": "Anthropic Claude Sonnet-4.6 system card (single-agent)",
        "url": "https://www.anthropic.com/news/claude-sonnet-4-6",
        "tier": "S",
        "trustScore": 0.7,
    },
    "gemini-3-1-flash.mmluPro": {
        "source": "Artificial Analysis Gemini-3.1-Flash model page",
        "url": "https://artificialanalysis.ai/models/gemini-3-1-flash",
        "tier": "I",
        "trustScore": 0.67,
    },
    "gemma-3-27b.mmluPro": {
        "source": "Hugging Face Gemma 3 blog",
        "url": "https://huggingface.co/blog/gemma3",
        "tier": "I",
        "trustScore": 0.87,
    },
    "gemma-4-26b-moe.mmluPro": {
        "source": "Google DeepMind Gemma 4 tech report",
        "url": "https://deepmind.google/models/gemma/gemma-4/",
        "tier": "S",
        "trustScore": 0.47,
    },
    "deepseek-v3-2.sweV": {
        "source": "DeepSeek V3.2-Exp Official GitHub README",
        "url": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
        "tier": "S",
        "trustScore": 0.7,
    },
    "deepseek-v3-2.lcb": {
        "source": "DeepSeek V3.2-Exp Official GitHub README",
        "url": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
        "tier": "S",
        "trustScore": 0.7,
    },
    "deepseek-v3-2.gpqa": {
        "source": "DeepSeek V3.2-Exp Official GitHub README",
        "url": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
        "tier": "S",
        "trustScore": 0.7,
    },
    "deepseek-v3-2.hle": {
        "source": "DeepSeek V3.2-Exp Official GitHub README",
        "url": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
        "tier": "S",
        "trustScore": 0.7,
    },
    "deepseek-v3-2.mmluPro": {
        "source": "DeepSeek V3.2-Exp Official GitHub README",
        "url": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
        "tier": "S",
        "trustScore": 0.7,
    },
    "deepseek-v3-2.browseComp": {
        "source": "DeepSeek V3.2-Exp Official GitHub README",
        "url": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
        "tier": "S",
        "trustScore": 0.7,
    },
    "deepseek-v3-2.simpleQa": {
        "source": "DeepSeek V3.2-Exp Official GitHub README",
        "url": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
        "tier": "S",
        "trustScore": 0.7,
    },
    "deepseek-v3-2.cfElo": {
        "source": "DeepSeek V3.2-Exp Official GitHub README",
        "url": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
        "tier": "S",
        "trustScore": 0.7,
    },
    "deepseek-v3-2.tb2": {
        "source": "DeepSeek V3.2-Exp Official GitHub README",
        "url": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
        "tier": "S",
        "trustScore": 0.7,
    },
    "deepseek-v3-2.sweMulti": {
        "source": "DeepSeek V3.2-Exp Official GitHub README",
        "url": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
        "tier": "S",
        "trustScore": 0.7,
    },
    "devstral-2.mmluPro": {
        "source": "Mistral AI Devstral 2 release blog",
        "url": "https://mistral.ai/news/devstral-2-vibe-cli",
        "tier": "S",
        "trustScore": 0.47,
    },
    "qwen3-32b.mmluPro": {
        "source": "Qwen3 technical report (arxiv)",
        "url": "https://arxiv.org/html/2505.09388v1",
        "tier": "S",
        "trustScore": 0.47,
    },
    "qwen3-6-35b-moe.mmluPro": {
        "source": "Qwen3.6 blog tech report",
        "url": "https://qwenlm.github.io/blog/qwen3.6/",
        "tier": "S",
        "trustScore": 0.47,
    },
    "qwen3-6-35b-moe.tau3": {
        "source": "Qwen3.6-35B-A3B HF model card",
        "url": "https://huggingface.co/Qwen/Qwen3.6-35B-A3B",
        "tier": "C",
        "trustScore": 0.27,
    },
    "qwen3-6-35b-moe.nl2Repo": {
        "source": "BenchLM Qwen3.6-35B-A3B model page",
        "url": "https://benchlm.ai/models/qwen3.6-35b-a3b",
        "tier": "I",
        "trustScore": 0.67,
    },
    "qwen-3-6-27b.mmluPro": {
        "source": "Qwen3.6 blog tech report",
        "url": "https://qwenlm.github.io/blog/qwen3.6/",
        "tier": "S",
        "trustScore": 0.47,
    },
    "qwen-3-6-27b.nl2Repo": {
        "source": "BenchLM Qwen3.6-27B model page",
        "url": "https://benchlm.ai/models/qwen3.6-27b",
        "tier": "I",
        "trustScore": 0.67,
    },
    "qwen-3-6-max.simpleQa": {
        "source": "Qwen3.6-Max-Preview blog release",
        "url": "https://qwenlm.github.io/blog/qwen3.6/",
        "tier": "S",
        "trustScore": 0.47,
    },
    "qwen-3-6-max.nl2Repo": {
        "source": "BenchLM Qwen3.6-Max model page",
        "url": "https://benchlm.ai/models/qwen3.6-max",
        "tier": "I",
        "trustScore": 0.67,
    },
    "qwen25-coder-14b.lcb": {
        "source": "Qwen2.5-Coder family blog",
        "url": "https://qwenlm.github.io/blog/qwen2.5-coder-family/",
        "tier": "S",
        "trustScore": 0.47,
    },
    "qwen3-235b.sweV": {
        "source": "Kimi K2.6 technical comparison paper (HF)",
        "url": "https://huggingface.co/moonshotai/Kimi-K2.6",
        "tier": "C",
        "trustScore": 0.27,
    },
    "glm-5-1.nl2Repo": {
        "source": "ZAI GLM-5.1 official release announcement",
        "url": "https://docs.z.ai/api-reference",
        "tier": "S",
        "trustScore": 0.47,
    },
    "kimi-k2-6.browseComp": {
        "source": "Moonshot Kimi K2.6 official announcement",
        "url": "https://platform.moonshot.cn/docs",
        "tier": "S",
        "trustScore": 0.7,
    },
    "kimi-k2-6.mcpA": {
        "source": "BuildFastWithAI Kimi K2.6 review",
        "url": "https://www.buildfastwithai.com/blogs/kimi-k2-6-review",
        "tier": "C",
        "trustScore": 0.27,
    },
    "kimi-k2-6.mmluPro": {
        "source": "BenchLM Kimi K2.6 model page",
        "url": "https://benchlm.ai/models/kimi-k2-6",
        "tier": "C",
        "trustScore": 0.27,
    },
    "kimi-k2-6.simpleQa": {
        "source": "BenchLM Kimi K2.6 model page",
        "url": "https://benchlm.ai/models/kimi-k2-6",
        "tier": "C",
        "trustScore": 0.27,
    },
    "kimi-k2-6.tb2": {
        "source": "Moonshot Kimi K2.6 official announcement (Terminal-Bench 2.0)",
        "url": "https://platform.moonshot.cn/docs",
        "tier": "S",
        "trustScore": 0.7,
    },
    "step-3-5-flash.mmluPro": {
        "source": "StepFun Step-3.5-Flash model card (HF/arxiv)",
        "url": "https://www.stepfun.com",
        "tier": "S",
        "trustScore": 0.47,
    },
    "step-3-5-flash.gpqa": {
        "source": "StepFun Step-3.5-Flash model card (HF/arxiv)",
        "url": "https://www.stepfun.com",
        "tier": "S",
        "trustScore": 0.47,
    },
    "step-3-5-flash.hle": {
        "source": "StepFun Step-3.5-Flash model card (HF/arxiv)",
        "url": "https://www.stepfun.com",
        "tier": "S",
        "trustScore": 0.47,
    },
    "nemotron-3-super.mmluPro": {
        "source": "NVIDIA Nemotron-3 Super tech report/comparison",
        "url": "https://build.nvidia.com",
        "tier": "S",
        "trustScore": 0.47,
    },
    "nemotron-3-super.tbHard": {
        "source": "Artificial Analysis Nemotron-3-Super article",
        "url": "https://artificialanalysis.ai/models/nemotron-3-super",
        "tier": "I",
        "trustScore": 0.67,
    },
    "minimax-m2-5.swePro": {
        "source": "MiniMax MiniMax-M2.5 official release (vendor)",
        "url": "https://platform.minimaxi.com/document",
        "tier": "S",
        "trustScore": 0.7,
    },
    "minimax-m2-5.sweMulti": {
        "source": "MiniMax MiniMax-M2.5 official release (vendor)",
        "url": "https://platform.minimaxi.com/document",
        "tier": "S",
        "trustScore": 0.7,
    },
    "minimax-m2-5.browseComp": {
        "source": "MiniMax MiniMax-M2.5 official release (vendor)",
        "url": "https://platform.minimaxi.com/document",
        "tier": "S",
        "trustScore": 0.7,
    },
    "minimax-m2-7.tau2": {
        "source": "BenchLM MiniMax-M2.7 comparison",
        "url": "https://benchlm.ai/models/minimax-m2-7",
        "tier": "C",
        "trustScore": 0.27,
    },
    "mimo-v2-flash.browseComp": {
        "source": "Xiaomi MiMo-V2 tech report (arxiv 2601.02780)",
        "url": "https://arxiv.org/abs/2601.02780",
        "tier": "S",
        "trustScore": 0.47,
    },
}

# ── Contradictions ────────────────────────────────────────────────────────────
CONTRADICTIONS = [
    # gpt-5-5.hle: S-tier existing wins over new C-tier — NO data change
    {
        "modelId": "gpt-5-5",
        "field": "hle",
        "candidates": [
            {
                "value": 41.4,
                "source": "OpenAI GPT-5.5 launch blog",
                "url": "https://openai.com/index/introducing-gpt-5-5/",
                "tier": "S",
                "fetched": "2026-04-29",
                "verifications": 2,
                "trustScore": 0.7,
            },
            {
                "value": 52.2,
                "source": "automatio.ai GPT-5.5 model page",
                "url": "https://automatio.ai/models/gpt-5-5",
                "tier": "C",
                "fetched": "2026-04-30",
                "verifications": 1,
                "trustScore": 0.27,
            },
        ],
        "delta": 10.8,
        "severity": "RED",
        "autoResolveWinner": {
            "value": 41.4,
            "trustScore": 0.7,
            "sourceUrl": "https://openai.com/index/introducing-gpt-5-5/",
            "tier": "S",
        },
    },
    # sonnet-4-6.tau2: I-tier vs S-tier derived
    {
        "modelId": "sonnet-4-6",
        "field": "tau2",
        "candidates": [
            {
                "value": 87.5,
                "source": "BenchLM Sonnet-4.6",
                "url": "https://benchlm.ai/models/sonnet-4-6",
                "tier": "I",
                "fetched": "2026-04-30",
                "verifications": 1,
                "trustScore": 0.67,
            },
            {
                "value": 94.8,
                "source": "Anthropic system card aggregate (derived)",
                "url": "https://www.anthropic.com/news/claude-sonnet-4-6",
                "tier": "S",
                "fetched": "2026-04-30",
                "verifications": 1,
                "trustScore": 0.47,
            },
        ],
        "delta": 7.3,
        "severity": "RED",
        "autoResolveWinner": {
            "value": 87.5,
            "trustScore": 0.67,
            "sourceUrl": "https://benchlm.ai/models/sonnet-4-6",
            "tier": "I",
        },
    },
    # deepseek-v3-2.sweV: newer S-tier wins (GREEN)
    {
        "modelId": "deepseek-v3-2",
        "field": "sweV",
        "candidates": [
            {
                "value": 70.0,
                "source": "DeepSeek V3 prior vendor docs",
                "url": "https://api-docs.deepseek.com",
                "tier": "S",
                "fetched": "2026-04-28",
                "verifications": 1,
                "trustScore": 0.47,
            },
            {
                "value": 67.8,
                "source": "DeepSeek V3.2-Exp Official GitHub",
                "url": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
                "tier": "S",
                "fetched": "2026-04-30",
                "verifications": 1,
                "trustScore": 0.7,
            },
        ],
        "delta": 2.2,
        "severity": "GREEN",
        "autoResolveWinner": {
            "value": 67.8,
            "trustScore": 0.7,
            "sourceUrl": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
            "tier": "S",
        },
    },
    # deepseek-v3-2.lcb: S-tier wins over prior C-tier (RED)
    {
        "modelId": "deepseek-v3-2",
        "field": "lcb",
        "candidates": [
            {
                "value": 83.3,
                "source": "morphllm community comparison (C-tier, likely error)",
                "url": "https://morphllm.com",
                "tier": "C",
                "fetched": "2026-04-28",
                "verifications": 1,
                "trustScore": 0.27,
            },
            {
                "value": 74.1,
                "source": "DeepSeek V3.2-Exp Official GitHub",
                "url": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
                "tier": "S",
                "fetched": "2026-04-30",
                "verifications": 1,
                "trustScore": 0.7,
            },
        ],
        "delta": 9.2,
        "severity": "RED",
        "autoResolveWinner": {
            "value": 74.1,
            "trustScore": 0.7,
            "sourceUrl": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
            "tier": "S",
        },
    },
    # deepseek-v3-2.gpqa: newer S-tier wins (GREEN)
    {
        "modelId": "deepseek-v3-2",
        "field": "gpqa",
        "candidates": [
            {
                "value": 82.4,
                "source": "Prior cycle vendor doc",
                "url": "https://api-docs.deepseek.com",
                "tier": "S",
                "fetched": "2026-04-28",
                "verifications": 1,
                "trustScore": 0.47,
            },
            {
                "value": 79.9,
                "source": "DeepSeek V3.2-Exp Official GitHub",
                "url": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
                "tier": "S",
                "fetched": "2026-04-30",
                "verifications": 1,
                "trustScore": 0.7,
            },
        ],
        "delta": 2.5,
        "severity": "GREEN",
        "autoResolveWinner": {
            "value": 79.9,
            "trustScore": 0.7,
            "sourceUrl": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
            "tier": "S",
        },
    },
    # deepseek-v3-2.hle: RED-critical — prior was likely cross-model error
    {
        "modelId": "deepseek-v3-2",
        "field": "hle",
        "candidates": [
            {
                "value": 40.8,
                "source": "Prior cycle C-tier (likely cross-model error)",
                "url": "https://deepinfra.com",
                "tier": "C",
                "fetched": "2026-04-28",
                "verifications": 1,
                "trustScore": 0.27,
            },
            {
                "value": 19.8,
                "source": "DeepSeek V3.2-Exp Official GitHub",
                "url": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
                "tier": "S",
                "fetched": "2026-04-30",
                "verifications": 1,
                "trustScore": 0.7,
            },
        ],
        "delta": 21.0,
        "severity": "RED",
        "autoResolveWinner": {
            "value": 19.8,
            "trustScore": 0.7,
            "sourceUrl": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
            "tier": "S",
        },
    },
    # kimi-k2-6.tb2: prior value suspicious (equals sweV=80.2), vendor says 66.7 (RED)
    {
        "modelId": "kimi-k2-6",
        "field": "tb2",
        "candidates": [
            {
                "value": 80.2,
                "source": "Prior cycle (suspected data error — same value as sweV)",
                "url": "",
                "tier": "C",
                "fetched": "2026-04-28",
                "verifications": 1,
                "trustScore": 0.27,
            },
            {
                "value": 66.7,
                "source": "Moonshot Kimi K2.6 official release (Terminal-Bench 2.0)",
                "url": "https://platform.moonshot.cn/docs",
                "tier": "S",
                "fetched": "2026-04-30",
                "verifications": 1,
                "trustScore": 0.7,
            },
        ],
        "delta": 13.5,
        "severity": "RED",
        "autoResolveWinner": {
            "value": 66.7,
            "trustScore": 0.7,
            "sourceUrl": "https://platform.moonshot.cn/docs",
            "tier": "S",
        },
    },
    # minimax-m2-5.swePro: prior value was for a different model version (RED)
    {
        "modelId": "minimax-m2-5",
        "field": "swePro",
        "candidates": [
            {
                "value": 36.81,
                "source": "Prior cycle Scale SEAL (likely minimax-2.1 data)",
                "url": "https://labs.scale.com/leaderboard",
                "tier": "C",
                "fetched": "2026-04-28",
                "verifications": 1,
                "trustScore": 0.27,
            },
            {
                "value": 55.4,
                "source": "MiniMax MiniMax-M2.5 official vendor release",
                "url": "https://platform.minimaxi.com/document",
                "tier": "S",
                "fetched": "2026-04-30",
                "verifications": 1,
                "trustScore": 0.7,
            },
        ],
        "delta": 18.59,
        "severity": "RED",
        "autoResolveWinner": {
            "value": 55.4,
            "trustScore": 0.7,
            "sourceUrl": "https://platform.minimaxi.com/document",
            "tier": "S",
        },
    },
]

# ── Key gaps (explicitly tried by agents, not found) ──────────────────────────
GAPS = [
    # webDevElo (LMArena SPA) — all models tried, none succeeded
    *[
        {
            "key": f"{m}.webDevElo",
            "reason": "LMArena WebDev Arena is SPA (spa_full) — no static Elo extraction possible via search snippets",
            "triedSources": ["https://web.lmarena.ai/leaderboard"],
            "triedQueries": [
                f"{m} LMArena WebDev Arena elo score 2026",
                f"{m} webdev arena chatbot elo 2026",
            ],
            "triedFormats": ["spa_full", "websearch_snippet"],
        }
        for m in [
            "gpt-5-4",
            "gpt-5-5",
            "opus-4-7",
            "sonnet-4-6",
            "claude-haiku-4-5",
            "grok-4-20",
            "grok-4-3",
            "grok-4-1-fast",
            "gemini-3-1-flash",
            "gemini-3-1-pro",
            "deepseek-v3-2",
            "deepseek-v4-pro",
            "mistral-large-3",
            "devstral-2",
            "qwen3-235b",
            "qwen3-6-35b-moe",
            "qwen-3-6-27b",
            "qwen-3-6-max",
            "kimi-k2-6",
            "glm-5-1",
            "minimax-m2-5",
            "nemotron-3-super",
            "llama-4-maverick",
        ]
    ],
    # nl2Repo — Scale SEAL SPA/restricted for most models
    *[
        {
            "key": f"{m}.nl2Repo",
            "reason": "Scale SEAL NL2Repo leaderboard SPA — model not found in search snippets",
            "triedSources": ["https://labs.scale.com/leaderboard"],
            "triedQueries": [
                f"{m} Scale SEAL nl2repo NL2Repo score 2026",
                f'"nl2repo" "{m}" benchmark score',
            ],
            "triedFormats": ["static_html_table", "websearch_snippet"],
        }
        for m in [
            "gpt-5-4",
            "gpt-5-5",
            "opus-4-7",
            "sonnet-4-6",
            "claude-haiku-4-5",
            "grok-4-20",
            "grok-4-3",
            "grok-4-1-fast",
            "deepseek-v4-pro",
            "deepseek-v4-flash",
            "mistral-large-3",
            "devstral-2",
            "codestral",
            "qwen3-235b",
            "qwen3-32b",
            "minimax-m2-5",
            "minimax-m2-7",
            "llama-4-maverick",
            "llama-4-scout",
            "nemotron-3-super",
            "mimo-v2-flash",
            "mimo-v2-pro",
            "step-3-5-flash",
            "kimi-k2-6",
        ]
    ],
    # tau3 — tau-bench canonical mostly MiMo/Qwen3/GLM
    *[
        {
            "key": f"{m}.tau3",
            "reason": "TAU3-bench top scorers are MiMo/Qwen/GLM-based — model not on leaderboard",
            "triedSources": [
                "https://github.com/sierra-research/tau-bench",
                "https://benchlm.ai/benchmarks/tau3Bench",
            ],
            "triedQueries": [
                f"{m} tau-bench v3 tau3 score 2026",
                f'"{m}" tau3 agentic benchmark 2026',
            ],
            "triedFormats": ["static_html_table", "websearch_snippet"],
        }
        for m in [
            "gpt-5-4",
            "gpt-5-5",
            "opus-4-7",
            "sonnet-4-6",
            "claude-haiku-4-5",
            "grok-4-20",
            "grok-4-3",
            "grok-4-1-fast",
            "gemini-3-1-flash",
            "gemini-3-1-pro",
            "deepseek-v3-2",
            "mistral-large-3",
            "devstral-2",
            "minimax-m2-5",
            "minimax-m2-7",
            "llama-4-maverick",
            "llama-4-scout",
            "nemotron-3-super",
            "step-3-5-flash",
            "kimi-k2-6",
        ]
    ],
    # grok models — specific gaps
    {
        "key": "grok-4-3.swePro",
        "reason": "Grok-4-3 not listed on Scale SEAL SWE-bench Pro leaderboard (new model)",
        "triedSources": ["https://labs.scale.com/leaderboard/swe_bench_pro_public"],
        "triedQueries": [
            "Grok 4.3 SWE-bench Pro score 2026",
            "xAI Grok-4.3 swePro benchmark",
        ],
        "triedFormats": ["static_html_table", "websearch_snippet"],
    },
    {
        "key": "grok-4-3.sweV",
        "reason": "Grok-4-3 not listed on SWE-bench Verified leaderboard",
        "triedSources": [
            "https://www.swebench.com/",
            "https://github.com/SWE-bench/experiments",
        ],
        "triedQueries": [
            "Grok 4.3 SWE-bench Verified score 2026",
            "xAI Grok-4.3 sweV benchmark",
        ],
        "triedFormats": ["spa_partial", "static_html_table", "websearch_snippet"],
    },
    {
        "key": "grok-4-1-fast.lcb",
        "reason": "Grok-4.1-fast not listed on LiveCodeBench as separate entry",
        "triedSources": [
            "https://livecodebench.github.io/leaderboard.html",
            "https://livecodebench.com/",
        ],
        "triedQueries": [
            "Grok 4.1 fast LiveCodeBench score 2026",
            "xAI grok-4.1-fast LCB benchmark",
        ],
        "triedFormats": ["spa_full", "static_html_table", "websearch_snippet"],
    },
    # deepseek-v3-2 specific gaps
    {
        "key": "deepseek-v3-2.nl2Repo",
        "reason": "DeepSeek V3.2 not on BenchLM NL2Repo; official GitHub has no NL2Repo entry",
        "triedSources": [
            "https://benchlm.ai/benchmarks/nl2Repo",
            "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
        ],
        "triedQueries": [
            "DeepSeek V3.2 NL2Repo benchmark score 2026",
            "deepseek-v3-2 nl2repo github",
        ],
        "triedFormats": [
            "static_html_table",
            "github_raw_markdown",
            "websearch_snippet",
        ],
    },
    {
        "key": "deepseek-v3-2.tau3",
        "reason": "TAU3-bench not in official DeepSeek V3.2 GitHub or any known leaderboard",
        "triedSources": ["https://github.com/deepseek-ai/DeepSeek-V3.2-Exp"],
        "triedQueries": [
            "DeepSeek V3.2 TAU3 benchmark 2026",
            "deepseek-v3.2 tau-bench v3",
        ],
        "triedFormats": ["github_raw_markdown", "websearch_snippet"],
    },
    # SWE-bench SPA gaps
    *[
        {
            "key": f"{m}.sweV",
            "reason": "SWE-bench Verified leaderboard SPA — model not found in search snippets",
            "triedSources": [
                "https://www.swebench.com/",
                "https://github.com/SWE-bench/experiments",
            ],
            "triedQueries": [
                f"{m} SWE-bench Verified score 2026",
                f'"{m}" sweV benchmark',
            ],
            "triedFormats": ["spa_partial", "static_html_table", "websearch_snippet"],
        }
        for m in [
            "gemma-4-26b-moe",
            "gemma-3-27b",
            "gemma-4-31b",
            "qwen3-32b",
            "qwen25-coder-14b",
            "qwen25-coder-32b",
            "qwen25-coder-7b",
            "deepseek-coder-v2-16b",
            "deepseek-r1-14b",
        ]
    ],
]

# ── Build artifact ────────────────────────────────────────────────────────────
NOW = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

models_arr = []
for model_id, bench_updates in UPDATES.items():
    sources = [
        {
            **v,
            "key": k,
            "value": bench_updates[k.split(".")[-1]],
            "fetched": TODAY,
            "verifications": 1,
        }
        for k, v in SOURCES.items()
        if k.startswith(model_id + ".")
    ]
    models_arr.append(
        {
            "id": model_id,
            "updates": {"bench": bench_updates, "lastUpdated": NOW},
            "sourcesAdded": sources,
            "notApplicable": [],
        }
    )

total_fills = sum(len(v) for v in UPDATES.values())
total_gaps = len(GAPS)

artifact = {
    "confidence": "MEDIUM",
    "synthesis": (
        f"5-bucket parallel refresh 2026-04-30. {total_fills} bench fills across "
        f"{len(UPDATES)} models. Critical: deepseek-v3-2 hle corrected 40.8→19.8 "
        "(prior value was cross-model error, S-tier GitHub README wins); "
        "deepseek-v3-2 lcb corrected 83.3→74.1 (C-tier vs S-tier RED). "
        "minimax-m2-5 swePro corrected 36.81→55.4 (prior was minimax-2.1 data). "
        "kimi-k2-6 tb2 corrected 80.2→66.7 (prior matched sweV, suspicious). "
        "First nl2Repo fills: qwen-3-6-27b=36.2, qwen-3-6-max=42.9, "
        "qwen3-6-35b-moe=29.4, glm-5-1=42.7. "
        "webDevElo/tau3 remain globally sparse (LMArena SPA blocker, tau3 leaderboard "
        "limited to top-10 specialist models). "
        "Health: Scale SEAL ok/static_html_table, AA ok/spa_full, LMArena ok/spa_full."
    ),
    "lineupChanges": {"new": [], "deprecated": [], "renamed": [], "removed": []},
    "lineup": {
        "openai": {"active": ["gpt-5-5", "gpt-5-4"], "deprecated": [], "renamed": []},
        "anthropic": {
            "active": ["opus-4-7", "sonnet-4-6", "claude-haiku-4-5"],
            "deprecated": [],
            "renamed": [],
        },
        "xai": {
            "active": ["grok-4-20", "grok-4-3", "grok-4-1-fast"],
            "deprecated": [],
            "renamed": [],
        },
    },
    "models": models_arr,
    "newModels": [],
    "contradictions": CONTRADICTIONS,
    "gaps": GAPS,
    "coverageMatrix": {
        "totalCells": 1175,
        "filledCells": total_fills,
        "filledThisCycle": total_fills,
        "gapsRecorded": total_gaps,
        "notApplicableCells": 0,
        "byBench": {},
        "byModel": {},
    },
    "validationCoverage": round(total_fills / 1175, 3),
    "partialReturn": True,
    "partialReason": {
        "code": "multi_bucket_partial",
        "cellsAttempted": total_fills + total_gaps,
        "cellsFilled": total_fills,
        "note": "5 bucket agents each covered partial scope; gap-gen supplements remaining cells",
    },
    "runtime": {
        "healthChecks": {
            "labs.scale.com": {
                "status": "ok",
                "observedFormat": "static_html_table",
                "observedAt": TODAY,
            },
            "artificialanalysis.ai": {
                "status": "ok",
                "observedFormat": "spa_full",
                "observedAt": TODAY,
            },
            "web.lmarena.ai": {
                "status": "ok",
                "observedFormat": "spa_full",
                "observedAt": TODAY,
            },
            "livecodebench.github.io": {
                "status": "ok",
                "observedFormat": "spa_full",
                "observedAt": TODAY,
            },
            "swebench.com": {
                "status": "ok",
                "observedFormat": "spa_partial",
                "observedAt": TODAY,
            },
        },
        "fetchErrors": [],
        "phaseTimings": {
            "phase0Ms": 0,
            "phase1Ms": 0,
            "phase2Ms": 0,
            "phase3Ms": 0,
            "totalMs": 0,
        },
    },
    "whitelistAdditions": [
        {
            "tier": "S",
            "domain": "github.com/deepseek-ai",
            "sampleUrl": "https://github.com/deepseek-ai/DeepSeek-V3.2-Exp",
            "extractedFields": [
                "deepseek-v3-2.sweV",
                "deepseek-v3-2.lcb",
                "deepseek-v3-2.gpqa",
                "deepseek-v3-2.hle",
                "deepseek-v3-2.mmluPro",
                "deepseek-v3-2.browseComp",
                "deepseek-v3-2.simpleQa",
                "deepseek-v3-2.cfElo",
                "deepseek-v3-2.tb2",
                "deepseek-v3-2.sweMulti",
            ],
            "rationale": "Official vendor GitHub README benchmark table — carries 12+ bench scores per release",
        }
    ],
    "discoveries": {"vendors": [], "benchmarks": []},
    "runMetadata": {
        "agentVersion": "unified-5bucket-2026-04-30",
        "startedAt": "2026-04-30T00:00:00Z",
        "finishedAt": NOW,
    },
    "error": None,
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(artifact, f, indent=2, ensure_ascii=False)

print(f"Written: {OUT}")
print(f"Models with fills: {len(models_arr)}")
print(f"Total fills: {total_fills}")
print(f"Total gaps recorded: {total_gaps}")
print(f"Contradictions: {len(CONTRADICTIONS)}")
