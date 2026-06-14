"""Deprecated (F2.2, 2026-05-17) — use scripts/local-synth.py instead.

gather-union.py is no longer the canonical synth path.
Canonical path: scripts/local-synth.py → scripts/lib/synth_core.py + scripts/lib/winner.py
ID remapping: scripts/lib/id_remap.py (lineup-cache driven; no hardcoded ID_FIXES)
Old implementation preserved at: scripts/gather-union.py.deprecated
"""

import sys


def main() -> int:
    print(
        "gather-union.py is deprecated (F2.2, 2026-05-17).\n"
        "Use: python scripts/local-synth.py",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
