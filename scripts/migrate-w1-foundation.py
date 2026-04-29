#!/usr/bin/env python3
"""One-shot W1 foundation migration.

Adds the schema fields the reform plan introduces:
  - data/models.json: every entry gets `notApplicableBenchKeys: []`
    + `benchQuarantine: {}` (idempotent — keeps existing values)
  - data/sources-whitelist.json: `_schema.contracts` block with the
    canonical thresholds + `_schema.notApplicableRules` skeleton +
    `_schema.benchAliases` (lifted out of agent.md) + `_schema.deprecatedBenchKeys`

Idempotent: safe to re-run; existing fields are preserved verbatim.

Usage:
  python scripts/migrate-w1-foundation.py [--dry-run]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
MODELS_PATH = PROJECT / "data" / "models.json"
WHITELIST_PATH = PROJECT / "data" / "sources-whitelist.json"


CONTRACTS_BLOCK = {
    "_purpose": (
        "SSOT for every threshold, retry count, and pass/fail criterion the "
        "skill + agent + scripts share. SKILL.md/agent.md reference this block "
        "rather than mirroring values; merge.py + audit-* scripts fetch via "
        "scripts/lib/whitelist.py contracts()."
    ),
    "ABSOLUTE_COVERAGE_FLOOR": 0.30,
    "MIN_SOURCES_PER_FILLED_CELL": 2,
    "COMPLETENESS_RETRY_LIMIT": 1,
    "VERIFICATION_AGREEMENT_THRESHOLD": 3,
    "VERIFICATION_AGREEMENT_PP": 1.5,
    "CONTRADICTION_WARN_PP": 3.0,
    "CONTRADICTION_BLOCK_PP": 5.0,
    "COVERAGE_TARGET": 0.85,
    "COVERAGE_HARD_BLOCK": 0.50,
    "STALE_DAYS": 14,
    "DEPRECATION_GRACE_DAYS": 60,
    "FAMILY_BASELINE_MIN": 30,
    "FETCH_TIMEOUT_SEC": 10,
    "FETCH_RETRY_COUNT": 1,
    "PARALLEL_FETCH_BATCH": 5,
    "HEALTH_CHECK_TTL_DAYS": 7,
}

# Tier-based N/A rules. Hardcoded model id YASAK — kural-bazlı.
NA_RULES = {
    "_purpose": (
        "Tier/capability based rules that mark a (model, benchKey) cell as "
        "naturally not-applicable so it does not count against the matrix "
        "invariant. Agent emits cells under these rules into "
        "models[].notApplicable[]; orchestrator reconciles."
    ),
    "_schema": {
        "rule": "<rule name>",
        "appliesTo": "<criteria — matched against model entry>",
        "excludeBenchKeys": "<list of bench keys naturally undefined>",
    },
    "rules": [
        {
            "rule": "embedding-only-tier",
            "appliesTo": {"tier": ["embedding"]},
            "excludeBenchKeys": [
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
                "toolDec",
                "browseComp",
                "aaCoding",
                "aaAgentic",
                "cfElo",
                "webDevElo",
            ],
        },
    ],
}

# Bench alias table — moved out of agent.md per P8 kuralsallaştırma.
# Format: canonicalKey → [human-readable aliases the agent matches against
# scraped page text]. Agent reads via _schema.benchAliases; never inlines.
BENCH_ALIASES = {
    "_purpose": (
        "Canonical bench-key ↔ human-name mapping. Agent extraction maps "
        "scraped names back to canonical keys via this table — replaces the "
        "hardcoded EXTRACTION_DISCIPLINE row 5 table."
    ),
    "swePro": ["SWE-bench Pro", "SEAL Pro", "SWE Pro", "SWEbench Pro"],
    "sweV": ["SWE-bench Verified", "SWE-V", "SWE Verified", "SWEbench Verified"],
    "sweMulti": ["SWE-bench Multilingual", "Multi-SWE", "SWEbench Multilingual"],
    "nl2Repo": ["NL2Repo", "NL-to-Repo"],
    "lcb": ["LiveCodeBench", "LCB", "LCB v6", "LCBv6"],
    "tb2": ["Terminal-Bench 2", "TB2", "Terminal Bench v2"],
    "tbHard": ["Terminal-Bench Hard", "TB Hard"],
    "tau2": ["tau-bench v2", "tau2", "tau-2"],
    "tau3": ["tau-bench v3", "tau3", "tau-3"],
    "mcpA": ["MCP-Atlas", "MCP Atlas"],
    "bfcl": ["BFCL", "Berkeley Function Calling"],
    "toolDec": ["ToolDec", "Tool-Dec"],
    "browseComp": ["BrowseComp", "Browse Comp"],
    "aaCoding": ["Artificial Analysis Coding Index", "AA Coding"],
    "aaAgentic": ["Artificial Analysis Agentic Index", "AA Agentic"],
    "aaIdx": [
        "Artificial Analysis Intelligence Index",
        "AA Intelligence Index",
        "AA Index",
        "aaIdx",
    ],
    "aaOmni": ["AA Omni", "Artificial Analysis Omni"],
    "cfElo": ["Codeforces Elo", "CF Elo", "Codeforces Rating"],
    "webDevElo": ["LMArena WebDev Elo", "WebDev Arena Elo", "WebDev Elo"],
    "mmluPro": ["MMLU-Pro", "MMLU Pro"],
    "simpleQa": ["SimpleQA", "Simple QA"],
    "mrcr": ["MRCR"],
    "arcAgi2": ["ARC-AGI-2", "ARC AGI 2"],
    "gpqa": ["GPQA", "GPQA Diamond"],
    "aime26": ["AIME 2026", "AIME26", "AIME"],
    "hle": ["HLE", "Humanity's Last Exam"],
}


DEPRECATED_BENCH_KEYS_SCAFFOLD: list[str] = []


def migrate_models(dry_run: bool) -> int:
    with open(MODELS_PATH, encoding="utf-8") as fp:
        models = json.load(fp)
    touched = 0
    for m in models:
        changed = False
        if "notApplicableBenchKeys" not in m:
            m["notApplicableBenchKeys"] = []
            changed = True
        if "benchQuarantine" not in m:
            m["benchQuarantine"] = {}
            changed = True
        if changed:
            touched += 1
    if not dry_run:
        with open(MODELS_PATH, "w", encoding="utf-8") as fp:
            json.dump(models, fp, indent=2, ensure_ascii=False)
            fp.write("\n")
    print(f"models.json: {touched} entries touched (of {len(models)})")
    return 0


def _ensure_block(schema: dict, key: str, payload: dict) -> bool:
    if key in schema and isinstance(schema[key], dict):
        return False
    schema[key] = payload
    return True


def migrate_whitelist(dry_run: bool) -> int:
    with open(WHITELIST_PATH, encoding="utf-8") as fp:
        wl = json.load(fp)
    schema = wl.setdefault("_schema", {})
    actions: list[str] = []
    if _ensure_block(schema, "contracts", CONTRACTS_BLOCK):
        actions.append("added _schema.contracts")
    if _ensure_block(schema, "notApplicableRules", NA_RULES):
        actions.append("added _schema.notApplicableRules")
    if _ensure_block(schema, "benchAliases", BENCH_ALIASES):
        actions.append("added _schema.benchAliases")
    if "deprecatedBenchKeys" not in schema:
        schema["deprecatedBenchKeys"] = list(DEPRECATED_BENCH_KEYS_SCAFFOLD)
        actions.append("added _schema.deprecatedBenchKeys (empty)")
    if not dry_run:
        with open(WHITELIST_PATH, "w", encoding="utf-8") as fp:
            json.dump(wl, fp, indent=2, ensure_ascii=False)
            fp.write("\n")
    print(f"sources-whitelist.json: {len(actions)} block(s) ensured")
    for a in actions:
        print(f"  - {a}")
    return 0


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    if not MODELS_PATH.exists():
        print(f"missing {MODELS_PATH}", file=sys.stderr)
        return 1
    if not WHITELIST_PATH.exists():
        print(f"missing {WHITELIST_PATH}", file=sys.stderr)
        return 1
    rc = migrate_models(dry_run)
    if rc != 0:
        return rc
    rc = migrate_whitelist(dry_run)
    return rc


if __name__ == "__main__":
    sys.exit(main())
