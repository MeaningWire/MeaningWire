#!/usr/bin/env python3
"""Conservative execution foundation for MeaningWire mappings.

This module intentionally executes only an explicit ``identity`` transform over
a value already selected by the caller. It does not traverse documents, parse
JSONPath, choose mappings, mutate inputs, contact remote services, or execute
arbitrary expressions/code.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import mapping_registry
import validate_contracts


class MappingExecutionError(ValueError):
    """Raised when a mapping cannot be executed by the current public engine."""


def _mapping_identity(mapping: dict[str, Any]) -> str:
    reference = mapping.get("mapping_id", {})
    namespace = reference.get("namespace", "<unknown-namespace>")
    identifier = reference.get("id", "<unknown-id>")
    version = reference.get("version", mapping.get("version", "<unknown-version>"))
    return f"{namespace}:{identifier}:{version}"


def execute_value(mapping: dict[str, Any], source_value: Any) -> dict[str, Any]:
    """Execute one mapping against one already-selected source value.

    Only ``transform.kind == 'identity'`` is executable in this foundation.
    The returned value is deep-copied so mutable inputs are never returned by
    reference. Unsupported or not-yet-implemented transform kinds fail closed.
    """

    try:
        validate_contracts.validate_mapping(mapping)
    except validate_contracts.ContractValidationError as exc:
        raise MappingExecutionError(f"mapping is invalid: {exc}") from exc

    transform = mapping.get("transform")
    if not isinstance(transform, dict):
        raise MappingExecutionError(
            f"mapping {_mapping_identity(mapping)} has no executable transform"
        )

    kind = transform.get("kind")
    if kind != "identity":
        raise MappingExecutionError(
            f"transform kind {kind!r} is not implemented; execution is fail-closed"
        )

    return {
        "mapping_id": deepcopy(mapping["mapping_id"]),
        "mapping_version": mapping["version"],
        "relationship": mapping["relationship"],
        "transform_kind": "identity",
        "value": deepcopy(source_value),
    }


def execute_registered_value(
    namespace: str,
    identifier: str,
    source_value: Any,
    *,
    version: str | None = None,
) -> dict[str, Any]:
    """Resolve exactly one registered mapping by identity and execute it."""

    mapping = mapping_registry.get_mapping(namespace, identifier, version)
    return execute_value(mapping, source_value)


def main() -> int:
    result = execute_registered_value(
        "urn:meaningwire:mapping",
        "example-crm-email",
        "person@example.invalid",
        version="0.1.0",
    )
    if result["value"] != "person@example.invalid":
        raise MappingExecutionError("identity smoke test changed the source value")
    print(
        "PASS: registered identity mapping executed deterministically; "
        "unimplemented transform kinds remain fail-closed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
