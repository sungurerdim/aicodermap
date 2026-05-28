#!/usr/bin/env python3
"""
Gap-gen supplement step for aicodermap refresh cycle.

Reads .aicodermap-agent-out.json (agent partial artifact, may not exist),
preserves all fills + explicit gaps the agent emitted, and adds auto-gap
entries for every remaining unfilled (active_model, bench_key) cell.

Result: .aicodermap-agent-out.json that satisfies merge.py MX1 invariant
(filled + gaps == totalCells) regardless of agent coverage. N/A retired
2026-05-25: every unmeasured cell is a gap, re-researched each cycle.

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

ROOT = Path(__file__).resolve().parent.parent
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

for entry in existing_artifact.get("models", []):
    mid = entry.get("id") or entry.get("modelId")
    if not mid or mid not in active_ids:
        continue
    for k, v in (entry.get("updates", {}) or {}).items():
        if k == "bench" and isinstance(v, dict):
            for bk, bv in v.items():
                if bk in core_keys and bv is not None:
                    agent_filled.add((mid, bk))
        elif k in core_keys and v is not None:
            agent_filled.add((mid, k))

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

# Also count existing filled cells from data/models.json (merge.py preserves them).
# N/A retired 2026-05-25: notApplicable / notApplicableBenchKeys are ignored —
# previously-N/A cells fall into `missing` below and become gaps.
existing_filled: set[tuple[str, str]] = set()
for m in active:
    bench = m.get("bench") or {}
    for k, v in bench.items():
        if k in core_keys and v is not None:
            existing_filled.add((m["id"], k))

all_covered = agent_filled | agent_gaps | existing_filled

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
            "notApplicable": [],
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

# Build gaps list (preserve existing explicit gaps + add auto-gaps for missing)
# Filter out agent gaps for cells already filled (overlap would break the
# filled+gaps invariant).
already_covered = existing_filled | agent_filled


def _gap_cell(g: dict) -> tuple[str, str] | None:
    key = g.get("key")
    if isinstance(key, str) and "." in key:
        mid, _, bk = key.partition(".")
        return (mid, bk)
    mid = g.get("modelId")
    bk = g.get("field")
    return (mid, bk) if mid and bk else None


def _normalize_existing_gap(g):
    """FAZ 4.B (2026-05-08): every gap carries `source` ∈ {'agent','orchestrator'}.
    autoGenerated=True is the authoritative signal for orchestrator stubs —
    overrides any previously-mistagged source field."""
    out = dict(g) if isinstance(g, dict) else {}
    if out.get("autoGenerated"):
        out["source"] = "orchestrator"
    elif "source" not in out:
        out["source"] = "agent"
    return out


existing_gaps = [
    _normalize_existing_gap(g)
    for g in existing_artifact.get("gaps", [])
    if _gap_cell(g) not in already_covered
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
            # FAZ 4.B (2026-05-08): explicit source so CHANGELOG + audit can
            # distinguish "agent tried-and-failed" from "orchestrator placeholder".
            "source": "orchestrator",
            "autoGenerated": True,
        }
    )
    auto_gap_count += 1

filled_count = len(existing_filled | agent_filled)
gap_count = len(existing_gaps)
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
    "notApplicable": [],
    "whitelistAdditions": existing_artifact.get("whitelistAdditions", []),
    "i18nUpdates": existing_artifact.get("i18nUpdates", {}),
    "runtime": existing_artifact.get(
        "runtime", {"healthChecks": {}, "fabricatedSuspicions": []}
    ),
    "coverageMatrix": {
        "filledCells": len(agent_filled),
        "gapsRecorded": gap_count,
        "notApplicableCells": 0,
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
    f"COVERED: {total_filled + gap_count} / {total_cells}  (filled={total_filled}, gaps={gap_count})"
)
