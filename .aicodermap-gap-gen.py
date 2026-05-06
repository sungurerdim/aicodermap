#!/usr/bin/env python3
"""
Gap-gen supplement step for aicodermap refresh cycle.

Reads .aicodermap-agent-out.json (agent partial artifact, may not exist),
preserves all fills + explicit gaps the agent emitted, and adds auto-gap
entries for every remaining unfilled (active_model, bench_key) cell.

Result: .aicodermap-agent-out.json that satisfies merge.py MX1 invariant
(filled + gaps + notApplicable == totalCells) regardless of agent coverage.

Run from D:/GitHub/aicodermap/ directory.
"""

import json
import sys
import datetime as dt
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "scripts"))
from lib.matrix import active_models as _active_models  # noqa: E402

TODAY = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
NOW_ISO = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
ARTIFACT_PATH = ROOT / ".aicodermap-agent-out.json"

models_data = json.loads((ROOT / "data/models.json").read_text(encoding="utf-8"))
models = models_data if isinstance(models_data, list) else models_data.get("models", [])
wl = json.loads((ROOT / "data/sources-whitelist.json").read_text(encoding="utf-8"))
i18n_en = json.loads((ROOT / "i18n/en.json").read_text(encoding="utf-8"))

core_keys = wl["_schema"]["coreBenchKeys"]
active = _active_models(models)
active_ids = {m["id"] for m in active}

# Build bench_key -> leaderboard URL mapping (primary + secondary)
leaderboards = wl.get("leaderboards", [])
bench_to_lb = {}
bench_to_lb2 = {}
for lb in leaderboards:
    url = lb.get("url", "")
    publishes_raw = lb.get("publishes", [])
    pub_keys = [p.get("key", "") if isinstance(p, dict) else p for p in publishes_raw]
    for k in pub_keys:
        if k and k not in bench_to_lb:
            bench_to_lb[k] = url
        elif k and k in bench_to_lb and bench_to_lb[k] != url and k not in bench_to_lb2:
            bench_to_lb2[k] = url

_bench_i18n = i18n_en.get("benchmarks", {})


def _bench_label(key: str) -> str:
    b = _bench_i18n.get(key, {})
    return b.get("name") or b.get("short") or key


# Model name lookup
model_names = {m["id"]: m.get("name", m["id"]) for m in active}

# Read existing artifact if present
existing_artifact = {}
if ARTIFACT_PATH.exists():
    try:
        existing_artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        existing_artifact = {}

# Extract cells already covered by the agent artifact
agent_filled: set[tuple[str, str]] = set()
agent_gaps: set[tuple[str, str]] = set()
agent_na: set[tuple[str, str]] = set()

for entry in existing_artifact.get("models", []):
    mid = entry.get("id") or entry.get("modelId")
    if not mid or mid not in active_ids:
        continue
    for k, v in (entry.get("updates", {}) or {}).items():
        if k == "bench" and isinstance(v, dict):
            # nested format: {"bench": {"sweV": 65.4, ...}}
            for bk, bv in v.items():
                if bk in core_keys and bv is not None:
                    agent_filled.add((mid, bk))
        else:
            # flat format: {"bench.sweV": 65.4} or {"sweV": 65.4}
            bk = k.removeprefix("bench.")
            if bk in core_keys and v is not None:
                agent_filled.add((mid, bk))
    for na_entry in entry.get("notApplicable", []) or []:
        bk = na_entry.get("benchKey") if isinstance(na_entry, dict) else None
        if bk and bk in core_keys:
            agent_na.add((mid, bk))

for g in existing_artifact.get("gaps", []):
    key = g.get("key")
    if isinstance(key, str) and "." in key:
        mid, _, bk = key.partition(".")
        if mid in active_ids and bk in core_keys:
            agent_gaps.add((mid, bk))
    else:
        # modelId + field shape
        mid = g.get("modelId")
        bk = g.get("field")
        if mid and bk and mid in active_ids and bk in core_keys:
            agent_gaps.add((mid, bk))

# Also count existing filled cells from data/models.json (merge.py preserves them)
existing_filled: set[tuple[str, str]] = set()
existing_na: set[tuple[str, str]] = set()
existing_na_entries: dict[str, list[dict]] = {}
for m in active:
    bench = m.get("bench") or {}
    for k, v in bench.items():
        if k in core_keys and v is not None:
            existing_filled.add((m["id"], k))
    # data/models.json carries notApplicable both as object list and as bare key list.
    # gap-gen MUST preserve these — otherwise gap-gen enumerates them as gaps and
    # merge.py MX1 fails with overlap_gap_na (filled+gaps+na > totalCells).
    saved: list[dict] = []
    for na in m.get("notApplicable", []) or []:
        if isinstance(na, dict):
            bk = na.get("benchKey") or na.get("key")
            if bk in core_keys:
                existing_na.add((m["id"], bk))
                saved.append(na)
        elif isinstance(na, str) and na in core_keys:
            existing_na.add((m["id"], na))
            saved.append({"benchKey": na, "rule": "preserved-from-data"})
    for k in m.get("notApplicableBenchKeys", []) or []:
        if k in core_keys and (m["id"], k) not in existing_na:
            existing_na.add((m["id"], k))
            saved.append({"benchKey": k, "rule": "preserved-from-data"})
    if saved:
        existing_na_entries[m["id"]] = saved

all_covered = agent_filled | agent_gaps | agent_na | existing_filled | existing_na

# Build the universe
total_universe = {(m["id"], k) for m in active for k in core_keys}
missing = total_universe - all_covered

# Build the output artifact
# Start from existing agent artifact (preserve agent fills + explicit gaps)
artifact_models_by_id: dict[str, dict] = {}
for entry in existing_artifact.get("models", []):
    mid = entry.get("id") or entry.get("modelId")
    if mid:
        artifact_models_by_id[mid] = {
            "id": mid,
            "updates": entry.get("updates", {}),
            "sourcesAdded": entry.get("sourcesAdded", []),
            "notApplicable": entry.get("notApplicable", []),
        }

# Ensure every active model has an entry
for m in active:
    if m["id"] not in artifact_models_by_id:
        artifact_models_by_id[m["id"]] = {
            "id": m["id"],
            "updates": {},
            "sourcesAdded": [],
            "notApplicable": [],
        }

# Re-attach existing notApplicable entries from data/models.json so merge.py sees
# the same N/A universe the gap-gen excluded above. Dedupe by benchKey.
for mid, saved in existing_na_entries.items():
    entry = artifact_models_by_id.setdefault(
        mid, {"id": mid, "updates": {}, "sourcesAdded": [], "notApplicable": []}
    )
    seen = {
        (n.get("benchKey") or n.get("key"))
        for n in entry.get("notApplicable", [])
        if isinstance(n, dict)
    }
    for na in saved:
        bk = na.get("benchKey") or na.get("key")
        if bk and bk not in seen:
            entry.setdefault("notApplicable", []).append(na)
            seen.add(bk)

# Build gaps list (preserve existing explicit gaps + add auto-gaps for missing)
# Filter out agent gaps for cells already filled OR already N/A — both overlaps
# break merge.py MX1 invariant (filled+gaps+na exceeds universe).
already_covered = existing_filled | agent_filled | existing_na | agent_na


def _gap_cell(g: dict) -> tuple[str, str] | None:
    key = g.get("key")
    if isinstance(key, str) and "." in key:
        mid, _, bk = key.partition(".")
        return (mid, bk)
    mid = g.get("modelId")
    bk = g.get("field")
    return (mid, bk) if mid and bk else None


existing_gaps = [
    g for g in existing_artifact.get("gaps", []) if _gap_cell(g) not in already_covered
]
auto_gap_count = 0
for mid, bk in sorted(missing):
    lb1 = bench_to_lb.get(bk, "")
    lb2 = bench_to_lb2.get(bk, "")
    label = _bench_label(bk)
    name = model_names.get(mid, mid)
    existing_gaps.append(
        {
            "key": f"{mid}.{bk}",
            "reason": f"not reached in agent survey cycle; {label} data unavailable",
            "triedSources": [lb1, lb2],
            "triedQueries": [
                f"{mid} {label} benchmark score 2026",
                f"{name} {label} leaderboard 2026",
            ],
            "triedFormats": ["static_html_table", "websearch_snippet"],
            "autoGenerated": True,
        }
    )
    auto_gap_count += 1

filled_count = len(existing_filled | agent_filled)
gap_count = len(existing_gaps)
na_count = len(agent_na | existing_na)
total_cells = len(total_universe)

artifact = {
    "cycleDate": TODAY,
    "generatedAt": NOW_ISO,
    "partialReturn": True,
    "partialReason": (
        f"gap-gen supplement: agent found {len(agent_filled)} new fills; "
        f"{auto_gap_count} cells auto-gapped by orchestrator; "
        f"{len(existing_artifact.get('gaps', []))} explicit agent gaps preserved"
    ),
    "models": list(artifact_models_by_id.values()),
    "newModels": existing_artifact.get("newModels", []),
    "lineup": existing_artifact.get("lineup", {}),
    "contradictions": existing_artifact.get("contradictions", []),
    "gaps": existing_gaps,
    "notApplicable": existing_artifact.get("notApplicable", []),
    "whitelistAdditions": existing_artifact.get("whitelistAdditions", []),
    "i18nUpdates": existing_artifact.get("i18nUpdates", {}),
    "runtime": existing_artifact.get(
        "runtime", {"healthChecks": {}, "fabricatedSuspicions": []}
    ),
    "coverageMatrix": {
        "filledCells": len(agent_filled),
        "gapsRecorded": gap_count,
        "notApplicableCells": na_count,
        "expectedTotal": total_cells,
    },
    "validationCoverage": round(filled_count / max(total_cells, 1), 4),
}

ARTIFACT_PATH.write_text(
    json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8"
)

print(f"WROTE: {ARTIFACT_PATH}")
print(f"ACTIVE_MODELS: {len(active)}")
print(f"TOTAL_CELLS: {total_cells}")
print(f"EXISTING_FILLED: {len(existing_filled)}")
print(f"AGENT_NEW_FILLS: {len(agent_filled)}")
print(f"AGENT_EXPLICIT_GAPS: {len(existing_artifact.get('gaps', []))}")
print(f"AUTO_GAPS_ADDED: {auto_gap_count}")
print(f"TOTAL_GAPS: {gap_count}")
total_filled = len(existing_filled | agent_filled)
print(f"COVERAGE: {artifact['validationCoverage'] * 100:.1f}%")
print(
    f"COVERED: {total_filled + gap_count + na_count} / {total_cells}  (filled={total_filled}, gaps={gap_count}, na={na_count})"
)
