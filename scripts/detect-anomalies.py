#!/usr/bin/env python3
"""Anomaly detector -> research-verification queue (Layer 3, 2026-05-27).

Flags benchmark cells that need DEEP VERIFICATION rather than silent acceptance
OR silent rejection. User directive (2026-05-27): a genuine breakthrough IS an
outlier, so anomalies must trigger RESEARCH (confirm / reclassify / flag), never
auto-dismissal. Writes data/_anomalies.json — a queue the next refresh injects
into the research agent's idea_context (agent.md "OUTLIERS -> INVESTIGATE"
resolves these FIRST). Advisory only: never mutates data/models.json.

Anomaly classes:
  source-mismatch — Elo-family cell sourced from a publisher of a SIBLING Elo
                    metric but not this one (likely misfiled scale).
  out-of-band     — value outside the bench's soft plausibility band
                    (_schema.benchRanges).
  single-source   — core-bench cell backed by < MIN_SOURCES distinct source URLs.
  peer-outlier    — value far from same-tier peers on the bench (> K_MAD * MAD).
  fresh-divergence — stored value disagrees with THIS cycle's fresh gather
                    observation by > CONTRADICTION_WARN_PP (from
                    data/_synth-traceability.json divergences[], when present).
                    Surfaces cases where a conservative historical-consensus
                    winner overrode a correct fresh correction (cycle 2026-05-28:
                    o3.arcAgi2 stored 87.5 [mislabeled ARC-AGI-1] vs fresh 2.9).

Stdlib-only. Idempotent. Run post-merge (or as a refresh PRELIM); the orchestrator
reads the queue into idea_context.anomalies for the next gather.
"""

from __future__ import annotations

import functools
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from lib.constants import ELO_BENCH_KEYS, MIN_SOURCES_PER_FILLED_CELL  # noqa: E402
from lib.util import extract_domain, today_iso  # noqa: E402
from lib.whitelist import build_domain_publishes, elo_swe_misfile  # noqa: E402

MIN_SOURCES = MIN_SOURCES_PER_FILLED_CELL  # SSOT: lib.constants
K_MAD = 4.0  # robust-outlier threshold (modified z ~ 0.6745*|x-med|/MAD)
MIN_PEERS = 4  # need this many same-tier peers to call a peer-outlier
ELO_FAMILY = ELO_BENCH_KEYS  # SSOT: lib.constants


@functools.lru_cache(maxsize=8192)
def _dom(u) -> str:
    # 6.2 — memoized: the same source URLs recur across hundreds of cells, so
    # cache url→domain instead of re-parsing per entry.
    return extract_domain(u)


def main() -> int:
    models = json.loads((ROOT / "data" / "models.json").read_text(encoding="utf-8"))
    sources = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))
    wl = json.loads(
        (ROOT / "data" / "sources-whitelist.json").read_text(encoding="utf-8")
    )
    schema = wl.get("_schema") or {}
    core = set(schema.get("coreBenchKeys") or [])
    ranges = schema.get("benchRanges") or {}

    # domain -> published benches (whitelist + known Arena Elo publishers).
    # SSOT: lib.whitelist.build_domain_publishes (was a duplicated inline copy
    # here, missing the independent-corroboration carve-out that
    # elo_swe_misfile applies below — see that function's docstring).
    dom_pub = build_domain_publishes(wl)

    # same-tier peer value pools per bench (for robust outlier detection).
    # 5.4: store (modelId, value) so the pool is filtered by IDENTITY, not value
    # — excluding the current model by `x != v` also dropped genuine same-valued
    # peers, collapsing a copy-paste cluster to mad=0 (never flagged).
    pools: dict[tuple, list[tuple]] = {}
    for m in models:
        tier = m.get("tier")
        for k, v in (m.get("bench") or {}).items():
            if isinstance(v, (int, float)):
                pools.setdefault((tier, k), []).append((m.get("id"), float(v)))

    def srcs(mid: str, k: str) -> list[dict]:
        return sources.get(f"{mid}.{k}") or []

    anomalies = []
    anomaly_by_cell: dict[
        tuple, dict
    ] = {}  # (mid,bk) -> entry, to merge fresh-divergence
    for m in models:
        mid, tier = m.get("id"), m.get("tier")
        for k, v in (m.get("bench") or {}).items():
            if not isinstance(v, (int, float)):
                continue
            reasons = []
            entries = srcs(mid, k)
            urls = {_dom(e.get("url")) for e in entries if e.get("url")}

            # source-mismatch (Elo family) — only when NO independent (neutral)
            # domain corroborates the cell (elo_swe_misfile's carve-out): a
            # cell backed by e.g. arxiv.org/github.com/llm-stats.com alongside
            # one sibling-flagged domain (huggingface.co hosting a different
            # page's Elo family) is well-corroborated, not a misfile — see
            # elo_swe_misfile docstring (deepseek-r1-14b.cfElo example).
            if k in ELO_FAMILY:
                source_urls = [e.get("url") for e in entries if e.get("url")]
                sibling_hit, is_hard = elo_swe_misfile(k, source_urls, dom_pub)
                if sibling_hit and is_hard:
                    dom, siblings = sibling_hit[2:].split("(has ", 1)
                    reasons.append(
                        f"source {dom} publishes {siblings.rstrip(')')}, not {k} "
                        "(no independent corroboration)"
                    )

            # out-of-band (soft)
            r = ranges.get(k) or {}
            slo, shi = r.get("softMin"), r.get("softMax")
            if (slo is not None and v < slo) or (shi is not None and v > shi):
                reasons.append(f"outside soft band [{slo},{shi}]")

            # single-source on a core bench
            if k in core and len([u for u in urls if u]) < MIN_SOURCES:
                reasons.append(f"single-source (<{MIN_SOURCES} distinct urls)")

            # variant-ambiguous (4.4) — a source entry the agent tagged because
            # the scraped "SWE-bench" carried no Verified/Pro/Multilingual qualifier.
            if any(e.get("_variantAmbiguous") for e in entries):
                reasons.append(
                    "variant-ambiguous (SWE-bench with no Verified/Pro/Multilingual qualifier)"
                )

            # peer-outlier (robust, same tier)
            peers = [val for (mid2, val) in pools.get((tier, k), []) if mid2 != mid]
            pool = peers + [v]
            if len(pool) >= MIN_PEERS:
                med = statistics.median(pool)
                mad = statistics.median([abs(x - med) for x in pool]) or 0.0
                if mad > 0 and abs(v - med) / mad > K_MAD:
                    reasons.append(
                        f"peer-outlier (v={v} vs tier median {med:g}, MAD {mad:g})"
                    )

            if reasons:
                entry = {
                    "modelId": mid,
                    "benchKey": k,
                    "value": v,
                    "reasons": reasons,
                    "sources": sorted(u for u in urls if u)[:5],
                }
                anomalies.append(entry)
                anomaly_by_cell[(mid, k)] = entry

    # fresh-divergence — ingest the synth traceability gate's advisory list
    # (grounded values that disagree with this cycle's fresh observations).
    # Closes the Defect-B loop: a stale-consensus winner that overrode a correct
    # fresh correction surfaces here for next-cycle research. Non-fatal if absent.
    trace_path = ROOT / "data" / "_synth-traceability.json"
    if trace_path.is_file():
        try:
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            for d in trace.get("divergences") or []:
                cell = d.get("cell") or ""
                if "." not in cell:
                    continue
                mid, k = cell.split(".", 1)
                reason = (
                    f"fresh-divergence (stored {d.get('value')} vs this-cycle "
                    f"obs {d.get('freshConsensus')}, Δ{d.get('deltaPp')}pp)"
                )
                # 5.5 — merge into the cell's existing anomaly instead of emitting a
                # second entry for the same (modelId, benchKey) (was double-emit).
                existing = anomaly_by_cell.get((mid, k))
                if existing is not None:
                    if reason not in existing["reasons"]:
                        existing["reasons"].append(reason)
                else:
                    entry = {
                        "modelId": mid,
                        "benchKey": k,
                        "value": d.get("value"),
                        "reasons": [reason],
                        "sources": [],
                    }
                    anomalies.append(entry)
                    anomaly_by_cell[(mid, k)] = entry
        except (OSError, json.JSONDecodeError):
            pass

    by_class: dict[str, int] = {}
    for a in anomalies:
        for r in a["reasons"]:
            tag = (
                "source-mismatch"
                if "publishes" in r
                else "out-of-band"
                if "soft band" in r
                else "single-source"
                if "single-source" in r
                else "fresh-divergence"
                if "fresh-divergence" in r
                else "variant-ambiguous"
                if "variant-ambiguous" in r
                else "peer-outlier"
            )
            by_class[tag] = by_class.get(tag, 0) + 1

    out = {
        "_purpose": "Cells needing deep verification next refresh (confirm / "
        "reclassify / flag). Advisory; never auto-applied. See "
        "agent.md OUTLIERS->INVESTIGATE + audit-data-coherence.py.",
        "generated": today_iso(),
        "counts": {"total": len(anomalies), **by_class},
        "anomalies": sorted(anomalies, key=lambda a: -len(a["reasons"])),
    }
    (ROOT / "data" / "_anomalies.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"=== ANOMALIES === total={len(anomalies)} {by_class}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
