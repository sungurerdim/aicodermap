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
# SSOT: AGENT_BUDGET_BUFFER + MAX_PARALLEL live in lib.constants (were independent
# literals here before 2026-06-06, free to silently diverge from the planner).
from .constants import AGENT_BUDGET_BUFFER, MAX_PARALLEL  # noqa: E402

CELLS_PER_TOOL_CALL = 3
MAX_BATCH_CELLS = AGENT_BUDGET_BUFFER * CELLS_PER_TOOL_CALL  # 150
# B2 (2026-05-31): 8→6. The 2026-05-30 cycle left ~191 cells never reached, the
# worst in the 8-model batches (8×17=136 cells vs a 50-tool-call budget — the
# CELLS_PER_TOOL_CALL=3 throughput assumption proved optimistic). 6 models ×17 =
# 102 cells fits the budget far better, so each slice fully sweeps. The cost of
# the extra batches is offset because the AA RSC extractor (PRELIM-G) now fills
# aaIdx/aaCoding/aaAgentic deterministically — ~81 of those 191 never-reached
# cells were exactly AA Coding/Agentic, so each gather agent has less to research.
ABSOLUTE_MAX_BATCH_MODELS = 6


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


def merge_small_buckets(
    buckets: list[list[dict[str, Any]]],
    *,
    small_threshold: int = 2,
    max_merged_size: int = 8,
) -> list[list[dict[str, Any]]]:
    """FAZ 7.D (2026-05-10) — collapse tiny family buckets into a single
    `smallVendors` bucket.

    Cycle 2026-05-10 measured 5 batches with ≤1 model each (StepFun, Nvidia,
    MoonshotAI, single-model Z.ai). Each carried full agent dispatch
    overhead (one ctx file, one Agent call, one wallclock, one synth slot)
    for ~10 cells of expected work. Merging them into one batch cuts
    dispatch overhead by 4-5×.

    Quality preserved: the resulting batch still operates per-model in
    target_model_ids; the agent walks each model's vendor URLs separately.
    The only collapse is "one Agent invocation instead of five".

    Buckets larger than `small_threshold` are left untouched. The merged
    bucket is capped at `max_merged_size` models to stay within the
    agent's tool-call budget.
    """
    if not buckets:
        return buckets
    big: list[list[dict[str, Any]]] = []
    smalls: list[dict[str, Any]] = []
    for b in buckets:
        if len(b) <= small_threshold:
            smalls.extend(b)
        else:
            big.append(b)
    if not smalls:
        return big
    # Slice the merged smalls into max_merged_size chunks (rare, but defensive).
    merged: list[list[dict[str, Any]]] = []
    for i in range(0, len(smalls), max_merged_size):
        merged.append(smalls[i : i + max_merged_size])
    return big + merged


def pack_batches(
    buckets: list[list[dict[str, Any]]],
    max_models: int,
) -> list[list[dict[str, Any]]]:
    """First-Fit-Decreasing pack of post-split buckets into the FEWEST batches
    of ≤ max_models (2026-06-06 efficiency reform).

    Root cause this fixes: family bucketing produced 18 batches for 76 models
    (sizes 6,6,6,6,6,6,5,5,4,4,4,3,3,3,3,3,2,1) — nine undersized. Each agent
    carries ~15-20 tool-calls of FIXED overhead (read agent.md + ctx + _rows +
    _aa-rows, Phase-0 lineup, self-audit) REGARDLESS of model count, so a 1- or
    3-model batch is almost pure overhead (measured: batch10 1 model = 379s/25
    tools, batch08 3 models = 419s/25 tools). FFD packs undersized buckets
    together → 13 batches (12×6 + 1×4), cutting ~5 agents of fixed overhead per
    cycle AND letting the plan fit one parallel wave (no wave-barrier idle time).

    A full-size family bucket (e.g. the 6-model Qwen slice) is placed first and
    stays intact (vendor-coherent); only undersized buckets get co-located. The
    6-model cap (B2 coverage budget) is never exceeded, so each slice still fully
    sweeps within the tool-call ceiling. Mixed-vendor batches are handled
    per-model via target_model_ids (same as the prior merge_small path).
    """
    bins: list[list[dict[str, Any]]] = []
    for b in sorted(buckets, key=len, reverse=True):
        for bin_ in bins:
            if len(bin_) + len(b) <= max_models:
                bin_.extend(b)
                break
        else:
            bins.append(list(b))
    return bins


def compute_dispatch_plan(
    active: list[dict[str, Any]],
    core_keys: list[str],
    *,
    max_parallel: int = MAX_PARALLEL,
    max_models_override: int | None = None,
    merge_small: bool = True,
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
    # Split oversize families to ≤mpb, THEN FFD-pack every undersized bucket
    # together so the plan uses the fewest agents (each agent's ~15-20-tool-call
    # fixed overhead is paid once per BATCH, not per model). pack_batches
    # subsumes the older merge_small_buckets (which only collapsed ≤2-model
    # families and left 3-5-model batches fragmented). merge_small=False keeps
    # the unpacked family layout for callers that want vendor-pure batches.
    sliced = split_oversize_batches(buckets, mpb)
    if merge_small:
        sliced = pack_batches(sliced, mpb)

    import re

    batches = []
    for i, bucket in enumerate(sliced):
        providers = sorted(
            p for p in {m.get("provider") for m in bucket} if isinstance(p, str)
        )
        # Use first provider name as a hint in the batchId so logs are readable.
        # FAZ 8.A (2026-05-18): filename-unsafe chars (parens, dots, slashes)
        # broke artifact file resolution for batches like
        # `batch10-z.ai_(zhipu_*`. Sanitize to [a-z0-9_-] only.
        family_hint = re.sub(
            r"[^a-z0-9_-]",
            "_",
            (providers[0] if providers else "other").lower(),
        )[:12]
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
