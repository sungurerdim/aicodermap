"""New-model first-cycle coverage floor (Fable-5 R5, 2026-07-11).

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

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from lib.util import configure_utf8_output, safe_json_load, today_iso  # noqa: E402
from lib.whitelist import contracts, core_bench_keys, load_whitelist  # noqa: E402


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


def _append_changelog_note(today: str, lines: list[str]) -> None:
    """Append a `### New-model coverage warning` section to today's CHANGELOG
    block (idempotent — replaces a same-day note from an earlier same-day run
    rather than duplicating it, mirroring merge.py's same-day consolidation)."""
    cl_path = REPO / "CHANGELOG.md"
    if not cl_path.is_file():
        return
    text = cl_path.read_text(encoding="utf-8")
    heading = "### New-model coverage warning"
    section = "\n" + heading + "\n" + "".join(f"- {ln}\n" for ln in lines)

    today_re = re.compile(r"(?ms)^## \[" + re.escape(today) + r"\].*?(?=^## \[|\Z)")
    m = today_re.search(text)
    if not m:
        return  # merge.py hasn't written today's block yet — nothing to attach to
    block = m.group(0)
    # Idempotent re-run: strip a prior same-day instance of this exact section
    # before appending the fresh one.
    block = re.sub(r"(?ms)^### New-model coverage warning$.*?(?=^### |\Z)", "", block)
    block = block.rstrip("\n") + "\n" + section
    text = text[: m.start()] + block + "\n" + text[m.end() :]
    cl_path.write_text(text, encoding="utf-8")


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

    under = under_covered_new_models(models, new_ids, core_keys, floor)
    if not under:
        print(
            f"check-new-model-coverage: {len(new_ids)} model(s) admitted today, "
            f"all >= {floor:.0%} coverage floor"
        )
        return 0

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
    return 0


if __name__ == "__main__":
    configure_utf8_output()
    raise SystemExit(main())
