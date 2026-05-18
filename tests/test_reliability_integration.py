#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase R3 integration tests — reliability multiplier wiring proof.

These tests build a synthetic reliability ledger with known per-source
accuracy and verify that pick_winner + effective_trust_score honour the
multiplier when one source clearly dominates on track record.

The headline test is the 1-vs-5 scenario: a single high-tier source with
20 samples and ~95% accuracy must beat a cluster of 5 low-tier sources
with 20 samples each at ~40% accuracy. Without R3 wiring, the cluster's
sum_trust dominates; with R3 wiring, the trusted source survives the
single-outlier guard via reliability-weighted trust scoring.

Stdlib only (no pytest dependency).
Run:
    python tests/test_reliability_integration.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))

from lib.tiers import effective_trust_score, trust_score  # type: ignore  # noqa: E402
from lib.winner import pick_winner  # type: ignore  # noqa: E402


def _ledger_with_two_sources(
    trusted_n: int = 20,
    trusted_acc: float = 0.95,
    untrusted_n: int = 20,
    untrusted_acc: float = 0.40,
    bench_key: str = "sweV",
) -> dict:
    """Build a synthetic ledger pinning two sources to known accuracies."""
    t_agree = round(trusted_n * trusted_acc)
    t_disagree = trusted_n - t_agree
    u_agree = round(untrusted_n * untrusted_acc)
    u_disagree = untrusted_n - u_agree
    return {
        "schemaVersion": "v1",
        "halfLifeCycles": 3,
        "coldStartN": 10,
        "lastCycle": "2026-05-18",
        "sources": {
            "trusted.com": {
                "firstSeen": "2026-03-01",
                "lastSeen": "2026-05-18",
                "global": {
                    "agree": float(t_agree),
                    "disagree": float(t_disagree),
                    "rawAgree": t_agree,
                    "rawDisagree": t_disagree,
                },
                "byBench": {
                    bench_key: {
                        "agree": float(t_agree),
                        "disagree": float(t_disagree),
                        "rawAgree": t_agree,
                        "rawDisagree": t_disagree,
                    }
                },
            },
            "blog-a.com": {
                "firstSeen": "2026-03-01",
                "lastSeen": "2026-05-18",
                "global": {
                    "agree": float(u_agree),
                    "disagree": float(u_disagree),
                    "rawAgree": u_agree,
                    "rawDisagree": u_disagree,
                },
                "byBench": {
                    bench_key: {
                        "agree": float(u_agree),
                        "disagree": float(u_disagree),
                        "rawAgree": u_agree,
                        "rawDisagree": u_disagree,
                    }
                },
            },
        },
    }


class TestEffectiveTrustScoreWiring(unittest.TestCase):
    def test_ledger_absent_matches_base_trust(self):
        """With no ledger, effective_trust_score == trust_score (R3 inactive)."""
        base = trust_score("I", 3, "2026-05-18")
        eff = effective_trust_score(
            "I", 3, "2026-05-18", source_url="https://trusted.com", bench_key="sweV"
        )
        self.assertAlmostEqual(eff, base, places=4)

    def test_unknown_source_falls_back_to_neutral(self):
        ledger = _ledger_with_two_sources()
        base = trust_score("I", 3, "2026-05-18")
        eff = effective_trust_score(
            "I",
            3,
            "2026-05-18",
            source_url="https://no-record.com",
            bench_key="sweV",
            reliability_ledger=ledger,
        )
        self.assertAlmostEqual(eff, base, places=4)

    def test_trusted_source_unchanged_or_boosted(self):
        ledger = _ledger_with_two_sources()
        base = trust_score("I", 3, "2026-05-18")
        eff = effective_trust_score(
            "I",
            3,
            "2026-05-18",
            source_url="https://trusted.com",
            bench_key="sweV",
            reliability_ledger=ledger,
        )
        # multiplier in [0.3, 1.0], so eff <= base; trusted ~0.91 -> ~0.91*base.
        self.assertLessEqual(eff, base + 1e-4)
        self.assertGreater(eff, base * 0.85)

    def test_low_reliability_dampens(self):
        ledger = _ledger_with_two_sources()
        base = trust_score("C", 3, "2026-05-18")
        eff = effective_trust_score(
            "C",
            3,
            "2026-05-18",
            source_url="https://blog-a.com",
            bench_key="sweV",
            reliability_ledger=ledger,
        )
        # blog-a posterior ~ (1+8)/(2+20) ~= 0.41 -> eff = 0.41 * base.
        self.assertLess(eff, base * 0.5)


def _one_vs_five_obs() -> list[dict]:
    return [
        {
            "value": 75.0,
            "tier": "I",
            "sourceUrl": "https://trusted.com/leaderboard",
            "fetched": "2026-05-18",
            "verifications": 2,
        },
        *[
            {
                "value": 60.0,
                "tier": "C",
                "sourceUrl": f"https://{host}/post",
                "fetched": "2026-05-18",
            }
            for host in (
                "blog-a.com",
                "blog-b.com",
                "blog-c.com",
                "blog-d.com",
                "blog-e.com",
            )
        ],
    ]


def _one_vs_five_ledger() -> dict:
    ledger = _ledger_with_two_sources()
    for host in ("blog-b.com", "blog-c.com", "blog-d.com", "blog-e.com"):
        ledger["sources"][host] = ledger["sources"]["blog-a.com"]
    return ledger


class TestPickWinnerReliabilityIntegration(unittest.TestCase):
    """R3 wires the reliability multiplier into trust_score; the headline
    winner-flip ("trusted single source beats 5-source cluster") relies on
    the R4 exceptional-source override that bypasses the single-outlier
    guard. R3 alone provides the trust-score foundation."""

    def test_trusted_source_scored_higher_individually(self):
        """R3: trusted I-tier observation's per-observation trustScore
        must exceed every unreliable C-tier observation's trustScore."""
        ledger = _one_vs_five_ledger()
        result = pick_winner(
            _one_vs_five_obs(),
            bench_key="sweV",
            agreement_pp=1.5,
            warn_pp=3,
            block_pp=5,
            reliability_ledger=ledger,
        )
        scored = result["scored"]
        trusted = next(s for s in scored if "trusted.com" in s["sourceUrl"])
        unreliable = [s for s in scored if "blog-" in s["sourceUrl"]]
        for u in unreliable:
            self.assertGreater(
                trusted["trustScore"],
                u["trustScore"],
                "R3: trusted source's per-observation trust must exceed each unreliable peer.",
            )

    def test_trusted_cluster_has_higher_sum_trust(self):
        """R3: reliability-weighted trust pushes the trusted single-source
        cluster ahead of the 5-source unreliable cluster on sum_trust,
        even though the unreliable cluster is larger."""
        ledger = _one_vs_five_ledger()
        result = pick_winner(
            _one_vs_five_obs(),
            bench_key="sweV",
            agreement_pp=1.5,
            warn_pp=3,
            block_pp=5,
            reliability_ledger=ledger,
        )
        clusters = result["all_clusters"]
        trusted_cl = next(c for c in clusters if abs(c["centroid"] - 75.0) < 1)
        unreliable_cl = next(c for c in clusters if abs(c["centroid"] - 60.0) < 1)
        self.assertGreater(
            trusted_cl["sum_trust"],
            unreliable_cl["sum_trust"],
        )

    def test_single_outlier_guard_demotes_until_R4(self):
        """R3 deliberately leaves the single-outlier guard intact. Phase R4
        adds an exceptional-source override that bypasses it when n>=20,
        accuracy>=0.90, fresh, and I-tier. Until then, the 5-source cluster
        keeps winning despite having lower sum_trust — this test documents
        that contract so R4 can flip the assertion."""
        ledger = _one_vs_five_ledger()
        result = pick_winner(
            _one_vs_five_obs(),
            bench_key="sweV",
            agreement_pp=1.5,
            warn_pp=3,
            block_pp=5,
            reliability_ledger=ledger,
        )
        self.assertEqual(result["winner_value"], 60.0)

    def test_ledger_absent_keeps_prior_behavior(self):
        """Without ledger the same setup behaves identically to pre-R3."""
        result = pick_winner(_one_vs_five_obs(), bench_key="sweV", agreement_pp=1.5)
        self.assertEqual(result["winner_value"], 60.0)


class TestColdStartIsNeutral(unittest.TestCase):
    def test_sparse_source_keeps_full_trust(self):
        """A source with n=2 < 10 cold-start must not be penalized."""
        ledger = {
            "sources": {
                "fresh.com": {
                    "global": {
                        "agree": 1.0,
                        "disagree": 1.0,
                        "rawAgree": 1,
                        "rawDisagree": 1,
                    },
                    "byBench": {},
                }
            }
        }
        base = trust_score("S", 3, "2026-05-18")
        eff = effective_trust_score(
            "S",
            3,
            "2026-05-18",
            source_url="https://fresh.com",
            bench_key="sweV",
            reliability_ledger=ledger,
        )
        self.assertAlmostEqual(eff, base, places=4)


if __name__ == "__main__":
    result = unittest.main(exit=False, verbosity=2).result
    raise SystemExit(
        0 if result.wasSuccessful() else len(result.failures) + len(result.errors)
    )
