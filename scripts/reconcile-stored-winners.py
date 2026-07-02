"""Reconcile stored bench values against the full accumulated provenance.

INVARIANT enforced: for every (model, bench) cell, the value stored in
`data/models.json` must equal `pick_winner(data/sources.json[cell])` — the
stored scalar is a DERIVED projection of the provenance pool, never an
independent fact.

Why this exists (2026-07-02): merge.py only recomputes a cell's winner when
that cycle produced FRESH observations for it. A `confirmed`/skip (T2) cell is
frozen and never re-evaluated, so an early minority value can persist forever
even as an overwhelming multi-source consensus accumulates in sources.json
(observed: deepseek-v4-pro.lcb stored 85.9 while 22 I/S-tier sources report
93.5; gemma-4-31b.gpqa stored 76.3 while 28 sources report 84.3). This pass
closes that gap deterministically without any network fetch.

Scope guards (conservative — only move toward better-supported values):
  * AA-definitional indices (aaIdx/aaCoding/aaAgentic) are SKIPPED — their
    authority is apply-aa-authoritative.py (adopts AA's current value), and
    the general trust-winner would fight the AA methodology-drift correction.
  * A correction is applied only when the recomputed winner differs from the
    stored value by more than AGREEMENT_PP AND the winning cluster strictly
    dominates the cluster that currently holds the stored value on distinct
    sources (>=) and sum_trust (>). This targets clear majority/minority
    flips and leaves genuinely scattered/contested cells untouched (they stay
    contradictions for the anomaly loop).

Deterministic, stdlib-only, idempotent. Rotates .bak. Non-fatal by default;
--apply writes, otherwise dry-run preview. Intended to run in refresh-finalize
AFTER merge + AA-authoritative, BEFORE the coherence audit / commit.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.winner import pick_winner  # noqa: E402
from lib.whitelist import contracts, core_bench_keys  # noqa: E402

AA_OWNED = {"aaIdx", "aaCoding", "aaAgentic"}


def _obs_from(entries: list[dict]) -> list[dict]:
    out = []
    for e in entries:
        out.append(
            {
                "value": e.get("value"),
                "tier": e.get("tier", "C"),
                "sourceUrl": e.get("url") or "",
                "fetched": e.get("date") or "",
                "verifications": e.get("verifications"),
            }
        )
    return out


def _cluster_of(result: dict, value: float, agreement_pp: float) -> dict | None:
    """Return the cluster in result whose centroid is within agreement_pp of value."""
    best = None
    best_d = None
    for c in result.get("all_clusters", []):
        d = abs(c["centroid"] - value)
        if d <= agreement_pp and (best_d is None or d < best_d):
            best, best_d = c, d
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--apply", action="store_true", help="write corrections (default: dry-run)"
    )
    args = ap.parse_args()

    wl = json.loads(
        (REPO / "data" / "sources-whitelist.json").read_text(encoding="utf-8")
    )
    models = json.loads((REPO / "data" / "models.json").read_text(encoding="utf-8"))
    sources = json.loads((REPO / "data" / "sources.json").read_text(encoding="utf-8"))

    ctr = contracts(wl)
    agreement_pp = float(ctr.get("VERIFICATION_AGREEMENT_PP", 1.5))
    core = set(core_bench_keys(wl))
    active_ids = {m["id"] for m in models if (m.get("status") or "active") == "active"}

    corrections = []
    for m in models:
        if m.get("id") not in active_ids:
            continue
        bench = m.get("bench", {}) or {}
        for k, stored in list(bench.items()):
            if stored is None or k in AA_OWNED:
                continue
            key = f"{m['id']}.{k}"
            ents = sources.get(key)
            if not ents:
                continue
            entries = ents if isinstance(ents, list) else [ents]
            if len(entries) < 2:
                continue
            res = pick_winner(
                _obs_from(entries), bench_key=k, agreement_pp=agreement_pp
            )
            w = res.get("winner_value")
            if w is None:
                continue
            try:
                if abs(float(stored) - float(w)) <= agreement_pp:
                    continue
            except (TypeError, ValueError):
                continue
            win_cl = res.get("winning_cluster") or {}
            stored_cl = _cluster_of(res, float(stored), agreement_pp)
            # Dominance guard: winning cluster must strictly out-support the
            # cluster currently holding the stored value.
            if stored_cl is not None:
                if not (
                    win_cl.get("distinct_sources", 0)
                    >= stored_cl.get("distinct_sources", 0)
                    and win_cl.get("sum_trust", 0) > stored_cl.get("sum_trust", 0)
                ):
                    continue
            corrections.append(
                {
                    "cell": key,
                    "from": stored,
                    "to": w,
                    "core": k in core,
                    "winSources": win_cl.get("distinct_sources"),
                    "winSumTrust": win_cl.get("sum_trust"),
                    "storedSources": (stored_cl or {}).get("distinct_sources", 0),
                    "override": res.get("override_mode"),
                }
            )
            if args.apply:
                m["bench"][k] = w

    corrections.sort(key=lambda c: -abs((c["from"] or 0) - (c["to"] or 0)))
    print(
        f"=== RECONCILE === candidates={len(corrections)} core={sum(1 for c in corrections if c['core'])} apply={args.apply}"
    )
    for c in corrections:
        print(
            f"  {c['cell']:34s} {c['from']:>7} -> {c['to']:>7}  "
            f"winSrc={c['winSources']} winTrust={c['winSumTrust']} storedSrc={c['storedSources']} {c['override'] or ''}"
        )

    if args.apply and corrections:
        mp = REPO / "data" / "models.json"
        b2 = REPO / "data" / "models.json.bak2"
        b1 = REPO / "data" / "models.json.bak"
        if b1.exists():
            shutil.copy2(b1, b2)
        shutil.copy2(mp, b1)
        mp.write_text(
            json.dumps(models, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print(
            f"  wrote data/models.json ({len(corrections)} cells corrected; .bak rotated)"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
