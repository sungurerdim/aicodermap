#!/usr/bin/env python3
"""Remove a bench key from every canonical surface.

Usage:
    python scripts/strip-bench-key.py <key> [--dry-run]

Surfaces patched:
  1. data/sources-whitelist.json  _schema.coreBenchKeys
  2. data/sources-whitelist.json  _schema.benchAliases
  3. data/sources-whitelist.json  _schema.benchCategories[*].keys
  4. data/sources-whitelist.json  leaderboards[].publishes[] (all entries)
  5. data/models.json             bench.<key> (null entries only — safety)
  6. data/sources.json            <modelId>.<key> entries
  7. i18n/en.json                 benchmarks.<key>
  8. i18n/tr.json                 benchmarks.<key>
  9. assets/js/core.js            BENCH_KEYS, DEFAULT_WEIGHTS, PRESETS

Post-condition: audit-data-coherence + audit-bench-source-mapping both PASS.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))


def _load(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data: dict | list, dry_run: bool) -> int:
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if dry_run:
        print(f"  [dry-run] would write {path.relative_to(PROJECT)}")
        return 0
    path.write_text(text, encoding="utf-8")
    return 1


def _strip_whitelist(key: str, dry_run: bool) -> int:
    path = PROJECT / "data" / "sources-whitelist.json"
    wl = _load(path)
    schema = wl.get("_schema", {})
    changed = 0

    # coreBenchKeys
    before = len(schema.get("coreBenchKeys", []))
    schema["coreBenchKeys"] = [k for k in schema.get("coreBenchKeys", []) if k != key]
    changed += before - len(schema["coreBenchKeys"])

    # benchAliases
    if key in schema.get("benchAliases", {}):
        del schema["benchAliases"][key]
        changed += 1

    # benchCategories
    for cat in schema.get("benchCategories", []):
        before_cat = len(cat.get("keys", []))
        cat["keys"] = [k for k in cat.get("keys", []) if k != key]
        changed += before_cat - len(cat["keys"])

    # leaderboards[].publishes[]
    for lb in wl.get("leaderboards", []):
        pubs = lb.get("publishes", [])
        new_pubs = []
        for item in pubs:
            if isinstance(item, str) and item == key:
                changed += 1
            elif isinstance(item, dict) and item.get("key") == key:
                changed += 1
            else:
                new_pubs.append(item)
        lb["publishes"] = new_pubs

    if changed:
        print(f"  sources-whitelist.json: {changed} reference(s) removed")
        return _save(path, wl, dry_run)
    print(f"  sources-whitelist.json: key '{key}' not found")
    return 0


def _strip_models(key: str, dry_run: bool) -> int:
    path = PROJECT / "data" / "models.json"
    models = _load(path)
    if not isinstance(models, list):
        models = models.get("models", [])
    changed = 0
    for m in models:
        bench = m.get("bench")
        if isinstance(bench, dict) and key in bench:
            # Only remove if null — non-null values should not exist if key is fictional
            if bench[key] is None:
                del bench[key]
                changed += 1
            else:
                print(
                    f"  WARNING: {m['id']}.bench.{key} = {bench[key]} (non-null; skipped)"
                )
    if changed:
        print(f"  models.json: {changed} null bench.{key} entries removed")
        return _save(path, models, dry_run)
    print(f"  models.json: key '{key}' not found in any bench object")
    return 0


def _strip_sources(key: str, dry_run: bool) -> int:
    path = PROJECT / "data" / "sources.json"
    sources = _load(path)
    suffix = f".{key}"
    to_delete = [k for k in sources if k.endswith(suffix)]
    for k in to_delete:
        del sources[k]
    if to_delete:
        print(f"  sources.json: {len(to_delete)} entries removed")
        return _save(path, sources, dry_run)
    print(f"  sources.json: no '{key}' suffix entries found")
    return 0


def _strip_i18n(key: str, lang: str, dry_run: bool) -> int:
    path = PROJECT / "i18n" / f"{lang}.json"
    data = _load(path)
    benchmarks = data.get("benchmarks", {})
    if key in benchmarks:
        del benchmarks[key]
        print(f"  i18n/{lang}.json: benchmarks.{key} removed")
        return _save(path, data, dry_run)
    print(f"  i18n/{lang}.json: benchmarks.{key} not found")
    return 0


def _strip_core_js(key: str, dry_run: bool) -> int:
    path = PROJECT / "assets" / "js" / "core.js"
    src = path.read_text(encoding="utf-8")
    changed = 0

    # BENCH_KEYS array: remove the key token
    new_src = re.sub(rf"'(?:{re.escape(key)})'\s*,?\s*", "", src)
    if new_src != src:
        changed += 1
        src = new_src

    # DEFAULT_WEIGHTS: remove key: N entry
    new_src = re.sub(rf"\b{re.escape(key)}\s*:\s*\d+\s*,?\s*", "", src)
    if new_src != src:
        changed += 1
        src = new_src

    if changed:
        print(f"  core.js: {changed} occurrence(s) removed")
        if not dry_run:
            path.write_text(src, encoding="utf-8")
        else:
            print(f"  [dry-run] would write assets/js/core.js")
        return 1
    print(f"  core.js: key '{key}' not found")
    return 0


def _run_audits() -> bool:
    py = sys.executable
    for script in ("audit-data-coherence.py", "audit-bench-source-mapping.py"):
        result = subprocess.run(
            [py, str(PROJECT / "scripts" / script)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            print(f"\n✗ {script} FAILED:", file=sys.stderr)
            print(result.stderr or result.stdout, file=sys.stderr)
            return False
        print(f"  ✓ {script} PASS")
    return True


def main() -> int:
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if not a.startswith("--")]
    if not args:
        print(
            "Usage: python scripts/strip-bench-key.py <key> [--dry-run]",
            file=sys.stderr,
        )
        return 2
    key = args[0]
    print(
        f"\nStripping bench key '{key}' from all canonical surfaces{' (dry-run)' if dry_run else ''}..."
    )

    _strip_whitelist(key, dry_run)
    _strip_models(key, dry_run)
    _strip_sources(key, dry_run)
    _strip_i18n(key, "en", dry_run)
    _strip_i18n(key, "tr", dry_run)
    _strip_core_js(key, dry_run)

    if not dry_run:
        print("\nRunning post-strip audits...")
        if not _run_audits():
            print("\n✗ Audits failed — review the output above.", file=sys.stderr)
            return 1
        print(f"\n✓ Key '{key}' fully stripped. All audits pass.")
    else:
        print(f"\n[dry-run complete] Run without --dry-run to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
