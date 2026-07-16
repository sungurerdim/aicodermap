#!/usr/bin/env python3
"""SINGLE SSOT admission step for NEW models — detect + gate + add in one pass.

This is the ONLY path that admits a freshly-released model into data/models.json.
Since c930089 (2026-06-27, lineup-first ordering) it runs TWICE per full cycle:
  (i)  PRE-GATHER (primary) — invoked from Step 0 right after lineup discovery,
       BEFORE the dispatch plan is built, so an admitted model enters
       matrix.active_models and Stage A fills its benches THIS SAME run
       (no-defer contract — never waits a cycle for scores);
  (ii) POST-MERGE (safety net) — invoked by refresh-finalize.py AFTER merge.py,
       catches a model first sighted mid-gather; idempotent (an id already
       admitted by (i) is skipped via `mid in existing`).
Both passes read this cycle's gather/synth/agent-out artifacts directly
(in-memory, no intermediate file) and write schema-complete stubs; bench cells
start null and are filled by Stage A this run for (i), or next refresh for (ii).
Metadata is DERIVED GENERICALLY from the candidate's own fields + the closest
already-tracked family sibling — never hand-authored per-model (see
feedback_no_hardcoded_model_patches). i18n strengths/weaknesses are written for
both TR and EN to keep parity audits green.

Consolidated 2026-06-27 (was two scripts: harvest-new-models.py wrote
.aicodermap-lineup.json's newModels[], then this script read it). That split lost
models every cycle:
  - the intermediate .aicodermap-lineup.json PERSISTED across cycles, so a
    candidate rejected once was re-fed (and re-rejected) every run;
  - the evidence gate REJECTED `evidenceConfidence=="confirmed"` (only high/medium
    passed) and counted `n_sources` from evidence[]/sources[] arrays ONLY — never
    `evidenceUrl` — so harvest entries (which carry evidenceUrl, not arrays) were
    always n_sources=0 and dropped as "low-confidence:confirmed". kimi-k2-7-code
    (2026-06-12) + glm-5-2 (2026-06-13) were detected 2026-06-16 yet never admitted.
Now: signals are unioned IN-MEMORY across ALL artifacts per candidate id (so a
model seen by two different hosts clears the ≥2-distinct-host bar), the gate is
fixed, and nothing is persisted between cycles — residue can't re-feed.

Two source-agnostic signal channels (mirrors the old harvest-new-models.py):
  1. `lineupHints[event='new']`  — incidental sightings a gather agent emits while
     researching its model slice (vendor lineup page may be SPA/403/dead).
  2. `lineupChanges.new[]`       — the dedicated Phase-0 WebSearch new-release net
     (agent.md step 3b) + vendor-lineup diff. Carries richer evidence
     (suggestedId, vendor, evidenceUrl, evidenceConfidence).

Two guards make admission automatic AND safe:
  1. GENERIC DERIVATION (derive_meta). provider / tier / open / license are
     inherited from the mode of existing models sharing the candidate's name LINE
     token; context / pricing / bench start empty and fill next cycle.
  2. SUPERSESSION FILTER (is_superseded). A "new" id is skipped iff an existing
     model shares its exact family key AND carries a strictly higher version
     (recomputed from live data every cycle — NOT a persistent skip registry).

STUB_META below is an OPTIONAL rich-copy override keyed by id; absence is fine.
"""

from __future__ import annotations

import glob
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
from lib.constants import SINGLE_ARTIFACT_PATH  # noqa: E402
from lib.util import (  # noqa: E402
    build_norm_id_index,
    canonical_display_name,
    configure_utf8_output,
    resolve_canonical_id,
    safe_json_load,
    slug_norm,
    today_iso,
    utc_now_iso,
    write_json,
)

NOW = utc_now_iso()

# Optional rich-copy overrides (id -> dict with provider/tier/open/license/context/
# released/api + tr_s/tr_w/en_s/en_w). Absence falls back to generic derivation.
STUB_META: dict[str, dict] = {}

# Confidence ranking for picking the strongest signal across artifacts.
_CONF_RANK = {"confirmed": 3, "high": 3, "medium": 2, "low": 1}

# A pure size/variant token (12B, 27B, 550B, A55B, E2B, E4B) — excluded from the
# family key so a new SIZE of an existing generation is admitted, not mistaken for
# a version bump.
SIZE_RE = re.compile(r"^[aex]?\d+(?:\.\d+)?[bm]$", re.I)
# A pure version token (4, 4.6, 4.20, 3.1).
VER_RE = re.compile(r"^\d+(?:\.\d+)*$")
# A version fused to a single-letter family marker (K2.7, V4, M2.7, K2) — the
# marker letter joins the family key (so it still matches its slug form, e.g.
# "kimi-k2-7-code"'s "k2" token) and the digits accumulate as version, same as
# VER_RE. Checked AFTER SIZE_RE so genuine size/variant tokens (A55B, E4B — same
# shape but end in b/m) are not reinterpreted. A multi-letter prefix ("Qwen3.7")
# never matches (only ONE leading letter) and keeps falling through to the plain
# alpha branch below, unaffected.
FUSED_VER_RE = re.compile(r"^([A-Za-z])(\d+(?:\.\d+)*)$")
# 2026-07-16: a fully-unseparated spelling ("glm5.2", "gpt5.5") has a
# MULTI-letter family prefix fused directly to the version digits — distinct
# from FUSED_VER_RE's single-letter marker case (K2.7, V4). Without this, the
# token fell through to the plain alpha branch below, which strips digits
# entirely and silently loses the version (family=("glm",), version=None) —
# is_superseded's `not ver` guard then fails open, so a re-listed OLDER
# snapshot spelled this way could be wrongly admitted as a fresh stub.
MULTI_FUSED_VER_RE = re.compile(r"^([A-Za-z]+?)(\d+(?:\.\d+)*)$")


def parse_name(name: str) -> tuple[tuple[str, ...], tuple[int, ...] | None]:
    """(family_key, version) from a display name. Family = lowercased alpha line
    tokens minus size tokens; version = first dotted/number token."""
    family: list[str] = []
    version: tuple[int, ...] | None = None
    for t in re.split(r"[\s\-_]+", (name or "").strip()):
        if not t:
            continue
        if VER_RE.fullmatch(t):
            # Accumulate consecutive numeric tokens so an id with a HYPHEN-separated
            # minor ("glm-5-2") parses to the same version as its dotted display
            # name ("GLM-5.2") → (5, 2). Without this, "glm-5-2" parsed to (5,) and
            # GLM-5.1=(5,1) FALSELY superseded it (a longer tuple with the same
            # prefix compares greater), silently blocking a genuinely-newer model.
            parts = tuple(int(x) for x in t.split("."))
            version = parts if version is None else version + parts
            continue
        if SIZE_RE.fullmatch(t):
            continue
        fused = FUSED_VER_RE.fullmatch(t)
        if fused:
            # Letter-fused version ("Kimi K2.7 Code", "MiniMax M2.7", "DeepSeek
            # V4 Pro") used to fall through to the plain alpha branch, which
            # stripped the digits and left version=None — is_superseded's `not
            # ver` guard then short-circuited to None (fails open), so a
            # re-listed older sibling ("Kimi K2.6 Code") was admitted as a fresh
            # stub even though a newer one was already tracked.
            family.append(fused.group(1).lower())
            parts = tuple(int(x) for x in fused.group(2).split("."))
            version = parts if version is None else version + parts
            continue
        multi_fused = MULTI_FUSED_VER_RE.fullmatch(t)
        if multi_fused:
            # A fully-unseparated spelling ("glm5.2") — see MULTI_FUSED_VER_RE
            # comment above.
            family.append(multi_fused.group(1).lower())
            parts = tuple(int(x) for x in multi_fused.group(2).split("."))
            version = parts if version is None else version + parts
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


def _hostname(url: str) -> str:
    h = (urlparse(url).hostname or "").lower()
    return h[4:] if h.startswith("www.") else h


def vendor_hostnames(vendor_entry: dict) -> set[str]:
    """Every hostname appearing in the vendor's whitelist urls block."""
    hosts = set()
    for u in (vendor_entry.get("urls") or {}).values():
        for url in u if isinstance(u, list) else [u]:
            if isinstance(url, str) and url.startswith("http"):
                h = _hostname(url)
                if h:
                    hosts.add(h)
    return hosts


def evidence_urls(nm: dict) -> list[str]:
    """Every evidence URL a candidate carries. The canonical candidate shape (built
    by collect_candidates) stores the cross-artifact union under `evidenceUrls`; raw
    `evidenceUrl`/`evidence[]`/`sources[]` shapes are tolerated too. The old gate
    ignored `evidenceUrl` entirely, which zeroed n_sources for every harvested
    entry — that bug is exactly what this consolidation fixes."""
    urls = (
        list(nm.get("evidenceUrls") or [])
        + [nm.get("evidenceUrl")]
        + list(nm.get("evidence") or [])
        + list(nm.get("sources") or [])
    )
    return [u for u in urls if isinstance(u, str) and u.startswith("http")]


def evidence_hosts(nm: dict) -> set[str]:
    return {h for u in evidence_urls(nm) if (h := _hostname(u))}


def is_official_evidence(nm: dict, vendors: dict) -> bool:
    """True iff any evidence URL is hosted on the candidate's OWN vendor's official
    domain (from the whitelist). A vendor announcing a model on its own site is the
    primary source for 'this model exists' — single-source sufficiency by design;
    ≥2-source applies to non-official evidence only."""
    urls = evidence_urls(nm)
    if not urls:
        return False
    vid = nm.get("vendor") or nm.get("provider") or ""
    if vid not in vendors:
        # Candidate's own vendor didn't resolve — do NOT fall back to matching
        # every whitelisted vendor's domain (that would call evidence hosted on
        # an UNRELATED vendor's site "official"). The ≥2-host / confirmed paths
        # in gate_admit still admit these candidates via their own logic.
        return False
    hosts = vendor_hostnames(vendors[vid] or {})
    return any(h == vh or h.endswith("." + vh) for u in urls if (h := _hostname(u)) for vh in hosts)


def _artifact_paths() -> list[str]:
    """Every artifact that may carry a new-model signal — gather batches plus the
    synth + final unified outputs AND the dedicated Step-0 lineup-sync artifact
    (source-agnostic: any single source failing must not suppress detection). The
    lineup artifact is the home of Channel-2 `lineupChanges.new[]` (the Phase-0
    WebSearch new-release net) when Step 0 is dispatched as a standalone agent;
    omitting it silently dropped fully-evidenced new models (kimi-k2-7-code +
    grok-4-20-multi-agent, 2026-06-27)."""
    paths = glob.glob(str(REPO / ".aicodermap-agent-out-*.gather.json"))
    for extra in (
        ".aicodermap-agent-out-synth.json",
        SINGLE_ARTIFACT_PATH,
        ".aicodermap-agent-out-lineup.json",
    ):
        p = REPO / extra
        if p.exists():
            paths.append(str(p))
    return paths


def collect_candidates(current_ids: set[str]) -> tuple[dict[str, dict], bool]:
    """Scan all artifacts; union both new-model channels per candidate id, merging
    EVERY evidence URL cross-artifact so a model sighted by two hosts clears the
    ≥2-distinct-host bar. Returns (candidates_by_id, any_artifact_seen)."""
    cands: dict[str, dict] = {}
    seen_artifact = False
    # 2026-07-16: normalize before comparing against already-tracked ids AND
    # before keying `cands` itself, so (a) a gather hint spelling an already-
    # tracked model differently ("GLM-5.2" when we track "glm-5-2") is not
    # mistaken for a genuinely new model, and (b) two artifacts reporting the
    # SAME new model under different spellings accumulate evidence into ONE
    # candidate entry instead of splitting it across two — each half possibly
    # failing the >=2-distinct-host evidence gate that the combined evidence
    # would have cleared.
    current_norm_index = build_norm_id_index(current_ids)
    cand_norm_index: dict[str, str] = {}

    def _merge(
        mid: str,
        *,
        name=None,
        provider=None,
        released=None,
        ev_url=None,
        conf=None,
        notes=None,
    ):
        canon = cand_norm_index.get(slug_norm(mid))
        if canon is not None:
            mid = canon
        else:
            cand_norm_index[slug_norm(mid)] = mid
        c = cands.setdefault(
            mid,
            {
                "id": mid,
                "name": None,
                "provider": None,
                "released": None,
                "evidenceUrls": [],
                "confidence": None,
                "notes": "",
            },
        )
        if name and not c["name"]:
            c["name"] = name
        if provider and not c["provider"]:
            c["provider"] = provider
        if released and not c["released"]:
            c["released"] = released
        if ev_url and isinstance(ev_url, str) and ev_url.startswith("http"):
            if ev_url not in c["evidenceUrls"]:
                c["evidenceUrls"].append(ev_url)
        if conf:
            cur = _CONF_RANK.get(str(c["confidence"] or "").lower(), 0)
            if _CONF_RANK.get(str(conf).lower(), 0) > cur:
                c["confidence"] = conf
        if notes and notes not in c["notes"]:
            c["notes"] = (c["notes"] + " " + notes).strip()

    for f in _artifact_paths():
        try:
            d = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        seen_artifact = True

        # Channel 1 — incidental gather sightings.
        for h in d.get("lineupHints", []) or []:
            if h.get("event") != "new":
                continue
            mid = h.get("modelId")
            if not mid or mid in current_ids or resolve_canonical_id(mid, current_norm_index):
                continue
            _merge(
                mid,
                ev_url=h.get("evidence"),
                conf=h.get("evidenceConfidence") or "gather-hint",
                notes=h.get("details", ""),
            )

        # Channel 2 — dedicated WebSearch new-release net / lineup diff.
        lc = d.get("lineupChanges") or {}
        for n in lc.get("new", []) or []:
            mid = n.get("suggestedId") or n.get("id")
            if not mid or mid in current_ids or resolve_canonical_id(mid, current_norm_index):
                continue
            _merge(
                mid,
                name=n.get("name"),
                provider=n.get("vendor") or n.get("provider"),
                released=n.get("released"),
                ev_url=n.get("evidenceUrl") or n.get("evidence"),
                conf=n.get("evidenceConfidence") or "newReleaseProbe",
                notes=n.get("notes") or n.get("observedVersion") or "",
            )
            # Some agents emit evidence as an array alongside evidenceUrl.
            for u in list(n.get("evidence") or []) + list(n.get("sources") or []):
                _merge(mid, ev_url=u)

    return cands, seen_artifact


def gate_admit(nm: dict, vendors: dict) -> tuple[bool, str]:
    """The evidence gate (consolidated + fixed 2026-06-27). Answers "is this model
    verifiably REAL?". Returns (admit, reason). Admit when ANY of:
      (a) OFFICIAL evidence (URL on the candidate's vendor whitelist domain) —
          vendor self-publication is definitionally authoritative;
      (b) confidence ∈ {confirmed, high, medium} (was: `confirmed` REJECTED);
      (c) ≥2 DISTINCT evidence hosts (evidenceUrl counted — was: IGNORED).
    In ALL cases a restricted/not-GA/preview/waitlist/invite note holds the
    candidate back (waits for GA), even if otherwise admissible."""
    official = is_official_evidence(nm, vendors)
    conf = str(nm.get("confidence") or "").lower()
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
    n_hosts = len(evidence_hosts(nm))
    admissible = official or conf in ("confirmed", "high", "medium") or n_hosts >= 2
    if restricted:
        return False, "restricted/not-GA"
    if not admissible:
        return False, f"insufficient-evidence (conf={conf or 'none'}, hosts={n_hosts})"
    return True, "ok"


def derive_meta(nm: dict, existing: list[dict], vendors: dict) -> dict:
    """Build stub metadata from the candidate + its family siblings. Explicit
    candidate values win; otherwise inherit the sibling mode; otherwise a safe
    default. Bench/pricing/context stay empty — they fill next cycle."""
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
    models_path = REPO / "data" / "models.json"
    models = json.loads(models_path.read_text(encoding="utf-8"))
    ms = models["models"] if isinstance(models, dict) else models
    existing = {m["id"] for m in ms}
    # 2026-07-16: a candidate id that's merely a spelling/format variant of an
    # already-tracked id ("GLM-5.2" surfacing when we already track "glm-5-2")
    # must not be admitted as a second, duplicate stub. See lib.util's
    # build_norm_id_index/resolve_canonical_id (pipeline-wide SSOT).
    existing_norm_index = build_norm_id_index(existing)
    vendors = json.loads(
        (REPO / "data" / "sources-whitelist.json").read_text(encoding="utf-8")
    ).get("vendors", {})

    tr = json.loads((REPO / "i18n" / "tr.json").read_text(encoding="utf-8"))
    en = json.loads((REPO / "i18n" / "en.json").read_text(encoding="utf-8"))

    candidates, seen_artifact = collect_candidates(existing)

    added, skipped = [], []
    for mid, nm in candidates.items():
        name = nm.get("name") or mid
        if mid in existing:
            continue
        dup_of = resolve_canonical_id(mid, existing_norm_index)
        if dup_of is not None:
            skipped.append((mid, f"duplicate spelling of tracked id {dup_of!r}"))
            print(f"  skip (spelling variant of already-tracked {dup_of!r}): {mid}")
            continue
        sup = is_superseded(name, ms)
        if sup:
            skipped.append((mid, sup))
            print(f"  skip (superseded by '{sup}'): {mid}")
            continue

        admit, reason = gate_admit(nm, vendors)
        if not admit:
            skipped.append((mid, reason))
            print(f"  skip (unverified — {reason}): {mid}")
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
            # Born-correct: a candidate without a display name falls back to the raw
            # id slug; canonicalize it ("minimax-m3" -> "MiniMax M3") using the
            # resolved provider so the stub is never published as a slug.
            "name": canonical_display_name(name, meta["provider"]),
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
        existing.add(mid)
        # Keep the norm index in sync so a spelling-variant of THIS candidate,
        # surfacing later in the same run, is caught too (not just variants of
        # ids that were already tracked before this run started).
        existing_norm_index[slug_norm(mid)] = mid
        tr["models"][mid] = {"strengths": meta["tr_s"], "weaknesses": meta["tr_w"]}
        en["models"][mid] = {"strengths": meta["en_s"], "weaknesses": meta["en_w"]}
        added.append(mid)
        print(f"  + stub: {mid} ({meta['provider']}, {meta['tier']}, open={meta['open']})")

    if added:
        models_path.write_text(json.dumps(models, ensure_ascii=False, indent=2), encoding="utf-8")
        (REPO / "i18n" / "tr.json").write_text(
            json.dumps(tr, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (REPO / "i18n" / "en.json").write_text(
            json.dumps(en, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        # Fable-5 R5 (2026-07-11): record ids admitted TODAY so
        # check-new-model-coverage.py (run post-merge by refresh-finalize.py)
        # can verify Stage A actually filled them, instead of a freshly-
        # admitted model silently sitting at near-zero coverage for cycles
        # (new models are the likeliest 0-fills — leaderboards/AA lag launches
        # by days-to-weeks). ADDITIVE + deduped: this script runs twice per
        # cycle (pre-gather + post-merge safety net); a same-day file already
        # present is unioned, never overwritten, so the pre-gather pass's ids
        # survive the post-merge pass's (usually empty) second call.
        cycle_file = REPO / f".aicodermap-new-models-{today_iso()}.json"
        prior_ids = set(safe_json_load(cycle_file, []) or [])
        write_json(cycle_file, sorted(prior_ids | set(added)))

    # Loud gate (feedback_no_silent_fails): detection ran this cycle (fresh
    # artifacts present) but admitted nothing → INFO, not a silent pass.
    if seen_artifact and not added:
        print(
            "  ℹ detection ran (artifacts present) but 0 new models admitted "
            f"({len(candidates)} candidate(s), {len(skipped)} gated)"
        )
    print(
        f"=== STUBS === added: {len(added)} {added} | "
        f"gated: {len(skipped)} {[s[0] for s in skipped]}"
    )
    return 0


if __name__ == "__main__":
    configure_utf8_output()
    raise SystemExit(main())
