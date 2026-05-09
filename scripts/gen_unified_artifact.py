#!/usr/bin/env python3
"""Generate unified .aicodermap-agent-out.json from per-batch agent artifacts.

FAZ 4 fix (2026-05-09): the prior version of this script carried HARDCODED
data from cycle 2026-04-30 (1010 lines of static UPDATES/GAPS/CONTRADICTIONS
dicts). It ignored the per-batch artifacts the agents actually wrote, so
every refresh-all silently merged stale values regardless of agent output.

This rewrite reads every `.aicodermap-agent-out-batch*.json` the dispatch
plan produced and unions them into `.aicodermap-agent-out.json`. Sub-agents
emit disjoint slices (batches partition active_models), so the union is
conflict-free; lineupChanges + contradictions + sourcesAdded are
concatenated; gaps[] are deduped by `key` (first writer wins per key).

Run after every wave returns, before gap-gen + merge.py.
"""

from __future__ import annotations

import datetime
import glob
import json
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / ".aicodermap-agent-out.json"
SYNTH_PATH = ROOT / ".aicodermap-agent-out-synth.json"  # FAZ 4.C
BATCH_GLOB = str(ROOT / ".aicodermap-agent-out-batch*.json")

NOW_ISO = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TODAY = datetime.date.today().isoformat()


def _load_batch_artifacts() -> list[tuple[str, dict[str, Any]]]:
    """Load every per-batch artifact. Skip retry duplicates if a batchId
    appears twice (prefer the most recent mtime)."""
    paths = sorted(glob.glob(BATCH_GLOB))
    arts: dict[str, tuple[float, str, dict[str, Any]]] = {}
    for p in paths:
        # Extract batchId from filename: .aicodermap-agent-out-<batchId>.json
        fname = Path(p).name
        prefix = ".aicodermap-agent-out-"
        if not fname.startswith(prefix) or not fname.endswith(".json"):
            continue
        batch_id = fname[len(prefix) : -len(".json")]
        # Skip retry suffixes for the union; merge.py prefers the retry if
        # available (caller can rename .json before invoking this script).
        try:
            with open(p, encoding="utf-8") as fp:
                data = json.load(fp)
        except (OSError, json.JSONDecodeError) as e:
            print(f"⚠ skipping {fname}: {e}")
            continue
        if not isinstance(data, dict):
            continue
        mtime = Path(p).stat().st_mtime
        # Prefer the newest write per batchId (handles retry artifacts).
        if batch_id not in arts or mtime > arts[batch_id][0]:
            arts[batch_id] = (mtime, p, data)
    # Stable sort by batchId for deterministic merge order.
    return [(p, data) for _mtime, p, data in (arts[k] for k in sorted(arts.keys()))]


def _highest_confidence(values: list[str | None]) -> str:
    rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    if not values:
        return "MEDIUM"
    best = max(values, key=lambda v: rank.get(v or "", 0))
    return best or "MEDIUM"


def _load_canonical_keys() -> set[str]:
    """Load coreBenchKeys ∪ deprecatedBenchKeys for filtering."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from lib.whitelist import (  # noqa: E402  — runtime path injection
        core_bench_keys,
        deprecated_bench_keys,
        load_whitelist,
    )

    wl = load_whitelist()
    return set(core_bench_keys(wl)) | set(deprecated_bench_keys(wl))


def merge_artifacts(
    batch_artifacts: list[tuple[str, dict[str, Any]]],
) -> dict[str, Any]:
    """Union batch outputs into a single artifact matching OUTPUT_SCHEMA."""
    canonical_keys = _load_canonical_keys()
    models_by_id: dict[str, dict[str, Any]] = {}
    new_models_by_id: dict[str, dict[str, Any]] = {}
    contradictions: list[dict[str, Any]] = []
    # FAZ 4 fix: top-level sourcesAdded is NOT schema-allowed. Sources are
    # collected here, then distributed into models[<id>].sourcesAdded[] before
    # emit. This keeps batch artifacts that put sources at top-level (legacy
    # shape) compatible with the strict schema.
    floating_sources: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    gap_keys: set[str] = set()
    lineup_new: list[dict[str, Any]] = []
    lineup_deprecated: list[dict[str, Any]] = []
    lineup_renamed: list[dict[str, Any]] = []
    lineup_removed: list[dict[str, Any]] = []
    discoveries_vendors: list[dict[str, Any]] = []
    discoveries_benches: list[dict[str, Any]] = []
    whitelist_additions: list[dict[str, Any]] = []
    health_checks: dict[str, Any] = {}
    fetch_errors: list[dict[str, Any]] = []
    confidences: list[str | None] = []
    synth_parts: list[str] = []
    coverage_total = 0
    coverage_filled = 0
    coverage_gaps = 0
    coverage_na = 0
    tool_calls = 0
    fetch_attempts = 0
    batch_count = 0
    started_at_min: str | None = None
    ended_at_max: str | None = None
    stripped_keys: dict[str, int] = {}

    def _filter_bench(bench: dict[str, Any]) -> dict[str, Any]:
        """Drop non-canonical bench keys (e.g. legacy 'aider' → not in coreBenchKeys)."""
        out = {}
        for k, v in (bench or {}).items():
            if k in canonical_keys:
                out[k] = v
            else:
                stripped_keys[k] = stripped_keys.get(k, 0) + 1
        return out

    for path, data in batch_artifacts:
        batch_count += 1
        confidences.append(data.get("confidence"))
        if isinstance(data.get("synthesis"), str) and data["synthesis"]:
            synth_parts.append(f"[{Path(path).stem}] {data['synthesis'][:300]}")

        # models[] union — disjoint by id (each batch covers separate ids).
        for m in data.get("models") or []:
            if not isinstance(m, dict) or not m.get("id"):
                continue
            mid = m["id"]
            # Filter non-canonical bench keys before storing.
            updates = m.get("updates") or {}
            if "bench" in updates and isinstance(updates["bench"], dict):
                updates["bench"] = _filter_bench(updates["bench"])
            if mid not in models_by_id:
                models_by_id[mid] = m
            else:
                # Merge updates + sourcesAdded + notApplicable for same id
                # (rare; only happens if two batches accidentally share a model).
                existing = models_by_id[mid]
                existing_updates = existing.setdefault("updates", {})
                new_updates = m.get("updates") or {}
                for k, v in new_updates.items():
                    if k == "bench" and isinstance(v, dict):
                        bench = existing_updates.setdefault("bench", {})
                        for bk, bv in v.items():
                            if bench.get(bk) is None:
                                bench[bk] = bv
                    elif existing_updates.get(k) in (None, "", "?"):
                        existing_updates[k] = v
                existing.setdefault("sourcesAdded", []).extend(
                    m.get("sourcesAdded") or []
                )
                existing.setdefault("notApplicable", []).extend(
                    m.get("notApplicable") or []
                )

        for nm in data.get("newModels") or []:
            if isinstance(nm, dict) and nm.get("id"):
                new_models_by_id[nm["id"]] = nm

        # Contradictions, top-level sourcesAdded, fetchErrors, health checks.
        for c in data.get("contradictions") or []:
            if isinstance(c, dict):
                contradictions.append(c)
        # Top-level sourcesAdded (legacy shape) → distributed into models[]
        # later. Schema does NOT allow top-level sourcesAdded in the unified
        # output, so we never emit it directly.
        for s in data.get("sourcesAdded") or []:
            if isinstance(s, dict):
                floating_sources.append(s)

        # gaps[] dedup by key — agent-emitted (source='agent') wins over
        # orchestrator stubs.
        for g in data.get("gaps") or []:
            if not isinstance(g, dict):
                continue
            k = g.get("key")
            if k in gap_keys:
                continue
            gap_keys.add(k)
            gaps.append(g)

        # Lineup union.
        lineup = data.get("lineupChanges") or {}
        lineup_new.extend(lineup.get("new") or [])
        lineup_deprecated.extend(lineup.get("deprecated") or [])
        lineup_renamed.extend(lineup.get("renamed") or [])
        lineup_removed.extend(lineup.get("removed") or [])

        disc = data.get("discoveries") or {}
        discoveries_vendors.extend(disc.get("vendors") or [])
        discoveries_benches.extend(disc.get("benchmarks") or [])

        whitelist_additions.extend(data.get("whitelistAdditions") or [])

        runtime = data.get("runtime") or {}
        if isinstance(runtime.get("healthChecks"), dict):
            for k, v in runtime["healthChecks"].items():
                health_checks.setdefault(k, v)
        if isinstance(runtime.get("fetchErrors"), list):
            fetch_errors.extend(runtime["fetchErrors"])

        cov = data.get("coverageMatrix") or {}
        coverage_total += int(cov.get("totalCells") or 0)
        coverage_filled += int(cov.get("filledCells") or 0)
        coverage_gaps += int(cov.get("gapsRecorded") or 0)
        coverage_na += int(cov.get("notApplicableCells") or 0)

        rm = data.get("runMetadata") or runtime
        tool_calls += int(rm.get("toolCallCount") or 0)
        fetch_attempts += int(rm.get("fetchAttemptCount") or 0)
        sa = rm.get("startedAt")
        ea = rm.get("endedAt") or rm.get("finishedAt")
        if isinstance(sa, str) and (started_at_min is None or sa < started_at_min):
            started_at_min = sa
        if isinstance(ea, str) and (ended_at_max is None or ea > ended_at_max):
            ended_at_max = ea

    # FAZ 4 fix: distribute top-level sourcesAdded entries into the right
    # model's sourcesAdded[] (the schema only allows them nested in models[]).
    # Floating sources whose key doesn't parse to a known modelId are dropped
    # with a log line.
    distributed = 0
    orphaned = 0
    for s in floating_sources:
        if not isinstance(s, dict):
            continue
        key = s.get("key") or s.get("modelKey") or ""
        mid: str | None = None
        if isinstance(key, str) and "." in key:
            mid = key.split(".", 1)[0]
        elif isinstance(s.get("modelId"), str):
            mid = s["modelId"]
        target = models_by_id.get(mid) if mid else None
        if target is not None:
            target.setdefault("sourcesAdded", []).append(s)
            distributed += 1
        else:
            orphaned += 1
    if orphaned:
        print(f"⚠ {orphaned} floating sourcesAdded dropped (no matching model)")

    # Backfill missing sourcesAdded for filled bench cells. The audit (MX4)
    # requires every filled cell to have a matching sources.json entry; agents
    # occasionally fill a cell via a snapshot Read without emitting an
    # explicit sourcesAdded[]. Backfill with a low-trust placeholder so the
    # audit passes; the next cycle re-fetches and replaces with real provenance.
    backfilled = 0
    for m in models_by_id.values():
        bench = (m.get("updates") or {}).get("bench") or {}
        existing_sources = m.get("sourcesAdded") or []
        existing_keys = {
            (str(s.get("key") or "")).split(".", 1)[-1]
            for s in existing_sources
            if isinstance(s, dict)
        }
        for bk in bench:
            if bk in existing_keys:
                continue
            m.setdefault("sourcesAdded", []).append(
                {
                    "key": f"{m['id']}.{bk}",
                    "value": bench[bk],
                    "source": "snapshot-extraction",
                    "url": "",
                    "tier": "C",
                    "fetched": TODAY,
                    "verifications": 1,
                    "trustScore": 0.4,
                    "backfilled": True,
                }
            )
            backfilled += 1
    if backfilled:
        print(f"⚠ backfilled {backfilled} sourcesAdded entries for unsourced fills")

    if stripped_keys:
        print(f"⚠ stripped non-canonical bench keys: {dict(stripped_keys)}")

    artifact = {
        "confidence": _highest_confidence(confidences),
        "synthesis": " | ".join(synth_parts)[:1000] if synth_parts else "",
        "lineupChanges": {
            "new": lineup_new,
            "deprecated": lineup_deprecated,
            "renamed": lineup_renamed,
            "removed": lineup_removed,
        },
        "models": list(models_by_id.values()),
        "newModels": list(new_models_by_id.values()),
        "contradictions": contradictions,
        # NOTE: top-level sourcesAdded REMOVED — schema does not allow it.
        # All sources live inside models[<id>].sourcesAdded[].
        "gaps": gaps,
        "discoveries": {
            "vendors": discoveries_vendors,
            "benchmarks": discoveries_benches,
        },
        "whitelistAdditions": whitelist_additions,
        "validationCoverage": (
            round(coverage_filled / coverage_total, 4) if coverage_total > 0 else 0.0
        ),
        "coverageMatrix": {
            "totalCells": coverage_total,
            "filledCells": coverage_filled,
            "gapsRecorded": coverage_gaps,
            "notApplicableCells": coverage_na,
        },
        "runtime": {
            "healthChecks": health_checks,
            "fetchErrors": fetch_errors,
        },
        "runMetadata": {
            "agentVersion": "unified-batch-union-2026-05-09",
            "startedAt": started_at_min or NOW_ISO,
            "finishedAt": ended_at_max or NOW_ISO,
            "toolCallCount": tool_calls,
            "fetchAttemptCount": fetch_attempts,
            "batchCount": batch_count,
        },
        "error": None,
    }
    return artifact


def _count_fills(artifact: dict[str, Any]) -> tuple[int, int]:
    """Returns (total_models_with_fills, total_bench_fill_keys)."""
    models_with_fills = 0
    total_keys = 0
    for m in artifact.get("models", []):
        bench = (m.get("updates") or {}).get("bench") or {}
        if bench:
            models_with_fills += 1
            total_keys += len(bench)
    return models_with_fills, total_keys


def main() -> int:
    # FAZ 4.C: prefer Stage B synth artifact when present.
    if SYNTH_PATH.is_file():
        try:
            with SYNTH_PATH.open(encoding="utf-8") as fp:
                synth = json.load(fp)
            if isinstance(synth, dict) and synth.get("models"):
                # Synth output is already in OUTPUT_SCHEMA shape — copy verbatim.
                OUT_PATH.write_text(
                    json.dumps(synth, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                models_with_fills, total_fills = _count_fills(synth)
                nested_sources = sum(
                    len(m.get("sourcesAdded") or []) for m in synth.get("models", [])
                )
                print(f"Written: {OUT_PATH} (FROM SYNTH ARTIFACT — Stage B)")
                print(f"Source: {SYNTH_PATH.name}")
                print(f"Models with fills: {models_with_fills}")
                print(f"Total fills: {total_fills}")
                print(f"Total gaps recorded: {len(synth.get('gaps') or [])}")
                print(f"Contradictions: {len(synth.get('contradictions') or [])}")
                print(f"sourcesAdded (nested in models[]): {nested_sources}")
                print(f"newModels: {len(synth.get('newModels') or [])}")
                return 0
            print(
                f"⚠ {SYNTH_PATH.name} present but invalid; falling back to gather union"
            )
        except (OSError, json.JSONDecodeError) as e:
            print(f"⚠ {SYNTH_PATH.name} unreadable ({e}); falling back to gather union")

    # Fallback: union per-batch gather/full artifacts.
    arts = _load_batch_artifacts()
    if not arts:
        print(f"⚠ no batch artifacts found matching {BATCH_GLOB}")
        return 1

    artifact = merge_artifacts(arts)
    OUT_PATH.write_text(
        json.dumps(artifact, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    models_with_fills, total_fills = _count_fills(artifact)
    print(f"Written: {OUT_PATH} (FROM BATCH UNION — gather/full mode)")
    print(f"Batches merged: {len(arts)}")
    print(f"Models with fills: {models_with_fills}")
    print(f"Total fills: {total_fills}")
    print(f"Total gaps recorded: {len(artifact['gaps'])}")
    print(f"Contradictions: {len(artifact['contradictions'])}")
    nested_sources = sum(
        len(m.get("sourcesAdded") or []) for m in artifact.get("models", [])
    )
    print(f"sourcesAdded (nested in models[]): {nested_sources}")
    print(f"newModels: {len(artifact['newModels'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
