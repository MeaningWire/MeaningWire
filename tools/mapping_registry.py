#!/usr/bin/env python3
"""Deterministic, dependency-free registry behavior for MeaningWire mappings.

The registry discovers and selects mapping definitions. It deliberately does not
execute transforms. Broad queries may return multiple candidates; callers must
make ambiguity explicit instead of relying on an implicit "best" mapping.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import validate_contracts

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "mappings" / "registry.json"
DEFINITIONS_ROOT = (ROOT / "mappings" / "definitions").resolve()


class MappingRegistryError(ValueError):
    """Raised when registry structure, integrity, or selection is invalid."""


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MappingRegistryError(f"{label} must be a non-empty string")
    return value


def reference_key(value: Any, label: str, *, require_version: bool = False) -> tuple[str, str, str]:
    if not isinstance(value, dict):
        raise MappingRegistryError(f"{label} must be an object")
    extra = set(value) - {"namespace", "id", "version"}
    if extra:
        raise MappingRegistryError(f"{label} contains unsupported keys: {sorted(extra)}")
    namespace = require_string(value.get("namespace"), f"{label}.namespace")
    identifier = require_string(value.get("id"), f"{label}.id")
    raw_version = value.get("version")
    if raw_version is None:
        if require_version:
            raise MappingRegistryError(f"{label}.version is required")
        version = ""
    else:
        version = require_string(raw_version, f"{label}.version")
    return namespace, identifier, version


def resolve_definition_path(relative_path: str) -> Path:
    path_text = require_string(relative_path, "mapping.path")
    path = Path(path_text)
    if path.is_absolute():
        raise MappingRegistryError("mapping.path must be repository-relative")
    candidate = (ROOT / path).resolve()
    try:
        candidate.relative_to(DEFINITIONS_ROOT)
    except ValueError as exc:
        raise MappingRegistryError("mapping.path must stay under mappings/definitions") from exc
    if not candidate.is_file():
        raise MappingRegistryError(f"registered mapping path does not exist: {path_text}")
    return candidate


def _record_sort_key(record: dict[str, Any]) -> tuple[str, str, str]:
    return reference_key(record["mapping"]["mapping_id"], "mapping.mapping_id", require_version=True)


def load_records() -> list[dict[str, Any]]:
    """Load, integrity-check, and deterministically order registered mappings."""

    registry = load_json(REGISTRY_PATH)
    if not isinstance(registry, dict):
        raise MappingRegistryError("mapping registry must be an object")
    extra = set(registry) - {"registry_version", "maturity", "mappings"}
    if extra:
        raise MappingRegistryError(f"mapping registry contains unsupported keys: {sorted(extra)}")
    require_string(registry.get("registry_version"), "registry.registry_version")
    require_string(registry.get("maturity"), "registry.maturity")

    entries = registry.get("mappings")
    if not isinstance(entries, list) or not entries:
        raise MappingRegistryError("mapping registry must contain mappings")

    records: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str, str]] = set()
    seen_paths: set[str] = set()

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise MappingRegistryError(f"registry.mappings[{index}] must be an object")
        extra = set(entry) - {"mapping_id", "version", "path"}
        if extra:
            raise MappingRegistryError(
                f"registry.mappings[{index}] contains unsupported keys: {sorted(extra)}"
            )

        entry_key = reference_key(
            entry.get("mapping_id"),
            f"registry.mappings[{index}].mapping_id",
            require_version=True,
        )
        version = require_string(entry.get("version"), f"registry.mappings[{index}].version")
        if entry_key[2] != version:
            raise MappingRegistryError(
                f"registry.mappings[{index}] mapping_id.version must equal version"
            )
        if entry_key in seen_keys:
            raise MappingRegistryError(f"duplicate mapping identity: {entry_key}")

        relative_path = require_string(entry.get("path"), f"registry.mappings[{index}].path")
        if relative_path in seen_paths:
            raise MappingRegistryError(f"duplicate mapping path: {relative_path}")
        definition_path = resolve_definition_path(relative_path)
        mapping = load_json(definition_path)

        try:
            validate_contracts.validate_mapping(mapping)
        except validate_contracts.ContractValidationError as exc:
            raise MappingRegistryError(f"invalid mapping {relative_path}: {exc}") from exc

        document_key = reference_key(mapping.get("mapping_id"), "mapping.mapping_id", require_version=True)
        document_version = require_string(mapping.get("version"), "mapping.version")
        if document_key != entry_key or document_version != version:
            raise MappingRegistryError(
                f"registry identity does not match mapping document: {relative_path}"
            )

        records.append({"path": relative_path, "mapping": mapping})
        seen_keys.add(entry_key)
        seen_paths.add(relative_path)

    return sorted(records, key=_record_sort_key)


def list_mappings() -> list[dict[str, Any]]:
    """Return all registered mapping documents in deterministic identity order."""

    return [record["mapping"] for record in load_records()]


def _reference_matches(actual: Any, expected: dict[str, str] | None) -> bool:
    if expected is None:
        return True
    actual_key = reference_key(actual, "mapping contract")
    expected_key = reference_key(expected, "query contract")
    for index, value in enumerate(expected_key):
        if value and actual_key[index] != value:
            return False
    return True


def find_mappings(
    *,
    source_contract: dict[str, str] | None = None,
    target_contract: dict[str, str] | None = None,
    source_path: str | None = None,
    target_path: str | None = None,
    relationship: str | None = None,
    maturity: str | None = None,
) -> list[dict[str, Any]]:
    """Return deterministic candidate mappings matching all supplied filters."""

    candidates: list[dict[str, Any]] = []
    for mapping in list_mappings():
        if not _reference_matches(mapping["source"]["contract"], source_contract):
            continue
        if not _reference_matches(mapping["target"]["contract"], target_contract):
            continue
        if source_path is not None and mapping["source"]["path"] != source_path:
            continue
        if target_path is not None and mapping["target"]["path"] != target_path:
            continue
        if relationship is not None and mapping["relationship"] != relationship:
            continue
        if maturity is not None and mapping["maturity"] != maturity:
            continue
        candidates.append(mapping)
    return candidates


def require_unique(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Return one candidate or fail explicitly on absence/ambiguity."""

    if not candidates:
        raise MappingRegistryError("no mapping matches the requested criteria")
    if len(candidates) > 1:
        identities = [reference_key(item["mapping_id"], "mapping.mapping_id", require_version=True) for item in candidates]
        raise MappingRegistryError(f"mapping selection is ambiguous: {identities}")
    return candidates[0]


def select_unique(**filters: Any) -> dict[str, Any]:
    """Find and require exactly one mapping for the supplied filters."""

    return require_unique(find_mappings(**filters))


def get_mapping(namespace: str, identifier: str, version: str | None = None) -> dict[str, Any]:
    """Resolve a mapping by identity; omitting version is allowed only if unique."""

    namespace = require_string(namespace, "namespace")
    identifier = require_string(identifier, "identifier")
    candidates = []
    for mapping in list_mappings():
        mapping_namespace, mapping_identifier, mapping_version = reference_key(
            mapping["mapping_id"], "mapping.mapping_id", require_version=True
        )
        if mapping_namespace != namespace or mapping_identifier != identifier:
            continue
        if version is not None and mapping_version != version:
            continue
        candidates.append(mapping)
    return require_unique(candidates)


def main() -> int:
    records = load_records()
    print(f"PASS: {len(records)} mappings registered with deterministic lookup and explicit ambiguity handling.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
