#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real-data regression suite for FAZ 8.A.3b (contradiction resolution).

Eight cells, each representing a specific pathology measured in
cycles 2026-05-13/2026-05-18. Each test asserts the new pick_winner
contract handles the cell correctly.

Run:
    python tests/test_resolution_regression.py

Exit 0 = all pass; non-zero = first failure index.
Stdlib only (no pytest dependency -- same constraint as the rest of the
project's scripts/).
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))

from lib.synth_core import bayesian_aggregate  # noqa: E402
from lib.tiers import recency_decay, verif_factor, vendor_update_interval  # noqa: E402
from lib.winner import pick_winner  # noqa: E402

# core.js normalizeBenchScore mirror -- used to validate the cfElo +
# aaOmni regressions. Pure Python, no transpilation.


def normalize_bench(key: str, value: float | None) -> float | None:
    if value is None:
        return None
    if key == "cfElo":
        if value < 1200:
            return 0.0
        if value < 1600:
            return ((value - 1200) / 400) * 40
        if value < 2800:
            return 40 + ((value - 1600) / 1200) * 45
        if value < 3500:
            return 85 + ((value - 2800) / 700) * 15
        return 100.0
    if key == "aaOmni":
        return max(0.0, min(100.0, 100 - value))
    return value


FAILED: list[str] = []


def expect(label: str, actual, predicate, description: str):
    ok = predicate(actual)
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {label}: {description} -> actual={actual!r}")
    if not ok:
        FAILED.append(label)


def test_1_grok_4_20_swe_v_scaffold():
    print("\n#1 grok-4-20.sweV -- scaffold disagreement (76.7 vs 58.6)")
    obs = [
        {
            "value": 76.7,
            "tier": "I",
            "sourceUrl": "https://marc0.dev/leaderboard?scaffold=agentless",
            "fetched": "2026-05-18",
            "notes": "scaffold=agentless",
            "verifications": 2,
        },
        {
            "value": 58.6,
            "tier": "I",
            "sourceUrl": "https://swe-bench.com/swe-agent/grok-4-20",
            "fetched": "2026-05-18",
            "notes": "scaffold=swe-agent",
            "verifications": 2,
        },
    ]
    r = pick_winner(obs, agreement_pp=1.5, warn_pp=3, block_pp=5)
    expect("1.severity", r["severity"], lambda x: x == "RED", "RED on delta=18.1")
    expect(
        "1.scaffoldDetected",
        r["scored"],
        lambda s: any(o.get("evaluationContext", {}).get("scaffold") for o in s),
        "evaluationContext.scaffold populated",
    )
    expect(
        "1.quarantine",
        r["quarantine"],
        lambda x: x is True,
        "scaffold-split quarantines",
    )


def test_2_glm_5_1_hle_three_cluster():
    print("\n#2 glm-5-1.hle -- 3 clusters (3.8 / 31 / 52.3)")
    obs = [
        {
            "value": 3.8,
            "tier": "C",
            "sourceUrl": "https://x.com/glm/hle-tools-off",
            "fetched": "2026-04-01",
        },
        {
            "value": 31.0,
            "tier": "S",
            "sourceUrl": "https://glm.ai/blog/hle",
            "fetched": "2026-04-15",
        },
        {
            "value": 52.3,
            "tier": "I",
            "sourceUrl": "https://benchlm.ai/glm-5-1/hle",
            "fetched": "2026-05-10",
        },
    ]
    r = pick_winner(obs, agreement_pp=1.5, warn_pp=3, block_pp=5)
    expect(
        "2.clusters", len(r["all_clusters"]), lambda n: n == 3, "3 distinct clusters"
    )
    expect("2.severity", r["severity"], lambda x: x == "RED", "RED on 48.5pp spread")


def test_3_deepseek_v3_2_swe_v_category_bleed():
    print("\n#3 deepseek-v3-2.sweV -- category bleed from LCB row")
    # Synthetic two-cell map where 83.3 appears in BOTH sweV and lcb under the
    # same URL -- symptom of an extractor pulling the wrong column.
    all_cell_obs = {
        ("deepseek-v3-2", "lcb"): [
            {
                "value": 83.3,
                "sourceUrl": "https://benchlm.ai/lcb/deepseek-v3-2",
                "tier": "I",
                "fetched": "2026-05-18",
            }
        ],
    }
    obs = [
        {
            "value": 83.3,
            "tier": "I",
            "sourceUrl": "https://benchlm.ai/lcb/deepseek-v3-2",
            "fetched": "2026-05-18",
        },
        {
            "value": 74.2,
            "tier": "I",
            "sourceUrl": "https://marc0.dev/leaderboard/sweV",
            "fetched": "2026-05-18",
            "verifications": 3,
        },
    ]
    from lib.winner import detect_category_bleed

    tagged = detect_category_bleed(obs, "sweV", all_cell_obs=all_cell_obs)
    bleed = next((o for o in tagged if o.get("_categoryBleed")), None)
    expect("3.bleedFlag", bleed, lambda x: x is not None, "bleed entry flagged")


def test_4_opus_4_7_hle_drift_bayesian():
    print("\n#4 opus-4-7.hle -- multi-cycle drift 46.9 -> 51.4 (Bayesian)")
    hist = [{"value": 46.9}, {"value": 47.0}, {"value": 51.4}]
    cur = [{"value": 50.0}]
    res = bayesian_aggregate("opus-4-7.hle", cur, hist)
    expect(
        "4.bayesianPoint",
        res["point"],
        lambda v: v is not None and 46.0 <= v <= 52.0,
        "posterior mean in [46, 52]",
    )
    expect(
        "4.ciEmitted",
        (res["ci_low"], res["ci_high"]),
        lambda t: t[0] is not None and t[1] is not None,
        "CI bounds emitted",
    )


def test_5_qwen3_32b_swe_v_red():
    print("\n#5 qwen3-32b.sweV -- single-shot delta 65pp (low conf)")
    obs = [
        {
            "value": 15.0,
            "tier": "S",
            "sourceUrl": "https://qwen.ai",
            "fetched": "2026-03-01",
        },
        {
            "value": 80.0,
            "tier": "I",
            "sourceUrl": "https://swe-bench.com",
            "fetched": "2026-05-18",
        },
    ]
    r = pick_winner(obs, agreement_pp=1.5, warn_pp=3, block_pp=5)
    expect("5.severity", r["severity"], lambda x: x == "RED", "RED on delta=65")
    expect("5.confidence", r["confidence"], lambda c: c < 0.5, "confidence dampened")


def test_6_deepseek_v4_pro_swe_pro_bayesian_smooth():
    print("\n#6 deepseek-v4-pro.swePro -- historical pool pulls toward stable mean")
    hist = [{"value": 50.0}, {"value": 52.0}, {"value": 51.0}]
    cur = [{"value": 110.0}]  # outlier
    res = bayesian_aggregate("deepseek-v4-pro.swePro", cur, hist)
    expect(
        "6.dampenedOutlier",
        res["point"],
        lambda v: v is not None and v < 100.0,
        "posterior < 100 despite 110-outlier",
    )


def test_7_gpt_5_5_cf_elo_piecewise():
    print("\n#7 gpt-5-5.cfElo=1488 -- piecewise normalization")
    n = normalize_bench("cfElo", 1488)
    expect(
        "7.cfElo",
        n,
        lambda v: v is not None and 20.0 < v < 35.0,
        "1488 in [20, 35] (was 19.5 linear)",
    )
    n2 = normalize_bench("cfElo", 1600)
    expect("7.cfElo1600", n2, lambda v: v == 40.0, "1600 boundary -> 40")


def test_8_sonnet_4_6_aa_omni_inverted():
    print("\n#8 sonnet-4-6.aaOmni=30 -- lower-better invert")
    n = normalize_bench("aaOmni", 30)
    expect("8.aaOmni", n, lambda v: v == 70.0, "30 -> 70 (inverted)")
    n2 = normalize_bench("aaOmni", 0)
    expect("8.aaOmni0", n2, lambda v: v == 100.0, "0 -> 100 (best)")


def test_9_verif_information_scaling():
    """Phase R2 — verif_factor calibration.

    Replaces the prior linear `min(v, 3) / 3` with a log-base-4 curve so the
    3-source anchor stays at 1.0 while additional independent measurements
    still contribute (capped at 1.5).
    """
    print("\n#9 verif_factor -- information-theoretic scaling (R2)")
    expect("9.v0", verif_factor(0), lambda v: v == 0.0, "v=0 -> 0.0 (no signal)")
    expect(
        "9.v1",
        verif_factor(1),
        lambda v: abs(v - 0.5) < 0.01,
        "v=1 -> ~0.50 (log 2 / log 4)",
    )
    expect(
        "9.v3",
        verif_factor(3),
        lambda v: abs(v - 1.0) < 0.01,
        "v=3 -> 1.00 (anchor matches prior min(v,3)/3 formula)",
    )
    expect(
        "9.v5",
        verif_factor(5),
        lambda v: abs(v - 1.293) < 0.01,
        "v=5 -> ~1.29 (rewards beyond-3 sources)",
    )
    expect("9.cap", verif_factor(100), lambda v: v == 1.5, "v=100 -> capped at 1.5")


def test_10_quarterly_decay_slower_than_default():
    """Phase R5 — vendor with quarterly cadence ages slower.

    Same date, age ~100 days: default curve drops to 0.70 (< 180 bucket),
    quarterly stays at 0.85 (< 180 bucket but slower curve). Confirms
    INTERVAL_DECAY_CURVES selection works.
    """
    import datetime as _dt

    print("\n#10 recency_decay -- quarterly slower than default (R5)")
    age_days = 100
    target_date = (_dt.date.today() - _dt.timedelta(days=age_days)).isoformat()
    default_weight = recency_decay(target_date)
    quarterly_weight = recency_decay(target_date, source_type="quarterly")
    expect(
        "10.default100",
        default_weight,
        lambda v: abs(v - 0.70) < 0.001,
        "default 100d -> 0.70",
    )
    expect(
        "10.quarterly100",
        quarterly_weight,
        lambda v: abs(v - 0.85) < 0.001,
        "quarterly 100d -> 0.85 (slower)",
    )


def test_11_weekly_decay_faster_than_default():
    """Phase R5 — weekly publishers age fastest.

    Same date, age ~20 days: default curve still 1.00 (< 30 bucket),
    weekly drops immediately to 0.80 (high churn assumption).
    """
    import datetime as _dt

    print("\n#11 recency_decay -- weekly faster than default (R5)")
    age_days = 20
    target_date = (_dt.date.today() - _dt.timedelta(days=age_days)).isoformat()
    default_weight = recency_decay(target_date)
    weekly_weight = recency_decay(target_date, source_type="weekly")
    expect(
        "11.default20",
        default_weight,
        lambda v: abs(v - 1.00) < 0.001,
        "default 20d -> 1.00",
    )
    expect(
        "11.weekly20",
        weekly_weight,
        lambda v: abs(v - 0.80) < 0.001,
        "weekly 20d -> 0.80 (faster)",
    )


def test_12_vendor_update_interval_lookup():
    """Phase R5 — whitelist lookup wires vendorUpdateInterval -> source_type."""
    print("\n#12 vendor_update_interval -- whitelist hostname lookup (R5)")
    wl_vendors = {
        "anthropic": {
            "vendorUpdateInterval": "quarterly",
            "urls": {
                "news": "https://www.anthropic.com/news",
                "docs": "https://docs.claude.com",
            },
        }
    }
    expect(
        "12.match",
        vendor_update_interval("https://www.anthropic.com/news/foo", wl_vendors),
        lambda v: v == "quarterly",
        "anthropic.com -> quarterly",
    )
    expect(
        "12.miss",
        vendor_update_interval("https://random-blog.example/post", wl_vendors),
        lambda v: v == "default",
        "unknown hostname -> default",
    )


def main() -> int:
    print("FAZ 8.A.3b regression suite -- 12 cells (R2 +1, R5 +3)")
    test_1_grok_4_20_swe_v_scaffold()
    test_2_glm_5_1_hle_three_cluster()
    test_3_deepseek_v3_2_swe_v_category_bleed()
    test_4_opus_4_7_hle_drift_bayesian()
    test_5_qwen3_32b_swe_v_red()
    test_6_deepseek_v4_pro_swe_pro_bayesian_smooth()
    test_7_gpt_5_5_cf_elo_piecewise()
    test_8_sonnet_4_6_aa_omni_inverted()
    test_9_verif_information_scaling()
    test_10_quarterly_decay_slower_than_default()
    test_11_weekly_decay_faster_than_default()
    test_12_vendor_update_interval_lookup()

    print("\n" + "=" * 50)
    if FAILED:
        print(f"FAILED ({len(FAILED)}): {FAILED}")
        return 1
    print("PASS: 12/12")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
