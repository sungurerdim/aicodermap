#!/usr/bin/env python3
"""Apply FAZ 6.B cluster-consensus winner rule to every bench cell.

Background — FAZ 6.B (2026-05-10):
The prior winner-selection picked the single observation with max
trustScore. That let a single high-tier outlier (verifs=1, fabricated
I-tier) override 5+ agreeing lower-tier sources. Concrete failure on
deepseek-v4-pro.swePro: 6 sources at 55.4 (incl. Scale SEAL trust=0.87)
plus a single benchlm.ai/ root-URL fabrication at 20.12 (trust=0.333),
yet 20.12 was the stored winner.

The new rule clusters observations by value (within agreement_pp) and
picks the cluster with max sum(trustScore). Multi-source agreement beats
single-source outliers regardless of tier.

This script applies the rule retroactively to every (modelId, benchKey)
cell present in data/sources.json, recomputes the winning value, and
updates data/models.json. Outliers stay in sources.json (preserved for
audit) but lose the contradictionRole=winner flag.

The same rule lives in scripts/lib/synth.py `_pick_winner` for the
forward path (next refresh cycle); this script handles the historical
data backlog only.
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
sys.path.insert(0, str(ROOT / "scripts"))

from lib.synth import _cluster_observations  # noqa: E402  - runtime path

SOURCES_PATH = ROOT / "data" / "sources.json"
MODELS_PATH = ROOT / "data" / "models.json"
WHITELIST_PATH = ROOT / "data" / "sources-whitelist.json"

# These thresholds are the same the runtime synth path uses, but we read
# them from the whitelist contracts block so the SSOT can re-tune both
# layers without touching code.
DEFAULT_AGREEMENT_PP = 1.5


def _load_contracts() -> dict[str, Any]:
    try:
        wl = json.loads(WHITELIST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return ((wl.get("_schema") or {}).get("contracts")) or {}


def _entry_to_obs(e: dict[str, Any]) -> dict[str, Any] | None:
    """Convert a sources.json entry dict into the obs shape _cluster_observations
    expects (value, trustScore, sourceUrl, tier, fetched). Skip entries with
    no usable value/trustScore."""
    val = e.get("value")
    if val is None:
        return None
    try:
        v = float(val)
    except (TypeError, ValueError):
        return None
    ts = e.get("trustScore")
    if ts is None:
        # Fallback: synthesise from tier + verifications. Very approximate
        # but keeps legacy entries (no trustScore stored) in the cluster
        # math instead of dropping them silently.
        tier_w = {"I": 1.0, "S": 0.7, "C": 0.4, "U": 0.1}.get(
            (e.get("tier") or "C").upper(), 0.4
        )
        verifs = max(1, min(int(e.get("verifications") or 1), 3))
        ts = round(tier_w * (verifs / 3), 3)
    return {
        "value": v,
        "trustScore": float(ts),
        "sourceUrl": e.get("url") or "",
        "tier": (e.get("tier") or "C").upper(),
        "fetched": e.get("date") or e.get("fetched") or "",
    }


def _rotate_bak(p: Path) -> None:
    bak = p.with_suffix(p.suffix + ".bak")
    bak2 = p.with_suffix(p.suffix + ".bak2")
    if bak.exists():
        shutil.copy2(bak, bak2)
    if p.exists():
        shutil.copy2(p, bak)


def main() -> int:
    contracts = _load_contracts()
    agreement_pp = float(
        contracts.get("VERIFICATION_AGREEMENT_PP", DEFAULT_AGREEMENT_PP)
    )
    block_pp = float(contracts.get("CONTRADICTION_BLOCK_PP", 5.0))
    # Override gate: require strong evidence before mutating stored values.
    # The stored value may be backed by historical data not represented in
    # current sources.json, so a weak consensus must NOT clobber it.
    #
    # Pass criterion: ≥3 distinct sources, OR (≥2 distinct AND sum_trust≥1.5).
    # The OR-distinct≥3 path catches cases with many low-trust corroborations
    # (community blogs); the AND path requires both breadth AND depth when
    # only two sources speak. The previous laxer rule (distinct≥2 OR
    # sum_trust≥1.5) accepted 2-source clusters with sum_trust=0.54
    # (qwen3-235b.sweV in the dry run), which is barely better than a
    # single-source override.
    MIN_DISTINCT_SAFE = 3
    MIN_DISTINCT_PAIRED = 2
    MIN_SUM_TRUST = 1.5
    print("=== FAZ 6.B BENCH CONSENSUS RECONCILE ===")
    print(f"agreement_pp        = {agreement_pp}")
    print(f"override Δ floor    = {block_pp}pp")
    print(
        f"override gate       = distinct >= {MIN_DISTINCT_SAFE}  OR  "
        f"(distinct >= {MIN_DISTINCT_PAIRED} AND sum_trust >= {MIN_SUM_TRUST})"
    )

    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    models = json.loads(MODELS_PATH.read_text(encoding="utf-8"))
    models_by_id = {m["id"]: m for m in models}

    # Aggregate observations from BOTH `<mid>.<key>` and legacy
    # `<mid>.bench.<key>` flat keys before clustering. Pre-FAZ 6.B,
    # processing each as a separate cell let two independent winners
    # ping-pong across sweeps.
    cell_sources: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for flatkey, entries in sources.items():
        if not isinstance(entries, list) or not entries:
            continue
        if "." not in flatkey:
            continue
        mid, fkey = flatkey.split(".", 1)
        if fkey.startswith("bench."):
            fkey = fkey[len("bench.") :]
        if not mid or not fkey:
            continue
        cell_sources.setdefault((mid, fkey), []).extend(entries)

    deltas: list[dict[str, Any]] = []
    skipped_weak: list[str] = []
    bench_cells_seen = 0
    bench_cells_changed = 0

    for (mid, fkey), entries in cell_sources.items():
        m = models_by_id.get(mid)
        if not m:
            continue
        bench = m.get("bench") or {}
        if fkey not in bench:
            continue
        bench_cells_seen += 1

        obs = [o for o in (_entry_to_obs(e) for e in entries) if o is not None]
        if not obs:
            continue

        clusters = _cluster_observations(obs, agreement_pp)
        if not clusters:
            continue
        winning_cluster = clusters[0]
        # Override gate — protect stored values from weak consensus.
        d = winning_cluster["distinct_sources"]
        s = winning_cluster["sum_trust"]
        passes = d >= MIN_DISTINCT_SAFE or (
            d >= MIN_DISTINCT_PAIRED and s >= MIN_SUM_TRUST
        )
        if not passes:
            skipped_weak.append(f"{mid}.{fkey}: cluster={d}× trust_sum={s}")
            continue
        winner_obs = max(
            winning_cluster["members"],
            key=lambda x: (x["trustScore"], x.get("fetched") or ""),
        )
        new_val = winner_obs["value"]
        old_val = bench.get(fkey)
        if old_val is None:
            continue
        try:
            old_f = float(old_val)
            new_f = float(new_val)
        except (TypeError, ValueError):
            continue
        # Significant change only — Δ must clear the contradiction block
        # threshold (5pp). Smaller drifts stay; the next refresh re-cites.
        if abs(old_f - new_f) < block_pp:
            continue
        bench[fkey] = new_val
        bench_cells_changed += 1
        deltas.append(
            {
                "cell": f"{mid}.{fkey}",
                "old": old_val,
                "new": new_val,
                "delta": round(new_f - old_f, 3),
                "winning_cluster_size": len(winning_cluster["members"]),
                "winning_cluster_distinct_sources": winning_cluster["distinct_sources"],
                "winning_cluster_sum_trust": winning_cluster["sum_trust"],
                "total_clusters": len(clusters),
                "winner_source_url": winner_obs.get("sourceUrl"),
                "winner_trust": winner_obs["trustScore"],
            }
        )

    print(f"\nBench cells seen:    {bench_cells_seen}")
    print(f"Bench cells changed: {bench_cells_changed}")

    if deltas:
        print("\n=== TOP-50 DELTAS (largest |Δ|) ===")
        for d in sorted(deltas, key=lambda x: -abs(x["delta"]))[:50]:
            print(
                f"  {d['cell']:<40} {str(d['old']):>8} → {str(d['new']):>8}  "
                f"Δ{d['delta']:+.2f}  cluster={d['winning_cluster_size']}× "
                f"({d['winning_cluster_distinct_sources']} distinct, "
                f"trust_sum={d['winning_cluster_sum_trust']})"
            )

    if deltas:
        _rotate_bak(MODELS_PATH)
        MODELS_PATH.write_text(
            json.dumps(models, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"\n✓ wrote {MODELS_PATH.relative_to(ROOT)}  (.bak rotated)")
    else:
        print("\nNo cells to update — current values already match consensus.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
