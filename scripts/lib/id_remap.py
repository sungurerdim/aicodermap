"""Lineup-driven model ID remap helper (F2.3).

Replaces the hardcoded ID_FIXES dict that was in gather-union.py (deprecated):
    ID_FIXES = {"kimi-k2": "kimi-k2-6", "grok-3-5": None}

All ID remaps are now derived from the lineup-cache written by Step 0
lineup discovery. The hardcoded dict violated feedback_no_hardcoded_model_patches.

Usage:
    from lib.id_remap import build_remap_table, fix_id

    remap = build_remap_table()          # loads from .aicodermap-lineup-cache.json
    canonical = fix_id("kimi-k2", remap) # → "kimi-k2-6" (or None if discarded)

Stdlib-only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT = Path(__file__).resolve().parents[2]
LINEUP_CACHE_PATH = PROJECT / "data" / ".aicodermap-lineup-cache.json"
LEGACY_LINEUP_CACHE_PATH = PROJECT / ".aicodermap-lineup-cache.json"


def build_remap_table(
    cache_path: str | Path | None = None,
) -> dict[str, str | None]:
    """Build a {old_id → new_id | None} remap table from the lineup cache.

    None as a value means "this model ID was determined to be fictional/discarded".
    If the cache does not exist, returns an empty table (no remaps — safe default).
    """
    paths_to_try: list[Path] = []
    if cache_path:
        paths_to_try.append(Path(cache_path))
    paths_to_try += [LINEUP_CACHE_PATH, LEGACY_LINEUP_CACHE_PATH]

    cache: dict[str, Any] = {}
    for p in paths_to_try:
        if p.is_file():
            try:
                cache = json.loads(p.read_text(encoding="utf-8"))
                break
            except (OSError, json.JSONDecodeError):
                continue

    remap: dict[str, str | None] = {}

    # Shape 1: {vendorId: {renamed: [{from, to}], discarded: [id, ...]}}
    for vendor_data in cache.values():
        if not isinstance(vendor_data, dict):
            continue
        for entry in vendor_data.get("renamed", []) or []:
            old = entry.get("from")
            new = entry.get("to")
            if isinstance(old, str) and old:
                remap[old] = new if isinstance(new, str) and new else None
        for discarded_id in vendor_data.get("discarded", []) or []:
            if isinstance(discarded_id, str) and discarded_id:
                remap[discarded_id] = None

    # Shape 2: top-level renamed[] array (flat format some lineup agents emit)
    for entry in cache.get("renamed", []) or []:
        if not isinstance(entry, dict):
            continue
        old = entry.get("from")
        new = entry.get("to")
        if isinstance(old, str) and old:
            remap[old] = new if isinstance(new, str) and new else None

    return remap


def fix_id(
    model_id: str,
    remap: dict[str, str | None] | None = None,
) -> str | None:
    """Return the canonical model ID for model_id.

    Returns:
        str   — canonical ID (may be unchanged if not in remap table)
        None  — model should be discarded (fictional / retired ID)

    If remap is None, loads the table from disk on every call (slow; for
    one-off use only — callers processing many IDs should pre-build the
    table with build_remap_table()).
    """
    if remap is None:
        remap = build_remap_table()
    if model_id not in remap:
        return model_id
    return remap[model_id]  # may be str or None


def apply_remap_to_observations(
    observations: list[dict],
    remap: dict[str, str | None],
) -> list[dict]:
    """Rewrite modelId in every observation using remap table.

    Observations whose modelId maps to None are dropped.
    """
    out: list[dict] = []
    for obs in observations:
        mid = obs.get("modelId") or ""
        canonical = fix_id(mid, remap)
        if canonical is None:
            continue  # discard this observation
        if canonical != mid:
            obs = {**obs, "modelId": canonical}
        out.append(obs)
    return out
