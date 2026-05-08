#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dispatch planner — turns a refresh-all cycle into an adaptive multi-batch
plan that NEVER lets a single agent exhaust its tool-call ceiling.

Root-cause analysis (2026-05-06): the prior cycle dispatched ONE sonnet agent
against 60 models × 26 bench keys = 1560 cells. The agent hit Claude Code's
~85 tool-call ceiling at ~174 cells filled (11 %); the remaining 1031 cells
came back as orchestrator auto-stub gaps.

Reform contract:
  AGENT_BUDGET_BUFFER     — never exceed this many tool calls per agent.
                            Conservative target: 50 (Claude Code ceiling
                            ~85; leaves headroom for retries + self-audit).
  CELLS_PER_TOOL_CALL     — empirical: each WebFetch + extraction yields
                            ~3-4 cells. Conservative: 3.
  MAX_BATCH_CELLS         — AGENT_BUDGET_BUFFER × CELLS_PER_TOOL_CALL = 150.
  MAX_BATCH_MODELS        — derived: MAX_BATCH_CELLS / |coreBenchKeys|.
                            With 26 keys: floor(150/26) = 5 models per batch.
  MAX_PARALLEL            — concurrent agent dispatch ceiling. Claude Code's
                            single-message Agent invocation supports up to
                            10 parallel sub-agents. Bumped 5→10 (FAZ 1.2,
                            2026-05-07) to halve wave count: 18 batches
                            now fit in 2 waves (10+8) instead of 4 waves
                            (5+5+5+3). Each wave's wallclock is bounded by
                            its slowest batch, so fewer waves = less total
                            wallclock. The orchestrator wallclock budget
                            is now enforced per-batch via deadline_unix
                            (FAZ 1.3), independent of parallel count.
  SEQUENTIAL_AFTER        — after MAX_PARALLEL batches return, the next
                            wave dispatches sequentially (still parallel
                            within the wave). Each wave is independent.

Output: list of dispatch waves; each wave is a list of batch specs that
        run in parallel. Waves run sequentially; batch within a wave runs
        in parallel.
"""

from __future__ import annotations

from typing import Any

# Conservative empirical defaults — see docstring.
AGENT_BUDGET_BUFFER = 50
CELLS_PER_TOOL_CALL = 3
MAX_BATCH_CELLS = AGENT_BUDGET_BUFFER * CELLS_PER_TOOL_CALL  # 150
MAX_PARALLEL = 10  # bumped 5→10 (FAZ 1.2, 2026-05-07): halve wave count
ABSOLUTE_MAX_BATCH_MODELS = 8


def models_per_batch(core_keys_count: int) -> int:
    """Derive how many models fit one agent under the budget cap."""
    if core_keys_count <= 0:
        return ABSOLUTE_MAX_BATCH_MODELS
    derived = MAX_BATCH_CELLS // core_keys_count
    return max(1, min(derived, ABSOLUTE_MAX_BATCH_MODELS))


def family_buckets(active: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Partition active models into provider-family buckets, then split any
    bucket that exceeds MAX_BATCH_MODELS so no agent ever sees more than its
    budget allows."""
    family_map: dict[str, list[dict[str, Any]]] = {}
    for m in active:
        provider = (m.get("provider") or "unknown").lower()
        # Coarse family normalization — group sibling providers under one batch
        # so OpenRouter/openai/etc. don't fragment.
        if "anthropic" in provider:
            family = "anthropic"
        elif "openai" in provider:
            family = "openai"
        elif "google" in provider or "deepmind" in provider:
            family = "google"
        elif "xai" in provider or "grok" in provider:
            family = "xai"
        elif "deepseek" in provider:
            family = "deepseek"
        elif "alibaba" in provider or "qwen" in provider:
            family = "qwen"
        elif "mistral" in provider:
            family = "mistral"
        elif "meta" in provider or "llama" in provider:
            family = "meta"
        elif "moonshot" in provider or "kimi" in provider:
            family = "moonshot"
        elif "zhipu" in provider or "z.ai" in provider:
            family = "zai"
        elif "minimax" in provider:
            family = "minimax"
        elif "xiaomi" in provider or "mimo" in provider:
            family = "xiaomi"
        elif "stepfun" in provider:
            family = "stepfun"
        elif "nvidia" in provider:
            family = "nvidia"
        else:
            family = "other"
        family_map.setdefault(family, []).append(m)
    return [family_map[k] for k in sorted(family_map.keys())]


def split_oversize_batches(
    buckets: list[list[dict[str, Any]]],
    max_models: int,
) -> list[list[dict[str, Any]]]:
    """Any bucket bigger than max_models gets sliced into N sub-batches of
    ≤ max_models. This is the key budget guard — no agent ever sees more
    models than its tool-call ceiling supports."""
    out: list[list[dict[str, Any]]] = []
    for b in buckets:
        if len(b) <= max_models:
            out.append(b)
            continue
        for i in range(0, len(b), max_models):
            out.append(b[i : i + max_models])
    return out


def compute_dispatch_plan(
    active: list[dict[str, Any]],
    core_keys: list[str],
    *,
    max_parallel: int = MAX_PARALLEL,
    max_models_override: int | None = None,
) -> dict[str, Any]:
    """Plan an adaptive multi-batch dispatch.

    Returns:
      {
        "totalModels": int,
        "coreKeys": int,
        "modelsPerBatch": int,
        "totalBatches": int,
        "totalWaves": int,
        "maxParallel": int,
        "expectedCellsPerBatch": int,
        "batches": [
          { "batchId": str, "waveIndex": int, "modelIds": [...],
            "modelCount": int, "expectedCells": int,
            "providers": [...] }
        ],
        "waves": [ [batchId, ...], ... ]
      }
    """
    keys = list(core_keys)
    mpb = max_models_override or models_per_batch(len(keys))
    buckets = family_buckets(active)
    sliced = split_oversize_batches(buckets, mpb)

    batches = []
    for i, bucket in enumerate(sliced):
        providers = sorted(
            p for p in {m.get("provider") for m in bucket} if isinstance(p, str)
        )
        # Use first provider name as a hint in the batchId so logs are readable.
        family_hint = (
            (providers[0] if providers else "other").lower().replace(" ", "_")[:12]
        )
        batch_id = f"batch{i:02d}-{family_hint}"
        batches.append(
            {
                "batchId": batch_id,
                "waveIndex": i // max_parallel,
                "modelIds": [m["id"] for m in bucket],
                "modelCount": len(bucket),
                "expectedCells": len(bucket) * len(keys),
                "providers": providers,
            }
        )

    waves: list[list[str]] = []
    for b in batches:
        wi = b["waveIndex"]
        while len(waves) <= wi:
            waves.append([])
        waves[wi].append(b["batchId"])

    return {
        "totalModels": len(active),
        "coreKeys": len(keys),
        "modelsPerBatch": mpb,
        "totalBatches": len(batches),
        "totalWaves": len(waves),
        "maxParallel": max_parallel,
        "expectedCellsPerBatch": mpb * len(keys),
        "agentBudgetBuffer": AGENT_BUDGET_BUFFER,
        "batches": batches,
        "waves": waves,
    }


def summarize_plan(plan: dict[str, Any]) -> str:
    """Compact one-block summary the orchestrator can paste into the cycle log."""
    out = []
    out.append("=== DISPATCH PLAN ===")
    out.append(
        f"models={plan['totalModels']} keys={plan['coreKeys']} "
        f"modelsPerBatch={plan['modelsPerBatch']} "
        f"agentBudgetBuffer={plan['agentBudgetBuffer']} "
        f"expectedCells/batch={plan['expectedCellsPerBatch']}"
    )
    out.append(
        f"totalBatches={plan['totalBatches']} waves={plan['totalWaves']} "
        f"parallel/wave={plan['maxParallel']}"
    )
    for w_idx, w in enumerate(plan["waves"]):
        out.append(f"  wave {w_idx}: {len(w)} parallel batches → {w}")
    out.append("")
    for b in plan["batches"]:
        out.append(
            f"  {b['batchId']} (wave {b['waveIndex']}): "
            f"{b['modelCount']} models × {plan['coreKeys']} keys "
            f"= {b['expectedCells']} cells expected"
        )
    return "\n".join(out)


if __name__ == "__main__":
    # CLI: print the plan for the current data/models.json + whitelist.
    import json
    import sys
    from pathlib import Path

    PROJECT = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(PROJECT / "scripts"))
    from lib.matrix import active_models  # noqa: E402
    from lib.whitelist import core_bench_keys, load_whitelist  # noqa: E402

    for stream in (sys.stdout, sys.stderr):
        reconf = getattr(stream, "reconfigure", None)
        if callable(reconf):
            try:
                reconf(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass

    wl = load_whitelist()
    keys = core_bench_keys(wl)
    with (PROJECT / "data" / "models.json").open(encoding="utf-8") as f:
        models = json.load(f)
    active = active_models(models)
    plan = compute_dispatch_plan(active, keys)
    print(summarize_plan(plan))
