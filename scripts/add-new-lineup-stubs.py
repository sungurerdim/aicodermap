#!/usr/bin/env python3
"""Add NEW models discovered by this cycle's lineup agent (.aicodermap-lineup.json)
as schema-complete stubs. Bench cells start null (next refresh fills them with
multi-source provenance); metadata is DERIVED GENERICALLY from the lineup entry's
own fields + the closest already-tracked family sibling — never hand-authored
per-model (see feedback_no_hardcoded_model_patches). i18n strengths/weaknesses are
written for both TR and EN to keep parity audits green.

Two guards make new-model admission automatic AND safe:

  1. GENERIC DERIVATION. provider / tier / open / license are inherited from the
     mode of existing models that share the candidate's name LINE token (e.g.
     "Grok Build 0.1" → line "grok" → inherits xAI/frontier from the Grok family);
     provider falls back to the whitelist vendor display name. context / pricing /
     bench start empty and fill next cycle. No STUB_META entry is required — the
     prior hard skip ("no STUB_META") silently dropped every genuinely-new model.

  2. SUPERSESSION FILTER. A "new" id surfaced by the WebSearch new-release net is
     often an OLDER snapshot the vendor still lists (e.g. "Claude Opus 4.6" when
     "Claude Opus 4.8" is already tracked). It is skipped iff an existing model
     shares its exact family key AND carries a strictly higher version. This is
     recomputed from live data every cycle (NOT a persistent skip registry — see
     feedback_known_gaps_registry), so a model stops being filtered the moment it
     is no longer superseded.

STUB_META below is an OPTIONAL rich-copy override keyed by id; absence is fine.
"""

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Optional rich-copy overrides (id -> dict with provider/tier/open/license/context/
# released/api + tr_s/tr_w/en_s/en_w). Absence falls back to generic derivation.
STUB_META: dict[str, dict] = {}

# A pure size/variant token (12B, 27B, 550B, A55B, E2B, E4B) — excluded from the
# family key so a new SIZE of an existing generation is admitted, not mistaken for
# a version bump.
SIZE_RE = re.compile(r"^[aex]?\d+(?:\.\d+)?[bm]$", re.I)
# A pure version token (4, 4.6, 4.20, 3.1).
VER_RE = re.compile(r"^\d+(?:\.\d+)*$")


def parse_name(name: str) -> tuple[tuple[str, ...], tuple[int, ...] | None]:
    """(family_key, version) from a display name. Family = lowercased alpha line
    tokens minus size tokens; version = first dotted/number token."""
    family: list[str] = []
    version: tuple[int, ...] | None = None
    for t in re.split(r"[\s\-_]+", (name or "").strip()):
        if not t:
            continue
        if VER_RE.fullmatch(t):
            if version is None:
                version = tuple(int(x) for x in t.split("."))
            continue
        if SIZE_RE.fullmatch(t):
            continue
        alpha = re.sub(r"[\d.]+", "", t).lower()
        if alpha:
            family.append(alpha)
    return tuple(family), version


def line_token(name: str) -> str | None:
    fam, _ = parse_name(name)
    return fam[0] if fam else None


def is_superseded(cand_name: str, existing: list[dict]) -> str | None:
    """Return the superseding model's name if the candidate is an older snapshot of
    an already-tracked line, else None."""
    fam, ver = parse_name(cand_name)
    if not ver:
        return None
    for m in existing:
        efam, ever = parse_name(m.get("name", ""))
        if efam == fam and ever is not None and ever > ver:
            return m.get("name") or m.get("id")
    return None


def _mode(vals):
    vals = [v for v in vals if v is not None]
    return Counter(vals).most_common(1)[0][0] if vals else None


def derive_meta(nm: dict, existing: list[dict], vendors: dict) -> dict:
    """Build stub metadata from the lineup entry + the candidate's family siblings.
    Explicit lineup values win; otherwise inherit the sibling mode; otherwise a
    safe default. Bench/pricing/context stay empty — they fill next cycle."""
    name = nm.get("name") or nm["id"]
    line = line_token(name)
    sibs = [m for m in existing if line and line_token(m.get("name", "")) == line]

    provider = (
        nm.get("providerDisplay")
        or _mode([m.get("provider") for m in sibs])
        or (vendors.get(nm.get("provider", ""), {}) or {}).get("name")
        or nm.get("provider")
        or "Unknown"
    )
    tier = nm.get("tier") or _mode([m.get("tier") for m in sibs]) or "frontier"
    open_ = nm.get("open")
    if open_ is None:
        open_ = _mode([m.get("open") for m in sibs])
    if open_ is None:
        open_ = False
    license_ = nm.get("license") or _mode([m.get("license") for m in sibs])
    released = nm.get("released")

    tr_s = (
        f"{name}, lineup keşfinde tespit edildi"
        + (f" (çıkış: {released})" if released else "")
        + ". Benchmark verileri sonraki yenilemede çok-kaynaklı provenance ile doldurulacak."
    )
    tr_w = (
        "Yeni tespit edildi; bağımsız benchmark doğrulaması, fiyatlandırma ve "
        "bağlam penceresi sonraki döngüde gelecek."
    )
    en_s = (
        f"{name} detected via lineup discovery"
        + (f" (released {released})" if released else "")
        + ". Benchmark data will be filled with multi-source provenance next refresh."
    )
    en_w = (
        "Newly detected; independent benchmark verification, pricing and context "
        "window arrive next cycle."
    )

    # Rich override merges on top of the generic base.
    base = dict(
        provider=provider,
        tier=tier,
        open=open_,
        license=license_,
        context=nm.get("context"),
        released=released,
        api=[],
        tr_s=tr_s,
        tr_w=tr_w,
        en_s=en_s,
        en_w=en_w,
    )
    base.update(STUB_META.get(nm["id"], {}))
    # bench-key set: mirror the closest sibling (matches emerging keys), else any.
    src = sibs[0] if sibs else (existing[0] if existing else {"bench": {}})
    base["_bench_keys"] = list((src.get("bench") or {}).keys())
    return base


def main() -> int:
    lineup = json.loads((REPO / ".aicodermap-lineup.json").read_text(encoding="utf-8"))
    models_path = REPO / "data" / "models.json"
    models = json.loads(models_path.read_text(encoding="utf-8"))
    ms = models["models"] if isinstance(models, dict) else models
    existing = {m["id"] for m in ms}
    vendors = json.loads(
        (REPO / "data" / "sources-whitelist.json").read_text(encoding="utf-8")
    ).get("vendors", {})

    tr = json.loads((REPO / "i18n" / "tr.json").read_text(encoding="utf-8"))
    en = json.loads((REPO / "i18n" / "en.json").read_text(encoding="utf-8"))

    added, skipped = [], []
    for nm in lineup.get("newModels", []):
        mid = nm["id"]
        name = nm.get("name") or mid
        if mid in existing:
            print(f"  skip (already present): {mid}")
            continue
        sup = is_superseded(name, ms)
        if sup:
            skipped.append((mid, sup))
            print(f"  skip (superseded by '{sup}'): {mid}")
            continue

        # EVIDENCE GATE (2026-06-06). Auto-stub only adds a model to the PUBLIC
        # dataset when it is verifiably real + generally available. A lone
        # low-confidence gather hint (single agent saw a blog mention) or an
        # explicitly restricted/not-GA model is held out as a lineup hint for
        # next-cycle ≥2-source verification — never auto-published. This stops
        # speculative/rumored entries (e.g. a blog-timeline "preview" model) from
        # polluting the model list. The high-confidence newReleaseProbe path
        # (vendor docs/lineup pages) is unaffected.
        conf = str(nm.get("evidenceConfidence") or "").lower()
        notes = str(nm.get("notes") or "").lower()
        restricted = any(
            t in notes
            for t in (
                "restricted",
                "not generally available",
                "not generally-available",
                "human review",
                "waitlist",
                "preview only",
                "invite",
            )
        )
        n_sources = len(nm.get("evidence") or nm.get("sources") or [])
        verified = (conf in ("high", "medium") or n_sources >= 2) and not restricted
        if not verified:
            reason = (
                "restricted/not-GA"
                if restricted
                else f"low-confidence:{conf or 'none'}"
            )
            skipped.append((mid, reason))
            print(f"  skip (unverified — {reason}; held as lineup hint): {mid}")
            continue

        meta = derive_meta(nm, ms, vendors)
        api = meta["api"]
        ins = [a["in"] for a in api if a.get("in") is not None]
        outs = [a["out"] for a in api if a.get("out") is not None]
        rng = {
            "in": [min(ins), max(ins)] if ins else None,
            "out": [min(outs), max(outs)] if outs else None,
            "cacheHit": None,
        }
        stub = {
            "id": mid,
            "name": name,
            "provider": meta["provider"],
            "released": meta["released"],
            "tier": meta["tier"],
            "open": meta["open"],
            "license": meta["license"],
            "context": meta["context"],
            "pricing": {"api": api, "range": rng},
            "bench": {k: None for k in meta["_bench_keys"]},
            "providers": len(api) if api else None,
            "uptime": None,
            "ollamaSize": None,
            "unslothVariants": [],
            "vramRequirement": None,
            "strengthsKey": f"{mid}.strengths",
            "weaknessesKey": f"{mid}.weaknesses",
            "lastUpdated": NOW,
            "status": "active",
        }
        ms.append(stub)
        tr["models"][mid] = {"strengths": meta["tr_s"], "weaknesses": meta["tr_w"]}
        en["models"][mid] = {"strengths": meta["en_s"], "weaknesses": meta["en_w"]}
        added.append(mid)
        print(
            f"  + stub: {mid} ({meta['provider']}, {meta['tier']}, open={meta['open']})"
        )

    if added:
        models_path.write_text(
            json.dumps(models, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        (REPO / "i18n" / "tr.json").write_text(
            json.dumps(tr, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        (REPO / "i18n" / "en.json").write_text(
            json.dumps(en, ensure_ascii=False, indent=1), encoding="utf-8"
        )
    print(
        f"=== STUBS === added: {len(added)} {added} | "
        f"superseded-skipped: {len(skipped)} {[s[0] for s in skipped]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
