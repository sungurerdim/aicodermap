"""Artificial Analysis (AA) structured extractor — RSC-aware.

AA's leaderboard is a Next.js app that ships its FULL per-model dataset inside
the static HTML as React Server Component streaming chunks
(`self.__next_f.push([1,"<chunk>"])`). The rendered table is JS-built, but the
DATA is already in the HTML — we just decode the chunks and read the JSON.

Why this exists: AA is the single richest source for the indices that are
otherwise systematically empty in our matrix (aaCoding, aaAgentic, aaOmni) plus
cross-checks for cfElo/arcAgi2/mrcr/tbHard/tau2/etc. Because AA is `spa_partial`,
live WebFetch returns the shell without the numbers, so gather agents recorded
"value unavailable" even after reaching the page (108 aaCoding/aaAgentic gaps in
the 2026-05-30 cycle, all having tried AA). This deterministic extractor reads
the embedded JSON ONCE and emits authoritative (slug, field, value) rows with
the EXACT AA field name — eliminating the "guess which Elo/index this number is"
misfile class at the source.

Stdlib only. Two modes:
  python scripts/extract-aa-rsc.py --dump-fields   # print numeric field union + a sample
  python scripts/extract-aa-rsc.py                 # write data/.leaderboard-snapshots/_aa-rows.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from lib.util import slug_norm as _norm  # noqa: E402  (SSOT)
from lib.util import configure_utf8_output, today_iso  # noqa: E402

AA_URL = "https://artificialanalysis.ai/leaderboards/models"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
OUT_PATH = REPO / "data" / ".leaderboard-snapshots" / "_aa-rows.json"
# Gather-schema artifact so the AA data flows through synth/merge exactly like an
# agent's gather output (deterministic, I-tier). batch90 prefix matches the
# `.aicodermap-agent-out-batch*.gather.json` glob in local-synth + gen_unified
# and sorts AFTER the real batches.
GATHER_PATH = REPO / ".aicodermap-agent-out-batch90-aa-rsc.gather.json"

# HIGH-CONFIDENCE field map only. (modelKey, scale). scale=1 keeps the AA value
# as-is (already 0-100 indices); scale=100 converts an AA 0-1 fraction to a
# percentage. Ambiguous AA fields are DELIBERATELY excluded to avoid the
# cross-bench misfile class (mmmuPro != mmluPro; lcr/omniscience unmapped):
#   intelligenceIndex/codingIndex/agenticIndex -> our AA composite indices
#   gpqa/hle/tau2/terminalbenchHard            -> a 2nd independent I-tier source
AA_FIELD_MAP: dict[str, tuple[str, float]] = {
    "intelligenceIndex": ("aaIdx", 1.0),
    "codingIndex": ("aaCoding", 1.0),
    "agenticIndex": ("aaAgentic", 1.0),
    "gpqa": ("gpqa", 100.0),
    "hle": ("hle", 100.0),
    "tau2": ("tau2", 100.0),
    "terminalbenchHard": ("tbHard", 100.0),
}
# AA's OWN definitional composites — AA authoritative, fed to synth. The rest of
# AA_FIELD_MAP are external benchmarks AA only *measures* (kept in _aa-rows.json
# for impossible-value detection, NOT injected as synth sources). See gather-write.
AA_COMPOSITE_KEYS = {"aaIdx", "aaCoding", "aaAgentic"}


def fetch(url: str, timeout: int = 40) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return (
        urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
    )


def decode_rsc_chunks(html: str) -> str:
    """Concatenate every self.__next_f.push([1,"<chunk>"]) payload, decoded from
    its JS/JSON string literal back to real text. The result is the RSC wire
    text with unescaped quotes, where the per-model JSON objects live."""
    out = []
    dec = json.JSONDecoder()
    for m in re.finditer(r"self\.__next_f\.push\(", html):
        start = m.end()
        # the argument is a JSON array literal: [1,"..."] or [2,"..."] etc.
        try:
            arr, _ = dec.raw_decode(html, _find_bracket(html, start))
        except (ValueError, IndexError):
            continue
        if isinstance(arr, list) and len(arr) >= 2 and isinstance(arr[1], str):
            out.append(arr[1])
    return "".join(out)


def _find_bracket(s: str, i: int) -> int:
    while i < len(s) and s[i] != "[":
        i += 1
    return i


def parse_models(rsc_text: str) -> list[dict]:
    """Find every per-model object (carries slug + intelligenceIndex) via brace
    matching + raw_decode. Dedupe by slug, last wins."""
    dec = json.JSONDecoder()
    by_slug: dict[str, dict] = {}
    for m in re.finditer(r'"intelligenceIndex"', rsc_text):
        start = rsc_text.rfind("{", 0, m.start())
        if start < 0:
            continue
        try:
            obj, _ = dec.raw_decode(rsc_text, start)
        except ValueError:
            continue
        slug = obj.get("slug")
        if slug and "intelligenceIndex" in obj:
            by_slug[slug] = obj
    return list(by_slug.values())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Decode the AA leaderboard RSC payload into _aa-rows.json."
    )
    parser.add_argument(
        "--dump-fields", action="store_true",
        help="print numeric field union + a sample and exit",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="print per-bench observation counts"
    )
    args = parser.parse_args()
    html = fetch(AA_URL)
    rsc = decode_rsc_chunks(html)
    models = parse_models(rsc)
    if not models:
        print("=== AA-RSC === parsed 0 models (format may have changed)")
        return 1

    if args.dump_fields:
        numeric: dict[str, int] = {}
        for o in models:
            for k, v in o.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    numeric[k] = numeric.get(k, 0) + 1
        print(f"parsed {len(models)} model objects")
        print("numeric fields (field: model_count):")
        for k in sorted(numeric, key=lambda x: -numeric[x]):
            print(f"  {k:28s} {numeric[k]}")
        # sample a couple frontier models with values
        for want in ("gpt-5", "opus-4", "qwen3", "gemini-3"):
            for o in models:
                if want in (o.get("slug") or "").lower():
                    print(
                        f"\n--- sample slug={o.get('slug')} creator={o.get('modelCreatorName')} ---"
                    )
                    for k, v in o.items():
                        if isinstance(v, (int, float)) and not isinstance(v, bool):
                            print(f"   {k} = {v}")
                    break
        return 0

    # ---- resolve AA slug/name -> our model id (exact-normalized only) ----
    our = json.loads((REPO / "data" / "models.json").read_text(encoding="utf-8"))
    by_norm: dict[str, str] = {}
    collisions: set[str] = set()
    for m in our:
        for cand in (m.get("id"), m.get("name")):
            n = _norm(cand)
            if not n:
                continue
            if n in by_norm and by_norm[n] != m["id"]:
                collisions.add(n)  # ambiguous normalized key -> never auto-match
            by_norm.setdefault(n, m["id"])
    for n in collisions:
        by_norm.pop(n, None)

    today = today_iso()
    observations: list[dict] = []
    matched_ids: set[str] = set()
    unmatched: list[str] = []
    for o in models:
        slug = o.get("slug") or ""
        name = o.get("name") or o.get("model_name") or ""
        mid = by_norm.get(_norm(slug)) or by_norm.get(_norm(name))
        if not mid:
            if any(AA_FIELD_MAP.get(k) for k in o):  # only report data-bearing misses
                unmatched.append(slug or name)
            continue
        matched_ids.add(mid)
        for field, (bk, scale) in AA_FIELD_MAP.items():
            v = o.get(field)
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                continue
            val = round(v * scale, 2)
            # sanity band: every mapped key is a 0-100 metric
            if not (0 <= val <= 100):
                continue
            observations.append(
                {
                    "modelId": mid,
                    "benchKey": bk,
                    "value": val,
                    "sourceUrl": AA_URL,
                    "tier": "I",
                    "fetched": today,
                    "_aaField": field,
                    "_aaSlug": slug,
                }
            )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(
            {
                "source": AA_URL,
                "fetched": today,
                "modelsParsed": len(models),
                "ourModelsMatched": sorted(matched_ids),
                "observations": observations,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    # Gather artifact for the synth/merge pipeline carries ONLY the AA-COMPOSITE
    # benches (aaIdx/aaCoding/aaAgentic) — AA's definitional indices, where AA is
    # authoritative. The AA-MEASURED externals (gpqa/hle/tau2/tbHard) are
    # DELIBERATELY excluded from synth: verification 2026-05-31 showed AA measures
    # them under a standardized (often no-tools) protocol that legitimately
    # disagrees with widely-reported vendor (tooled) numbers — e.g. sonnet-4-6.hle
    # is 51 across 8 sources incl. Anthropic, but AA's standardized score is 13.
    # Injecting AA's externals as I-tier sources would manufacture spurious
    # contradictions against well-corroborated data. They stay in _aa-rows.json
    # only, used by apply-aa-authoritative.py / audit-agent-misfiles.py to flag
    # physically-IMPOSSIBLE stored values (outside AA's observed envelope).
    composite_obs = [o for o in observations if o["benchKey"] in AA_COMPOSITE_KEYS]
    import time as _time

    GATHER_PATH.write_text(
        json.dumps(
            {
                "batchId": "batch90-aa-rsc",
                "mode": "gather",
                "observations": composite_obs,
                "runtime": {
                    "startedAt": int(_time.time()),
                    "source": "aa-rsc-deterministic",
                    "fills": len(composite_obs),
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(
        f"=== AA-RSC === parsed={len(models)} matched_our={len(matched_ids)}/"
        f"{len(our)} observations={len(observations)} -> {OUT_PATH.name}"
    )
    if args.verbose:
        import collections

        perbench = collections.Counter(o["benchKey"] for o in observations)
        print("  per-bench observations:", dict(perbench))
        print(f"  data-bearing AA models with NO match to our set: {len(unmatched)}")
    return 0


if __name__ == "__main__":
    configure_utf8_output()
    raise SystemExit(main())
