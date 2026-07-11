#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for the previously-uncovered scripts/lib modules (TEST-01,
2026-06-10): util, cluster, whitelist, matrix, dispatch, freshness,
telemetry, idea_context.

Stdlib unittest only (matches the rest of the project's test convention).

Run:
    python tests/test_lib_units.py
"""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))

from lib import util  # noqa: E402
from lib.cluster import _apply_low_confidence_penalty, _cluster_observations  # noqa: E402
from lib import whitelist as wl  # noqa: E402
from lib import matrix  # noqa: E402
from lib import dispatch  # noqa: E402
from lib.freshness import classify_cell, compute_skip_cells  # noqa: E402
from lib.telemetry import aggregate_per_batch_telemetry  # noqa: E402
from lib import idea_context  # noqa: E402

# scripts/add-new-lineup-stubs.py is hyphenated (a script, not a package module),
# so load it by path for the new-model admission gate regression tests.
import importlib.util as _ilu  # noqa: E402

_stub_spec = _ilu.spec_from_file_location(
    "add_new_lineup_stubs", PROJECT / "scripts" / "add-new-lineup-stubs.py"
)
add_stubs = _ilu.module_from_spec(_stub_spec)
_stub_spec.loader.exec_module(add_stubs)


# ── util ─────────────────────────────────────────────────────────────────────


class TestUtil(unittest.TestCase):
    def test_slug_norm_collapses_variants(self):
        for variant in ("Qwen3.6-Max", "qwen3-6-max", "Qwen 3.6 Max"):
            self.assertEqual(util.slug_norm(variant), "qwen36max")

    def test_extract_domain_strips_www_prefix_only(self):
        """Regression: lstrip('www.') mangled openrouter.ai → penrouter.ai."""
        self.assertEqual(util.extract_domain("https://www.openrouter.ai/models"), "openrouter.ai")
        self.assertEqual(util.extract_domain("https://openai.com/blog"), "openai.com")
        self.assertEqual(util.extract_domain("https://ollama.com"), "ollama.com")
        self.assertEqual(util.extract_domain(""), "")

    def test_safe_json_load_default_on_missing(self):
        self.assertEqual(util.safe_json_load("Z:/nope/missing.json", default={}), {})

    def test_parse_locale_decimal_variants(self):
        self.assertEqual(util.parse_locale_decimal("87.6"), 87.6)
        self.assertEqual(util.parse_locale_decimal("87,6"), 87.6)
        self.assertEqual(util.parse_locale_decimal("1,234.56"), 1234.56)
        self.assertEqual(util.parse_locale_decimal("1.234,56"), 1234.56)
        self.assertEqual(util.parse_locale_decimal("1,234"), 1234.0)
        self.assertEqual(util.parse_locale_decimal("95%"), 95.0)
        self.assertEqual(util.parse_locale_decimal(42), 42.0)
        self.assertIsNone(util.parse_locale_decimal(None))
        self.assertIsNone(util.parse_locale_decimal("n/a"))

    def test_canonical_display_name_version_dot(self):
        self.assertEqual(util.canonical_display_name("Qwen3 7 Max"), "Qwen3.7 Max")
        # Param sizes and dotted versions must be untouched.
        self.assertEqual(util.canonical_display_name("Gemma 3 27B"), "Gemma 3 27B")
        self.assertEqual(util.canonical_display_name("GPT-5.5"), "GPT-5.5")

    def test_canonical_display_name_slug_repair(self):
        self.assertEqual(util.canonical_display_name("minimax-m3", "MiniMax"), "MiniMax M3")
        self.assertEqual(util.canonical_display_name("minimax-m2-7", "MiniMax"), "MiniMax M2.7")
        # Already-formatted names never re-enter the slug path.
        self.assertEqual(util.canonical_display_name("MiniMax M2.7", "MiniMax"), "MiniMax M2.7")

    def test_normalize_anomaly_verdict_mapping_and_idempotence(self):
        raw = {
            "verdict": "correct",
            "evidence": ["https://a.example", "https://b.example"],
            "correctedBenchKey": "webDevElo",
            "correctedValue": 1234,
            "note": "moved to sibling",
        }
        out = util.normalize_anomaly_verdict(raw)
        self.assertEqual(out["action"], "correct")
        self.assertEqual(out["evidence"], "https://a.example; https://b.example")
        self.assertEqual(out["toBench"], "webDevElo")
        self.assertEqual(out["toValue"], 1234)
        self.assertEqual(out["reason"], "moved to sibling")
        self.assertEqual(util.normalize_anomaly_verdict(out), out)  # idempotent


# ── cluster ──────────────────────────────────────────────────────────────────


def _obs(value, trust, url, fetched=""):
    return {"value": value, "trustScore": trust, "sourceUrl": url, "fetched": fetched}


class TestCluster(unittest.TestCase):
    def test_within_agreement_one_cluster_weighted_centroid(self):
        scored = [
            _obs(80.0, 1.0, "https://a.example/lb"),
            _obs(84.0, 0.5, "https://b.example/lb"),
        ]
        clusters = _cluster_observations(scored, agreement_pp=5.0)
        self.assertEqual(len(clusters), 1)
        c = clusters[0]
        self.assertAlmostEqual(c["centroid"], (80 * 1.0 + 84 * 0.5) / 1.5, places=3)
        self.assertEqual(c["sum_trust"], 1.5)
        self.assertEqual(c["distinct_sources"], 2)

    def test_outlier_forms_second_cluster_and_ranks_below(self):
        scored = [
            _obs(80.0, 1.0, "https://a.example"),
            _obs(80.5, 0.9, "https://b.example"),
            _obs(95.0, 0.2, "https://c.example"),  # outlier, low trust
        ]
        clusters = _cluster_observations(scored, agreement_pp=1.5)
        self.assertEqual(len(clusters), 2)
        self.assertAlmostEqual(clusters[0]["centroid"], 80.237, places=2)
        self.assertEqual(clusters[1]["members"][0]["value"], 95.0)

    def test_recency_tiebreak_within_trust_band(self):
        """FAZ 6.D: clusters within the 0.5 trust band re-order by recency."""
        scored = [
            _obs(50.0, 1.0, "https://old.example", fetched="2026-06-09"),
            _obs(70.0, 1.2, "https://new.example", fetched="2026-06-01"),
        ]
        clusters = _cluster_observations(scored, agreement_pp=1.5)
        # Same bucket (round(1.0/0.5)=2 == round(1.2/0.5)=2), same distinct
        # count → fresher latest_fetched wins despite lower sum_trust.
        self.assertEqual(clusters[0]["latest_fetched"], "2026-06-09")

    def test_low_confidence_penalty(self):
        scored = [_obs(80.0, 1.0, "https://root.example/")]
        out = _apply_low_confidence_penalty(scored, {"https://root.example"}, 0.5)
        self.assertEqual(out[0]["trustScore"], 0.5)
        self.assertTrue(out[0]["_lowConfidence"])

    def test_penalty_noop_when_multiplier_is_one(self):
        scored = [_obs(80.0, 1.0, "https://root.example/")]
        out = _apply_low_confidence_penalty(scored, {"https://root.example"}, 1.0)
        self.assertEqual(out[0]["trustScore"], 1.0)
        self.assertNotIn("_lowConfidence", out[0])


# ── whitelist ────────────────────────────────────────────────────────────────


SYNTH_WL = {
    "_schema": {
        "contracts": {"STALE_DAYS": 21},
        "coreBenchKeys": ["swePro", "cfElo"],
        "emergingBenchKeys": ["mcpA"],
        "benchRanges": {
            "cfElo": {"hardMin": 800, "hardMax": 3800},
            "_default": {"hardMin": 0, "hardMax": 100},
        },
    },
    "leaderboards": [
        {
            "url": "https://swebench.example/leaderboard",
            "format": "static_html_table",
            "tier": "I",
            "publishes": ["swePro"],
        },
        {
            "url": "https://webdev.example/arena",
            "format": "spa_partial",
            "tier": "I",
            "publishes": [{"key": "webDevElo", "priority": "secondary"}],
        },
    ],
    "aggregators": [],
}


class TestWhitelist(unittest.TestCase):
    def test_contracts_overlay_safe_defaults(self):
        merged = wl.contracts(SYNTH_WL)
        self.assertEqual(merged["STALE_DAYS"], 21)  # schema override
        self.assertEqual(merged["CONTRADICTION_WARN_PP"], 3.0)  # default kept

    def test_bench_band_accepts_full_whitelist_or_schema_block(self):
        """Regression: passing a bare _schema block used to double-extract and
        wrongly band cfElo 3206 as outside [0,100]."""
        self.assertEqual(wl.bench_band(SYNTH_WL, "cfElo"), (800.0, 3800.0))
        self.assertEqual(wl.bench_band(SYNTH_WL["_schema"], "cfElo"), (800.0, 3800.0))
        self.assertEqual(wl.bench_band(SYNTH_WL, "swePro"), (0.0, 100.0))

    def test_all_bench_keys_is_core_union_emerging(self):
        self.assertEqual(wl.all_bench_keys(SYNTH_WL), ["swePro", "cfElo", "mcpA"])

    def test_required_bench_keys_unions_presets(self):
        schema_wl = {
            "_schema": {
                "presets": {
                    "swe-focused": {"requiredBenches": ["swePro", "lcb"]},
                    "agentic-focused": {"requiredBenches": ["tau2", "tb2"]},
                    "consensus": {"kind": "vendorConsensus"},  # no requiredBenches
                }
            }
        }
        self.assertEqual(wl.required_bench_keys(schema_wl), {"swePro", "lcb", "tau2", "tb2"})
        self.assertEqual(wl.required_bench_keys(SYNTH_WL), set())

    def test_hostname_index_maps_format_and_tier(self):
        idx = wl.hostname_index(SYNTH_WL)
        self.assertEqual(idx["swebench.example"], ("static_html_table", "I"))

    def test_bench_universe_handles_both_publishes_shapes(self):
        universe = wl.bench_universe(SYNTH_WL)
        self.assertIn("swePro", universe)
        self.assertIn("webDevElo", universe)  # dict-shaped publishes entry

    def test_leaderboard_index_priority_resolution(self):
        idx = wl.leaderboard_index_by_bench(SYNTH_WL)
        self.assertEqual(idx["swePro"][0]["priority"], "primary")  # legacy default
        self.assertEqual(idx["webDevElo"][0]["priority"], "secondary")

    def test_confusable_family(self):
        self.assertIn("lmArenaElo", wl.confusable_family("cfElo"))
        self.assertEqual(wl.confusable_family("gpqa"), set())

    def test_build_domain_publishes_seeds_arena_elo(self):
        dp = wl.build_domain_publishes({})
        self.assertEqual(dp["lmarena.ai"], {"lmArenaElo", "webDevElo"})

    def test_elo_swe_misfile_hard_and_soft(self):
        dp = {
            "webdev.example": {"webDevElo"},
            "cf.example": {"cfElo"},
        }
        # Sibling-only support for a HARD_CONFUSABLE key → merge-blocking.
        hit, hard = wl.elo_swe_misfile("cfElo", ["https://webdev.example/arena"], dp)
        self.assertIsNotNone(hit)
        self.assertTrue(hard)
        # A by-name publisher present → advisory only.
        hit2, hard2 = wl.elo_swe_misfile(
            "cfElo",
            ["https://webdev.example/arena", "https://cf.example/rating"],
            dp,
        )
        self.assertIsNotNone(hit2)
        self.assertFalse(hard2)
        # Non-confusable bench → never a misfile.
        self.assertEqual(wl.elo_swe_misfile("gpqa", ["https://x.example"], dp), (None, False))

    def test_load_whitelist_reads_file_and_raises_on_missing(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "wl.json"
            p.write_text(json.dumps({"_schema": {"coreBenchKeys": ["swePro"]}}), encoding="utf-8")
            self.assertEqual(wl.load_whitelist(p)["_schema"]["coreBenchKeys"], ["swePro"])
            with self.assertRaises(FileNotFoundError):
                wl.load_whitelist(Path(td) / "missing.json")

    def test_filter_for_batch_warns_loudly_on_zero_vendor_match(self):
        # Regression for the "Z.ai (Zhipu AI)" -> zai_glm silent-empty-bundle
        # bug (2026-07-11): a provider with no vendor-key match must print a
        # loud warning, not silently ship an empty vendors{} bundle.
        whitelist = {
            "_schema": {"coreBenchKeys": ["swePro"]},
            "vendors": {"zai_glm": {"name": "Z.ai (Zhipu AI)"}},
            "leaderboards": [],
            "aggregators": [],
        }
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            out = wl.filter_for_batch(whitelist, {"Z.ai (Zhipu AI)"})
        self.assertIn("zai_glm", out["vendors"])
        self.assertEqual(buf.getvalue(), "")  # matched -> no warning

        buf2 = io.StringIO()
        with contextlib.redirect_stderr(buf2):
            out2 = wl.filter_for_batch(whitelist, {"Totally Unknown Vendor Inc"})
        self.assertEqual(out2["vendors"], {})
        self.assertIn("WARN", buf2.getvalue())
        self.assertIn("totally unknown vendor inc", buf2.getvalue())


# ── matrix ───────────────────────────────────────────────────────────────────


class TestMatrix(unittest.TestCase):
    MODELS = [
        {"id": "alpha", "bench": {"swePro": 70.0, "cfElo": None}},
        {"id": "beta", "status": "deprecated", "bench": {"swePro": 50.0}},
        {"id": "gamma", "status": "archived", "bench": {"swePro": 60.0}},
    ]

    def test_active_models_excludes_deprecated_and_archived(self):
        # 2026-06-27: deprecated + archived are both OUT of the research universe
        # (data frozen, still rendered). Only status 'active' is researched.
        ids = [m["id"] for m in matrix.active_models(self.MODELS)]
        self.assertEqual(ids, ["alpha"])

    def test_filled_and_universe_and_expected_total(self):
        active = matrix.active_models(self.MODELS)
        keys = ["swePro", "cfElo"]
        self.assertEqual(matrix.expected_total(active, keys), 2)
        self.assertEqual(
            matrix.total_universe(active, keys),
            {
                ("alpha", "swePro"),
                ("alpha", "cfElo"),
            },
        )
        # None-valued cells are NOT filled.
        self.assertEqual(
            matrix.filled_cells_from_models(active, keys),
            {("alpha", "swePro")},
        )

    def test_parse_gap_cell_both_shapes(self):
        self.assertEqual(matrix.parse_gap_cell({"key": "alpha.cfElo"}), ("alpha", "cfElo"))
        self.assertEqual(
            matrix.parse_gap_cell({"modelId": "alpha", "field": "cfElo"}),
            ("alpha", "cfElo"),
        )
        self.assertIsNone(matrix.parse_gap_cell({"key": "alpha.bench.cfElo"}))
        self.assertIsNone(matrix.parse_gap_cell({}))

    def test_verify_matrix_invariant(self):
        universe = {("a", "k1"), ("a", "k2")}
        ok = matrix.verify_matrix_invariant({("a", "k1")}, {("a", "k2")}, universe)
        self.assertTrue(ok["ok"])
        missing = matrix.verify_matrix_invariant({("a", "k1")}, set(), universe)
        self.assertFalse(missing["ok"])
        self.assertEqual(missing["missing"], [("a", "k2")])
        overlap = matrix.verify_matrix_invariant(
            {("a", "k1"), ("a", "k2")}, {("a", "k2")}, universe
        )
        self.assertFalse(overlap["ok"])
        self.assertEqual(overlap["overlap"]["filled_gap"], [("a", "k2")])

    def test_priority_cells_boosts_rank_critical_over_raw_starvation(self):
        # 2026-07-11: a model missing only its LAST required bench (flagship,
        # already well-covered) must outrank a barely-covered model's cells
        # that aren't required by any preset, even though raw starve ratios
        # would sort the barely-covered model's cells first.
        keys = ["swePro", "lcb", "other"]
        active = [
            {"id": "flagship", "bench": {"swePro": 90.0, "lcb": None, "other": 50.0}},
            {"id": "poor", "bench": {"swePro": None, "lcb": None, "other": None}},
        ]
        pc = matrix.priority_cells(active, keys, limit=10, required_keys={"swePro", "lcb"})
        order = [(c["modelId"], c["benchKey"]) for c in pc]
        self.assertEqual(order[0], ("flagship", "lcb"))
        flagship_entry = next(c for c in pc if c["modelId"] == "flagship")
        self.assertTrue(flagship_entry.get("rankCritical"))
        poor_entries = [c for c in pc if c["modelId"] == "poor"]
        self.assertTrue(all(not c.get("rankCritical") for c in poor_entries))

    def test_priority_cells_starved_still_beats_rank_critical(self):
        # gapHistory-starved cells (-1.0) stay strictly ahead of the new
        # rank-critical tier (-0.5) — starvation is a stronger signal than
        # "would unlock ranking" (a starved cell has already failed repeatedly).
        # Each model is missing exactly ONE required bench (the qualifying
        # condition for the rank-critical boost); "starved" additionally has
        # gapHistory on its one missing cell.
        keys = ["swePro", "lcb"]
        active = [
            {"id": "starved-model", "bench": {"swePro": None, "lcb": 80.0}},
            {"id": "fresh-model", "bench": {"swePro": 70.0, "lcb": None}},
        ]
        vmap = {"cells": {"starved-model.swePro": {"gapHistory": ["2026-07-02", "2026-07-11"]}}}
        pc = matrix.priority_cells(
            active,
            keys,
            limit=10,
            verification_map=vmap,
            required_keys={"swePro", "lcb"},
        )
        self.assertEqual((pc[0]["modelId"], pc[0]["benchKey"]), ("starved-model", "swePro"))
        self.assertTrue(pc[0]["starved"])
        self.assertEqual((pc[1]["modelId"], pc[1]["benchKey"]), ("fresh-model", "lcb"))
        self.assertTrue(pc[1].get("rankCritical"))

    def test_gap_source_by_cell_defaults_untagged_to_agent(self):
        artifact = {
            "gaps": [
                {"key": "alpha.swePro", "source": "orchestrator"},
                {"key": "alpha.lcb", "source": "agent"},
                {"key": "beta.gpqa"},  # no explicit source -> defaults to agent
            ]
        }
        self.assertEqual(
            matrix.gap_source_by_cell(artifact),
            {
                ("alpha", "swePro"): "orchestrator",
                ("alpha", "lcb"): "agent",
                ("beta", "gpqa"): "agent",
            },
        )

    def test_priority_cells_chronic_flag_requires_agent_sourced_history(self):
        # CHRONIC_AGENT_CYCLES (3) consecutive AGENT-sourced attempts -> chronic.
        # A cell with the same total gapHistory length but sourced from the
        # orchestrator placeholder (never actually researched) is NOT chronic.
        keys = ["swePro"]
        active = [
            {"id": "chronic-model", "bench": {"swePro": None}},
            {"id": "unreached-model", "bench": {"swePro": None}},
        ]
        vmap = {
            "cells": {
                "chronic-model.swePro": {
                    "gapHistory": ["2026-06-15", "2026-06-27", "2026-07-11"],
                    "gapHistoryAgent": ["2026-06-15", "2026-06-27", "2026-07-11"],
                },
                "unreached-model.swePro": {
                    "gapHistory": ["2026-06-15", "2026-06-27", "2026-07-11"],
                    "gapHistoryAgent": [],
                },
            }
        }
        pc = matrix.priority_cells(active, keys, limit=10, verification_map=vmap)
        by_model = {c["modelId"]: c for c in pc}
        self.assertTrue(by_model["chronic-model"].get("chronic"))
        self.assertFalse(by_model["unreached-model"].get("chronic"))


# ── dispatch ─────────────────────────────────────────────────────────────────


def _models(n, provider):
    return [{"id": f"{provider.lower()}-m{i}", "provider": provider} for i in range(n)]


class TestDispatch(unittest.TestCase):
    def test_family_of_normalization(self):
        self.assertEqual(dispatch.family_of("Google DeepMind"), "google")
        self.assertEqual(dispatch.family_of("Alibaba (Qwen)"), "qwen")
        self.assertEqual(dispatch.family_of("Z.ai (Zhipu)"), "zai")
        self.assertEqual(dispatch.family_of(None), "other")

    def test_models_per_batch_budget_derivation(self):
        # 150-cell budget: 26 keys → 5; tiny key count caps at the absolute max.
        self.assertEqual(dispatch.models_per_batch(26), 5)
        self.assertEqual(dispatch.models_per_batch(10), dispatch.ABSOLUTE_MAX_BATCH_MODELS)
        self.assertEqual(dispatch.models_per_batch(0), dispatch.ABSOLUTE_MAX_BATCH_MODELS)

    def test_split_oversize_batches(self):
        out = dispatch.split_oversize_batches([_models(7, "Acme")], 3)
        self.assertEqual([len(b) for b in out], [3, 3, 1])

    def test_pack_batches_ffd_minimizes_bins(self):
        buckets = [_models(6, "A"), _models(3, "B"), _models(2, "C"), _models(1, "D")]
        bins = dispatch.pack_batches(buckets, 6)
        self.assertEqual(sorted(len(b) for b in bins), [6, 6])

    def test_compute_dispatch_plan_covers_every_model_once(self):
        active = _models(8, "TestVendor")
        plan = dispatch.compute_dispatch_plan(active, [f"k{i}" for i in range(25)])
        all_ids = [mid for b in plan["batches"] for mid in b["modelIds"]]
        self.assertEqual(sorted(all_ids), sorted(m["id"] for m in active))
        self.assertEqual(len(all_ids), len(set(all_ids)))  # no duplicates
        for b in plan["batches"]:
            self.assertLessEqual(b["modelCount"], plan["modelsPerBatch"])
            self.assertRegex(b["batchId"], r"^batch\d{2}-[a-z0-9_-]+$")
            self.assertEqual(b["expectedCells"], b["modelCount"] * 25)

    def test_dense_family_shrinks_to_vendor_pure_batches(self):
        active = _models(6, "OpenAI") + _models(2, "Acme")
        plan = dispatch.compute_dispatch_plan(
            active,
            [f"k{i}" for i in range(25)],
            dense_families={"openai"},
            dense_max_models=4,
        )
        openai_batches = [b for b in plan["batches"] if all("openai-" in m for m in b["modelIds"])]
        self.assertTrue(openai_batches, "expected vendor-pure openai batches")
        for b in openai_batches:
            self.assertLessEqual(b["modelCount"], 4)

    def test_mixed_family_batch_gets_mixed_label(self):
        # Fable-5 R4 (2026-07-11): a batch spanning multiple vendor families
        # (sparse-leftover FFD packing) must self-label as `mixed-<fam>-<fam>`
        # instead of a single-vendor name that hides the other family present
        # (observed: `batch09-anthropic` silently containing Google DeepMind
        # models too — see scripts/lib/whitelist.filter_for_batch guard).
        active = _models(1, "Google DeepMind") + _models(1, "Anthropic")
        plan = dispatch.compute_dispatch_plan(
            active, [f"k{i}" for i in range(5)], max_models_override=10
        )
        self.assertEqual(len(plan["batches"]), 1)
        batch_id = plan["batches"][0]["batchId"]
        self.assertIn("mixed-", batch_id)
        self.assertIn("google", batch_id)
        self.assertIn("anthropic", batch_id)

    def test_single_family_batch_keeps_plain_label(self):
        active = _models(2, "Anthropic")
        plan = dispatch.compute_dispatch_plan(
            active, [f"k{i}" for i in range(5)], max_models_override=10
        )
        self.assertNotIn("mixed-", plan["batches"][0]["batchId"])
        self.assertRegex(plan["batches"][0]["batchId"], r"^batch00-anthropic")


# ── freshness ────────────────────────────────────────────────────────────────


class TestFreshness(unittest.TestCase):
    TODAY = date(2026, 6, 10)

    def _cell(self, **over):
        cell = {
            "confirmed": True,
            "verifications": [{}, {}, {}],
            "lastChecked": "2026-06-08",
        }
        cell.update(over)
        return cell

    def test_t2_skip_when_confirmed(self):
        cls = classify_cell(self._cell(), self.TODAY)
        self.assertEqual(cls["tier"], "T2")
        self.assertTrue(cls["skip"])
        self.assertEqual(cls["ageDays"], 2)  # informational only

    def test_t2_skip_ignores_age(self):
        # TTL removed 2026-06-27: a confirmed cell skips regardless of age — a
        # released model's published score is frozen, so age is irrelevant.
        cls = classify_cell(self._cell(lastChecked="2026-02-01"), self.TODAY)
        self.assertEqual(cls["tier"], "T2")
        self.assertTrue(cls["skip"])

    def test_t1_disqualifiers(self):
        self.assertEqual(classify_cell(None, self.TODAY)["reason"], "no-map-entry")
        self.assertEqual(classify_cell(self._cell(confirmed=False), self.TODAY)["tier"], "T1")
        # contradiction is the SOLE event that re-opens a confirmed cell.
        self.assertEqual(classify_cell(self._cell(contradicted=True), self.TODAY)["tier"], "T1")

    def test_compute_skip_cells_meta_counts(self):
        vm = {"cells": {"alpha.swePro": self._cell()}}
        skip = compute_skip_cells(vm, self.TODAY, ["alpha"], ["swePro", "cfElo"])
        self.assertEqual(skip["_meta"], {"t1Count": 1, "t2Count": 1, "totalConsidered": 2})
        self.assertIn("swePro", skip["alpha"])
        self.assertNotIn("cfElo", skip.get("alpha", {}))


# ── telemetry ────────────────────────────────────────────────────────────────


class TestTelemetry(unittest.TestCase):
    def test_aggregate_mixed_gather_and_full_modes(self):
        arts = [
            {
                "batchId": "batch00-acme",
                "mode": "gather",
                "observations": [{}, {}, {}],
                "rawGaps": [{}],
                "runtime": {"toolCallCount": 12, "wallclockSec": 300.0},
            },
            {
                "batchId": "batch01-beta",
                "models": [{"updates": {"bench": {"swePro": 70, "lcb": 60}}}],
                "gaps": [
                    {"source": "orchestrator"},
                    {"source": "agent"},
                ],
                "runtime": {"toolCallCount": 8, "wallclockSec": 100.0},
            },
            {
                "batchId": "batch02-empty",
                "mode": "gather",
                "observations": [],
                "runtime": {"toolCallCount": 2},
            },
        ]
        tele = aggregate_per_batch_telemetry(arts)
        self.assertEqual(tele["totalBatches"], 3)
        self.assertEqual(tele["zeroFillBatches"], ["batch02-empty"])
        self.assertEqual(tele["totals"]["fills"], 5)  # 3 obs + 2 bench updates
        self.assertEqual(tele["totals"]["gaps"], 3)
        self.assertEqual(tele["totals"]["orchestratorGaps"], 1)
        self.assertEqual(tele["totals"]["toolCallSum"], 22)
        self.assertEqual(tele["totals"]["wallclockSecMax"], 300.0)

    def test_aggregate_mixed_timestamp_types_no_crash(self):
        # Regression (2026-06-16): gather artifacts store runtime.startedAt as
        # int epoch in some batches and ISO string in others; min()/max() over
        # the mixed list used to raise TypeError. Normalized at ingestion now.
        arts = [
            {
                "batchId": "b0",
                "mode": "gather",
                "observations": [{}],
                "runtime": {"startedAt": 1781623839, "endedAt": 1781624400},
            },
            {
                "batchId": "b1",
                "mode": "gather",
                "observations": [{}],
                "runtime": {
                    "startedAt": "2026-06-16T15:30:00Z",
                    "endedAt": "2026-06-16T15:42:00Z",
                },
            },
            {
                "batchId": "b2",
                "mode": "gather",
                "observations": [{}],
                "runtime": {"startedAt": 1781624000.5},
            },
        ]
        tele = aggregate_per_batch_telemetry(arts)  # must not raise
        self.assertEqual(tele["totalBatches"], 3)
        # min/max computed over normalized ISO strings
        self.assertTrue(isinstance(tele["cycleStartedAt"], str))
        self.assertTrue(isinstance(tele["cycleEndedAt"], str))
        self.assertEqual(tele["cycleStartedAt"], "2026-06-16T15:30:00Z")
        self.assertEqual(tele["cycleEndedAt"], "2026-06-16T15:42:00Z")


# ── idea_context slims ───────────────────────────────────────────────────────


class TestIdeaContextSlims(unittest.TestCase):
    def test_slim_snapshots_keeps_path_only(self):
        snaps = {
            "https://a.example": {
                "path": "data/.leaderboard-snapshots/a.html",
                "etag": "x",
            },
            "https://b.example": "data/.leaderboard-snapshots/b.html",
            "https://broken.example": {"contentLength": 12},
        }
        out = idea_context.slim_snapshots(snaps)
        self.assertEqual(
            out,
            {
                "https://a.example": "data/.leaderboard-snapshots/a.html",
                "https://b.example": "data/.leaderboard-snapshots/b.html",
            },
        )
        self.assertEqual(idea_context.slim_snapshots(None), {})

    def test_slim_verification_slice_filters_by_model(self):
        vm = {"cells": {"alpha.swePro": {"v": 1}, "beta.swePro": {"v": 2}}}
        out = idea_context.slim_verification_slice(vm, ["alpha"])
        self.assertEqual(list(out["cells"].keys()), ["alpha.swePro"])

    def test_slim_skip_cells_preserves_meta(self):
        skip = {"alpha": {"swePro": {}}, "beta": {}, "_meta": {"t2Count": 1}}
        out = idea_context.slim_skip_cells(skip, ["alpha"])
        self.assertEqual(set(out.keys()), {"alpha", "_meta"})

    def test_slim_priority_cells(self):
        cells = [{"modelId": "alpha"}, {"modelId": "beta"}]
        self.assertEqual(idea_context.slim_priority_cells(cells, ["beta"]), [{"modelId": "beta"}])


# ── new-model admission gate (2026-06-27 consolidation regression) ────────────


class TestNewModelGate(unittest.TestCase):
    """Regression for the two bugs that silently dropped kimi-k2-7-code +
    glm-5-2 every cycle: (a) evidenceConfidence=="confirmed" was REJECTED;
    (b) evidenceUrl hosts were never counted toward the ≥2-source bar."""

    VENDORS = {
        "moonshot": {"urls": {"lineup": "https://platform.moonshot.ai/models"}},
    }

    def test_confirmed_confidence_admits(self):
        # THE core bug: a harvested entry tagged confidence='confirmed' must pass.
        nm = {"id": "kimi-k2-7-code", "confidence": "confirmed", "evidenceUrls": []}
        admit, reason = add_stubs.gate_admit(nm, self.VENDORS)
        self.assertTrue(admit, reason)

    def test_two_distinct_hosts_admit(self):
        # glm-5-2: marktechpost (channel 2) ∪ artificialanalysis (channel 1).
        nm = {
            "id": "glm-5-2",
            "confidence": "newReleaseProbe",
            "evidenceUrls": [
                "https://www.marktechpost.com/2026/06/13/glm-5-2/",
                "https://artificialanalysis.ai/models/glm-5-2",
            ],
        }
        self.assertEqual(len(add_stubs.evidence_hosts(nm)), 2)
        admit, reason = add_stubs.gate_admit(nm, self.VENDORS)
        self.assertTrue(admit, reason)

    def test_official_single_source_admits(self):
        nm = {
            "id": "kimi-k2-7-code",
            "provider": "moonshot",
            "confidence": "newReleaseProbe",
            "evidenceUrls": ["https://platform.moonshot.ai/docs/kimi-k2-7"],
        }
        self.assertTrue(add_stubs.is_official_evidence(nm, self.VENDORS))
        admit, _ = add_stubs.gate_admit(nm, self.VENDORS)
        self.assertTrue(admit)

    def test_single_nonofficial_low_conf_rejected(self):
        nm = {
            "id": "rumor-x",
            "confidence": "newReleaseProbe",
            "evidenceUrls": ["https://randomblog.example/rumor"],
        }
        admit, reason = add_stubs.gate_admit(nm, self.VENDORS)
        self.assertFalse(admit)
        self.assertIn("insufficient-evidence", reason)

    def test_hyphenated_minor_version_not_superseded(self):
        # glm-5-2 (slug form) must parse to (5, 2), NOT (5,), so GLM-5.1=(5,1)
        # does not falsely supersede it. Existing snapshot from the live lineup.
        existing = [
            {"id": "glm-5-1", "name": "GLM-5.1"},
            {"id": "glm-5", "name": "GLM-5"},
        ]
        self.assertEqual(add_stubs.parse_name("glm-5-2")[1], (5, 2))
        self.assertIsNone(add_stubs.is_superseded("glm-5-2", existing))
        # A genuinely-older snapshot IS still superseded.
        self.assertEqual(
            add_stubs.is_superseded("Claude Opus 4.6", [{"name": "Claude Opus 4.8"}]),
            "Claude Opus 4.8",
        )

    def test_letter_fused_version_not_falsely_open(self):
        # PY-01: a version fused to a single-letter marker ("K2.7", "K2.6")
        # used to parse to version=None, so is_superseded's `not ver` guard
        # short-circuited to None (fails OPEN) — a re-listed older sibling was
        # admitted as a fresh stub even though a newer one was already tracked.
        existing = [{"id": "kimi-k2-7-code", "name": "Kimi K2.7 Code"}]
        self.assertEqual(add_stubs.parse_name("Kimi K2.7 Code"), (("kimi", "k", "code"), (2, 7)))
        # A re-listed older sibling IS recognized as superseded.
        self.assertEqual(add_stubs.is_superseded("Kimi K2.6 Code", existing), "Kimi K2.7 Code")
        # A genuinely-new, higher version in the same family is NOT flagged.
        self.assertIsNone(add_stubs.is_superseded("Kimi K3 Code", existing))

    def test_restricted_held_even_if_admissible(self):
        nm = {
            "id": "preview-y",
            "confidence": "confirmed",
            "notes": "preview only, waitlist required",
            "evidenceUrls": [
                "https://a.example/y",
                "https://b.example/y",
            ],
        }
        admit, reason = add_stubs.gate_admit(nm, self.VENDORS)
        self.assertFalse(admit)
        self.assertEqual(reason, "restricted/not-GA")


if __name__ == "__main__":
    result = unittest.main(verbosity=2, exit=False).result
    sys.exit(0 if result.wasSuccessful() else 1)
