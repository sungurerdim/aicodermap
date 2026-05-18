#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase R1 unit tests for the source-reliability ledger.

Stdlib unittest only (matches the rest of the project's test convention).

Run:
    python tests/test_reliability.py

Exit 0 = all pass; non-zero = failure count.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))

from lib import reliability  # type: ignore  # noqa: E402


class TestPosteriorAccuracy(unittest.TestCase):
    def test_uniform_prior(self):
        """Beta(1,1) with no data -> mean 0.5."""
        self.assertAlmostEqual(reliability.posterior_accuracy(0, 0), 0.5)

    def test_high_evidence_saturates(self):
        """100 agreements, 0 disagreements -> >= 0.99."""
        p = reliability.posterior_accuracy(100, 0)
        self.assertGreaterEqual(p, 0.99)

    def test_balanced_evidence(self):
        """10/10 -> ~0.5."""
        self.assertAlmostEqual(reliability.posterior_accuracy(10, 10), 0.5)


class TestDecay(unittest.TestCase):
    def test_decay_idempotent_same_cycle(self):
        """Running decay twice on the same date must not double-decay."""
        ledger = {
            "lastCycle": "2026-05-18",
            "sources": {
                "a.com": {
                    "global": {
                        "agree": 10.0,
                        "disagree": 5.0,
                        "rawAgree": 10,
                        "rawDisagree": 5,
                    },
                    "byBench": {},
                }
            },
        }
        reliability.decay_counters(ledger, "2026-05-18")
        self.assertEqual(ledger["sources"]["a.com"]["global"]["agree"], 10.0)
        self.assertEqual(ledger["sources"]["a.com"]["global"]["disagree"], 5.0)

    def test_decay_3_cycles_halves_counts(self):
        """21 days elapsed = 3 cycles -> counts halve (decay_factor^3 = 0.5)."""
        ledger = {
            "lastCycle": "2026-04-27",
            "sources": {
                "a.com": {
                    "global": {
                        "agree": 10.0,
                        "disagree": 4.0,
                        "rawAgree": 10,
                        "rawDisagree": 4,
                    },
                    "byBench": {
                        "sweV": {
                            "agree": 6.0,
                            "disagree": 2.0,
                            "rawAgree": 6,
                            "rawDisagree": 2,
                        },
                    },
                }
            },
        }
        reliability.decay_counters(ledger, "2026-05-18")
        self.assertAlmostEqual(
            ledger["sources"]["a.com"]["global"]["agree"], 5.0, places=3
        )
        self.assertAlmostEqual(
            ledger["sources"]["a.com"]["global"]["disagree"], 2.0, places=3
        )
        self.assertAlmostEqual(
            ledger["sources"]["a.com"]["byBench"]["sweV"]["agree"], 3.0, places=3
        )
        # rawAgree never decays
        self.assertEqual(ledger["sources"]["a.com"]["global"]["rawAgree"], 10)


class TestColdStart(unittest.TestCase):
    def test_unknown_source_returns_neutral(self):
        m = reliability.reliability_multiplier(
            {"sources": {}}, "https://unknown.com/x", "sweV"
        )
        self.assertEqual(m, 1.0)

    def test_below_cold_start_threshold_returns_neutral(self):
        """n=5 < 10 cold-start -> neutral 1.0."""
        ledger = {
            "sources": {
                "a.com": {
                    "global": {
                        "agree": 5.0,
                        "disagree": 0.0,
                        "rawAgree": 5,
                        "rawDisagree": 0,
                    },
                    "byBench": {},
                }
            }
        }
        self.assertEqual(
            reliability.reliability_multiplier(ledger, "https://a.com/x", "sweV"),
            1.0,
        )


class TestHierarchicalFallback(unittest.TestCase):
    def test_bench_sparse_falls_through_to_global(self):
        """byBench n=3 (cold) but global n=20 -> use global posterior."""
        ledger = {
            "sources": {
                "a.com": {
                    "global": {
                        "agree": 18.0,
                        "disagree": 2.0,
                        "rawAgree": 18,
                        "rawDisagree": 2,
                    },
                    "byBench": {
                        "sweV": {
                            "agree": 3.0,
                            "disagree": 0.0,
                            "rawAgree": 3,
                            "rawDisagree": 0,
                        },
                    },
                }
            }
        }
        m = reliability.reliability_multiplier(ledger, "https://a.com/x", "sweV")
        # global posterior = (1+18)/(2+20) = 19/22 ~= 0.864
        self.assertGreater(m, 0.80)
        self.assertLess(m, 0.90)


class TestSourceIdentity(unittest.TestCase):
    def test_hostname_extraction(self):
        self.assertEqual(
            reliability.source_identity("https://artificialanalysis.ai/path/x"),
            "artificialanalysis.ai",
        )

    def test_www_strip(self):
        self.assertEqual(
            reliability.source_identity("https://www.example.com"), "example.com"
        )

    def test_trailing_slash_normalization(self):
        # urlparse keeps hostname unchanged regardless of trailing slash
        self.assertEqual(
            reliability.source_identity("https://example.com/"), "example.com"
        )
        self.assertEqual(
            reliability.source_identity("https://example.com"), "example.com"
        )

    def test_fallback_to_label(self):
        self.assertEqual(reliability.source_identity("", "My Source"), "my source")
        self.assertEqual(reliability.source_identity("not a url at all", ""), "")


class TestOneVsFiveScenario(unittest.TestCase):
    def test_trusted_high_reliability_posterior(self):
        """The 1-vs-5 setup: trusted source with n=20, agree=19 -> posterior ~0.91."""
        ledger = {
            "sources": {
                "trusted.com": {
                    "global": {
                        "agree": 19.0,
                        "disagree": 1.0,
                        "rawAgree": 19,
                        "rawDisagree": 1,
                    },
                    "byBench": {
                        "sweV": {
                            "agree": 19.0,
                            "disagree": 1.0,
                            "rawAgree": 19,
                            "rawDisagree": 1,
                        },
                    },
                }
            }
        }
        m = reliability.reliability_multiplier(ledger, "https://trusted.com/x", "sweV")
        # posterior = 20/22 ~= 0.909
        self.assertGreater(m, 0.85)
        self.assertLess(m, 0.95)


class TestUpdateBookkeeping(unittest.TestCase):
    def test_single_agree_updates_both_global_and_bench(self):
        ledger = {"sources": {}}
        reliability.update_reliability(
            ledger, "https://a.com/x", "sweV", True, "2026-05-18"
        )
        src = ledger["sources"]["a.com"]
        self.assertEqual(src["global"]["agree"], 1.0)
        self.assertEqual(src["global"]["rawAgree"], 1)
        self.assertEqual(src["byBench"]["sweV"]["agree"], 1.0)
        self.assertEqual(src["byBench"]["sweV"]["rawAgree"], 1)
        self.assertEqual(src["firstSeen"], "2026-05-18")
        self.assertEqual(src["lastSeen"], "2026-05-18")

    def test_disagreement_increments_disagree_only(self):
        ledger = {"sources": {}}
        reliability.update_reliability(
            ledger, "https://a.com/x", "sweV", False, "2026-05-18"
        )
        src = ledger["sources"]["a.com"]
        self.assertEqual(src["global"]["agree"], 0.0)
        self.assertEqual(src["global"]["disagree"], 1.0)
        self.assertEqual(src["global"]["rawDisagree"], 1)

    def test_no_url_no_label_noops(self):
        ledger = {"sources": {}}
        reliability.update_reliability(ledger, "", "sweV", True, "2026-05-18")
        self.assertEqual(ledger["sources"], {})


class TestLoadSaveRoundtrip(unittest.TestCase):
    def test_round_trip_precision(self):
        ledger = {
            "schemaVersion": "v1",
            "halfLifeCycles": 3,
            "coldStartN": 10,
            "lastCycle": "2026-05-18",
            "sources": {
                "a.com": {
                    "firstSeen": "2026-05-11",
                    "lastSeen": "2026-05-18",
                    "global": {
                        "agree": 12.3456,
                        "disagree": 1.2345,
                        "rawAgree": 15,
                        "rawDisagree": 2,
                    },
                    "byBench": {},
                }
            },
        }
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "rel.json"
            reliability.save_ledger(path, ledger)
            loaded = reliability.load_ledger(path)
        self.assertAlmostEqual(loaded["sources"]["a.com"]["global"]["agree"], 12.3456)
        self.assertEqual(loaded["sources"]["a.com"]["global"]["rawAgree"], 15)
        self.assertEqual(loaded["lastCycle"], "2026-05-18")

    def test_load_missing_returns_scaffold(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "nonexistent.json"
            loaded = reliability.load_ledger(path)
        self.assertEqual(loaded["sources"], {})
        self.assertEqual(loaded["schemaVersion"], "v1")
        self.assertEqual(loaded["coldStartN"], 10)


class TestAccuracyCI(unittest.TestCase):
    def test_zero_observations_returns_unit_interval(self):
        self.assertEqual(reliability.accuracy_ci(0, 0), (0.0, 1.0))

    def test_ci_narrows_with_more_data(self):
        lo1, hi1 = reliability.accuracy_ci(5, 5)
        lo2, hi2 = reliability.accuracy_ci(50, 50)
        # 50/50 should produce a much tighter band than 5/5.
        self.assertLess(hi2 - lo2, hi1 - lo1)


if __name__ == "__main__":
    # unittest.main() defaults to exit=True; explicit return code for CI clarity.
    result = unittest.main(exit=False, verbosity=2).result
    raise SystemExit(
        0 if result.wasSuccessful() else len(result.failures) + len(result.errors)
    )
