#!/usr/bin/env python3
"""Deterministic mapping application for a deliberately small member-path subset.

MeaningWire does not claim full JSONPath support here. This module accepts only
``$`` or dot-separated ASCII member shorthand such as ``$.email`` and
``$.contact.email``. It applies one explicit mapping to one source object and
uses the existing fail-closed mapping executor for transform behavior.
"""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

import mapping_executor
import validate_contracts

_MEMBER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class MappingApplicationError(ValueError):
    """Raised when a mapping path or application operation is invalid."""


def parse_simple_member_path(path: Any) -> tuple[str, ...]:
    """Parse MeaningWire's bounded simple-member path subset.

    Supported forms are ``$`` and ``$.name[.name...]`` where every name is an
    ASCII identifier. Rich JSONPath selectors are deliberately rejected.
    """

    if not isinstance(path, str) or not path:
        raise MappingApplicationError("mapping path must be a non-empty string")
    if path == "$":
        return ()
    if not path.startswith("$."):
        raise MappingApplicationError(
            "unsupported mapping path; expected '$' or '$.member[.member...]'"
        )
    parts = path[2:].split(".")
    if not parts or any(not _MEMBER.fullmatch(part) for part in parts):
        raise MappingApplicationError(
            "unsupported mapping path; only simple ASCII member shorthand is implemented"
        )
    return tuple(parts)


def get_value(source: Any, path: str) -> Any:
    """Read exactly one value from a source object using the bounded path subset."""

    parts = parse_simple_member_path(path)
    current = source
    if not parts:
        return deepcopy(current)
    for part in parts:
        if not isinstance(current, dict):
            raise MappingApplicationError(
                f"source path {path!r} crosses a non-object before member {part!r}"
            )
        if part not in current:
            raise MappingApplicationError(f"source path does not exist: {path}")
        current = current[part]
    return deepcopy(current)


def set_value(target: dict[str, Any], path: str, value: Any) -> dict[str, Any]:
    """Return a new object with one value written at an explicit target path."""

    if not isinstance(target, dict):
        raise MappingApplicationError("target root must be an object")
    parts = parse_simple_member_path(path)
    if not parts:
        if not isinstance(value, dict):
            raise MappingApplicationError("root target path '$' requires an object value")
        if target:
            raise MappingApplicationError("root target path '$' requires an empty target object")
        return deepcopy(value)

    result = deepcopy(target)
    current: dict[str, Any] = result
    for part in parts[:-1]:
        existing = current.get(part)
        if existing is None:
            child: dict[str, Any] = {}
            current[part] = child
            current = child
        elif isinstance(existing, dict):
            current = existing
        else:
            raise MappingApplicationError(
                f"target path {path!r} collides with non-object member {part!r}"
            )

    leaf = parts[-1]
    if leaf in current:
        raise MappingApplicationError(f"target path already contains a value: {path}")
    current[leaf] = deepcopy(value)
    return result


def apply_mapping(mapping: dict[str, Any], source_data: Any) -> dict[str, Any]:
    """Apply one explicit mapping to source data and return a fresh target object."""

    try:
        validate_contracts.validate_mapping(mapping)
    except validate_contracts.ContractValidationError as exc:
        raise MappingApplicationError(f"mapping is invalid: {exc}") from exc

    source_path = mapping["source"]["path"]
    target_path = mapping["target"]["path"]
    source_value = get_value(source_data, source_path)
    try:
        execution = mapping_executor.execute_value(mapping, source_value)
    except mapping_executor.MappingExecutionError as exc:
        raise MappingApplicationError(str(exc)) from exc

    target_data = set_value({}, target_path, execution["value"])
    return {
        "mapping_id": deepcopy(mapping["mapping_id"]),
        "mapping_version": mapping["version"],
        "relationship": mapping["relationship"],
        "source_path": source_path,
        "target_path": target_path,
        "transform_kind": execution["transform_kind"],
        "target_data": target_data,
    }


def main() -> int:
    import mapping_registry

    mapping = mapping_registry.get_mapping(
        "urn:meaningwire:mapping", "example-crm-email", "0.1.0"
    )
    result = apply_mapping(mapping, {"email": "person@example.invalid"})
    expected = {"contact": {"email": "person@example.invalid"}}
    if result["target_data"] != expected:
        raise MappingApplicationError("mapping application smoke result was unexpected")
    print("PASS: simple-member identity mapping applied deterministically.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
