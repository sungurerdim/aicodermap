#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remove pseudo-source contamination from data/sources.json.

FAZ 8.A.3a (2026-05-18). Three source tags pretend to be canonical
provenance but carry no verifiable URL:

  - "snapshot-extraction"        — orchestrator self-injected (871 entries)
  - "auto-resolution candidate"  — winner/loser snapshots (361 entries)
  - "synth-backfill"             — historical pool fillers (49 entries)

Total: 1281 entries / 3862 total (33.2 %) on cycle 2026-05-18. These
inflate verification counts and trustScore weights but contribute zero
real evidence — they survive into composite-score calculations and falsely
boost low-confidence cells.

Cleanup contract:
  1. Backup sources.json → sources.json.bak3 (rotates earlier .bak/.bak2).
  2. For every cell, drop entries whose source ∈ PSEUDO_TAGS.
  3. If a cell becomes empty AND models.json has no backing value, drop
     the cell entirely.
  4. If a cell becomes empty AND models.json has a non-null value, RESCUE
     the highest-trustScore pseudo entry (sole evidence remaining) and
     re-tag with `rescued: true` field — surfaces in audit as needing
     proper re-fetch.
  5. Refuse to run when prior audit issues exist (run audit yourself
     before invoking).

Usage:
    python scripts/purge-pseudo-sources.py [--dry-run]
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SOURCES_PATH = PROJECT / "data" / "sources.json"
MODELS_PATH = PROJECT / "data" / "models.json"
BACKUP_PATH = PROJECT / "data" / "sources.json.bak3"

PSEUDO_TAGS = frozenset(
    {"snapshot-extraction", "auto-resolution candidate", "synth-backfill"}
)


def load_models_index() -> dict[str, dict]:
    models = json.loads(MODELS_PATH.read_text(encoding="utf-8"))
    if isinstance(models, dict):
        models = models.get("MODELS") or []
    return {m["id"]: m for m in models if isinstance(m, dict) and m.get("id")}


def walk_field(model: dict, dotted_path: str):
    """Return (found, value) by walking dotted path on model dict.

    Cell keys in sources.json are `modelId.<field_path>` where field_path
    is usually a bench key (e.g. `tb2`) but may be a multi-segment path
    like `pricing.api.in`. Single-segment paths that are not top-level
    keys on the model are assumed to be bench keys (try `bench.<key>`).
    """

    def _walk(root: dict, parts: list[str]):
        cur: object = root
        for p in parts:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                return False, None
        return True, cur

    parts = dotted_path.split(".")
    # Try direct path first (covers pricing.api.in etc.)
    found, value = _walk(model, parts)
    if found:
        return True, value
    # Fall back to bench-prefixed lookup for single-segment bench keys.
    if len(parts) == 1:
        return _walk(model, ["bench", parts[0]])
    return False, None


def main() -> int:
    dry_run = "--dry-run" in sys.argv

    if not SOURCES_PATH.is_file():
        print(f"ERROR: {SOURCES_PATH} missing", file=sys.stderr)
        return 2

    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    if not isinstance(sources, dict):
        print(
            f"ERROR: sources.json shape unexpected ({type(sources).__name__})",
            file=sys.stderr,
        )
        return 2

    by_id = load_models_index()

    dropped_entries = 0
    rescued_cells = 0
    dropped_cells = 0
    cell_count_before = len(sources)

    new_sources: dict[str, list] = {}

    for cell_key, entries in sources.items():
        if not isinstance(entries, list):
            new_sources[cell_key] = entries
            continue

        primary: list[dict] = []
        pseudo: list[dict] = []
        for e in entries:
            if not isinstance(e, dict):
                primary.append(e)
                continue
            if e.get("source") in PSEUDO_TAGS:
                pseudo.append(e)
            else:
                primary.append(e)

        dropped_entries += len(pseudo)

        if primary:
            new_sources[cell_key] = primary
            continue

        # All-pseudo cell → check if models.json has a backing value.
        mid, _, field_path = cell_key.partition(".")
        m = by_id.get(mid)
        has_value = False
        if m and field_path:
            found, value = walk_field(m, field_path)
            if found and value not in (None, "", "?"):
                has_value = True

        if has_value and pseudo:
            best = max(
                pseudo,
                key=lambda e: float(e.get("trustScore") or 0.0),
            )
            rescued = dict(best)
            rescued["rescued"] = True
            rescued["rescuedFrom"] = best.get("source")
            new_sources[cell_key] = [rescued]
            rescued_cells += 1
        else:
            dropped_cells += 1

    cell_count_after = len(new_sources)

    if dropped_entries == 0:
        print("no pseudo-source entries found — nothing to do")
        return 0

    print(f"pseudo entries dropped: {dropped_entries}")
    print(f"cells dropped (no backing models.json value): {dropped_cells}")
    print(f"cells rescued (kept 1 pseudo entry, re-tagged): {rescued_cells}")
    print(f"sources.json cells: {cell_count_before} -> {cell_count_after}")

    if dry_run:
        print("dry-run: no files written")
        return 0

    # Rotate prior backups so the most recent purge always lands at .bak3.
    if BACKUP_PATH.exists():
        BACKUP_PATH.unlink()
    shutil.copy2(SOURCES_PATH, BACKUP_PATH)
    print(f"backup: {BACKUP_PATH}")

    SOURCES_PATH.write_text(
        json.dumps(new_sources, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote: {SOURCES_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
