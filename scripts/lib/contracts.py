"""Bench-type-aware contract helpers (F5.2).

Single source for per-bench delta thresholds. Previously the contradiction
pipeline used flat global constants (CONTRADICTION_WARN_PP=3.0 / BLOCK_PP=5.0)
which caused false positives on ELO benches (±50 is normal) and false negatives
on tight percentage benches (±1 is meaningful).

Schema source: data/sources-whitelist.json `_schema.benchTypes`
Shape per entry:
  {
    "swePro":   {"scale": "percent", "warnDelta": 1.5, "blockDelta": 3.0, "range": [0, 100]},
    "cfElo":    {"scale": "elo",     "warnDelta": 25,  "blockDelta": 50,  "range": [800, 2000]},
    "aiderPoly":{"scale": "percent", "warnDelta": 2.0, "blockDelta": 4.0, "range": [0, 100]}
  }

Falls back to global CONTRADICTION_WARN_PP / CONTRADICTION_BLOCK_PP from
scripts/lib/constants.py when a key is absent from the schema.

Stdlib-only.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT = Path(__file__).resolve().parents[2]
WHITELIST_PATH = PROJECT / "data" / "sources-whitelist.json"

# Hard-coded fallback defaults (mirror constants.py)
_DEFAULT_WARN_PP: float = 3.0
_DEFAULT_BLOCK_PP: float = 5.0
_DEFAULT_AGREEMENT_PP: float = 1.5

# Built-in bench-type defaults applied when whitelist entry missing.
# Keys: canonical bench key → (scale, warnDelta, blockDelta)
_BUILTIN_BENCH_TYPES: dict[str, tuple[str, float, float]] = {
    # Percentage benchmarks — tight thresholds
    "swePro": ("percent", 1.5, 3.0),
    "sweV": ("percent", 2.0, 4.0),
    "sweMulti": ("percent", 2.0, 4.0),
    "lcb": ("percent", 2.0, 4.0),
    "lcbV6": ("percent", 2.0, 4.0),
    "aider": ("percent", 2.0, 4.0),
    "aiderPoly": ("percent", 2.0, 4.0),
    "tb2": ("percent", 2.0, 4.0),
    "tau2": ("percent", 2.0, 4.0),
    "mcpA": ("percent", 2.0, 4.0),
    "bfcl": ("percent", 2.0, 4.0),
    "gpqa": ("percent", 2.0, 4.0),
    "hle": ("percent", 2.0, 4.0),
    "mmluPro": ("percent", 2.0, 4.0),
    "aime26": ("percent", 2.0, 4.0),
    "aaIdx": ("percent", 2.0, 4.0),
    "aaCoding": ("percent", 2.0, 4.0),
    "aaAgentic": ("percent", 2.0, 4.0),
    "aaOmni": ("percent", 2.0, 4.0),
    # ELO benchmarks — wide thresholds
    "cfElo": ("elo", 25.0, 50.0),
    "webDevElo": ("elo", 25.0, 50.0),
}


def _load_bench_types(whitelist_path: Path | None = None) -> dict[str, dict[str, Any]]:
    """Load _schema.benchTypes from whitelist. Returns {} on missing/error."""
    path = whitelist_path or WHITELIST_PATH
    try:
        wl = json.loads(path.read_text(encoding="utf-8"))
        return wl.get("_schema", {}).get("benchTypes") or {}
    except (OSError, json.JSONDecodeError, AttributeError):
        return {}


def bench_delta_thresholds(
    bench_key: str,
    *,
    whitelist_path: Path | None = None,
    bench_types: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return per-bench contradiction thresholds for bench_key.

    Lookup order:
      1. Caller-supplied bench_types dict (avoids repeated disk reads)
      2. data/sources-whitelist.json `_schema.benchTypes`
      3. _BUILTIN_BENCH_TYPES hardcoded defaults
      4. Global fallback (3.0 / 5.0)

    Returns
    -------
    dict with keys:
        scale       str   — "percent" | "elo" | "raw"
        warnDelta   float — YELLOW contradiction threshold
        blockDelta  float — RED contradiction threshold
        agreementPP float — within-cluster agreement tolerance
        range       [min, max] | None
    """
    # 1. Caller-supplied
    bt = bench_types if bench_types is not None else _load_bench_types(whitelist_path)
    entry = bt.get(bench_key)

    if entry and isinstance(entry, dict):
        scale = str(entry.get("scale") or "percent")
        warn = float(entry.get("warnDelta") or _DEFAULT_WARN_PP)
        block = float(entry.get("blockDelta") or _DEFAULT_BLOCK_PP)
        rng = entry.get("range")
        # Agreement tolerance = warnDelta / 2 (reasonable heuristic)
        agree = float(entry.get("agreementPP") or warn / 2)
        return {
            "scale": scale,
            "warnDelta": warn,
            "blockDelta": block,
            "agreementPP": agree,
            "range": rng,
        }

    # 3. Built-in defaults
    if bench_key in _BUILTIN_BENCH_TYPES:
        scale, warn, block = _BUILTIN_BENCH_TYPES[bench_key]
        return {
            "scale": scale,
            "warnDelta": warn,
            "blockDelta": block,
            "agreementPP": warn / 2,
            "range": [0, 100] if scale == "percent" else None,
        }

    # 4. Global fallback
    return {
        "scale": "percent",
        "warnDelta": _DEFAULT_WARN_PP,
        "blockDelta": _DEFAULT_BLOCK_PP,
        "agreementPP": _DEFAULT_AGREEMENT_PP,
        "range": None,
    }


def all_bench_thresholds(
    bench_keys: list[str],
    *,
    whitelist_path: Path | None = None,
) -> dict[str, dict[str, Any]]:
    """Batch-load thresholds for all bench_keys (single whitelist read)."""
    bt = _load_bench_types(whitelist_path)
    return {k: bench_delta_thresholds(k, bench_types=bt) for k in bench_keys}
