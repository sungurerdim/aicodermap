#!/usr/bin/env python3
"""One-time mechanical migration: clean cfElo metric mis-classification (2026-05-27).

The cfElo cell must hold a Codeforces competitive-programming rating ONLY
(CodeElo / contest-judging; realistic 2026 frontier range ~2000-3300; human
scale 800-3800). Targeted research (primary sources: DeepSeek HF card, Qwen3
Technical Report arXiv:2505.09388, OpenAI o3/o4-mini announcement, Codeforces
blog 137539, Artificial Analysis) found the cell polluted with three other
things, mis-recorded into cfElo:

  - LMArena / Chatbot-Arena general chat Elo (~1480-1500) — belongs in
    lmArenaElo, NOT cfElo.
  - GDPval-AA agentic Elo (a third AA metric) — belongs in neither column.
  - A wrong-model copy (qwen3-235b's 2056 duplicated onto the 480B Coder row).

Verdicts (model -> action), each backed by the research above:
  CLEAR cfElo (value + provenance + quarantine flag) — value is not a Codeforces
  rating for this model:
    gpt-5-4 (1484, LMArena), gpt-5-5 (1488, LMArena), grok-4-20 (1491, LMArena),
    grok-4-3 (1500, GDPval-AA), qwen3-coder-480b (2056, wrong-model attribution).
  UN-QUARANTINE cfElo — value confirmed a real Codeforces rating by a primary
  source, so it should count:
    deepseek-v4-pro (3206, DeepSeek official HF card; field 2800-3200).
  DROP a single mis-attributed observation (keep the real winner):
    o4-mini.cfElo: drop 2070 (that figure is DeepSeek v3.1 Div.2 from
    arXiv:2602.05891, mis-labeled), keep 2719 (OpenAI official).

KEEP untouched (confirmed real Codeforces): qwen3-235b (2056), gemma-3-27b (110,
genuinely below-Newbie), o3 (2727), gemini-3-1-pro (3052).

Mechanical + research-sourced (per project rule: schema/metric migrations may use
scripts; the per-cell verdict comes from cited research, not an arbitrary patch).
Idempotent. Rotates .bak. Recurrence is prevented by the agent.md cfElo/lmArenaElo
disambiguation rule + the audit-data-coherence cfElo plausibility check.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "data" / "models.json"
SOURCES = ROOT / "data" / "sources.json"

CLEAR_CFELO = {
    "gpt-5-4",
    "gpt-5-5",
    "grok-4-20",
    "grok-4-3",
    "qwen3-coder-480b",
}
UNQUARANTINE_CFELO = {"deepseek-v4-pro"}
DROP_OBS = {("o4-mini", "cfElo", 2070.0)}


def main() -> int:
    models = json.loads(MODELS.read_text(encoding="utf-8"))
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))
    cleared, unquar, dropped = [], [], []

    for m in models:
        mid = m.get("id")
        bench = m.get("bench") or {}
        bq = m.get("benchQuarantine") or {}
        if mid in CLEAR_CFELO and bench.get("cfElo") is not None:
            cleared.append(f"{mid}={bench['cfElo']}")
            bench.pop("cfElo", None)
            bq.pop("cfElo", None)
            sources.pop(f"{mid}.cfElo", None)
        if mid in UNQUARANTINE_CFELO and bq.get("cfElo"):
            unquar.append(f"{mid}={bench.get('cfElo')}")
            bq.pop("cfElo", None)
        if "benchQuarantine" in m:
            m["benchQuarantine"] = bq

    for mid, bk, badval in DROP_OBS:
        key = f"{mid}.{bk}"
        entries = sources.get(key)
        if isinstance(entries, list):
            kept = [
                e
                for e in entries
                if e.get("value") is None or round(float(e["value"]), 0) != badval
            ]
            if len(kept) != len(entries):
                dropped.append(f"{key} -{badval}")
                sources[key] = kept

    shutil.copy2(MODELS, MODELS.with_suffix(".json.bak"))
    shutil.copy2(SOURCES, SOURCES.with_suffix(".json.bak"))
    MODELS.write_text(
        json.dumps(models, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    SOURCES.write_text(
        json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"cleared cfElo (misfiled): {cleared}")
    print(f"un-quarantined cfElo (confirmed real): {unquar}")
    print(f"dropped mis-attributed obs: {dropped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
