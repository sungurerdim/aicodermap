#!/usr/bin/env python3
"""Validate .aicodermap-agent-out.json against the agent output schema.

Usage:
    python scripts/validate-agent-out.py [path]

Exit code:
  0  valid
  1  validation errors
  2  file not found / JSON parse error
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.jsonschema_min import validate  # noqa: E402

SCHEMA_PATH = Path(__file__).resolve().parent / "lib" / "agent-out.schema.json"
DEFAULT_ARTIFACT = PROJECT / ".aicodermap-agent-out.json"

for _stream in (sys.stdout, sys.stderr):
    _reconf = getattr(_stream, "reconfigure", None)
    if callable(_reconf):
        try:
            _reconf(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    artifact_path = Path(args[0]) if args else DEFAULT_ARTIFACT

    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"validate-agent-out: cannot load schema: {exc}", file=sys.stderr)
        return 2

    try:
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(
            f"validate-agent-out: artifact not found: {artifact_path}", file=sys.stderr
        )
        return 2
    except json.JSONDecodeError as exc:
        print(
            f"validate-agent-out: JSON parse error in {artifact_path}: {exc}",
            file=sys.stderr,
        )
        return 2

    errors = validate(artifact, schema)

    # F3: reject flat bench keys (e.g. updates["bench.swePro"] instead of updates.bench.swePro)
    flat_key_errors: list[str] = []
    bench_prefix_src_errors: list[str] = []
    for model_entry in artifact.get("models") or []:
        mid = model_entry.get("id") or "?"
        updates = model_entry.get("updates") or {}
        flat_bench = [k for k in updates if k.startswith("bench.")]
        if flat_bench:
            flat_key_errors.append(
                f"model {mid}: flat bench keys in updates (must use nested bench object): "
                + ", ".join(flat_bench[:5])
            )
        for s in model_entry.get("sourcesAdded") or []:
            if not isinstance(s, dict):
                continue
            key = s.get("key", "")
            if ".bench." in key or key.startswith("bench."):
                bench_prefix_src_errors.append(
                    f"model {mid}: sourcesAdded key '{key}' uses legacy bench.X prefix"
                )
    if flat_key_errors:
        errors = (errors or []) + [f"FLAT_BENCH_KEY: {e}" for e in flat_key_errors]
    if bench_prefix_src_errors:
        errors = (errors or []) + [
            f"LEGACY_BENCH_PREFIX: {e}" for e in bench_prefix_src_errors
        ]

    if errors:
        print(f"✗ Agent output INVALID — {len(errors)} error(s):", file=sys.stderr)
        for e in errors[:20]:
            print(f"  {e}", file=sys.stderr)
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more", file=sys.stderr)
        return 1

    cycles = artifact.get("cycleDate", "?")
    models_n = len(artifact.get("models", []))
    gaps_n = len(artifact.get("gaps", []))
    print(
        f"✓ Agent output valid  (cycleDate={cycles}, models={models_n}, gaps={gaps_n})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
