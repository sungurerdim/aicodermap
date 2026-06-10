#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for the artifact-validation + merge-helper layer (TEST-01,
2026-06-10): lib/gather_validator, lib/escalation, and merge.py's pure
helpers (merge_pricing, append_source, apply_model_update, validate_gaps).

Stdlib unittest only.

Run:
    python tests/test_pipeline_validation.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))

from lib.escalation import EscalationAction, classify_batch, classify_wave  # noqa: E402
from lib.gather_validator import validate_gather, validate_gather_file  # noqa: E402

# merge.py is a script, not a package module — load it by path once.
_spec = importlib.util.spec_from_file_location(
    "merge_module", PROJECT / "scripts" / "merge.py"
)
merge = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(merge)


# ── gather_validator ─────────────────────────────────────────────────────────


def _gather_artifact(**over):
    art = {
        "batchId": "batch00-acme",
        "mode": "gather",
        "observations": [
            {
                "modelId": "acme-coder-1",
                "benchKey": "swePro",
                "value": 71.5,
                "sourceUrl": "https://swebench.example/leaderboard",
                "tier": "I",
                "fetched": "2026-06-10",
            },
            {
                "modelId": "acme-coder-1",
                "benchKey": "lcb",
                "value": 64.2,
                "sourceUrl": "https://livecodebench.example",
                "tier": "I",
                "fetched": "2026-06-10",
            },
            {
                "modelId": "acme-coder-1",
                "benchKey": "gpqa",
                "value": 55.0,
                "sourceUrl": "https://vendor.example/blog",
                "tier": "S",
                "fetched": "2026-06-10",
            },
        ],
        "runtime": {"startedAt": "2026-06-10T10:00:00Z"},
    }
    art.update(over)
    return art


class TestValidateGather(unittest.TestCase):
    TARGETS = ["acme-coder-1"]

    def test_valid_flat_artifact_passes(self):
        v = validate_gather(_gather_artifact(), self.TARGETS)
        self.assertTrue(v["valid"], v["errors"])
        self.assertEqual(v["stats"]["observations"], 3)
        self.assertFalse(v["stats"]["isWeakBatch"])

    def test_full_schema_bleed_is_a_hard_error(self):
        v = validate_gather(_gather_artifact(models=[], gaps=[]), self.TARGETS)
        self.assertFalse(v["valid"])
        self.assertIn("schema bleed", v["errors"][0])

    def test_wrong_mode_and_missing_batch_id(self):
        v = validate_gather(_gather_artifact(mode="full", batchId=None), self.TARGETS)
        self.assertFalse(v["valid"])
        self.assertTrue(any("mode=" in e for e in v["errors"]))
        self.assertTrue(any("batchId" in e for e in v["errors"]))

    def test_bad_observations_are_dropped_with_warnings(self):
        art = _gather_artifact()
        art["observations"].extend(
            [
                {"modelId": "acme-coder-1"},  # missing required fields
                {  # non-target model
                    "modelId": "other-model",
                    "benchKey": "swePro",
                    "value": 50,
                    "sourceUrl": "https://x.example",
                    "tier": "I",
                    "fetched": "2026-06-10",
                },
                {  # non-numeric value
                    "modelId": "acme-coder-1",
                    "benchKey": "tb2",
                    "value": "n/a",
                    "sourceUrl": "https://x.example",
                    "tier": "I",
                    "fetched": "2026-06-10",
                },
            ]
        )
        v = validate_gather(art, self.TARGETS)
        self.assertTrue(v["valid"])  # still 3 good observations
        self.assertEqual(v["stats"]["observations"], 3)
        self.assertEqual(len(v["warnings"]), 3)

    def test_zero_observations_is_invalid(self):
        v = validate_gather(_gather_artifact(observations=[]), self.TARGETS)
        self.assertFalse(v["valid"])
        self.assertTrue(any("zero valid observations" in e for e in v["errors"]))

    def test_weak_batch_flagged_below_min_avg(self):
        art = _gather_artifact()
        art["observations"] = art["observations"][:1]
        v = validate_gather(art, self.TARGETS)
        self.assertTrue(v["stats"]["isWeakBatch"])
        self.assertIn("acme-coder-1", v["stats"]["weakModels"])

    def test_file_missing_and_stale_mtime(self):
        v = validate_gather_file("Z:/nope/missing.gather.json", self.TARGETS)
        self.assertFalse(v["valid"])
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "batch00.gather.json"
            p.write_text(json.dumps(_gather_artifact()), encoding="utf-8")
            mtime = p.stat().st_mtime
            # Cycle started 400s AFTER the file was written (> 300s grace) →
            # prior-cycle leftover, must be rejected as STALE.
            stale = validate_gather_file(
                p, self.TARGETS, cycle_started_unix=mtime + 400
            )
            self.assertFalse(stale["valid"])
            self.assertTrue(stale["stats"].get("stale"))
            # Fresh mtime + clock-less placeholder startedAt → advisory only.
            fresh = validate_gather_file(
                p, self.TARGETS, cycle_started_unix=time.time() - 60
            )
            self.assertTrue(fresh["valid"], fresh["errors"])


# ── escalation ───────────────────────────────────────────────────────────────


class TestEscalation(unittest.TestCase):
    SPEC = {"batchId": "batch00-acme", "modelIds": ["m1", "m2"]}

    def test_zero_fill_escalates(self):
        art = {"runtime": {"fills": 0, "cellsAttempted": 40}, "observations": []}
        r = classify_batch(art, self.SPEC)
        self.assertEqual(r["action"], EscalationAction.RETRY_SONNET)
        self.assertIn("0-fill", r["reason"])

    def test_weak_gather_escalates(self):
        art = {"runtime": {"fills": 3}, "observations": [{}] * 3}  # avg 1.5 < 3
        r = classify_batch(art, self.SPEC)
        self.assertEqual(r["action"], EscalationAction.RETRY_SONNET)
        self.assertIn("weak-gather", r["reason"])

    def test_healthy_batch_passes(self):
        art = {"runtime": {"fills": 8}, "observations": [{}] * 8}  # avg 4 ≥ 3
        r = classify_batch(art, self.SPEC)
        self.assertEqual(r["action"], EscalationAction.NONE)

    def test_already_retried_never_loops(self):
        art = {"_retry_attempted": True, "runtime": {"fills": 0}, "observations": []}
        r = classify_batch(art, self.SPEC)
        self.assertEqual(r["action"], EscalationAction.NONE)
        self.assertIn("already retried", r["reason"])

    def test_classify_wave_returns_only_escalations(self):
        good = ({"runtime": {"fills": 8}, "observations": [{}] * 8}, self.SPEC)
        bad = (
            {"runtime": {"fills": 0, "cellsAttempted": 10}, "observations": []},
            self.SPEC,
        )
        out = classify_wave([good, bad])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["action"], EscalationAction.RETRY_SONNET)


# ── merge.py helpers ─────────────────────────────────────────────────────────


class TestMergePricing(unittest.TestCase):
    def test_dedupe_by_provider_newest_fetched_wins(self):
        dst = {
            "api": [
                {"provider": "Acme", "in": 3.0, "out": 15.0, "fetched": "2026-05-01"}
            ]
        }
        merge.merge_pricing(
            dst,
            {
                "api": [
                    {
                        "provider": "Acme",
                        "in": 2.5,
                        "out": 12.0,
                        "fetched": "2026-06-01",
                    },
                    {
                        "provider": "Beta",
                        "in": 0.4,
                        "out": 1.6,
                        "fetched": "2026-06-01",
                    },
                ]
            },
        )
        by_prov = {e["provider"]: e for e in dst["api"]}
        self.assertEqual(len(dst["api"]), 2)
        self.assertEqual(by_prov["Acme"]["in"], 2.5)  # newer fetched replaced older
        self.assertEqual(dst["range"]["in"], [0.4, 2.5])
        self.assertEqual(dst["range"]["out"], [1.6, 12.0])

    def test_older_fetched_does_not_evict(self):
        dst = {
            "api": [
                {"provider": "Acme", "in": 2.5, "out": 12.0, "fetched": "2026-06-01"}
            ]
        }
        merge.merge_pricing(
            dst,
            {
                "api": [
                    {
                        "provider": "Acme",
                        "in": 9.9,
                        "out": 99.0,
                        "fetched": "2026-04-01",
                    }
                ]
            },
        )
        self.assertEqual(dst["api"][0]["in"], 2.5)


class TestAppendSource(unittest.TestCase):
    ENTRY = {
        "value": 71.5,
        "source": "swebench-leaderboard",
        "url": "https://swebench.example/leaderboard",
        "date": "2026-06-10",
        "tier": "I",
        "trustScore": 0.9,
    }

    def test_legacy_bench_key_rejected(self):
        with self.assertRaises(ValueError):
            merge.append_source({}, "acme-coder-1.bench.swePro", dict(self.ENTRY))

    def test_appends_then_dedupes_by_url_value(self):
        sources = {}
        self.assertTrue(
            merge.append_source(sources, "acme-coder-1.swePro", dict(self.ENTRY))
        )
        updated = dict(self.ENTRY, trustScore=0.95)
        # Same (url, value) → no second row, but fresher fields are applied.
        self.assertFalse(merge.append_source(sources, "acme-coder-1.swePro", updated))
        self.assertEqual(len(sources["acme-coder-1.swePro"]), 1)
        self.assertEqual(sources["acme-coder-1.swePro"][0]["trustScore"], 0.95)


class TestApplyModelUpdate(unittest.TestCase):
    def test_bench_update_stamps_per_cell_date(self):
        model = {"id": "acme-coder-1", "bench": {"swePro": 60.0}}
        touched = merge.apply_model_update(
            model, {"bench": {"swePro": 71.5, "lcb": None}}
        )
        self.assertTrue(touched)
        self.assertEqual(model["bench"]["swePro"], 71.5)
        self.assertNotIn("lcb", model["bench"])  # null returns leave cell alone
        self.assertEqual(model["benchUpdated"]["swePro"], merge.TODAY)
        self.assertEqual(model["lastUpdated"], merge.NOW)

    def test_no_delta_means_untouched(self):
        model = {"id": "acme-coder-1", "context": 200000}
        touched = merge.apply_model_update(model, {"context": 200000})
        self.assertFalse(touched)
        self.assertNotIn("lastUpdated", model)

    def test_privacy_dict_merge_preserves_known_fields(self):
        model = {"id": "x", "privacy": {"soc2": True, "gdpr": True}}
        merge.apply_model_update(model, {"privacy": {"gdpr": False}})
        self.assertEqual(model["privacy"], {"soc2": True, "gdpr": False})


class TestValidateGaps(unittest.TestCase):
    def test_malformed_gap_repaired_in_place_not_stripped(self):
        out = {
            "gaps": [
                {"modelId": "acme-coder-1", "field": "tbHard", "reason": "not found"}
            ]
        }
        suspicions = merge.validate_gaps(out)
        g = out["gaps"][0]
        self.assertEqual(len(out["gaps"]), 1)  # repaired, NOT stripped (MX1 guard)
        self.assertEqual(g["triedSources"], [merge.GAP_REPAIR_STUB_SOURCE])
        self.assertEqual(len(g["triedQueries"]), 2)
        self.assertEqual(
            set(g["_repaired"]), {"triedSources", "triedQueries", "triedFormats"}
        )
        self.assertEqual(out["runtime"]["repairedGaps"][0]["field"], "tbHard")
        self.assertTrue(suspicions and suspicions[0]["repairedFields"])

    def test_well_formed_gap_passes_clean(self):
        out = {
            "gaps": [
                {
                    "modelId": "acme-coder-1",
                    "field": "tbHard",
                    "reason": "leaderboard lacks model",
                    "triedSources": [f"https://s{i}.example" for i in range(5)],
                    "triedQueries": [
                        "acme coder tbHard",
                        "acme coder terminal-bench hard",
                    ],
                    "triedFormats": ["static_html_table"],
                }
            ]
        }
        suspicions = merge.validate_gaps(out)
        self.assertEqual(suspicions, [])
        self.assertNotIn("_repaired", out["gaps"][0])
        # validate_gaps always materializes runtime via setdefault; a clean
        # pass just leaves it without repair/suspicion records.
        self.assertNotIn("repairedGaps", out.get("runtime", {}))
        self.assertNotIn("fabricatedSuspicions", out.get("runtime", {}))


if __name__ == "__main__":
    result = unittest.main(verbosity=2, exit=False).result
    sys.exit(0 if result.wasSuccessful() else 1)
