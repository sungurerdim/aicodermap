#!/usr/bin/env python3
"""Complete whitelist `publishes[]` from observed provenance (2026-05-27).

Layer-1 source-authorization was scoped to the Elo family because the whitelist
`publishes[]` lists were incomplete (e.g. Artificial Analysis declares sweV but
not swePro, though it reports both) — a strict all-family check cried wolf
(167 false positives). This derives each scoped source's REAL bench coverage from
what it has actually contributed in data/sources.json and UNIONS it into the
whitelist entry's `publishes[]`. Result: accurate, data-driven, self-maintaining
(re-run each refresh) coverage that lets the audit's source-authorization guard
run across ALL confusable families with low noise. Also improves the agent's
source routing (which sources publish which benches).

Policy:
  - Only entries that ALREADY declare a NON-EMPTY publishes[] are extended
    (scoped leaderboards). Aggregators with empty publishes[] (openrouter,
    together = "publish everything", pricing) stay unconstrained.
  - publishes[] := sorted(declared ∪ observed-for-domain ∩ canonical benches).
    Union only — never removes a declared bench.

Stdlib-only. Idempotent. Rotates .bak.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from lib.util import extract_domain  # noqa: E402

WL = ROOT / "data" / "sources-whitelist.json"
SOURCES = ROOT / "data" / "sources.json"
CATS = ("leaderboards", "aggregators", "local", "community", "registries")


def _dom(u) -> str:
    return extract_domain(u or "")


def main() -> int:
    wl = json.loads(WL.read_text(encoding="utf-8"))
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))
    schema = wl.get("_schema") or {}
    canonical = set(schema.get("coreBenchKeys") or []) | set(
        schema.get("emergingBenchKeys") or []
    )

    # domain -> observed bench keys (from real provenance)
    observed: dict[str, set] = {}
    for key, entries in sources.items():
        if "." not in key or not isinstance(entries, list):
            continue
        bk = key.rsplit(".", 1)[1]
        if bk not in canonical:
            continue
        for e in entries:
            d = _dom(e.get("url"))
            if d:
                observed.setdefault(d, set()).add(bk)

    changed = 0
    added_total = 0
    for cat in CATS:
        for e in wl.get(cat) or []:
            declared = e.get("publishes")
            if not declared:  # unconstrained (aggregator) — leave as-is
                continue
            d = _dom(e.get("url"))
            obs = observed.get(d, set())
            new = sorted((set(declared) | obs) & canonical)
            if new != sorted(declared):
                added = sorted(set(new) - set(declared))
                added_total += len(added)
                changed += 1
                e["publishes"] = new

    shutil.copy2(WL, WL.with_suffix(".json.bak"))
    WL.write_text(json.dumps(wl, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"=== DERIVE PUBLISHES === entries updated: {changed}  benches added: {added_total}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
