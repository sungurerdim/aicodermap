#!/usr/bin/env python3
"""Read-only diagnostic for the source-reliability ledger (Phase R1).

Usage:
    python scripts/show-reliability.py
    python scripts/show-reliability.py --source artificialanalysis.ai
    python scripts/show-reliability.py --bench sweV
    python scripts/show-reliability.py --source artificialanalysis.ai --bench sweV

Output is intentionally ASCII-clean (no emoji) so it renders on cp1254
Windows terminals as well as UTF-8 *nix shells.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "scripts"))

from lib import reliability  # type: ignore  # noqa: E402


def _fmt_source(sid: str, data: dict, *, filter_bench: str | None = None) -> None:
    g = data.get("global") or {}
    raw_a = int(g.get("rawAgree", 0))
    raw_d = int(g.get("rawDisagree", 0))
    dec_a = float(g.get("agree", 0.0))
    dec_d = float(g.get("disagree", 0.0))
    n_dec = dec_a + dec_d
    p = reliability.posterior_accuracy(dec_a, dec_d)
    ci_lo, ci_hi = reliability.accuracy_ci(dec_a, dec_d)
    half = (ci_hi - ci_lo) / 2.0
    above = n_dec >= reliability.COLD_START_N
    mark = "OK" if above else "WARN"
    status = (
        "above cold-start"
        if above
        else f"below cold-start (n<{reliability.COLD_START_N})"
    )
    print(f"{sid}:")
    print(
        f"  global: {raw_a}a/{raw_d}d (decayed {dec_a:.1f}/{dec_d:.1f})  "
        f"accuracy={p:.3f} +/- {half:.3f}  n={n_dec:.1f}  [{mark}] {status}"
    )
    by_bench = data.get("byBench") or {}
    if not by_bench:
        return
    keys = sorted(by_bench)
    if filter_bench:
        keys = [k for k in keys if k == filter_bench]
        if not keys:
            return
    print("  byBench:")
    for bk in keys:
        b = by_bench[bk] or {}
        bra = int(b.get("rawAgree", 0))
        brd = int(b.get("rawDisagree", 0))
        bda = float(b.get("agree", 0.0))
        bdd = float(b.get("disagree", 0.0))
        bn = bda + bdd
        bp = reliability.posterior_accuracy(bda, bdd)
        bci_lo, bci_hi = reliability.accuracy_ci(bda, bdd)
        bh = (bci_hi - bci_lo) / 2.0
        bm = (
            "OK"
            if bn >= reliability.COLD_START_N
            else f"WARN n<{reliability.COLD_START_N}"
        )
        print(
            f"    {bk:14s} {bra}a/{brd}d  accuracy={bp:.3f} +/- {bh:.3f}  n={bn:.1f}  [{bm}]"
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="Dump source-reliability ledger")
    ap.add_argument("--source", help="Filter by source identity (hostname)")
    ap.add_argument("--bench", help="Filter by bench key")
    ap.add_argument(
        "--path",
        default=str(PROJECT / "data" / "source-reliability.json"),
        help="Path to source-reliability.json",
    )
    args = ap.parse_args()

    ledger = reliability.load_ledger(args.path)
    sources = ledger.get("sources") or {}
    print(
        f"# source-reliability ledger  lastCycle={ledger.get('lastCycle')}  "
        f"schemaVersion={ledger.get('schemaVersion')}"
    )
    print(
        f"# halfLifeCycles={ledger.get('halfLifeCycles')}  "
        f"coldStartN={ledger.get('coldStartN')}  sourcesTracked={len(sources)}"
    )
    print()
    if not sources:
        print("(empty ledger)")
        return 0
    ids = sorted(sources)
    if args.source:
        ids = [s for s in ids if s == args.source]
        if not ids:
            print(f"(no source matches '{args.source}')")
            return 0
    for sid in ids:
        _fmt_source(sid, sources[sid], filter_bench=args.bench)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
