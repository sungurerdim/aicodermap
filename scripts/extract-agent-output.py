#!/usr/bin/env python3
"""Extract last balanced JSON object containing 'confidence' from a Claude Code
persisted tool-result file. Writes the slice to OUT_PATH.

Usage: python scripts/extract-agent-output.py <persisted_path> <out_path>
"""

import json
import sys
from pathlib import Path


def find_last_json(text: str, marker: str = '"confidence"') -> str:
    """Find every JSON object that starts at a `{` and contains `marker`,
    parse-validate each, and return the LAST one that parses cleanly."""
    occurrences = []
    i = -1
    while True:
        i = text.find(marker, i + 1)
        if i < 0:
            break
        occurrences.append(i)

    candidates: list[str] = []
    for occ in occurrences:
        # Walk back to nearest `{` (not inside a string would require full lex,
        # but in agent output the marker is always a top-level key so the `{`
        # right before is the object opener)
        s = occ
        while s > 0 and text[s] != "{":
            s -= 1
        if text[s] != "{":
            continue
        depth = 0
        in_str = False
        esc = False
        end = -1
        for j in range(s, len(text)):
            c = text[j]
            if esc:
                esc = False
                continue
            if c == "\\" and in_str:
                esc = True
                continue
            if c == '"':
                in_str = not in_str
                continue
            if in_str:
                continue
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    end = j
                    break
        if end > s:
            slice_ = text[s : end + 1]
            try:
                json.loads(slice_)
                candidates.append(slice_)
            except json.JSONDecodeError:
                pass
    if not candidates:
        raise SystemExit(f"no parseable JSON object found containing {marker}")
    return candidates[-1]


def text_from_persisted_array(path: Path) -> str:
    """Persisted tool-result format: JSON array of {type, text} blocks."""
    arr = json.loads(path.read_text(encoding="utf-8"))
    return "".join(blk.get("text", "") for blk in arr if blk.get("type") == "text")


def text_from_subagent_jsonl(path: Path) -> str:
    """Subagent transcript: one JSON message per line. Concatenate every
    assistant-text-block content (in order) so the final emit lands at the tail."""
    parts: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        # message may be at top level or nested under 'message'
        body = msg.get("message", msg)
        content = body.get("content")
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            for blk in content:
                if isinstance(blk, dict) and blk.get("type") == "text":
                    parts.append(blk.get("text", ""))
    return "\n".join(parts)


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "usage: extract-agent-output.py <persisted_path|subagent_jsonl> <out_path>",
            file=sys.stderr,
        )
        return 2
    persisted = Path(sys.argv[1])
    out = Path(sys.argv[2])
    if persisted.suffix == ".jsonl":
        text = text_from_subagent_jsonl(persisted)
    else:
        text = text_from_persisted_array(persisted)
    obj_str = find_last_json(text)
    obj = json.loads(obj_str)
    out.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    keys = ",".join(list(obj.keys())[:8])
    print(
        f"wrote {out} ({len(obj_str)} chars; keys={keys}; models={len(obj.get('models', []))})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
