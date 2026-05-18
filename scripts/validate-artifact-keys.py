#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pre-merge guard: reject artifacts containing non-canonical bench keys.

Runs between `gen_unified_artifact.py` and `gap_gen.py`. If any
`models[].updates.bench` key is missing from
`_schema.coreBenchKeys ∪ _schema.emergingBenchKeys`, exit 1 BEFORE
merge.py rolls back.

Without this gate, cycle 2026-05-18 saw synth emit `lcbV6, aider,
aaCoding` (when not yet promoted to core) — merge.py audit MX4 then
rolled back the entire models.json write, losing every valid update.
Pre-emit detection saves the cycle.

Usage:
    python scripts/validate-artifact-keys.py <artifact.json> [<artifact2.json> ...]

Exit codes:
    0  all artifacts clean
    1  non-canonical keys detected
    2  usage / IO error
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))

from lib.whitelist import all_bench_keys, load_whitelist  # noqa: E402


def validate_one(path: Path, canonical: set[str]) -> list[str]:
    """Return list of human-readable violation messages for one artifact."""
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"{path.name}: parse error ({e})"]

    violations: list[str] = []
    models = obj.get("models", []) or []
    for m in models:
        if not isinstance(m, dict):
            continue
        mid = m.get("id") or m.get("modelId") or "<unknown>"
        bench = ((m.get("updates") or {}).get("bench")) or {}
        if not isinstance(bench, dict):
            continue
        bad = [k for k in bench.keys() if k not in canonical]
        for k in bad:
            violations.append(f"{path.name}: {mid}.{k} (non-canonical)")
    return violations


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "usage: validate-artifact-keys.py <artifact.json> [...]",
            file=sys.stderr,
        )
        return 2

    wl = load_whitelist()
    canonical = set(all_bench_keys(wl))
    if not canonical:
        print(
            "ERROR: whitelist coreBenchKeys + emergingBenchKeys empty", file=sys.stderr
        )
        return 2

    all_violations: list[str] = []
    for arg in sys.argv[1:]:
        p = Path(arg)
        if not p.exists():
            print(f"skip: {p} (missing)", file=sys.stderr)
            continue
        all_violations.extend(validate_one(p, canonical))

    if all_violations:
        print(
            f"REJECT: {len(all_violations)} non-canonical bench key(s) "
            f"(canonical universe size={len(canonical)})",
            file=sys.stderr,
        )
        for v in all_violations[:50]:
            print(f"  {v}", file=sys.stderr)
        if len(all_violations) > 50:
            print(f"  ... +{len(all_violations) - 50} more", file=sys.stderr)
        return 1

    print(f"OK: {len(sys.argv) - 1} artifact(s), 0 non-canonical keys")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
