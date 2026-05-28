"""Remap non-canonical bench keys in agent artifact before merge.

Canonical keys per data/sources-whitelist.json._schema.coreBenchKeys.
Synth agent occasionally emits version-suffixed (`lcbV6`) or legacy
(`aider`, `aaAgentic`, `aaCoding`) keys. Policy:
  - `lcbV6` -> `lcb`  (V6 is the current LiveCodeBench revision)
  - everything else not in coreBenchKeys -> drop

Operates on .aicodermap-agent-out.json IN PLACE. Stdlib-only.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ARTIFACT = REPO / ".aicodermap-agent-out.json"
WL = REPO / "data" / "sources-whitelist.json"

REMAP = {"lcbV6": "lcb"}


def main() -> int:
    wl = json.loads(WL.read_text(encoding="utf-8"))
    canon = set(wl.get("_schema", {}).get("coreBenchKeys", []))
    if not canon:
        print("ERROR: empty coreBenchKeys")
        return 1

    art = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    remapped = 0
    dropped = 0

    for m in art.get("models", []):
        upd = m.get("updates", {})
        if not isinstance(upd, dict):
            continue
        bench = upd.get("bench")
        if not isinstance(bench, dict):
            continue
        new_bench: dict = {}
        for k, v in bench.items():
            target = REMAP.get(k, k)
            if target in canon:
                # range check for bench values
                if isinstance(v, (int, float)) and (v < 0 or v > 100):
                    print(f"  drop {m['id']}.{k}={v} (out of [0,100])")
                    dropped += 1
                    continue
                if target != k:
                    remapped += 1
                new_bench[target] = v
            else:
                dropped += 1
        upd["bench"] = new_bench

        srcs = m.get("sourcesAdded", [])
        if isinstance(srcs, list):
            new_srcs = []
            for s in srcs:
                if not isinstance(s, dict):
                    continue
                key = s.get("key", "")
                if "." in key:
                    prefix, suffix = key.rsplit(".", 1)
                    if suffix in REMAP:
                        s["key"] = f"{prefix}.{REMAP[suffix]}"
                        remapped += 1
                new_srcs.append(s)
            m["sourcesAdded"] = new_srcs

    contradictions = art.get("contradictions", [])
    if isinstance(contradictions, list):
        new_c = []
        for c in contradictions:
            if not isinstance(c, dict):
                continue
            field = c.get("field", "")
            if field in REMAP:
                c["field"] = REMAP[field]
                remapped += 1
            elif field and field not in canon and "." not in field:
                dropped += 1
                continue
            new_c.append(c)
        art["contradictions"] = new_c

    ARTIFACT.write_text(json.dumps(art, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"=== FIX === remapped={remapped} dropped={dropped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
