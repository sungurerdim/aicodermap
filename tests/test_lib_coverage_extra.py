#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for zero-coverage lib modules (TEST-02 B7, 2026-06-14):
changelog, jsonschema_min, id_remap.

Stdlib unittest only (matches the rest of the project's test convention).

Run:
    python tests/test_lib_coverage_extra.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))

from lib.changelog import render_changelog_markdown  # noqa: E402
from lib.jsonschema_min import validate  # noqa: E402
from lib.id_remap import build_remap_table, fix_id, apply_remap_to_observations  # noqa: E402


# ── changelog ────────────────────────────────────────────────────────────────


class TestRenderChangelogMarkdown(unittest.TestCase):
    def _base_log(self, **overrides):
        base = {
            "added": [],
            "updated": [],
            "lineup_deprecated": [],
            "lineup_renamed": [],
            "contradictions": [],
        }
        base.update(overrides)
        return base

    def _base_out(self, **overrides):
        base: dict = {}
        base.update(overrides)
        return base

    def test_header_contains_date(self):
        result = render_changelog_markdown(
            self._base_log(),
            self._base_out(),
            metadata_row="78 models | 68.1% coverage",
            coverage_warn="",
            partial_info="",
            today="2026-06-14",
        )
        self.assertIn("## [2026-06-14]", result)
        self.assertIn("autonomous refresh-all", result)

    def test_metadata_row_present(self):
        result = render_changelog_markdown(
            self._base_log(),
            self._base_out(),
            metadata_row="78 models | 68.1% coverage",
            coverage_warn="",
            partial_info="",
            today="2026-06-14",
        )
        self.assertIn("78 models | 68.1% coverage", result)

    def test_added_models_listed(self):
        log = self._base_log(added=["qwen3-235b-a22b", "gemini-2-5-pro"])
        result = render_changelog_markdown(
            log,
            self._base_out(),
            metadata_row="80 models",
            coverage_warn="",
            partial_info="",
            today="2026-06-14",
        )
        self.assertIn("### Added", result)
        self.assertIn("`qwen3-235b-a22b`", result)
        self.assertIn("`gemini-2-5-pro`", result)
        self.assertIn("new model from vendor lineup discovery", result)

    def test_updated_models_count_and_names(self):
        log = self._base_log(updated=["claude-opus-4", "gpt-5", "deepseek-v4-pro"])
        result = render_changelog_markdown(
            log,
            self._base_out(),
            metadata_row="80 models",
            coverage_warn="",
            partial_info="",
            today="2026-06-14",
        )
        self.assertIn("### Updated", result)
        self.assertIn("3 models", result)
        self.assertIn("`claude-opus-4`", result)

    def test_deprecated_models_listed(self):
        log = self._base_log(lineup_deprecated=["gpt-4-turbo"])
        result = render_changelog_markdown(
            log,
            self._base_out(),
            metadata_row="79 models",
            coverage_warn="",
            partial_info="",
            today="2026-06-14",
        )
        self.assertIn("### Deprecated", result)
        self.assertIn("`gpt-4-turbo`", result)
        self.assertIn("vendor-marked deprecated", result)

    def test_renamed_models_listed(self):
        log = self._base_log(lineup_renamed=["kimi-k2 -> kimi-k2-6"])
        result = render_changelog_markdown(
            log,
            self._base_out(),
            metadata_row="79 models",
            coverage_warn="",
            partial_info="",
            today="2026-06-14",
        )
        self.assertIn("### Renamed", result)
        self.assertIn("kimi-k2 -> kimi-k2-6", result)

    def test_contradictions_section(self):
        log = self._base_log(contradictions=["deepseek-v3-2.sweV: 83.3 -> 74.2"])
        result = render_changelog_markdown(
            log,
            self._base_out(),
            metadata_row="79 models",
            coverage_warn="",
            partial_info="",
            today="2026-06-14",
        )
        self.assertIn("### Resolved", result)
        self.assertIn("deepseek-v3-2.sweV", result)

    def test_gaps_agent_and_orchestrator_split(self):
        gaps = [
            {"key": "qwen3-32b.hle", "reason": "fetch timeout", "source": "agent"},
            {"key": "qwen3-32b.lcb", "reason": "fetch timeout", "source": "agent"},
            {"key": "gpt-5.sweV", "reason": "not reached", "source": "orchestrator"},
        ]
        result = render_changelog_markdown(
            self._base_log(),
            {"gaps": gaps},
            metadata_row="78 models",
            coverage_warn=" — WARN: coverage 60%",
            partial_info="",
            today="2026-06-14",
        )
        self.assertIn("### Gaps", result)
        self.assertIn("agent:2", result)
        self.assertIn("orchestrator:1", result)
        self.assertIn("*(agent)*", result)
        self.assertIn("*(orchestrator)*", result)

    def test_empty_log_no_sections(self):
        result = render_changelog_markdown(
            self._base_log(),
            self._base_out(),
            metadata_row="78 models",
            coverage_warn="",
            partial_info="",
            today="2026-06-14",
        )
        self.assertNotIn("### Added", result)
        self.assertNotIn("### Updated", result)
        self.assertNotIn("### Deprecated", result)
        self.assertNotIn("### Gaps", result)

    def test_gaps_overflow_shows_ellipsis(self):
        # 8 agent gaps: only first 6 shown + ellipsis
        gaps = [
            {"key": f"model-{i}.hle", "reason": "timeout", "source": "agent"}
            for i in range(8)
        ]
        result = render_changelog_markdown(
            self._base_log(),
            {"gaps": gaps},
            metadata_row="78 models",
            coverage_warn="",
            partial_info="",
            today="2026-06-14",
        )
        self.assertIn("... and 2 more", result)


# ── jsonschema_min ────────────────────────────────────────────────────────────


class TestJsonSchemaMinValidator(unittest.TestCase):
    def test_valid_doc_returns_no_errors(self):
        schema = {
            "type": "object",
            "required": ["id", "score"],
            "properties": {
                "id": {"type": "string"},
                "score": {"type": "number", "minimum": 0, "maximum": 100},
            },
        }
        errors = validate({"id": "claude-opus-4", "score": 82.5}, schema)
        self.assertEqual(errors, [])

    def test_wrong_type_top_level(self):
        schema = {"type": "object"}
        errors = validate(["not", "an", "object"], schema)
        self.assertTrue(any("expected type 'object'" in e for e in errors))

    def test_missing_required_property(self):
        schema = {
            "type": "object",
            "required": ["id", "score"],
            "properties": {
                "id": {"type": "string"},
                "score": {"type": "number"},
            },
        }
        errors = validate({"id": "deepseek-v4-pro"}, schema)
        self.assertTrue(any("missing required property 'score'" in e for e in errors))

    def test_pattern_mismatch(self):
        schema = {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"}
        errors = validate("not-a-date", schema)
        self.assertTrue(any("does not match pattern" in e for e in errors))

    def test_pattern_match_passes(self):
        schema = {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"}
        errors = validate("2026-06-14", schema)
        self.assertEqual(errors, [])

    def test_additional_properties_false(self):
        schema = {
            "type": "object",
            "properties": {"id": {"type": "string"}},
            "additionalProperties": False,
        }
        errors = validate({"id": "gpt-5", "extra": "not allowed"}, schema)
        self.assertTrue(
            any("unexpected additional property 'extra'" in e for e in errors)
        )

    def test_additional_properties_allowed_by_default(self):
        schema = {
            "type": "object",
            "properties": {"id": {"type": "string"}},
        }
        errors = validate({"id": "gpt-5", "extra": "allowed"}, schema)
        self.assertEqual(errors, [])

    def test_one_of_exactly_one_matches(self):
        schema = {
            "oneOf": [
                {"type": "string"},
                {"type": "integer"},
            ]
        }
        self.assertEqual(validate("claude-sonnet-4-6", schema), [])
        self.assertEqual(validate(42, schema), [])

    def test_one_of_no_match_is_error(self):
        schema = {
            "oneOf": [
                {"type": "string"},
                {"type": "integer"},
            ]
        }
        errors = validate(3.14, schema)
        self.assertTrue(any("oneOf matched 0" in e for e in errors))

    def test_one_of_multiple_matches_is_error(self):
        # Both string sub-schemas match "hello" — but with distinct required
        # fields they won't both match. Use overlapping type schemas instead.
        schema = {
            "oneOf": [
                {"type": "number"},
                {"type": "number", "minimum": 0},
            ]
        }
        # 5 matches both branches
        errors = validate(5, schema)
        self.assertTrue(any("oneOf matched 2" in e for e in errors))

    def test_minimum_maximum_constraint(self):
        schema = {"type": "number", "minimum": 0, "maximum": 100}
        self.assertEqual(validate(50.0, schema), [])
        errors_low = validate(-1, schema)
        self.assertTrue(any("minimum" in e for e in errors_low))
        errors_high = validate(101, schema)
        self.assertTrue(any("maximum" in e for e in errors_high))

    def test_min_length_constraint(self):
        schema = {"type": "string", "minLength": 3}
        self.assertEqual(validate("abc", schema), [])
        errors = validate("ab", schema)
        self.assertTrue(any("minLength" in e for e in errors))

    def test_enum_constraint(self):
        schema = {"type": "string", "enum": ["I", "S", "C", "U"]}
        self.assertEqual(validate("I", schema), [])
        errors = validate("X", schema)
        self.assertTrue(any("not in enum" in e for e in errors))

    def test_array_items_validated(self):
        schema = {
            "type": "array",
            "items": {"type": "number", "minimum": 0},
        }
        self.assertEqual(validate([1.0, 2.5, 99.9], schema), [])
        errors = validate([1.0, -5.0], schema)
        self.assertTrue(any("minimum" in e for e in errors))

    def test_nested_object_property_type(self):
        schema = {
            "type": "object",
            "properties": {
                "meta": {
                    "type": "object",
                    "properties": {"version": {"type": "integer"}},
                }
            },
        }
        errors = validate({"meta": {"version": "not-an-int"}}, schema)
        self.assertTrue(any("expected type 'integer'" in e for e in errors))


# ── id_remap ─────────────────────────────────────────────────────────────────


class TestBuildRemapTable(unittest.TestCase):
    def _write_cache(self, data: dict) -> Path:
        """Write a JSON lineup cache to a temp file and return its Path."""
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        )
        json.dump(data, tmp)
        tmp.close()
        return Path(tmp.name)

    def test_empty_cache_returns_empty_table(self):
        p = self._write_cache({})
        remap = build_remap_table(cache_path=p)
        self.assertEqual(remap, {})

    def test_vendor_shape_renamed_entry(self):
        data = {
            "anthropic": {
                "renamed": [{"from": "claude-opus-4-5", "to": "claude-opus-4"}],
                "discarded": [],
            }
        }
        p = self._write_cache(data)
        remap = build_remap_table(cache_path=p)
        self.assertEqual(remap.get("claude-opus-4-5"), "claude-opus-4")

    def test_vendor_shape_discarded_entry(self):
        data = {
            "openai": {
                "renamed": [],
                "discarded": ["gpt-5-rumour"],
            }
        }
        p = self._write_cache(data)
        remap = build_remap_table(cache_path=p)
        self.assertIsNone(remap.get("gpt-5-rumour"))
        self.assertIn("gpt-5-rumour", remap)

    def test_flat_renamed_array_shape(self):
        data = {
            "renamed": [
                {"from": "kimi-k2", "to": "kimi-k2-6"},
            ]
        }
        p = self._write_cache(data)
        remap = build_remap_table(cache_path=p)
        self.assertEqual(remap.get("kimi-k2"), "kimi-k2-6")

    def test_missing_cache_returns_empty_table(self):
        remap = build_remap_table(cache_path="/nonexistent/path/lineup.json")
        self.assertEqual(remap, {})

    def test_malformed_cache_returns_empty_table(self):
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        )
        tmp.write("not valid json {{{{")
        tmp.close()
        remap = build_remap_table(cache_path=Path(tmp.name))
        self.assertEqual(remap, {})


class TestFixId(unittest.TestCase):
    def test_unknown_id_returned_unchanged(self):
        remap = {"kimi-k2": "kimi-k2-6"}
        self.assertEqual(fix_id("qwen3-235b-a22b", remap), "qwen3-235b-a22b")

    def test_renamed_id_resolved(self):
        remap = {"kimi-k2": "kimi-k2-6"}
        self.assertEqual(fix_id("kimi-k2", remap), "kimi-k2-6")

    def test_discarded_id_returns_none(self):
        remap = {"gpt-5-rumour": None}
        self.assertIsNone(fix_id("gpt-5-rumour", remap))

    def test_no_remap_table_uses_empty_fallback(self):
        # build_remap_table() returns {} when no cache exists on disk;
        # fix_id with remap={} must return the id unchanged.
        result = fix_id("claude-sonnet-4-6", {})
        self.assertEqual(result, "claude-sonnet-4-6")


class TestApplyRemapToObservations(unittest.TestCase):
    def test_renamed_id_rewritten_in_obs(self):
        remap = {"kimi-k2": "kimi-k2-6"}
        obs = [{"modelId": "kimi-k2", "value": 72.3}]
        out = apply_remap_to_observations(obs, remap)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["modelId"], "kimi-k2-6")

    def test_discarded_id_dropped(self):
        remap = {"gpt-5-rumour": None}
        obs = [
            {"modelId": "gpt-5-rumour", "value": 90.0},
            {"modelId": "claude-opus-4", "value": 80.0},
        ]
        out = apply_remap_to_observations(obs, remap)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["modelId"], "claude-opus-4")

    def test_unchanged_ids_pass_through(self):
        remap: dict = {}
        obs = [
            {"modelId": "deepseek-v4-pro", "value": 65.1},
            {"modelId": "gemini-2-5-pro", "value": 71.4},
        ]
        out = apply_remap_to_observations(obs, remap)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]["modelId"], "deepseek-v4-pro")

    def test_original_obs_dict_not_mutated(self):
        remap = {"kimi-k2": "kimi-k2-6"}
        original = {"modelId": "kimi-k2", "value": 72.3}
        obs = [original]
        apply_remap_to_observations(obs, remap)
        # The original dict must be unchanged
        self.assertEqual(original["modelId"], "kimi-k2")


if __name__ == "__main__":
    unittest.main()
