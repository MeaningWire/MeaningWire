#!/usr/bin/env python3
"""Standards-compliant JSON Schema Draft 2020-12 validation for MeaningWire.

This validator complements, rather than replaces, the dependency-free bootstrap
validator in ``tools/validate_contracts.py``. MeaningWire schema URNs are
resolved only from ``schemas/registry.json``; this tool performs no remote
schema retrieval.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "schemas" / "registry.json"
FIXTURE_MANIFEST_PATH = ROOT / "tests" / "fixtures" / "manifest.json"

SCHEMA_BY_FIXTURE_KIND = {
    "envelope": "urn:meaningwire:schema:core:envelope:0.1.0",
    "mapping": "urn:meaningwire:schema:mapping:definition:0.1.0",
}


class StandardsValidationError(ValueError):
    """Raised when project schema or fixture validation fails."""


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_registry() -> tuple[Registry, dict[str, dict[str, Any]]]:
    """Build an in-memory Draft 2020-12 registry from public repo entries."""

    raw_registry = load_json(REGISTRY_PATH)
    entries = raw_registry.get("schemas")
    if not isinstance(entries, list) or not entries:
        raise StandardsValidationError("schema registry must contain schemas")

    registry = Registry()
    schemas: dict[str, dict[str, Any]] = {}
    seen_paths: set[str] = set()

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise StandardsValidationError(f"registry[{index}] must be an object")

        schema_id = entry.get("id")
        relative_path = entry.get("path")
        if not isinstance(schema_id, str) or not schema_id:
            raise StandardsValidationError(f"registry[{index}].id must be a non-empty string")
        if not isinstance(relative_path, str) or not relative_path:
            raise StandardsValidationError(f"registry[{index}].path must be a non-empty string")
        if schema_id in schemas:
            raise StandardsValidationError(f"duplicate schema id: {schema_id}")
        if relative_path in seen_paths:
            raise StandardsValidationError(f"duplicate schema path: {relative_path}")

        path = ROOT / relative_path
        if not path.is_file():
            raise StandardsValidationError(f"registered schema path does not exist: {relative_path}")

        schema = load_json(path)
        if not isinstance(schema, dict):
            raise StandardsValidationError(f"schema must be an object: {relative_path}")
        if schema.get("$id") != schema_id:
            raise StandardsValidationError(f"schema $id does not match registry: {relative_path}")

        try:
            Draft202012Validator.check_schema(schema)
        except Exception as exc:  # jsonschema exposes several schema error types
            raise StandardsValidationError(f"invalid Draft 2020-12 schema {relative_path}: {exc}") from exc

        registry = registry.with_resource(schema_id, DRAFT202012.create_resource(schema))
        schemas[schema_id] = schema
        seen_paths.add(relative_path)

    return registry, schemas


def validator_for(
    schema_id: str,
    registry: Registry,
    schemas: dict[str, dict[str, Any]],
) -> Draft202012Validator:
    schema = schemas.get(schema_id)
    if schema is None:
        raise StandardsValidationError(f"schema is not registered: {schema_id}")
    return Draft202012Validator(schema, registry=registry)


def validate_registered_schemas() -> int:
    _, schemas = build_registry()
    return len(schemas)


def validate_fixture_manifest() -> tuple[int, int]:
    registry, schemas = build_registry()
    manifest = load_json(FIXTURE_MANIFEST_PATH)
    entries = manifest.get("fixtures")
    if not isinstance(entries, list) or not entries:
        raise StandardsValidationError("fixture manifest must contain fixtures")

    valid_count = 0
    invalid_count = 0

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise StandardsValidationError(f"fixture[{index}] must be an object")

        kind = entry.get("kind")
        schema_id = SCHEMA_BY_FIXTURE_KIND.get(kind)
        if schema_id is None:
            raise StandardsValidationError(f"unknown fixture kind: {kind}")

        relative_path = entry.get("path")
        if not isinstance(relative_path, str) or not relative_path:
            raise StandardsValidationError(f"fixture[{index}].path must be a non-empty string")

        expected_valid = entry.get("valid")
        if not isinstance(expected_valid, bool):
            raise StandardsValidationError(f"fixture[{index}].valid must be boolean")

        instance = load_json(ROOT / relative_path)
        validator = validator_for(schema_id, registry, schemas)
        errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.absolute_path))

        if expected_valid:
            if errors:
                first = errors[0]
                raise StandardsValidationError(
                    f"{relative_path} unexpectedly failed Draft 2020-12 validation: {first.message}"
                )
            valid_count += 1
        else:
            if not errors:
                raise StandardsValidationError(
                    f"{relative_path} unexpectedly passed Draft 2020-12 validation"
                )
            invalid_count += 1

    return valid_count, invalid_count


def main() -> int:
    schema_count = validate_registered_schemas()
    valid_count, invalid_count = validate_fixture_manifest()
    print(
        "PASS: "
        f"{schema_count} Draft 2020-12 schemas validated and registered; "
        f"{valid_count} valid fixtures accepted; "
        f"{invalid_count} invalid fixtures rejected."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
