#!/usr/bin/env python3
"""Purge fabricated citations sourced from SPA-shell leaderboard URLs.

Background — FAZ 6.A (2026-05-10):
A previous cycle (2026-05-09) extracted 26 `tb2` values from
`https://tbench.ai/leaderboard`, citing them as I-tier with verifications=1
and trustScore=0.333. The actual snapshot of that URL is a 57KB SPA shell
with zero model rows — the values were either WebSearch snippet hallucinations
or cross-row misattribution. The I-tier-overrides-S-tier auto-resolution
rule then promoted these fabricated values over multi-source S/C consensus.

Concrete impact:
  • deepseek-v4-pro.tb2 = 50.3 (SPA) ← consensus 67.9×4 (officechai S-tier + 2 community)
  • glm-5-1.tb2         = 9.1  (SPA) ← consensus 63.5×5 (proper www.tbench.ai/.../2.0 subpath)
  • deepseek-v4-flash.tb2 = 48.9 (SPA) ← consensus 56.9×2
  • 9 cells with NO other source (pure fabrications) — bench cleared to null

This script:
  1. Reads data/sources.json + data/models.json
  2. Drops every entry whose URL matches any URL in
     sources-whitelist.json `_runtime.unhealthy` map (the SPA-shell list)
  3. Recomputes the bench value per cell from remaining citations
     (highest trustScore wins; if no remaining citation, set to null)
  4. Writes models.json + sources.json (.bak rotation handled by merge.py
     pre-existing convention; here we rotate ourselves to be safe)
  5. Prints a per-cell delta report

This is a defensive one-shot. Going forward, agents must be prevented from
re-citing SPA-shell URLs — see scripts/lib/synth.py FAZ 6.A guard for the
runtime defense.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

ROOT = Path(__file__).resolve().parent.parent
SOURCES_PATH = ROOT / "data" / "sources.json"
MODELS_PATH = ROOT / "data" / "models.json"
WHITELIST_PATH = ROOT / "data" / "sources-whitelist.json"


def _norm_url(u: str | None) -> str:
    return (u or "").strip().rstrip("/").lower()


def _rotate_bak(p: Path) -> None:
    bak = p.with_suffix(p.suffix + ".bak")
    bak2 = p.with_suffix(p.suffix + ".bak2")
    if bak.exists():
        shutil.copy2(bak, bak2)
    if p.exists():
        shutil.copy2(p, bak)


def main() -> int:
    wl = json.loads(WHITELIST_PATH.read_text(encoding="utf-8"))
    unhealthy_map = (wl.get("_runtime") or {}).get("unhealthy") or {}
    unhealthy_urls = {_norm_url(u) for u, flag in unhealthy_map.items() if flag}
    if not unhealthy_urls:
        print("⚠ no unhealthy URLs in whitelist _runtime — nothing to purge")
        return 0

    print(f"=== PURGING SPA-SHELL CITATIONS ===")
    print(f"unhealthy URL set: {sorted(unhealthy_urls)}")

    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    models = json.loads(MODELS_PATH.read_text(encoding="utf-8"))
    models_by_id = {m["id"]: m for m in models}

    purged_count = 0
    affected_cells: list[tuple[str, Any, Any, str]] = []  # (flatkey, old, new, reason)

    for flatkey, entries in list(sources.items()):
        if not isinstance(entries, list):
            continue
        # Split into kept vs purged.
        kept = []
        dropped = []
        for e in entries:
            if not isinstance(e, dict):
                kept.append(e)
                continue
            if _norm_url(e.get("url")) in unhealthy_urls:
                dropped.append(e)
            else:
                kept.append(e)
        if not dropped:
            continue
        purged_count += len(dropped)
        sources[flatkey] = kept

        # Recompute bench value if this is a bench cell (modelId.benchKey).
        if "." not in flatkey:
            continue
        mid, fkey = flatkey.split(".", 1)
        # bench cells live under model.bench.<key>
        if fkey.startswith("bench."):
            fkey = fkey[len("bench.") :]
        m = models_by_id.get(mid)
        if not m:
            continue
        bench = m.setdefault("bench", {})
        if fkey not in bench:
            continue

        old_val = bench.get(fkey)
        # Pick winner from kept entries: highest trustScore × verifications,
        # tiebreak by tier (I>S>C) then most recent date.
        TIER_RANK = {"I": 3, "S": 2, "C": 1, "U": 0}

        def _key(e: dict[str, Any]) -> tuple[float, int, str]:
            ts = float(e.get("trustScore") or 0)
            tr = TIER_RANK.get(e.get("tier") or "", 0)
            dt = str(e.get("date") or e.get("fetched") or "")
            return (ts, tr, dt)

        candidates = [
            e for e in kept if isinstance(e, dict) and e.get("value") is not None
        ]
        if not candidates:
            new_val = None
            reason = "no other citations — cleared to null"
        else:
            winner = max(candidates, key=_key)
            new_val = winner.get("value")
            reason = (
                f"reverted to {winner.get('tier')}-tier {winner.get('source', '?')[:30]}"
                f" trust={winner.get('trustScore')}"
            )
        if new_val != old_val:
            bench[fkey] = new_val
            affected_cells.append((flatkey, old_val, new_val, reason))

    print(
        f"\n✓ purged {purged_count} fabricated citations across "
        f"{len(affected_cells)} bench cells\n"
    )

    if affected_cells:
        print(f"{'Cell':<36} {'old':>8} → {'new':>8}  reason")
        print(f"{'-' * 36} {'-' * 8}   {'-' * 8}  {'-' * 40}")
        for fk, old, new, reason in affected_cells:
            print(f"{fk:<36} {str(old):>8} → {str(new):>8}  {reason}")

    # Rotate backups + write.
    _rotate_bak(SOURCES_PATH)
    _rotate_bak(MODELS_PATH)
    SOURCES_PATH.write_text(
        json.dumps(sources, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    MODELS_PATH.write_text(
        json.dumps(models, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\n✓ wrote {SOURCES_PATH.relative_to(ROOT)}")
    print(f"✓ wrote {MODELS_PATH.relative_to(ROOT)}")
    print(f"  backups rotated to .bak / .bak2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
