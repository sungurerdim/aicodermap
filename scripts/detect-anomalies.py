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

import json
import statistics
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
MIN_SOURCES = 2
K_MAD = 4.0  # robust-outlier threshold (modified z ~ 0.6745*|x-med|/MAD)
MIN_PEERS = 4  # need this many same-tier peers to call a peer-outlier
ELO_FAMILY = {"cfElo", "lmArenaElo", "webDevElo"}


def _dom(u) -> str:
    return urlparse(u or "").netloc.lower().replace("www.", "")


def main() -> int:
    models = json.loads((ROOT / "data" / "models.json").read_text(encoding="utf-8"))
    sources = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))
    wl = json.loads(
        (ROOT / "data" / "sources-whitelist.json").read_text(encoding="utf-8")
    )
    schema = wl.get("_schema") or {}
    core = set(schema.get("coreBenchKeys") or [])
    ranges = schema.get("benchRanges") or {}

    # domain -> published benches (whitelist + known Arena Elo publishers)
    dom_pub: dict[str, set] = {}
    for cat in ("leaderboards", "aggregators", "local", "community", "registries"):
        for e in wl.get(cat) or []:
            pub, d = e.get("publishes") or [], _dom(e.get("url") or "")
            if pub and d:
                dom_pub.setdefault(d, set()).update(pub)
    for ad in ("lmarena.ai", "arena.ai", "lmsys.org", "chatbot-arena.com"):
        dom_pub.setdefault(ad, set()).update({"lmArenaElo", "webDevElo"})

    # same-tier peer value pools per bench (for robust outlier detection)
    pools: dict[tuple, list[float]] = {}
    for m in models:
        tier = m.get("tier")
        for k, v in (m.get("bench") or {}).items():
            if isinstance(v, (int, float)):
                pools.setdefault((tier, k), []).append(float(v))

    def srcs(mid: str, k: str) -> list[dict]:
        return sources.get(f"{mid}.{k}") or []

    anomalies = []
    for m in models:
        mid, tier = m.get("id"), m.get("tier")
        for k, v in (m.get("bench") or {}).items():
            if not isinstance(v, (int, float)):
                continue
            reasons = []
            entries = srcs(mid, k)
            urls = {_dom(e.get("url")) for e in entries if e.get("url")}

            # source-mismatch (Elo family)
            if k in ELO_FAMILY:
                for d in urls:
                    pub = dom_pub.get(d)
                    if pub and (pub & ELO_FAMILY) and k not in pub:
                        reasons.append(
                            f"source {d} publishes {sorted(pub & ELO_FAMILY)}, not {k}"
                        )
                        break

            # out-of-band (soft)
            r = ranges.get(k) or {}
            slo, shi = r.get("softMin"), r.get("softMax")
            if (slo is not None and v < slo) or (shi is not None and v > shi):
                reasons.append(f"outside soft band [{slo},{shi}]")

            # single-source on a core bench
            if k in core and len([u for u in urls if u]) < MIN_SOURCES:
                reasons.append(f"single-source (<{MIN_SOURCES} distinct urls)")

            # peer-outlier (robust, same tier)
            pool = [x for x in pools.get((tier, k), []) if x != v] + [v]
            if len(pool) >= MIN_PEERS:
                med = statistics.median(pool)
                mad = statistics.median([abs(x - med) for x in pool]) or 0.0
                if mad > 0 and abs(v - med) / mad > K_MAD:
                    reasons.append(
                        f"peer-outlier (v={v} vs tier median {med:g}, MAD {mad:g})"
                    )

            if reasons:
                anomalies.append(
                    {
                        "modelId": mid,
                        "benchKey": k,
                        "value": v,
                        "reasons": reasons,
                        "sources": sorted(u for u in urls if u)[:5],
                    }
                )

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
                anomalies.append(
                    {
                        "modelId": mid,
                        "benchKey": k,
                        "value": d.get("value"),
                        "reasons": [
                            f"fresh-divergence (stored {d.get('value')} vs this-cycle "
                            f"obs {d.get('freshConsensus')}, Δ{d.get('deltaPp')}pp)"
                        ],
                        "sources": [],
                    }
                )
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
                else "peer-outlier"
            )
            by_class[tag] = by_class.get(tag, 0) + 1

    out = {
        "_purpose": "Cells needing deep verification next refresh (confirm / "
        "reclassify / flag). Advisory; never auto-applied. See "
        "agent.md OUTLIERS->INVESTIGATE + audit-data-coherence.py.",
        "generated": __import__("datetime").date.today().isoformat(),
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
