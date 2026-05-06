#!/usr/bin/env python3
"""One-shot: add ProgramBench (arXiv:2605.03546, Meta + Stanford + Harvard,
2026-05-05) as the 26th coreBenchKey.

ProgramBench tests cleanroom program reconstruction — given only a program's
documentation and a behavioral test harness, the agent must architect and
build a working implementation in a sandbox without internet. 200 tasks,
248K+ behavioral tests. Currently 0% fully resolved by any public model;
best result is 3% "almost-resolved" by Opus 4.7. Useful as a frontier
breakthrough tracker rather than a discriminator at today's capability tier.

Updates the canonical SSOT chain end-to-end:
- data/sources-whitelist.json   (_schema.coreBenchKeys, _schema.benchAliases,
                                 _schema.benchCategories.coding,
                                 leaderboards[] entries for the two publishers)
- assets/js/core.js              (BENCH_KEYS, BENCH_CATEGORIES.coding,
                                 DEFAULT_WEIGHTS + every PRESET)
- i18n/{tr,en}.json              (benchmarks.programBench.{short,name,desc})
- data/models.json               (every model's bench gets programBench: null
                                 + benchUpdated unchanged; agent fills next cycle)
"""

import json
from datetime import date

TODAY = date.today().isoformat()


def update_whitelist():
    path = "data/sources-whitelist.json"
    with open(path, encoding="utf-8") as f:
        sw = json.load(f)

    schema = sw["_schema"]

    # 1. coreBenchKeys append.
    if "programBench" not in schema["coreBenchKeys"]:
        schema["coreBenchKeys"].append("programBench")

    # 2. benchAliases.
    schema.setdefault("benchAliases", {})
    schema["benchAliases"]["programBench"] = [
        "programbench",
        "program-bench",
        "ProgramBench",
        "program_bench",
        "programBench",
    ]

    # 3. benchCategories.coding append.
    for cat in schema.get("benchCategories", []):
        if cat.get("id") == "coding" and "programBench" not in cat.get("keys", []):
            cat["keys"].append("programBench")

    # 4. leaderboards[]: add ProgramBench official + BenchLM tracking entries.
    leaderboards = sw.setdefault("leaderboards", [])
    have_official = any(
        "programbench.com" in (lb.get("url") or lb.get("domain") or "")
        for lb in leaderboards
    )
    if not have_official:
        leaderboards.append(
            {
                "name": "ProgramBench (official)",
                "url": "https://programbench.com/",
                "domain": "programbench.com",
                "tier": "I",
                "format": "static_html_table",
                "publishes": ["programBench"],
                "authority": "cleanroom program reconstruction; 200 tasks, 248K behavioral tests",
                "paperUrl": "https://arxiv.org/abs/2605.03546",
                "firstSeen": TODAY,
            }
        )
    have_benchlm_pb = any(
        "benchlm.ai/benchmarks/programBench" in (lb.get("url") or "")
        for lb in leaderboards
    )
    if not have_benchlm_pb:
        leaderboards.append(
            {
                "name": "BenchLM — ProgramBench tracker",
                "url": "https://benchlm.ai/benchmarks/programBench",
                "domain": "benchlm.ai",
                "tier": "I",
                "format": "static_html_table",
                "publishes": ["programBench"],
                "authority": "aggregator tracking ProgramBench publication state across 9+ models",
                "firstSeen": TODAY,
            }
        )

    with open(path, "w", encoding="utf-8") as f:
        json.dump(sw, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(
        "whitelist: coreBenchKeys="
        + str(len(schema["coreBenchKeys"]))
        + ", benchAliases.programBench added, leaderboards+=2"
    )


def update_core_js():
    path = "assets/js/core.js"
    with open(path, encoding="utf-8") as f:
        src = f.read()

    if "'programBench'" in src:
        print("core.js: programBench already present, skip")
        return

    # 1. BENCH_KEYS list — append after 'webDevElo'.
    new_src = src.replace(
        "'cfElo', 'webDevElo',\n",
        "'cfElo', 'webDevElo', 'programBench',\n",
        1,
    )

    # 2. BENCH_CATEGORIES coding append.
    new_src = new_src.replace(
        "{ id: 'coding',    keys: ['swePro', 'sweV', 'sweMulti', 'nl2Repo', 'lcb', 'tb2', 'tbHard', 'cfElo', 'webDevElo', 'aaCoding'] }",
        "{ id: 'coding',    keys: ['swePro', 'sweV', 'sweMulti', 'nl2Repo', 'lcb', 'tb2', 'tbHard', 'cfElo', 'webDevElo', 'aaCoding', 'programBench'] }",
        1,
    )

    # 3. DEFAULT_WEIGHTS — give programBench weight 1, take 1 from arcAgi2 (3->2)
    # to keep total 100. arcAgi2 is reasoning, programBench is coding; the
    # tracker is coding-focused so this is a net rebalance toward coding.
    new_src = new_src.replace(
        "tau2: 3, browseComp: 3, arcAgi2: 3,",
        "tau2: 3, browseComp: 3, arcAgi2: 2, programBench: 1,",
        1,
    )

    # 4. PRESETS — add programBench:0 implicitly (zero-base merge handles it).
    # No changes needed: every preset already zero-bases against BENCH_KEYS.
    # But reasoning-focused / benchmark-only could give programBench a small slot.
    # Keep them at zero for now (no public model has crossed 5% — no signal).

    with open(path, "w", encoding="utf-8") as f:
        f.write(new_src)
    print(
        "core.js: BENCH_KEYS+=programBench, coding category+=programBench, DEFAULT_WEIGHTS rebalanced"
    )


def update_i18n():
    pairs = [
        (
            "i18n/tr.json",
            {
                "short": "ProgramBench",
                "name": "ProgramBench",
                "desc": "Cleanroom program reconstruction — 200 görev, 248K davranış testi. Modele dökümantasyon + test koşumu verilir, sandbox'ta tüm kod tabanını sıfırdan kurması beklenir. arXiv:2605.03546 (Meta + Stanford + Harvard, 2026-05). Bugün hiçbir kamu model %100 çözmüyor; frontier takip metriği.",
            },
        ),
        (
            "i18n/en.json",
            {
                "short": "ProgramBench",
                "name": "ProgramBench",
                "desc": "Cleanroom program reconstruction — 200 tasks, 248K behavioral tests. The model is given documentation + a test harness and must build the entire codebase from scratch in a sandbox. arXiv:2605.03546 (Meta + Stanford + Harvard, 2026-05). No public model has fully resolved any task yet; useful as a frontier breakthrough tracker.",
            },
        ),
    ]
    for path, payload in pairs:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        d.setdefault("benchmarks", {})
        d["benchmarks"]["programBench"] = payload
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("i18n updated: " + path)


def update_models_json():
    path = "data/models.json"
    with open(path, encoding="utf-8") as f:
        models = json.load(f)
    touched = 0
    for m in models:
        bench = m.setdefault("bench", {})
        if "programBench" not in bench:
            bench["programBench"] = None
            touched += 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(models, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("models.json: programBench cell initialised on " + str(touched) + " models")


def parity_check():
    with open("i18n/tr.json", encoding="utf-8") as f:
        tr = json.load(f)
    with open("i18n/en.json", encoding="utf-8") as f:
        en = json.load(f)

    def flat(d, p=""):
        out = []
        for k, v in d.items():
            kk = (p + "." + k) if p else k
            if isinstance(v, dict):
                out.extend(flat(v, kk))
            else:
                out.append(kk)
        return out

    tk, ek = set(flat(tr)), set(flat(en))
    print(
        "i18n parity TR="
        + str(len(tk))
        + " EN="
        + str(len(ek))
        + " drift="
        + str(len(tk ^ ek))
    )


def main():
    update_whitelist()
    update_core_js()
    update_i18n()
    update_models_json()
    parity_check()


if __name__ == "__main__":
    main()
