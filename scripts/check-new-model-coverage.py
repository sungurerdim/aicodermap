"""New-model first-cycle coverage floor + official-extraction gate.

Part 2 — OFFICIAL-EXTRACTION GATE (2026-07-24). Step 0's merged
discovery+extraction contract says the lineup agent mines each new model's
vendor announcement for benchmark values in the same fetch that discovered it.
Nothing enforced it: on 2026-07-24 the agent admitted `claude-opus-5` citing
https://www.anthropic.com/news/claude-opus-5 and extracted ZERO official
observations from it (inkling got 7 the same run), so the day's flagship
shipped with only aggregator cells and 39% coverage. A model admitted from a
vendor page with no S-tier observation is therefore treated as a pipeline
MISS, not as "the vendor published nothing": the gate writes a machine-readable
retry queue the orchestrator must drain (one targeted re-extraction of that
exact URL) and exits 2 so the miss cannot pass silently.

Part 1 — coverage floor (Fable-5 R5, 2026-07-11).

Models admitted THIS cycle (see add-new-lineup-stubs.py's per-cycle
`.aicodermap-new-models-<date>.json`) are the likeliest 0-fills: independent
leaderboards and AA typically lag a launch by days-to-weeks, so Stage A's
same-cycle survey (the no-defer contract) often can't find much yet. Nothing
previously distinguished "freshly-launched, genuinely under-covered so far"
from any other low-coverage model — this script checks admitted-this-cycle
coverage AFTER merge and surfaces it loudly (stderr + a short CHANGELOG note)
so an operator knows to expect thin data on a new model rather than mistake
it for a pipeline miss.

Advisory only — never mutates data/models.json. Run by refresh-finalize.py
AFTER merge.py + add-new-lineup-stubs.py, so the coverage it reads reflects
this cycle's actual Stage A/B fills.

Stdlib-only. Idempotent (re-running re-derives the same warning from current
state; does not duplicate the CHANGELOG note across re-runs the same day).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from lib.util import (  # noqa: E402
    configure_utf8_output,
    extract_domain,
    safe_json_load,
    today_iso,
)
from lib.whitelist import (  # noqa: E402
    contracts,
    core_bench_keys,
    load_whitelist,
    vendor_index,
)


def coverage_of(model: dict, core_keys: list[str]) -> float:
    """Fraction of `core_keys` that are non-null in `model["bench"]`."""
    if not core_keys:
        return 1.0
    bench = model.get("bench") or {}
    filled = sum(1 for k in core_keys if bench.get(k) is not None)
    return filled / len(core_keys)


def under_covered_new_models(
    models: list[dict], new_ids: list[str], core_keys: list[str], floor: float
) -> list[tuple[str, float]]:
    """[(modelId, coverage), ...] for admitted ids whose coverage < floor.
    Skips benchMirrorOf variants (their bench map is intentionally empty —
    they mirror a sibling's scores at render time, see lib.matrix.active_models)
    and ids no longer present (renamed/removed before this check ran)."""
    by_id = {m["id"]: m for m in models if isinstance(m, dict) and "id" in m}
    out: list[tuple[str, float]] = []
    for mid in new_ids:
        m = by_id.get(mid)
        if not m or m.get("benchMirrorOf"):
            continue
        cov = coverage_of(m, core_keys)
        if cov < floor:
            out.append((mid, cov))
    return sorted(out)


def _vendor_hosts(wl: dict) -> set[str]:
    """Every hostname the whitelist knows as an official vendor surface.

    Union of all `vendors.<id>.urls.*` hosts — the set of pages whose benchmark
    tables are S-tier evidence. A model admitted from one of these must come
    back with S-tier observations.
    """
    hosts: set[str] = set()
    for vendor in (vendor_index(wl) or {}).values():
        if not isinstance(vendor, dict):
            continue
        for url in (vendor.get("urls") or {}).values():
            if not isinstance(url, str):
                continue
            host = extract_domain(url)
            if host:
                hosts.add(host)
    return hosts


def _evidence_urls(artifacts: list[dict], model_id: str) -> list[str]:
    """Every evidence URL this cycle's artifacts cite for `model_id`.

    Reads both admission channels — the dedicated lineup pass
    (`lineupChanges.new[]`, `newModels[]`) and gather-agent sightings
    (`lineupHints[]`) — because either can be the one that admitted the model.
    """
    urls: list[str] = []
    for art in artifacts:
        buckets = [
            ((art.get("lineupChanges") or {}).get("new") or []),
            (art.get("newModels") or []),
            (art.get("lineupHints") or []),
        ]
        for bucket in buckets:
            for entry in bucket or []:
                if not isinstance(entry, dict):
                    continue
                ident = entry.get("id") or entry.get("suggestedId") or entry.get("modelId")
                if ident != model_id:
                    continue
                url = entry.get("evidenceUrl") or entry.get("url")
                if isinstance(url, str) and url and url not in urls:
                    urls.append(url)
    return urls


def official_extraction_misses(
    new_ids: list[str],
    sources: dict,
    artifacts: list[dict],
    wl: dict,
    core_keys: list[str],
    models: list[dict],
) -> list[dict]:
    """Models admitted from an official vendor page that produced no S-tier cell.

    Returns one queue entry per miss: the model, the vendor URLs to re-extract,
    and the core benches still empty (what the retry should look for).
    """
    hosts = _vendor_hosts(wl)
    by_id = {m["id"]: m for m in models if isinstance(m, dict) and "id" in m}
    out: list[dict] = []
    for mid in new_ids:
        model = by_id.get(mid)
        if not model or model.get("benchMirrorOf"):
            continue
        vendor_urls = [u for u in _evidence_urls(artifacts, mid) if extract_domain(u) in hosts]
        if not vendor_urls:
            continue  # discovered via a third party — no official page to mine
        has_official = any(
            isinstance(obs, dict) and str(obs.get("tier") or "").upper() == "S"
            for key, entries in sources.items()
            if key.startswith(f"{mid}.")
            for obs in (entries or [])
        )
        if has_official:
            continue
        bench = model.get("bench") or {}
        out.append(
            {
                "modelId": mid,
                "vendorUrls": vendor_urls,
                "missingCoreKeys": [k for k in core_keys if bench.get(k) is None],
            }
        )
    return sorted(out, key=lambda e: e["modelId"])


def _append_changelog_note(
    today: str, lines: list[str], heading: str = "### New-model coverage warning"
) -> None:
    """Append a `### <heading>` section to today's CHANGELOG block (idempotent —
    replaces a same-day note from an earlier same-day run rather than
    duplicating it, mirroring merge.py's same-day consolidation)."""
    cl_path = REPO / "CHANGELOG.md"
    if not cl_path.is_file():
        return
    text = cl_path.read_text(encoding="utf-8")
    section = "\n" + heading + "\n" + "".join(f"- {ln}\n" for ln in lines)

    today_re = re.compile(r"(?ms)^## \[" + re.escape(today) + r"\].*?(?=^## \[|\Z)")
    m = today_re.search(text)
    if not m:
        return  # merge.py hasn't written today's block yet — nothing to attach to
    block = m.group(0)
    # Idempotent re-run: strip a prior same-day instance of this exact section
    # before appending the fresh one.
    block = re.sub(
        r"(?ms)^" + re.escape(heading) + r"$.*?(?=^### |\Z)", "", block
    )
    block = block.rstrip("\n") + "\n" + section
    text = text[: m.start()] + block + "\n" + text[m.end() :]
    cl_path.write_text(text, encoding="utf-8")


def _run_official_gate(
    today: str, new_ids: list[str], models: list[dict], wl: dict, core_keys: list[str]
) -> bool:
    """Official-extraction gate. Returns True when a miss was queued.

    Writes `.aicodermap-official-extraction-retry.json` — the orchestrator MUST
    drain it (one targeted re-extraction per URL) before the cycle is done.
    The file is rewritten every run, so a drained queue leaves no stale entry.
    """
    artifacts: list[dict] = []
    for path in sorted(REPO.glob(".aicodermap-agent-out*.json")):
        art = safe_json_load(path, None)
        if isinstance(art, dict):
            artifacts.append(art)
    sources = safe_json_load(REPO / "data" / "sources.json", {}) or {}
    misses = official_extraction_misses(
        new_ids, sources, artifacts, wl, core_keys, models
    )
    queue_file = REPO / ".aicodermap-official-extraction-retry.json"
    queue_file.write_text(
        json.dumps(misses, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if not misses:
        return False
    lines = [
        f"`{e['modelId']}` — admitted from {', '.join(e['vendorUrls'])} but the "
        f"cycle produced NO S-tier observation from it; the vendor announcement "
        f"was never mined. Queued for targeted re-extraction "
        f"({len(e['missingCoreKeys'])} core cells still empty)."
        for e in misses
    ]
    print(
        f"GATE: {len(misses)}/{len(new_ids)} model(s) admitted today from an "
        "official vendor page yielded zero official benchmark cells "
        f"(queue: {queue_file.name}):",
        file=sys.stderr,
    )
    for ln in lines:
        print(f"  - {ln}", file=sys.stderr)
    _append_changelog_note(today, lines, heading="### Official-extraction gate")
    return True


def main() -> int:
    today = today_iso()
    cycle_file = REPO / f".aicodermap-new-models-{today}.json"
    new_ids = safe_json_load(cycle_file, []) or []
    if not new_ids:
        print("check-new-model-coverage: no models admitted today, nothing to check")
        return 0

    models = safe_json_load(REPO / "data" / "models.json", [])
    wl = load_whitelist(REPO / "data" / "sources-whitelist.json")
    core_keys = core_bench_keys(wl)
    floor = float(contracts(wl).get("ABSOLUTE_COVERAGE_FLOOR", 0.3))

    gate_fired = _run_official_gate(today, new_ids, models, wl, core_keys)

    under = under_covered_new_models(models, new_ids, core_keys, floor)
    if not under:
        print(
            f"check-new-model-coverage: {len(new_ids)} model(s) admitted today, "
            f"all >= {floor:.0%} coverage floor"
        )
        return 2 if gate_fired else 0

    lines = [
        f"`{mid}` — {cov:.0%} core coverage after this cycle's Stage A/B "
        f"(below the {floor:.0%} floor; independent leaderboards/AA typically "
        "lag a launch by days-to-weeks — expected for a same-day admission, "
        "re-check next cycle before treating as a research gap)"
        for mid, cov in under
    ]
    print(
        f"WARN: {len(under)}/{len(new_ids)} model(s) admitted today are below "
        f"the {floor:.0%} new-model coverage floor:",
        file=sys.stderr,
    )
    for ln in lines:
        print(f"  - {ln}", file=sys.stderr)

    _append_changelog_note(today, lines)
    return 2 if gate_fired else 0


if __name__ == "__main__":
    configure_utf8_output()
    raise SystemExit(main())
