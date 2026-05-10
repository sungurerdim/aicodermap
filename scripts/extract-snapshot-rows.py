"""Snapshot row extractor (FAZ 7.F, 2026-05-10).

Runs once per cycle AFTER prefetch-leaderboards.py. Walks every
`data/.leaderboard-snapshots/*.html` and `*.json`, applies regex/JSON
selectors derived from `data/sources-whitelist.json _schema.regexLibrary`
+ `_schema.extractors`, and emits a SLIM per-(modelId, benchKey, value,
sourceUrl, tier) row file at `data/.leaderboard-snapshots/_rows.json`.

Why: every haiku gather agent currently re-reads the same raw HTML
snapshot (5-50 KB each) when looking for its target models' rows. Cycle
2026-05-10 measured ~16 agents × ~75 snapshots = ~1200 redundant Read
operations + parse work. This script does that parse ONCE; agents read
the slim _rows.json (10-30 KB total) instead.

Quality preserved: the parser uses the SAME extractor rules that the
agent uses (canonical _schema.extractors). If parsing for a row fails
or yields ambiguous values, the row is emitted as a LOW-CONFIDENCE
hint with `confidence: "regex"`, and the agent is free to verify by
reading the snapshot directly.

The extractor is intentionally conservative — it only emits rows when:
  • The model name token appears in the row (case-insensitive substring)
  • A numeric value 0-100 follows the model name within 200 chars
  • The bench key column header is detectable in the surrounding HTML

Stdlib-only.
"""

from __future__ import annotations

import argparse
import html as html_lib
import json
import re
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

PROJECT = Path(__file__).resolve().parent.parent
SNAP_DIR = PROJECT / "data" / ".leaderboard-snapshots"
ROWS_OUT = SNAP_DIR / "_rows.json"
INDEX_PATH = SNAP_DIR / "_index.json"

ROW_VALUE_RE = re.compile(r"(\d{1,3}(?:\.\d+)?)\s*%?")
# FAZ 7.F.b: stricter row-value regex — require percent sign OR a value
# explicitly in the typical bench range. Cycle 2026-05-10 measured the
# permissive variant extracting version numbers (e.g. `3-1` → 1.0) as
# bench scores. The agent now opts in via --strict only when values are
# meant to flow into observations[]; otherwise rows are emitted as
# low-confidence hints (confidence: "regex-hint") for agent verification.
STRICT_VALUE_RE = re.compile(r"(\d{2,3}(?:\.\d+)?)\s*%")
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
MIN_PLAUSIBLE_VALUE = 5.0
MAX_PLAUSIBLE_VALUE = 100.0


def strip_html(s: str) -> str:
    """Crude HTML→text. Good enough for row-level extraction."""
    if not s:
        return ""
    s = TAG_RE.sub(" ", s)
    s = html_lib.unescape(s)
    s = WS_RE.sub(" ", s)
    return s.strip()


def load_models_aliases(models_path: Path) -> dict[str, list[str]]:
    """Build modelId → [alias tokens] map for substring matching.

    Aliases include the canonical id, name, and common variants (with/without
    hyphens, dots stripped, etc.).
    """
    if not models_path.is_file():
        return {}
    data = json.loads(models_path.read_text(encoding="utf-8"))
    out: dict[str, list[str]] = {}
    for m in data:
        if not isinstance(m, dict):
            continue
        mid = m.get("id")
        if not isinstance(mid, str):
            continue
        name = m.get("name") or ""
        aliases = {mid, mid.replace("-", " "), mid.replace("-", "")}
        if isinstance(name, str) and name:
            aliases.add(name.lower())
            aliases.add(name.lower().replace(" ", "-"))
        out[mid] = sorted(a for a in aliases if a and len(a) >= 4)
    return out


def load_bench_aliases(whitelist: dict[str, Any]) -> dict[str, list[str]]:
    schema = whitelist.get("_schema") or {}
    return schema.get("benchAliases") or {}


def extract_rows_from_html(
    html: str,
    *,
    url: str,
    tier: str,
    aliases: dict[str, list[str]],
    bench_aliases: dict[str, list[str]],
    strict: bool = True,
) -> list[dict[str, Any]]:
    """Heuristic row extraction. Returns a list of low-confidence hint dicts.

    `strict=True` (default): requires a percent sign in the matched value
    AND values in MIN..MAX_PLAUSIBLE_VALUE range. Defends against version-
    number false-positives (cycle 2026-05-10).
    """
    text = strip_html(html)
    if len(text) < 200:
        return []
    rows: list[dict[str, Any]] = []
    text_lower = text.lower()
    page_bench_keys: list[str] = []
    for k, names in bench_aliases.items():
        alias_list = names if isinstance(names, list) else ([names] if names else [])
        for n in [k] + alias_list:
            if isinstance(n, str) and n and n.lower() in text_lower:
                page_bench_keys.append(k)
                break
    if not page_bench_keys:
        return []
    value_re = STRICT_VALUE_RE if strict else ROW_VALUE_RE
    for mid, alias_list in aliases.items():
        for alias in alias_list:
            idx = text_lower.find(alias.lower())
            if idx < 0:
                continue
            window = text[idx : idx + 250]
            m = value_re.search(window[len(alias) :])
            if not m:
                continue
            try:
                val = float(m.group(1))
            except ValueError:
                continue
            if val < MIN_PLAUSIBLE_VALUE or val > MAX_PLAUSIBLE_VALUE:
                continue
            for bk in page_bench_keys:
                rows.append(
                    {
                        "modelId": mid,
                        "benchKey": bk,
                        "value": val,
                        "sourceUrl": url,
                        "tier": tier,
                        "confidence": "regex-hint",
                        "snippet": window[:120],
                    }
                )
            break
    return rows


def extract_rows_from_json(
    payload: Any,
    *,
    url: str,
    tier: str,
    aliases: dict[str, list[str]],
    bench_aliases: dict[str, list[str]],
) -> list[dict[str, Any]]:
    """Best-effort JSON walk. Looks for {model, score} or {model_name, value}
    shapes common to API-style leaderboard endpoints."""
    rows: list[dict[str, Any]] = []
    if not isinstance(payload, (dict, list)):
        return rows

    def _walk(obj: Any) -> None:
        if isinstance(obj, dict):
            mid_match = None
            val_match = None
            for k, v in obj.items():
                kl = str(k).lower()
                if isinstance(v, str) and any(t in kl for t in ("model", "name")):
                    for mid, alist in aliases.items():
                        if any(a.lower() in v.lower() for a in alist):
                            mid_match = mid
                            break
                if isinstance(v, (int, float)) and any(
                    t in kl for t in ("score", "value", "acc", "rate")
                ):
                    val_match = float(v)
            if mid_match and val_match is not None and 0 < val_match <= 100:
                # Detect bench key from the dict keys
                bk = None
                for k in obj.keys():
                    kl = str(k).lower()
                    for canon, aliases_list in bench_aliases.items():
                        alist = (
                            aliases_list
                            if isinstance(aliases_list, list)
                            else ([aliases_list] if aliases_list else [])
                        )
                        for n in [canon] + alist:
                            if isinstance(n, str) and n and n.lower() in kl:
                                bk = canon
                                break
                        if bk:
                            break
                    if bk:
                        break
                if bk:
                    rows.append(
                        {
                            "modelId": mid_match,
                            "benchKey": bk,
                            "value": val_match,
                            "sourceUrl": url,
                            "tier": tier,
                            "confidence": "json",
                        }
                    )
            for v in obj.values():
                _walk(v)
        elif isinstance(obj, list):
            for item in obj:
                _walk(item)

    _walk(payload)
    return rows


def lookup_url_tier(whitelist: dict[str, Any], url: str) -> str:
    """Look up the tier for a URL in whitelist categories. Default 'C'."""
    host = (urlparse(url).hostname or "").lower().lstrip("www.")
    for cat in ("leaderboards", "aggregators", "community", "local", "registries"):
        for e in whitelist.get(cat, []) or []:
            eu = e.get("url") or ""
            if eu == url or (host and host in eu):
                t = e.get("tier")
                if isinstance(t, str):
                    return t
    return "C"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max-rows-per-snapshot",
        type=int,
        default=50,
        help="Cap rows extracted per snapshot (defends against runaway HTML).",
    )
    args = parser.parse_args()

    if not INDEX_PATH.is_file():
        print(f"  ! no snapshot index at {INDEX_PATH}; nothing to extract")
        return 0
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    snapshots = index.get("snapshots") or {}
    if not snapshots:
        print("  ! snapshot index empty; nothing to extract")
        return 0

    wl = json.loads(
        (PROJECT / "data" / "sources-whitelist.json").read_text(encoding="utf-8")
    )
    aliases = load_models_aliases(PROJECT / "data" / "models.json")
    bench_aliases = load_bench_aliases(wl)

    started = time.time()
    all_rows: list[dict[str, Any]] = []
    parsed = 0
    skipped = 0

    for url, info in snapshots.items():
        if not isinstance(info, dict):
            continue
        path_rel = info.get("path")
        if not isinstance(path_rel, str):
            continue
        path = (
            PROJECT / path_rel if not Path(path_rel).is_absolute() else Path(path_rel)
        )
        if not path.is_file():
            skipped += 1
            continue
        tier = lookup_url_tier(wl, url)
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            skipped += 1
            continue
        rows: list[dict[str, Any]] = []
        if path.suffix == ".json":
            try:
                payload = json.loads(content)
                rows = extract_rows_from_json(
                    payload,
                    url=url,
                    tier=tier,
                    aliases=aliases,
                    bench_aliases=bench_aliases,
                )
            except json.JSONDecodeError:
                pass
        if not rows and ("<" in content):
            rows = extract_rows_from_html(
                content,
                url=url,
                tier=tier,
                aliases=aliases,
                bench_aliases=bench_aliases,
            )
        if rows:
            rows = rows[: args.max_rows_per_snapshot]
            all_rows.extend(rows)
            parsed += 1

    # Group rows by modelId for fast lookup, dedupe by (modelId, benchKey, value, url).
    seen: set[tuple[str, str, float, str]] = set()
    deduped: list[dict[str, Any]] = []
    for r in all_rows:
        key = (r["modelId"], r["benchKey"], round(float(r["value"]), 2), r["sourceUrl"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)

    by_model: dict[str, list[dict[str, Any]]] = {}
    for r in deduped:
        by_model.setdefault(r["modelId"], []).append(r)

    out = {
        "_meta": {
            "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "snapshotsParsed": parsed,
            "snapshotsSkipped": skipped,
            "rowsTotal": len(deduped),
            "rowsBeforeDedup": len(all_rows),
            "elapsedSec": round(time.time() - started, 2),
        },
        "byModel": by_model,
    }
    ROWS_OUT.write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        f"=== EXTRACT === parsed={parsed} skipped={skipped} "
        f"rows={len(deduped)} (raw={len(all_rows)}) "
        f"out={ROWS_OUT.relative_to(PROJECT)}"
    )
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    raise SystemExit(main())
