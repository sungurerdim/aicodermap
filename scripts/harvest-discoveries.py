#!/usr/bin/env python3
"""Systematic new-BENCHMARK / new-VENDOR detection — harvest `discoveries.*` from
EVERY refresh artifact into data/discoveries.json, and (opt-in) auto-promote
benchmarks that clear AC6 (≥2 independent publishers).

Root cause this fixes (2026-06-16): the Phase-0 sub-probes emit
`discoveries.benchmarks[]` / `discoveries.vendors[]`, but NOTHING ever wrote them
to data/discoveries.json — local-synth.py drops the `discoveries` block,
gen_unified_artifact.py copies the synth artifact verbatim (bypassing its own
union that would have collected them), and the only writer of data/discoveries.json
was the manual promote-discovery.py. Net effect: every new benchmark a sub-probe
saw was silently lost, so a brand-new coding leaderboard could never enter the
tracker. This harvest closes that gap source-agnostically (gather + synth +
agent-out), exactly like harvest-new-models.py does for new MODELS.

Modes:
  (default)   harvest discoveries → data/discoveries.json (pending, AC6-flagged).
  --promote   additionally auto-add AC6-passing benchmarks to the bench-key
              universe (whitelist emergingBenchKeys + benchCategories →
              gen-bench-keys.py → core.js, plus i18n en/tr labels), then
              re-run audit-data-coherence.py. AUDIT-GATED: any coherence
              failure rolls back ALL surfaces and leaves the benchmark queued.

AC6 = ≥2 distinct publisher domains (suggestedPublishers ∪ sourceUrl host).
Idempotent. Non-fatal in harvest mode. Stdlib only.
"""

from __future__ import annotations

import glob
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from lib.whitelist import all_bench_keys, load_whitelist  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DISCOVERIES_PATH = ROOT / "data" / "discoveries.json"
WHITELIST_PATH = ROOT / "data" / "sources-whitelist.json"
CORE_JS = ROOT / "assets" / "js" / "core.js"
EN_PATH = ROOT / "i18n" / "en.json"
TR_PATH = ROOT / "i18n" / "tr.json"

# Emerging benchmarks with no known category land here (neutral bucket — emerging
# keys are excluded from DEFAULT_WEIGHTS/PRESETS, so this never skews a preset).
DEFAULT_CATEGORY = "general"


def _host(url: str) -> str:
    h = (urlparse(url or "").hostname or "").lower()
    return h[4:] if h.startswith("www.") else h


def _publisher_domains(entry: dict) -> set[str]:
    pubs = entry.get("suggestedPublishers") or entry.get("publishers") or []
    domains = set()
    for p in pubs:
        if isinstance(p, str):
            domains.add(_host(p) if "/" in p or "." in p else p.lower())
    h = _host(entry.get("sourceUrl") or entry.get("url") or "")
    if h:
        domains.add(h)
    domains.discard("")
    return domains


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data, indent: int = 2):
    # Preserve each file's native indent — i18n/*.json use indent=1, data/*.json
    # use indent=2. Reformatting untouched lines is a scope violation + noisy diff.
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=indent) + "\n", encoding="utf-8"
    )


def _artifact_paths() -> list[str]:
    # Broad glob (`-*.gather.json`) catches the gather batches AND any dedicated
    # lineup/Phase-0 gather artifact. Plus the synth + final unified outputs and
    # the consolidated lineup file — wherever a Phase-0 sub-probe's discoveries
    # land, they're harvested (source-agnostic).
    paths = glob.glob(str(ROOT / ".aicodermap-agent-out-*.gather.json"))
    for extra in (
        ".aicodermap-agent-out-synth.json",
        ".aicodermap-agent-out.json",
        ".aicodermap-lineup.json",
    ):
        p = ROOT / extra
        if p.exists():
            paths.append(str(p))
    return paths


def harvest() -> dict:
    """Union discoveries.{benchmarks,vendors} from all artifacts into
    data/discoveries.json. Returns summary counts."""
    wl = load_whitelist()
    known_benchkeys = set(all_bench_keys(wl))
    known_vendors = set((wl.get("vendors") or {}).keys())

    disc = (
        _load(DISCOVERIES_PATH)
        if DISCOVERIES_PATH.exists()
        else {
            "_note": "Discovery review queue.",
            "vendors": [],
            "benchmarks": [],
            "leaderboards": [],
        }
    )
    bench_by_key = {e.get("key"): e for e in disc.get("benchmarks", []) if e.get("key")}
    vendor_by_id = {e.get("id"): e for e in disc.get("vendors", []) if e.get("id")}

    new_bench = 0
    new_vendor = 0
    for f in _artifact_paths():
        try:
            d = _load(Path(f))
        except Exception:
            continue
        dd = d.get("discoveries") or {}
        for b in dd.get("benchmarks", []) or []:
            key = b.get("key")
            if not key or key in known_benchkeys:
                continue  # already a tracked bench key — not a discovery
            domains = _publisher_domains(b)
            prior = bench_by_key.get(key, {})
            merged_domains = set(prior.get("publisherDomains") or []) | domains
            entry = {
                "key": key,
                "label": b.get("label") or prior.get("label") or key,
                "sourceUrl": b.get("sourceUrl")
                or b.get("url")
                or prior.get("sourceUrl"),
                "firstObserved": prior.get("firstObserved") or b.get("firstObserved"),
                "publisherDomains": sorted(merged_domains),
                "publisherCount": len(merged_domains),
                "ac6Pass": len(merged_domains) >= 2,
                "status": prior.get("status", "pending"),
            }
            if key not in bench_by_key:
                new_bench += 1
            bench_by_key[key] = entry
        for v in dd.get("vendors", []) or []:
            vid = v.get("id")
            if not vid or vid in known_vendors:
                continue
            if vid not in vendor_by_id:
                new_vendor += 1
            prior = vendor_by_id.get(vid, {})
            vendor_by_id[vid] = {
                "id": vid,
                "observedAt": prior.get("observedAt") or v.get("observedAt"),
                "modelCount": v.get("modelCount") or prior.get("modelCount"),
                "latestRelease": v.get("latestRelease") or prior.get("latestRelease"),
                "suggestedTier": v.get("suggestedTier")
                or prior.get("suggestedTier", "S"),
                "status": prior.get("status", "pending"),
            }

    disc["benchmarks"] = list(bench_by_key.values())
    disc["vendors"] = list(vendor_by_id.values())
    disc.setdefault("leaderboards", [])
    _save(DISCOVERIES_PATH, disc)

    pending_bench = [e for e in disc["benchmarks"] if e.get("status") == "pending"]
    ac6_ready = [e for e in pending_bench if e.get("ac6Pass")]
    print(
        f"=== DISCOVERY HARVEST === +{new_bench} new benchmarks, "
        f"+{new_vendor} new vendors | pending: {len(pending_bench)} benchmarks "
        f"({len(ac6_ready)} AC6-ready), {len([v for v in disc['vendors'] if v.get('status') == 'pending'])} vendors"
    )
    for e in ac6_ready:
        print(
            f"  🔎 AC6-ready benchmark: {e['key']} ({e['publisherCount']} publishers) — {e['label']}"
        )
    return {"newBench": new_bench, "newVendor": new_vendor, "ac6Ready": ac6_ready}


def _short_label(label: str, key: str) -> str:
    return label if 0 < len(label) <= 10 else key


def promote_ac6() -> int:
    """Auto-add AC6-passing pending benchmarks to the bench-key universe.
    Audit-gated: rolls back every surface on coherence failure."""
    disc = _load(DISCOVERIES_PATH) if DISCOVERIES_PATH.exists() else {"benchmarks": []}
    ready = [
        e
        for e in disc.get("benchmarks", [])
        if e.get("status") == "pending" and e.get("ac6Pass")
    ]
    if not ready:
        print("=== PROMOTE === no AC6-ready benchmarks to promote")
        return 0

    surfaces = [WHITELIST_PATH, CORE_JS, EN_PATH, TR_PATH, DISCOVERIES_PATH]
    snapshots = {p: p.read_text(encoding="utf-8") for p in surfaces}

    wl = _load(WHITELIST_PATH)
    schema = wl["_schema"]
    emerging = schema.setdefault("emergingBenchKeys", [])
    cats = schema.setdefault("benchCategories", [])
    cat = next((c for c in cats if c.get("id") == DEFAULT_CATEGORY), None)
    if cat is None:
        cat = {"id": DEFAULT_CATEGORY, "keys": []}
        cats.append(cat)
    en = _load(EN_PATH)
    tr = _load(TR_PATH)
    en.setdefault("benchmarks", {})
    tr.setdefault("benchmarks", {})

    promoted = []
    review = []
    for e in ready:
        key = e["key"]
        label = e.get("label") or key
        short = _short_label(label, key)
        if key not in emerging:
            emerging.append(key)
        if key not in cat["keys"]:
            cat["keys"].append(key)
        # A benchmark name is a proper noun — identical across locales, never
        # translated (avoids the Turkish-uppercase / dotless-I traps). The desc
        # is the one field that benefits from human Turkish; we seed BOTH locales
        # with the EN description rather than fabricating a low-quality machine
        # Turkish, and flag the entry for locale review so a human refines TR.
        en_desc = (
            e.get("description")
            or e.get("desc")
            or f"{label} — emerging benchmark (auto-detected from discovery queue)."
        )
        labels = {"name": label, "short": short, "desc": en_desc}
        en["benchmarks"][key] = dict(labels)
        tr["benchmarks"][key] = dict(labels)
        e["status"] = "accepted"
        e["promotedTo"] = "emergingBenchKeys"
        e["needsLocaleReview"] = True
        promoted.append(key)
        review.append(key)

    _save(WHITELIST_PATH, wl)
    _save(EN_PATH, en, indent=1)
    _save(TR_PATH, tr, indent=1)
    _save(DISCOVERIES_PATH, disc)

    # Sync core.js BENCH_KEYS from the (now-updated) benchCategories, then
    # re-verify SSOT coherence. utf-8 env so a cp1254 child never crashes on the
    # status glyphs and falsely trips the rollback gate.
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}

    def _run(script: str):
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts" / script)],
            capture_output=True,
            text=True,
            env=env,
        )

    gen = _run("gen-bench-keys.py")
    audit = _run("audit-data-coherence.py")
    if gen.returncode != 0 or audit.returncode != 0:
        for p, text in snapshots.items():
            p.write_text(text, encoding="utf-8")
        _run("gen-bench-keys.py")
        print(
            "=== PROMOTE ROLLED BACK === coherence audit failed; benchmarks left "
            f"queued: {promoted}\n{audit.stdout}\n{audit.stderr}"
        )
        return 1

    print(f"=== PROMOTE === auto-added {len(promoted)} AC6 benchmarks: {promoted}")
    if review:
        print(
            f"  ⚠ TR locale review pending (desc seeded from EN): {review} — "
            f"refine i18n/tr.json benchmarks.<key>.desc when convenient."
        )
    return 0


def main() -> int:
    summary = harvest()
    if "--promote" in sys.argv[1:] and summary["ac6Ready"]:
        return promote_ac6()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
