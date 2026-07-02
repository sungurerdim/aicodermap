#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for zero-coverage lib modules (TEST-02 B7, 2026-06-14):
changelog, jsonschema_min.

Stdlib unittest only (matches the rest of the project's test convention).

Run:
    python tests/test_lib_coverage_extra.py
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "scripts"))

from lib.changelog import render_changelog_markdown  # noqa: E402
from lib.jsonschema_min import validate  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
