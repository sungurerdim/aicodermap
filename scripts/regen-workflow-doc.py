#!/usr/bin/env python3
"""Sync docs/WORKFLOW.md with SKILL.md (F6.1).

Detects and repairs known drift points between SKILL.md orchestration spec
and docs/WORKFLOW.md. Does NOT regenerate the whole document — it targets
specific lines that encode workflow step descriptions and replaces them when
they diverge from the canonical SKILL.md behaviour.

Usage:
  python scripts/regen-workflow-doc.py          # apply fixes + add marker
  python scripts/regen-workflow-doc.py --check  # exit 1 if drift detected

The top-of-file marker signals the document is managed by this script:
  <!-- AUTO-GENERATED FROM SKILL.md - DO NOT EDIT MANUALLY -->

Stdlib-only.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
WORKFLOW_MD = PROJECT / "docs" / "WORKFLOW.md"
SKILL_MD = PROJECT / ".claude" / "skills" / "aicodermap" / "SKILL.md"

_AUTO_MARKER = "<!-- AUTO-GENERATED FROM SKILL.md - DO NOT EDIT MANUALLY -->"

# Each tuple: (pattern_to_find [regex], replacement_text).
# Patterns are anchored to the ASCII-box step lines in section 1 (Happy Path).
# SKILL.md authority for each fix:
#   - auto-approve: feedback_autonomy_default memory + SKILL.md no explicit user-approve step
#   - auto-push: feedback_skill_auto_push memory + SKILL.md Step 12 auto git push
_DRIFT_FIXES: list[tuple[str, str]] = [
    (
        r"│10\. User review \+ approve \(or override per-entry\)\s*│",
        "│10. Skill auto-validates diff (no manual approval — autonomous)    │",
    ),
    (
        r"│13\. User git commit \+ push \(or skill auto with confirmation\)\s*│",
        "│13. Skill: git add + commit + push (auto on clean self-check)      │",
    ),
    (
        # Section 3 step 3 — old "skill asks scope question" wording that implies blocking prompt
        r"│ 3\. Skill asks: \"Full refresh\? Specific model\? New release\?\"\s*│",
        "│ 3. Skill resolves scope (refresh-all / specific / new-release)   │",
    ),
    (
        # "Adding a new bench key" checklist step 4 — old manual BENCH_KEYS edit instruction
        r"(4\. `assets/js/core\.js BENCH_KEYS` — append to mirror canonical universe\.)",
        "4. Run `python scripts/gen-bench-keys.py` (auto-syncs core.js BENCH_KEYS from whitelist).",
    ),
]


def _apply_fixes(text: str) -> tuple[str, list[str]]:
    """Apply all drift fixes. Returns (new_text, list_of_applied_fix_descriptions)."""
    applied: list[str] = []
    for pattern, replacement in _DRIFT_FIXES:
        new_text, n = re.subn(pattern, replacement, text)
        if n:
            # ASCII-safe description for Windows consoles that reject Unicode box chars
            desc = (
                pattern[:60].encode("ascii", errors="replace").decode("ascii").rstrip()
            )
            applied.append(desc)
            text = new_text
    return text, applied


def _check_drift(text: str) -> list[str]:
    """Return list of patterns that still match (i.e. drift present)."""
    drifted: list[str] = []
    for pattern, _ in _DRIFT_FIXES:
        if re.search(pattern, text):
            desc = (
                pattern[:60].encode("ascii", errors="replace").decode("ascii").rstrip()
            )
            drifted.append(desc)
    return drifted


def _ensure_marker(text: str) -> str:
    """Prepend auto-generated marker if not already present."""
    if _AUTO_MARKER in text:
        return text
    return _AUTO_MARKER + "\n\n" + text


def main() -> int:
    check_only = "--check" in sys.argv

    if not WORKFLOW_MD.exists():
        print(f"ERROR: {WORKFLOW_MD} not found", file=sys.stderr)
        return 1

    text = WORKFLOW_MD.read_text(encoding="utf-8")

    if check_only:
        drifted = _check_drift(text)
        marker_missing = _AUTO_MARKER not in text
        if not drifted and not marker_missing:
            print("OK: WORKFLOW.md in sync with SKILL.md")
            return 0
        if marker_missing:
            print(
                "DRIFT: AUTO-GENERATED marker missing from WORKFLOW.md", file=sys.stderr
            )
        for d in drifted:
            print(f"DRIFT: stale wording still present: {d}", file=sys.stderr)
        return 1

    new_text, applied = _apply_fixes(text)
    new_text = _ensure_marker(new_text)

    if new_text == text:
        print("OK: WORKFLOW.md already in sync")
        return 0

    WORKFLOW_MD.write_text(new_text, encoding="utf-8")
    if _AUTO_MARKER not in text:
        print("Added AUTO-GENERATED marker")
    for a in applied:
        print(f"Fixed: {a}")
    print("WORKFLOW.md updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
