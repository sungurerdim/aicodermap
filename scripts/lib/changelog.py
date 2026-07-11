"""CHANGELOG markdown rendering — pure string-building, no I/O.

Extracted from merge.py (2026-06-06). merge.py keeps the same-day
consolidation + file-write orchestration; this module only renders the
per-cycle entry blob from the merge log + artifact.

Stdlib-only.
"""

from __future__ import annotations

from typing import Any


def render_changelog_markdown(
    log: dict[str, Any],
    out: dict[str, Any],
    metadata_row: str,
    coverage_warn: str,
    partial_info: str,
    today: str,
) -> str:
    """Build the `## [today]` CHANGELOG entry blob (string). Pure: no I/O,
    no side effects. The caller prepends it with same-day consolidation."""
    cl_lines = [
        f"\n## [{today}] — autonomous refresh-all{coverage_warn}{partial_info}\n",
        f"\n{metadata_row}\n",
    ]
    if log["added"]:
        cl_lines.append("\n### Added\n")
        for mid in log["added"]:
            cl_lines.append(f"- `{mid}` — new model from vendor lineup discovery\n")
    if log["updated"]:
        cl_lines.append("\n### Updated\n")
        cl_lines.append(
            f"- {len(log['updated'])} models: {', '.join(f'`{x}`' for x in log['updated'])}\n"
        )
    if log["lineup_deprecated"]:
        cl_lines.append("\n### Deprecated\n")
        for mid in log["lineup_deprecated"]:
            cl_lines.append(f"- `{mid}` — vendor-marked deprecated\n")
    if log["lineup_renamed"]:
        cl_lines.append("\n### Renamed\n")
        for r in log["lineup_renamed"]:
            cl_lines.append(f"- {r}\n")
    if log["contradictions"]:
        cl_lines.append("\n### Resolved (auto via trustScore)\n")
        for c in log["contradictions"]:
            cl_lines.append(f"- {c}\n")
    if out.get("gaps"):
        # FAZ 4.B (2026-05-08): split gaps by source ('agent' vs 'orchestrator').
        # Agent gaps = "tried and failed"; orchestrator gaps = "didn't reach".
        agent_gaps = [g for g in out["gaps"] if g.get("source") == "agent"]
        orch_gaps = [g for g in out["gaps"] if g.get("source") == "orchestrator"]
        # Legacy entries without source field default to 'agent'.
        unknown_gaps = [g for g in out["gaps"] if g.get("source") not in ("agent", "orchestrator")]
        agent_gaps.extend(unknown_gaps)
        cl_lines.append(
            f"\n### Gaps ({len(out['gaps'])} entries — agent:{len(agent_gaps)} "
            f"orchestrator:{len(orch_gaps)} — see data/known-gaps.json or next refresh)\n"
        )
        # Show agent gaps first (real research effort), then orchestrator stubs.
        for g in agent_gaps[:6]:
            cl_lines.append(f"- `{g.get('key')}` *(agent)*: {g.get('reason')}\n")
        if orch_gaps:
            for g in orch_gaps[:2]:
                cl_lines.append(f"- `{g.get('key')}` *(orchestrator)*: {g.get('reason')}\n")
        total_shown = min(6, len(agent_gaps)) + min(2, len(orch_gaps))
        if len(out["gaps"]) > total_shown:
            cl_lines.append(f"- ... and {len(out['gaps']) - total_shown} more\n")

    # Fable-5 R2 (2026-07-11): chronic cells — >=N consecutive cycles where an
    # AGENT (not the orchestrator auto-gap placeholder) actively researched
    # this cell and found nothing. A short, model-grouped list distinct from
    # the (often 400+ entry) raw Gaps dump above — this is the "keeps
    # failing despite real effort" signal an operator should actually read.
    # See lib.matrix.CHRONIC_AGENT_CYCLES / gap_source_by_cell / priority_cells.
    if log.get("chronic"):
        by_model: dict[str, list[str]] = {}
        for cell_key in log["chronic"]:
            mid, _, bk = cell_key.partition(".")
            by_model.setdefault(mid, []).append(bk)
        cl_lines.append(
            f"\n### Chronically unfilled ({len(log['chronic'])} cells across "
            f"{len(by_model)} models — agent has actively researched these "
            "for 3+ consecutive cycles with no result)\n"
        )
        for mid in sorted(by_model):
            keys = ", ".join(f"`{k}`" for k in sorted(by_model[mid]))
            cl_lines.append(f"- `{mid}`: {keys}\n")

    return "".join(cl_lines)
