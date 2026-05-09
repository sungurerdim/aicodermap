#!/usr/bin/env python3
"""
FAZ 4.C.1 GATHER stage — extract observations from snapshots for DeepSeek batch.
"""

import json
import re
from pathlib import Path
from datetime import datetime

# Target models for this batch
TARGET_MODELS = [
    "deepseek-v3-2",
    "deepseek-v4-flash",
    "deepseek-v4-pro",
    "deepseek-coder-v2-16b",
    "deepseek-r1-14b",
]

# Core bench keys to search for
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

# Bench key aliases (what the benchmarks are called in leaderboards)
BENCH_ALIASES = {
    "swePro": [
        "swe-bench pro",
        "swe-bench-pro",
        "swepro",
        "sweBenchPro",
        "SWE-Bench Pro",
    ],
    "sweV": [
        "swe-bench verified",
        "swe-bench-verified",
        "swev",
        "sweBenchV",
        "SWE-Bench Verified",
    ],
    "sweMulti": ["swe-bench multi", "swe-bench-multi", "swemulti", "SWE-Bench Multi"],
    "tb2": ["terminal bench 2", "terminalbench", "tb2", "terminalBench2"],
    "lcb": ["livecodebenching", "livecodebench", "lcb", "LiveCodeBench"],
    "tau2": ["tau-bench 2", "taubench", "tau2"],
    "gpqa": ["gpqa", "gpqa-diamond"],
    "aime26": ["aime 2026", "aime26"],
    "hle": ["human-level evaluation", "hle"],
    "cfElo": ["codeforces elo", "cf-elo", "cfelo"],
    "programBench": ["programbench", "program bench"],
}


def extract_numeric_values(text):
    """Extract numbers from text (percentage, scores, etc.)"""
    # Match numbers with optional % and decimal
    pattern = r"(\d+(?:\.\d+)?)\s*%?"
    matches = re.findall(pattern, text)
    return [float(m) for m in matches if m]


def grep_model_in_file(filepath, model_id):
    """Search for a specific model ID in a snapshot file."""
    observations = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Case-insensitive search for the model
        pattern = re.compile(
            r"(?:"
            + "|".join(
                re.escape(v)
                for v in [
                    model_id,
                    model_id.replace("-", "_"),
                    model_id.replace("-", " "),
                ]
            )
            + r")",
            re.IGNORECASE,
        )

        if pattern.search(content):
            # Found the model, now search for bench values in proximity
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if pattern.search(line):
                    # Look at this line and surrounding ones for bench patterns
                    context = "\n".join(lines[max(0, i - 2) : min(len(lines), i + 3)])

                    # Try to match bench keywords
                    for bench_key, aliases in BENCH_ALIASES.items():
                        for alias in aliases:
                            if re.search(
                                r"\b" + re.escape(alias) + r"\b", context, re.IGNORECASE
                            ):
                                # Extract numbers near the match
                                numbers = extract_numeric_values(context)
                                if numbers:
                                    # Take the first reasonable score (0-100 or 0-3500 for cfElo)
                                    for num in numbers:
                                        if (
                                            bench_key == "cfElo" and 0 <= num <= 3500
                                        ) or (0 <= num <= 100):
                                            observations.append(
                                                {
                                                    "benchKey": bench_key,
                                                    "value": num,
                                                    "context": context[:100],
                                                }
                                            )
                                            break
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

    return observations


def main():
    snapshots_dir = Path("D:/GitHub/aicodermap/data/.leaderboard-snapshots")
    index_file = snapshots_dir / "_index.json"

    with open(index_file, "r") as f:
        index = json.load(f)

    # Result structure for gather mode
    results = {
        "batchId": "batch01-deepseek",
        "mode": "gather",
        "models": [],
        "rawGaps": [],
        "runtime": {
            "perModelObservations": {},
            "totalObservations": 0,
            "snapshotsProcessed": 0,
            "snapshotsAttempted": list(index["snapshots"].keys()),
        },
    }

    # Process each target model
    for model_id in TARGET_MODELS:
        model_obs = {
            "id": model_id,
            "observations": [],
            "lineupHints": None,
            "naCandidates": [],
        }

        total_obs_count = 0

        # Walk through snapshots
        for snapshot_url, snapshot_info in index["snapshots"].items():
            snapshot_path = snapshots_dir / snapshot_info["path"].split("/")[-1]

            if not snapshot_path.exists():
                continue

            obs = grep_model_in_file(str(snapshot_path), model_id)

            for ob in obs:
                # Deduplicate: one observation per source per benchKey
                existing_for_key = [
                    o
                    for o in model_obs["observations"]
                    if o["benchKey"] == ob["benchKey"]
                ]

                # Only add if we don't have this bench from this source already
                if not existing_for_key:
                    model_obs["observations"].append(
                        {
                            "benchKey": ob["benchKey"],
                            "value": ob["value"],
                            "source": {
                                "url": snapshot_url,
                                "tier": snapshot_info.get("category", "leaderboards")
                                == "leaderboards"
                                and "I"
                                or "C",
                                "fetched": snapshot_info.get(
                                    "fetchedAt", datetime.now().isoformat() + "Z"
                                ),
                            },
                        }
                    )
                    total_obs_count += 1

        results["runtime"]["perModelObservations"][model_id] = total_obs_count
        results["models"].append(model_obs)

    # Summary
    results["runtime"]["totalObservations"] = sum(
        len(m["observations"]) for m in results["models"]
    )
    results["runtime"]["snapshotsProcessed"] = len(index["snapshots"])

    # Write artifact
    artifact_path = Path(
        "D:/GitHub/aicodermap/.aicodermap-agent-out-batch01-deepseek.gather.json"
    )
    with open(artifact_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Wrote {artifact_path}")
    print(
        f"Models: {len(results['models'])}, Total observations: {results['runtime']['totalObservations']}"
    )


if __name__ == "__main__":
    main()
