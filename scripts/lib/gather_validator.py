"""Gather artifact schema validator (FAZ 4.C.1.c).

Validates flat-schema haiku gather artifacts. Returns a structured
verdict the orchestrator uses to decide retry vs accept.

Contract: gather artifacts have FLAT shape (every entry carries `modelId`),
not nested `models[].observations[]`. See agent.md GATHER_MODE for spec.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Permitted top-level keys in a gather artifact. Anything else = full/synth schema bleed.
GATHER_TOP_KEYS = {
    "batchId",
    "mode",
    "observations",
    "modelMeta",
    "pricingObs",
    "ollamaObs",
    "unslothObs",
    "lineupHints",
    "naCandidates",
    "rawGaps",
    "runtime",
    "partialReason",
}

# Keys that signal the agent emitted FULL schema (forbidden in gather).
FULL_SCHEMA_BLEED_KEYS = {
    "models",  # full uses models[].updates[]; gather uses flat observations[]
    "newModels",
    "contradictions",
    "confidence",
    "synthesis",
    "lineupChanges",
    "coverageMatrix",
    "validationCoverage",
    "runMetadata",
    "discoveries",
    "whitelistAdditions",
    "error",
    "sourcesAdded",
    "gaps",
}

REQUIRED_OBS_FIELDS = {"modelId", "benchKey", "value", "sourceUrl", "tier", "fetched"}
ALLOWED_TIERS = {"I", "S", "C"}

MIN_AVG_OBS_PER_MODEL = 3


def validate_gather(
    artifact: dict[str, Any],
    target_model_ids: list[str],
    min_avg: int = MIN_AVG_OBS_PER_MODEL,
) -> dict[str, Any]:
    """Returns a verdict dict.

    {
      "valid": bool,
      "errors": [str, ...],   # hard schema violations
      "warnings": [str, ...], # soft issues (low obs count, etc.)
      "stats": {
        "observations": int,
        "pricingObs": int,
        "ollamaObs": int,
        "rawGaps": int,
        "perModelObs": {modelId: int},
        "avgObs": float,
        "weakModels": [modelId, ...]  # < min_avg observations
      }
    }
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(artifact, dict):
        return {
            "valid": False,
            "errors": ["artifact is not a dict"],
            "warnings": [],
            "stats": {},
        }

    # Top-level key audit.
    keys = set(artifact.keys())
    bleed = keys & FULL_SCHEMA_BLEED_KEYS
    if bleed:
        errors.append(
            f"FULL/SYNTH schema bleed — forbidden top-level keys present: {sorted(bleed)}"
        )
    extra = keys - GATHER_TOP_KEYS - FULL_SCHEMA_BLEED_KEYS
    if extra:
        warnings.append(f"unrecognized top-level keys: {sorted(extra)}")

    if artifact.get("mode") != "gather":
        errors.append(f"mode='{artifact.get('mode')}' but expected 'gather'")

    if not isinstance(artifact.get("batchId"), str):
        errors.append("batchId missing or not a string")

    # Observations validation.
    observations = artifact.get("observations") or []
    if not isinstance(observations, list):
        errors.append("observations is not a list")
        observations = []

    valid_observations = []
    target_set = set(target_model_ids)
    for i, o in enumerate(observations):
        if not isinstance(o, dict):
            warnings.append(f"observations[{i}] is not a dict")
            continue
        missing = REQUIRED_OBS_FIELDS - set(o.keys())
        if missing:
            warnings.append(f"observations[{i}] missing fields: {sorted(missing)}")
            continue
        if o.get("tier") not in ALLOWED_TIERS:
            warnings.append(
                f"observations[{i}].tier='{o.get('tier')}' invalid (need I|S|C)"
            )
        if o.get("modelId") not in target_set:
            warnings.append(
                f"observations[{i}].modelId='{o.get('modelId')}' not in target_model_ids"
            )
            continue
        try:
            float(o["value"])
        except (TypeError, ValueError):
            warnings.append(f"observations[{i}].value={o.get('value')!r} not numeric")
            continue
        valid_observations.append(o)

    # Per-model count.
    per_model: dict[str, int] = {mid: 0 for mid in target_model_ids}
    for o in valid_observations:
        mid = o["modelId"]
        per_model[mid] = per_model.get(mid, 0) + 1
    weak_models = [mid for mid, c in per_model.items() if c < min_avg]

    avg_obs = (
        sum(per_model.values()) / max(len(target_model_ids), 1)
        if target_model_ids
        else 0
    )

    if avg_obs < min_avg:
        warnings.append(
            f"avg observations/model = {avg_obs:.1f} < {min_avg} (weak gather)"
        )
    if len(valid_observations) == 0:
        errors.append("zero valid observations — gather is empty")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "stats": {
            "observations": len(valid_observations),
            "rawObservations": len(observations),
            "pricingObs": len(artifact.get("pricingObs") or []),
            "ollamaObs": len(artifact.get("ollamaObs") or []),
            "unslothObs": len(artifact.get("unslothObs") or []),
            "rawGaps": len(artifact.get("rawGaps") or []),
            "naCandidates": len(artifact.get("naCandidates") or []),
            "lineupHints": len(artifact.get("lineupHints") or []),
            "perModelObs": per_model,
            "avgObs": round(avg_obs, 2),
            "weakModels": weak_models,
            "isWeakBatch": len(weak_models) > 0 or avg_obs < min_avg,
        },
    }


def feedback_message(
    verdict: dict[str, Any], target_model_ids: list[str], output_path: str
) -> str:
    """Generate concise retry feedback for an invalid artifact.

    Used to inject corrective guidance into the next dispatch prompt
    when a haiku gather fails validation.
    """
    if verdict.get("valid") and not verdict.get("stats", {}).get("isWeakBatch"):
        return ""
    lines = [
        f"PRIOR EMIT REJECTED. Rewrite the file at {output_path}.",
        "",
        f"target_model_ids ({len(target_model_ids)}): {target_model_ids}",
        "",
        "PRIOR ERRORS:",
    ]
    for e in verdict.get("errors", [])[:5]:
        lines.append(f"  - {e}")
    if verdict.get("warnings"):
        lines.append("PRIOR WARNINGS:")
        for w in verdict.get("warnings", [])[:5]:
            lines.append(f"  - {w}")
    stats = verdict.get("stats", {})
    if stats.get("avgObs", 0) < MIN_AVG_OBS_PER_MODEL:
        lines.append(
            f"  - avg observations/model = {stats.get('avgObs', 0):.1f} "
            f"< {MIN_AVG_OBS_PER_MODEL} (need more)"
        )
    if stats.get("weakModels"):
        lines.append(f"  - models below threshold: {stats['weakModels']}")
    lines.extend(
        [
            "",
            "FIX: emit FLAT schema. ONLY these top-level keys:",
            "  batchId, mode, observations, modelMeta, pricingObs, ollamaObs,",
            "  unslothObs, lineupHints, naCandidates, rawGaps, runtime, partialReason",
            "",
            "FORBIDDEN top-level keys (REMOVE THESE):",
            "  models, newModels, confidence, synthesis, lineupChanges, gaps,",
            "  coverageMatrix, validationCoverage, runMetadata, error,",
            "  sourcesAdded, contradictions, discoveries, whitelistAdditions",
            "",
            "Each observations[] entry MUST have:",
            '  {"modelId": "<id>", "benchKey": "<key>", "value": <number>,',
            '   "sourceUrl": "<url>", "tier": "I"|"S"|"C", "fetched": "YYYY-MM-DD"}',
        ]
    )
    return "\n".join(lines)


def validate_gather_file(
    path: str | Path, target_model_ids: list[str]
) -> dict[str, Any]:
    """Convenience wrapper — load artifact then validate."""
    p = Path(path)
    if not p.is_file():
        return {
            "valid": False,
            "errors": [f"file not found: {p}"],
            "warnings": [],
            "stats": {},
        }
    try:
        with p.open(encoding="utf-8") as fp:
            artifact = json.load(fp)
    except (OSError, json.JSONDecodeError) as e:
        return {
            "valid": False,
            "errors": [f"unreadable/unparseable: {e}"],
            "warnings": [],
            "stats": {},
        }
    return validate_gather(artifact, target_model_ids)


if __name__ == "__main__":
    import sys
    import glob

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from lib.dispatch import compute_dispatch_plan  # noqa: E402
    from lib.matrix import active_models  # noqa: E402
    from lib.whitelist import core_bench_keys, load_whitelist  # noqa: E402

    project = Path(__file__).resolve().parents[2]
    with (project / "data" / "models.json").open(encoding="utf-8") as f:
        models = json.load(f)
    wl = load_whitelist()
    plan = compute_dispatch_plan(active_models(models), core_bench_keys(wl))
    target_by_batch = {b["batchId"]: b["modelIds"] for b in plan["batches"]}

    print("=== GATHER VALIDATION ===")
    weak_count = 0
    valid_count = 0
    for path in sorted(
        glob.glob(str(project / ".aicodermap-agent-out-batch*.gather.json"))
    ):
        bid = (
            Path(path)
            .name.replace(".aicodermap-agent-out-", "")
            .replace(".gather.json", "")
        )
        targets = target_by_batch.get(bid)
        if targets is None:
            print(f"[?] {bid}: no target_model_ids found in plan, skipping")
            continue
        v = validate_gather_file(path, targets)
        s = v["stats"]
        flag = "OK" if v["valid"] and not s.get("isWeakBatch") else "WEAK"
        print(
            f"[{flag:4}] {bid:30} obs={s.get('observations', 0):3} "
            f"avg={s.get('avgObs', 0):.1f} errors={len(v['errors'])} warnings={len(v['warnings'])}"
        )
        for e in v["errors"][:2]:
            print(f"        ERROR: {e}")
        if not v["valid"] or s.get("isWeakBatch"):
            weak_count += 1
        if v["valid"]:
            valid_count += 1

    print(f"\nSUMMARY: weak={weak_count} valid={valid_count}")
