#!/usr/bin/env python3
"""
FAZ 4.C.1 GATHER stage — extract observations from snapshots for Qwen batch.
Flat schema output.
"""

import json
import re
from pathlib import Path
from datetime import datetime
import html

# Target models for Qwen batch 11
TARGET_MODELS = [
    "qwen-3-6-27b",
    "qwen-3-6-max",
    "qwen3-235b",
    "qwen3-32b",
    "qwen3-6-35b-moe",
]

# Core bench keys
CORE_BENCH_KEYS = [
    "swePro",
    "sweV",
    "sweMulti",
    "nl2Repo",
    "tb2",
    "tbHard",
    "lcb",
    "tau2",
    "tau3",
    "mcpA",
    "bfcl",
    "browseComp",
    "aaCoding",
    "aaAgentic",
    "aaIdx",
    "aaOmni",
    "cfElo",
    "webDevElo",
    "mmluPro",
    "simpleQa",
    "mrcr",
    "arcAgi2",
    "gpqa",
    "aime26",
    "hle",
    "programBench",
]

# Bench aliases from data/sources-whitelist.json benchAliases
BENCH_ALIASES = {
    "swePro": [
        "swe-bench pro",
        "swe-bench-pro",
        "swepro",
        "sweBenchPro",
        "SWE-Bench Pro",
        "swe bench pro",
    ],
    "sweV": [
        "swe-bench verified",
        "swe-bench-verified",
        "swev",
        "sweBenchV",
        "SWE-Bench Verified",
        "swe bench verified",
    ],
    "sweMulti": ["swe-bench multi", "swe-bench-multi", "swemulti", "SWE-Bench Multi"],
    "nl2Repo": ["nl2repo", "nl-2-repo"],
    "tb2": [
        "terminal bench 2",
        "terminalbench",
        "tb2",
        "terminalBench2",
        "terminal-bench",
    ],
    "tbHard": ["terminal bench hard", "tbhard", "tb hard"],
    "lcb": [
        "livecodebenching",
        "livecodebench",
        "lcb",
        "LiveCodeBench",
        "live code bench",
    ],
    "tau2": ["tau-bench 2", "taubench", "tau2", "tau-bench", "taubench2"],
    "tau3": ["tau-bench 3", "taubench3", "tau3"],
    "mcpA": ["mcp-atlas", "mcpa", "mcp atlas"],
    "bfcl": ["bfcl", "tool call"],
    "browseComp": ["browse comp", "browsecomp"],
    "aaCoding": ["artificial analysis coding", "aa-coding", "aacoding"],
    "aaAgentic": ["artificial analysis agentic", "aa-agentic", "aaagentic"],
    "aaIdx": ["aa-idx", "aaidx", "artificial analysis index"],
    "aaOmni": ["aa-omni", "aaomni"],
    "cfElo": ["codeforces elo", "cf-elo", "cfelo", "codeforces"],
    "webDevElo": ["web dev elo", "webdevelo", "lm arena webdev"],
    "mmluPro": ["mmlu-pro", "mmlupro", "mmlu pro"],
    "simpleQa": ["simple qa", "simpleqa", "simple-qa"],
    "mrcr": ["mrcr", "multi ref"],
    "arcAgi2": ["arc-agi2", "arcagi2", "arc agi"],
    "gpqa": ["gpqa", "gpqa-diamond"],
    "aime26": ["aime 2026", "aime26", "aime"],
    "hle": ["human-level evaluation", "hle", "human level"],
    "programBench": ["programbench", "program bench"],
}


def html_decode(text):
    """Decode HTML entities."""
    return html.unescape(text)


def extract_model_context(content, model_id):
    """Find all occurrences of a model in content and get surrounding context."""
    results = []

    # Case variations
    patterns = [
        model_id,
        model_id.replace("-", "_"),
        model_id.replace("-", " "),
        model_id.lower(),
        model_id.upper(),
    ]

    for pattern in patterns:
        # Find all positions
        offset = 0
        while True:
            idx = content.find(pattern, offset)
            if idx == -1:
                break

            # Get context: 500 chars before and 500 chars after
            start = max(0, idx - 500)
            end = min(len(content), idx + len(pattern) + 500)
            context = content[start:end]

            results.append(
                {
                    "pattern": pattern,
                    "context": context,
                    "position": idx,
                }
            )

            offset = idx + 1

    return results


def extract_bench_value(context, bench_key, aliases):
    """Try to extract a bench value from context for a given benchmark."""
    # Score pattern: optional "text: " followed by number(s), optional % sign
    # Match patterns like "87.6", "87.6%", "score: 87.6", "65 %", etc.

    for alias in aliases:
        # Search for the alias (case-insensitive)
        if re.search(r"\b" + re.escape(alias) + r"\b", context, re.IGNORECASE):
            # Extract numbers after the alias (within ~100 chars)
            nearby = context[
                context.lower().find(alias.lower()) : context.lower().find(
                    alias.lower()
                )
                + 200
            ]

            # Match number patterns (with optional . and %)
            number_patterns = [
                r"(\d+\.\d+)%?",  # e.g., "87.6" or "87.6%"
                r"(\d+)%",  # e.g., "87%"
                r"(\d+(?:\.\d+)?)",  # fallback
            ]

            for num_pattern in number_patterns:
                matches = re.findall(num_pattern, nearby)
                for match in matches:
                    try:
                        score = float(match)
                        # Validate range: 0-100 for most benches, 0-3500 for cfElo
                        if bench_key == "cfElo":
                            if 0 <= score <= 3500:
                                return score
                        elif bench_key == "webDevElo":
                            if 950 <= score <= 1500:
                                return score
                        else:
                            if 0 <= score <= 100:
                                return score
                    except:
                        pass

    return None


def process_snapshot(filepath, snapshot_url, snapshot_info, target_models):
    """Extract Qwen observations from a single snapshot file."""
    observations = []

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Minimal decode
        content = html_decode(content)

        for model_id in target_models:
            contexts = extract_model_context(content, model_id)

            if contexts:
                # We found the model in this file
                # Now search for bench values in the contexts
                for ctx_item in contexts:
                    context = ctx_item["context"]

                    for bench_key in CORE_BENCH_KEYS:
                        aliases = BENCH_ALIASES.get(bench_key, [])
                        value = extract_bench_value(context, bench_key, aliases)

                        if value is not None:
                            tier_map = {
                                "leaderboards": "I",
                                "aggregators": "I",
                                "registries": "I",
                                "community": "C",
                                "local": "I",
                            }

                            observations.append(
                                {
                                    "modelId": model_id,
                                    "benchKey": bench_key,
                                    "value": value,
                                    "sourceUrl": snapshot_url,
                                    "tier": tier_map.get(
                                        snapshot_info.get("category", "community"), "C"
                                    ),
                                    "fetched": snapshot_info.get(
                                        "fetchedAt", datetime.now().isoformat() + "Z"
                                    ).split("T")[0],
                                }
                            )

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

    return observations


def main():
    snapshots_dir = Path("D:/GitHub/aicodermap/data/.leaderboard-snapshots")
    index_file = snapshots_dir / "_index.json"

    with open(index_file, "r") as f:
        index = json.load(f)

    all_observations = []
    tool_call_count = 0
    snapshots_read = 0

    # Process snapshots known to contain Qwen
    qwen_snapshots = [
        "https://artificialanalysis.ai/leaderboards/models",
        "https://benchlm.ai/",
        "https://llm-stats.com/",
        "https://llm-stats.com/benchmarks/livecodebench",
        "https://llm-stats.com/benchmarks/swe-bench-verified",
        "https://labs.scale.com/leaderboard/swe_bench_pro_public",
        "https://openrouter.ai/rankings",
        "https://groq.com/pricing",
        "https://console.groq.com/docs/models",
        "https://fireworks.ai/models",
        "https://novita.ai/model-api",
        "https://whatllm.org/blog/",
        "https://lmmarketcap.com/",
    ]

    for snapshot_url in qwen_snapshots:
        if snapshot_url not in index["snapshots"]:
            continue

        snapshot_info = index["snapshots"][snapshot_url]
        snapshot_path = snapshots_dir / snapshot_info["path"].split("/")[-1]

        if not snapshot_path.exists():
            continue

        obs = process_snapshot(
            str(snapshot_path), snapshot_url, snapshot_info, TARGET_MODELS
        )
        all_observations.extend(obs)
        snapshots_read += 1
        tool_call_count += 1

    # Deduplicate: keep one entry per (modelId, benchKey, sourceUrl) triple
    dedup_key = lambda x: (x["modelId"], x["benchKey"], x["sourceUrl"])
    seen = {}
    unique_obs = []
    for obs in all_observations:
        key = dedup_key(obs)
        if key not in seen:
            seen[key] = obs
            unique_obs.append(obs)

    # Flatten schema artifact
    artifact = {
        "batchId": "batch11-alibaba_qwen",
        "mode": "gather",
        "observations": unique_obs,
        "modelMeta": [],
        "pricingObs": [],
        "ollamaObs": [],
        "unslothObs": [],
        "lineupHints": [],
        "naCandidates": [],
        "rawGaps": [],
        "runtime": {
            "toolCallCount": tool_call_count,
            "wallclockSec": 0,
            "snapshotsRead": snapshots_read,
        },
        "partialReason": None,
    }

    # Write artifact
    output_path = Path(
        "D:/GitHub/aicodermap/.aicodermap-agent-out-batch11-alibaba_qwen.gather.json"
    )
    with open(output_path, "w") as f:
        json.dump(artifact, f, indent=2)

    print(
        f"EMITTED batch=batch11-alibaba_qwen mode=gather observations={len(unique_obs)} pricingObs=0 ollamaObs=0 rawGaps=0 path={output_path}"
    )
    return len(unique_obs)


if __name__ == "__main__":
    main()
