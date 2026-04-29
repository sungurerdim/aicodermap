"""Minimal Draft-07 JSON Schema validator — stdlib only.

Supports: type, required, additionalProperties, properties, items,
          oneOf, pattern, minLength, minimum, maximum, enum.

Returns a list of error strings (empty = valid).
"""

from __future__ import annotations

import re
from typing import Any


def validate(instance: Any, schema: dict, path: str = "#") -> list[str]:
    errors: list[str] = []
    if not isinstance(schema, dict):
        return errors

    # type check
    if "type" in schema:
        expected = schema["type"]
        if not _check_type(instance, expected):
            errors.append(
                f"{path}: expected type '{expected}', got {type(instance).__name__}"
            )
            return errors  # further checks meaningless if type wrong

    # enum
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value not in enum {schema['enum']!r}")

    # string constraints
    if isinstance(instance, str):
        if "pattern" in schema:
            if not re.search(schema["pattern"], instance):
                errors.append(
                    f"{path}: value {instance!r} does not match pattern {schema['pattern']!r}"
                )
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(
                f"{path}: length {len(instance)} < minLength {schema['minLength']}"
            )

    # number constraints
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} > maximum {schema['maximum']}")

    # object constraints
    if isinstance(instance, dict):
        if "required" in schema:
            for req in schema["required"]:
                if req not in instance:
                    errors.append(f"{path}: missing required property '{req}'")

        props = schema.get("properties", {})
        for k, v in instance.items():
            if k in props:
                errors.extend(validate(v, props[k], f"{path}.{k}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected additional property '{k}'")

        # Validate declared properties even if not present (for required check above)
        for k, sub in props.items():
            if k in instance:
                errors.extend(validate(instance[k], sub, f"{path}.{k}"))

    # array constraints
    if isinstance(instance, list):
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(instance):
                errors.extend(validate(item, item_schema, f"{path}[{i}]"))

    # oneOf
    if "oneOf" in schema:
        matches = []
        for i, sub in enumerate(schema["oneOf"]):
            sub_errors = validate(instance, sub, f"{path}(oneOf[{i}])")
            if not sub_errors:
                matches.append(i)
        if len(matches) != 1:
            errors.append(
                f"{path}: oneOf matched {len(matches)} schema(s) (expected exactly 1); "
                f"value keys: {list(instance.keys()) if isinstance(instance, dict) else instance!r}"
            )

    return errors


def _check_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "null":
        return value is None
    return True
