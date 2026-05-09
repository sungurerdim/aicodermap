#!/usr/bin/env python3
"""Extract kimi-k2-6 bench observations from snapshot HTMLs."""

import json
import re
from pathlib import Path

# Load snapshot index
index_path = Path("D:/GitHub/aicodermap/data/.leaderboard-snapshots/_index.json")
with open(index_path) as f:
    index = json.load(f)

# Bench patterns to match (model + score pairs)
bench_patterns = [
    (r"kimi[- ]?k2[- ]?\.?6", r"swePro", r"(?:SWE[- ]?Pro|SWE-Pro).*?(\d+\.?\d*)"),
    (
        r"kimi[- ]?k2[- ]?\.?6",
        r"sweV",
        r"(?:SWE[- ]?Verified|SWE-Verified).*?(\d+\.?\d*)",
    ),
    (
        r"kimi[- ]?k2[- ]?\.?6",
        r"tb2",
        r"(?:Terminal[- ]?Bench|TB2|TerMUX).*?(\d+\.?\d*)",
    ),
    (
        r"kimi[- ]?k2[- ]?\.?6",
        r"lcb",
        r"(?:LiveCode[- ]?Bench|LCB[- ]?v6).*?(\d+\.?\d*)",
    ),
    (r"kimi[- ]?k2[- ]?\.?6", r"gpqa", r"(?:GPQA|General Purpose QA).*?(\d+\.?\d*)"),
    (r"kimi[- ]?k2[- ]?\.?6", r"aime26", r"(?:AIME|AIME 2026).*?(\d+\.?\d*)"),
    (
        r"kimi[- ]?k2[- ]?\.?6",
        r"hle",
        r"(?:HumanEval[- ]?Evolutionary|HLE).*?(\d+\.?\d*)",
    ),
    (
        r"kimi[- ]?k2[- ]?\.?6",
        r"tau2",
        r"(?:Tau[- ]?bench|Tau-bench|tau2).*?(\d+\.?\d*)",
    ),
    (r"kimi[- ]?k2[- ]?\.?6", r"mmluPro", r"(?:MMLU[- ]?Pro|MMLU-Pro).*?(\d+\.?\d*)"),
]

observations = {}
found_sources = set()

# Walk snapshots
snapshot_dir = Path("D:/GitHub/aicodermap/data/.leaderboard-snapshots")
for snap_url, snap_meta in index.get("snapshots", {}).items():
    snap_path = snapshot_dir / snap_meta["path"].split("/")[-1]
    if not snap_path.exists():
        continue

    try:
        with open(snap_path, encoding="utf-8", errors="ignore") as f:
            content = f.read(50000)  # First 50KB only
    except:
        continue

    # Check if kimi appears in this snapshot
    if not re.search(r"kimi[- ]?k2[- ]?\.?6", content, re.IGNORECASE):
        continue

    found_sources.add(snap_url)

    # Extract bench values per pattern
    for model_re, bench_key, score_pattern in bench_patterns:
        match = re.search(score_pattern, content, re.IGNORECASE)
        if match:
            try:
                score = float(match.group(1))
                if bench_key not in observations:
                    observations[bench_key] = []
                observations[bench_key].append(
                    {
                        "value": score,
                        "source": snap_url,
                        "format": snap_meta.get("format", "unknown"),
                    }
                )
            except (ValueError, IndexError):
                pass

# Output summary
print(
    json.dumps(
        {
            "model": "kimi-k2-6",
            "sources_with_kimi": len(found_sources),
            "source_urls": list(found_sources)[:5],
            "observations": {k: len(v) for k, v in observations.items()},
            "example_observations": {
                k: v[0] if v else None for k, v in observations.items()
            },
        },
        indent=2,
    )
)
