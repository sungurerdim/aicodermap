#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for the artifact-validation + merge-helper layer (TEST-01,
2026-06-10): lib/gather_validator and merge.py's pure helpers
(merge_pricing, append_source, apply_model_update, validate_gaps).

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

from lib.gather_validator import (  # noqa: E402
    validate_gather,
    validate_gather_file,
    zero_obs_models,
)

# merge.py is a script, not a package module — load it by path once.
_spec = importlib.util.spec_from_file_location("merge_module", PROJECT / "scripts" / "merge.py")
merge = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(merge)

_cov_spec = importlib.util.spec_from_file_location(
    "check_new_model_coverage_module", PROJECT / "scripts" / "check-new-model-coverage.py"
)
new_model_coverage = importlib.util.module_from_spec(_cov_spec)
_cov_spec.loader.exec_module(new_model_coverage)


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

    def test_spelling_variant_of_target_id_is_canonicalized_not_dropped(self):
        """2026-07-16: a gather agent spelling the target id differently
        ("ACME_Coder-1" vs canonical "acme-coder-1") used to get its
        observation dropped as "not in target_model_ids" — real data lost for
        a pure formatting reason. It must now canonicalize and count."""
        art = _gather_artifact()
        variant_obs = {
            "modelId": "ACME_Coder-1",
            "benchKey": "mmluPro",
            "value": 71.0,
            "sourceUrl": "https://x.example",
            "tier": "I",
            "fetched": "2026-06-10",
        }
        art["observations"].append(variant_obs)
        v = validate_gather(art, self.TARGETS)
        self.assertTrue(v["valid"])
        self.assertEqual(v["stats"]["observations"], 4)
        self.assertTrue(any("canonicalized" in w for w in v["warnings"]))
        self.assertEqual(variant_obs["modelId"], "acme-coder-1")

    def test_true_non_target_model_still_dropped(self):
        """A genuinely different model id (not a spelling variant) must still
        be dropped — canonicalization must not paper over real mismatches."""
        art = _gather_artifact()
        art["observations"].append(
            {
                "modelId": "other-model",
                "benchKey": "swePro",
                "value": 50,
                "sourceUrl": "https://x.example",
                "tier": "I",
                "fetched": "2026-06-10",
            }
        )
        v = validate_gather(art, self.TARGETS)
        self.assertEqual(v["stats"]["observations"], 3)
        self.assertTrue(
            any("not in target_model_ids" in w for w in v["warnings"])
        )

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
            stale = validate_gather_file(p, self.TARGETS, cycle_started_unix=mtime + 400)
            self.assertFalse(stale["valid"])
            self.assertTrue(stale["stats"].get("stale"))
            # Fresh mtime + clock-less placeholder startedAt → advisory only.
            fresh = validate_gather_file(p, self.TARGETS, cycle_started_unix=time.time() - 60)
            self.assertTrue(fresh["valid"], fresh["errors"])


class TestZeroObsModels(unittest.TestCase):
    """Fable-5 R1 (2026-07-11): cross-batch union of models with 0 total
    observations, feeding the SKILL.md Stage A rescue-batch dispatch."""

    def test_unions_zero_obs_models_across_batches(self):
        v1 = validate_gather(
            _gather_artifact(), ["acme-coder-1", "acme-coder-2"]
        )  # acme-coder-2 gets 0 (no observations for it in the fixture)
        v2 = validate_gather(
            _gather_artifact(observations=[]), ["beta-model-1"]
        )  # whole batch 0-obs
        self.assertEqual(zero_obs_models([v1, v2]), ["acme-coder-2", "beta-model-1"])

    def test_model_present_in_original_and_retry_only_zero_if_both_zero(self):
        original = validate_gather(_gather_artifact(observations=[]), ["acme-coder-1"])
        retry_recovered = validate_gather(_gather_artifact(), ["acme-coder-1"])
        self.assertEqual(zero_obs_models([original, retry_recovered]), [])
        retry_still_empty = validate_gather(_gather_artifact(observations=[]), ["acme-coder-1"])
        self.assertEqual(zero_obs_models([original, retry_still_empty]), ["acme-coder-1"])

    def test_empty_input_yields_empty_list(self):
        self.assertEqual(zero_obs_models([]), [])


class TestNewModelCoverageFloor(unittest.TestCase):
    """Fable-5 R5 (2026-07-11): a model admitted this cycle should surface a
    loud, distinct warning when it's still under the coverage floor after
    Stage A/B — not silently indistinguishable from a chronic gap."""

    CORE = ["swePro", "lcb", "tb2", "gpqa"]

    def test_coverage_of_counts_only_core_keys(self):
        m = {"bench": {"swePro": 50.0, "lcb": None, "extraKey": 99.0}}
        # 1 of 4 core keys filled (extraKey isn't in CORE) -> 0.25.
        self.assertEqual(new_model_coverage.coverage_of(m, self.CORE), 0.25)

    def test_coverage_of_empty_core_keys_is_full(self):
        self.assertEqual(new_model_coverage.coverage_of({"bench": {}}, []), 1.0)

    def test_under_covered_new_models_filters_by_floor(self):
        models = [
            {"id": "fresh-a", "bench": {"swePro": None, "lcb": None, "tb2": None, "gpqa": None}},
            {"id": "fresh-b", "bench": {"swePro": 1.0, "lcb": 2.0, "tb2": 3.0, "gpqa": 4.0}},
            {"id": "fresh-c", "bench": {"swePro": 1.0, "lcb": None, "tb2": None, "gpqa": None}},
        ]
        under = new_model_coverage.under_covered_new_models(
            models, ["fresh-a", "fresh-b", "fresh-c"], self.CORE, floor=0.3
        )
        self.assertEqual([mid for mid, _ in under], ["fresh-a", "fresh-c"])

    def test_under_covered_new_models_skips_bench_mirror_and_missing(self):
        models = [
            {"id": "mirror-variant", "bench": {}, "benchMirrorOf": "base-model"},
        ]
        under = new_model_coverage.under_covered_new_models(
            models, ["mirror-variant", "never-admitted-id"], self.CORE, floor=0.3
        )
        self.assertEqual(under, [])


# ── merge.py helpers ─────────────────────────────────────────────────────────


class TestMergePricing(unittest.TestCase):
    def test_dedupe_by_provider_newest_fetched_wins(self):
        dst = {"api": [{"provider": "Acme", "in": 3.0, "out": 15.0, "fetched": "2026-05-01"}]}
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
        dst = {"api": [{"provider": "Acme", "in": 2.5, "out": 12.0, "fetched": "2026-06-01"}]}
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
        self.assertTrue(merge.append_source(sources, "acme-coder-1.swePro", dict(self.ENTRY)))
        updated = dict(self.ENTRY, trustScore=0.95)
        # Same (url, value) → no second row, but fresher fields are applied.
        self.assertFalse(merge.append_source(sources, "acme-coder-1.swePro", updated))
        self.assertEqual(len(sources["acme-coder-1.swePro"]), 1)
        self.assertEqual(sources["acme-coder-1.swePro"][0]["trustScore"], 0.95)


class TestApplyModelUpdate(unittest.TestCase):
    def test_bench_update_stamps_per_cell_date(self):
        model = {"id": "acme-coder-1", "bench": {"swePro": 60.0}}
        touched = merge.apply_model_update(model, {"bench": {"swePro": 71.5, "lcb": None}})
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


class TestApplyModelUpdatesIdCanonicalization(unittest.TestCase):
    """2026-07-16: merge.py's per-model update loop must recognize a spelling/
    format variant of a canonical id ("GLM-5.2" vs "glm-5-2") as the SAME
    model — not drop it as "unknown id", and not orphan its sourcesAdded[]
    provenance under a never-associated top-level sources.json key."""

    def _models_by(self, models):
        by_id = {m["id"]: m for m in models}
        by_norm = merge.build_norm_id_index(by_id.keys())
        return by_id, by_norm

    def test_spelling_variant_update_id_resolves_to_canonical_model(self):
        models = [{"id": "glm-5-2", "bench": {}}]
        models_by_id, models_by_norm_id = self._models_by(models)
        sources = {}
        log = {"updated": [], "gaps": [], "format_warnings": [], "sources_appended": 0,
               "spa_guard_rejections": 0}
        out = {
            "models": [
                {
                    "id": "GLM-5.2",
                    "updates": {"bench": {"swePro": 71.5}},
                    "sourcesAdded": [],
                }
            ]
        }
        merge._apply_model_updates(out, sources, models_by_id, models_by_norm_id, {}, set(), log)
        self.assertEqual(models[0]["bench"]["swePro"], 71.5)
        self.assertEqual(log["updated"], ["glm-5-2"])
        self.assertNotIn("unknown id in updates: GLM-5.2", log["gaps"])
        self.assertTrue(any("canonicalized" in w for w in log["format_warnings"]))

    def test_truly_unknown_id_still_reported_as_gap(self):
        models = [{"id": "glm-5-2", "bench": {}}]
        models_by_id, models_by_norm_id = self._models_by(models)
        log = {"updated": [], "gaps": [], "format_warnings": [], "sources_appended": 0,
               "spa_guard_rejections": 0}
        out = {"models": [{"id": "totally-different-model", "updates": {}, "sourcesAdded": []}]}
        merge._apply_model_updates(out, {}, models_by_id, models_by_norm_id, {}, set(), log)
        self.assertEqual(log["gaps"], ["unknown id in updates: totally-different-model"])

    def test_sourcesAdded_key_spelling_variant_canonicalized_not_orphaned(self):
        """A sourcesAdded[] entry whose key's modelId segment is spelled
        differently than the enclosing model's real id must land under the
        REAL canonical key, not create an orphaned top-level sources.json
        entry that never gets associated with this model's provenance."""
        models = [{"id": "glm-5-2", "bench": {}}]
        models_by_id, models_by_norm_id = self._models_by(models)
        sources = {}
        log = {"updated": [], "gaps": [], "format_warnings": [], "sources_appended": 0,
               "spa_guard_rejections": 0}
        out = {
            "models": [
                {
                    "id": "glm-5-2",
                    "updates": {},
                    "sourcesAdded": [
                        {
                            "key": "glm_5_2.aaIdx",  # spelling variant of the key's own model
                            "value": 42.0,
                            "source": "artificialanalysis.ai",
                            "url": "https://artificialanalysis.ai/models/glm-5-2",
                            "tier": "I",
                        }
                    ],
                }
            ]
        }
        merge._apply_model_updates(out, sources, models_by_id, models_by_norm_id, {}, set(), log)
        self.assertIn("glm-5-2.aaIdx", sources)
        self.assertNotIn("glm_5_2.aaIdx", sources)
        self.assertEqual(sources["glm-5-2.aaIdx"][0]["value"], 42.0)


class TestProcessLineupChangesIdCanonicalization(unittest.TestCase):
    def test_deprecation_spelling_variant_resolves_to_canonical_model(self):
        models = [{"id": "old-model-1", "status": "active"}]
        models_by_id = {m["id"]: m for m in models}
        models_by_norm_id = merge.build_norm_id_index(models_by_id.keys())
        log = {"lineup_deprecated": [], "lineup_renamed": [], "format_warnings": []}
        out = {"lineupChanges": {"deprecated": [{"id": "Old_Model-1", "successor": "new-model-2"}]}}
        merge._process_lineup_changes(
            out, models_by_id, models_by_norm_id, log, "2026-07-16", "2026-07-16T00:00:00Z"
        )
        self.assertEqual(models[0]["status"], "deprecated")
        self.assertEqual(models[0]["successor"], "new-model-2")
        self.assertEqual(log["lineup_deprecated"], ["old-model-1"])


class TestValidateGaps(unittest.TestCase):
    def test_malformed_gap_repaired_in_place_not_stripped(self):
        out = {"gaps": [{"modelId": "acme-coder-1", "field": "tbHard", "reason": "not found"}]}
        suspicions = merge.validate_gaps(out)
        g = out["gaps"][0]
        self.assertEqual(len(out["gaps"]), 1)  # repaired, NOT stripped (MX1 guard)
        self.assertEqual(g["triedSources"], [merge.GAP_REPAIR_STUB_SOURCE])
        self.assertEqual(len(g["triedQueries"]), 2)
        self.assertEqual(set(g["_repaired"]), {"triedSources", "triedQueries", "triedFormats"})
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


class TestStampGapHistory(unittest.TestCase):
    """Fable-5 R2 (2026-07-11): gapHistoryAgent tracks only agent-sourced gap
    cycles, a subset of gapHistory (which tracks every gap regardless of
    source) — this is what lib.matrix's `chronic` classification reads."""

    def _entry(self):
        return {"gapHistory": [], "gapSince": None}

    def test_agent_source_appends_both_ledgers(self):
        entry = self._entry()
        merge._stamp_gap_history(entry, "2026-07-11", "agent")
        self.assertEqual(entry["gapHistory"], ["2026-07-11"])
        self.assertEqual(entry["gapHistoryAgent"], ["2026-07-11"])

    def test_orchestrator_source_only_appends_general_ledger(self):
        entry = self._entry()
        merge._stamp_gap_history(entry, "2026-07-11", "orchestrator")
        self.assertEqual(entry["gapHistory"], ["2026-07-11"])
        self.assertNotIn("gapHistoryAgent", entry)

    def test_default_source_is_agent(self):
        entry = self._entry()
        merge._stamp_gap_history(entry, "2026-07-11")
        self.assertEqual(entry.get("gapHistoryAgent"), ["2026-07-11"])

    def test_same_cycle_id_not_duplicated_in_either_ledger(self):
        entry = self._entry()
        merge._stamp_gap_history(entry, "2026-07-11", "agent")
        merge._stamp_gap_history(entry, "2026-07-11", "agent")
        self.assertEqual(entry["gapHistory"], ["2026-07-11"])
        self.assertEqual(entry["gapHistoryAgent"], ["2026-07-11"])


if __name__ == "__main__":
    result = unittest.main(verbosity=2, exit=False).result
    sys.exit(0 if result.wasSuccessful() else 1)
