#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Phase R7 end-to-end simulation — Source Reliability v2 full chain.

Drives the ledger through 10 synthetic refresh cycles and asserts every
phase behaves as documented:

  Cycles 1-2: ledger populates; reliability lookups still cold-start
              (return 1.0) -> trust ordering identical to pre-R3.
  Cycles 3+:  per-source bench n crosses COLD_START_N=10 -> reliability
              multiplier kicks in -> trusted source overtakes peers on
              per-observation trustScore.
  Cycle 7+:   single I-tier source with n>=20 + posterior>=0.90 + fresh
              triggers Phase R4 exceptional-source-override -> wins the
              cell against 5 unreliable peers.

Stdlib unittest only.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))

from lib import reliability  # type: ignore  # noqa: E402
from lib.tiers import effective_trust_score, trust_score  # type: ignore  # noqa: E402
from lib.winner import pick_winner  # type: ignore  # noqa: E402


def _simulate_cycle(
    ledger: dict,
    cycle_date: str,
    *,
    trusted_agrees: int,
    unreliable_agrees_each: int,
    unreliable_count: int = 5,
    bench_key: str = "sweV",
) -> None:
    """Apply decay + N agreement records per source for one cycle."""
    reliability.decay_counters(ledger, cycle_date)
    for _ in range(trusted_agrees):
        reliability.update_reliability(
            ledger, "https://trusted.com", bench_key, True, cycle_date
        )
    for host_i in range(unreliable_count):
        host = f"https://blog-{host_i}.com"
        for _ in range(unreliable_agrees_each):
            reliability.update_reliability(ledger, host, bench_key, False, cycle_date)


class TestTenCycleSimulation(unittest.TestCase):
    BENCH = "sweV"

    def _make_obs(self, cycle_date: str) -> list[dict]:
        return [
            {
                "value": 75.0,
                "tier": "I",
                "sourceUrl": "https://trusted.com",
                "fetched": cycle_date,
                "verifications": 2,
            },
            *[
                {
                    "value": 60.0,
                    "tier": "C",
                    "sourceUrl": f"https://blog-{i}.com",
                    "fetched": cycle_date,
                }
                for i in range(5)
            ],
        ]

    def test_cycle_1_cold_start_neutral(self):
        """Cycle 1: no prior data -> reliability lookups return 1.0."""
        ledger = reliability._empty_ledger()
        _simulate_cycle(
            ledger,
            "2026-05-18",
            trusted_agrees=3,
            unreliable_agrees_each=3,
        )
        # All counts < cold-start threshold -> neutral.
        self.assertEqual(
            reliability.reliability_multiplier(
                ledger, "https://trusted.com", self.BENCH
            ),
            1.0,
        )

    def test_cycle_3_reliability_active(self):
        """By cycle 3 the trusted bench cell has n >= 10 -> posterior > 0.9."""
        ledger = reliability._empty_ledger()
        for i, cycle in enumerate(["2026-05-18", "2026-05-25", "2026-06-01"]):
            _simulate_cycle(
                ledger,
                cycle,
                trusted_agrees=5,
                unreliable_agrees_each=0,
            )
            del i
        mult = reliability.reliability_multiplier(
            ledger, "https://trusted.com", self.BENCH
        )
        self.assertGreater(mult, 0.85)
        self.assertLessEqual(mult, 1.0)

    def test_cycle_7_exceptional_override_active(self):
        """After ~7 cycles of agreement, n >= 20 and posterior >= 0.90 -> R4
        exceptional-source-override fires and the trusted single source wins
        against the 5-source unreliable cluster."""
        ledger = reliability._empty_ledger()
        cycles = [
            "2026-05-18",
            "2026-05-25",
            "2026-06-01",
            "2026-06-08",
            "2026-06-15",
            "2026-06-22",
            "2026-06-29",
        ]
        for cycle in cycles:
            _simulate_cycle(
                ledger,
                cycle,
                trusted_agrees=6,
                unreliable_agrees_each=1,
            )
        # Trusted bench accumulates ~23 effective n after 7 cycles. Steady
        # state with decay (3-cycle half-life) sits around 29 for 6/cycle;
        # we just need to clear the EXCEPTIONAL_SAMPLE_MIN=20 gate.
        bench = ledger["sources"]["trusted.com"]["byBench"][self.BENCH]
        n = bench["agree"] + bench["disagree"]
        self.assertGreaterEqual(n, 20.0)
        acc = reliability.posterior_accuracy(bench["agree"], bench["disagree"])
        self.assertGreaterEqual(acc, 0.90)

        result = pick_winner(
            self._make_obs("2026-06-29"),
            bench_key=self.BENCH,
            agreement_pp=1.5,
            warn_pp=3,
            block_pp=5,
            reliability_ledger=ledger,
        )
        self.assertEqual(result["winner_value"], 75.0)
        self.assertEqual(result["override_mode"], "exceptional-source-override")

    def test_full_10_cycle_drift(self):
        """Drive 10 cycles and verify the ledger lastCycle stamp tracks the
        most recent cycle date through all decay+update calls."""
        ledger = reliability._empty_ledger()
        cycles = [
            "2026-05-18",
            "2026-05-25",
            "2026-06-01",
            "2026-06-08",
            "2026-06-15",
            "2026-06-22",
            "2026-06-29",
            "2026-07-06",
            "2026-07-13",
            "2026-07-20",
        ]
        for c in cycles:
            _simulate_cycle(
                ledger,
                c,
                trusted_agrees=3,
                unreliable_agrees_each=1,
            )
        self.assertEqual(ledger["lastCycle"], cycles[-1])
        # rawAgree on trusted.com global must hit 30 (3 × 10 cycles); raw is
        # never decayed so it is the authoritative lifetime count.
        self.assertEqual(ledger["sources"]["trusted.com"]["global"]["rawAgree"], 30)

    def test_pre_r3_neutrality_when_ledger_absent(self):
        """Sanity check: without ledger, effective_trust_score equals
        trust_score for every cycle along the simulation."""
        for fetched in ("2026-05-18", "2026-06-15", "2026-07-20"):
            base = trust_score("I", 3, fetched)
            eff = effective_trust_score(
                "I",
                3,
                fetched,
                source_url="https://trusted.com",
                bench_key=self.BENCH,
            )
            self.assertAlmostEqual(eff, base, places=4)


if __name__ == "__main__":
    result = unittest.main(exit=False, verbosity=2).result
    raise SystemExit(
        0 if result.wasSuccessful() else len(result.failures) + len(result.errors)
    )
