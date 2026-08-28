#!/usr/bin/env python3
"""Dependency-free bootstrap validation for MeaningWire experimental contracts.

This validates the first semantic invariants and registry consistency.
It is not a complete JSON Schema Draft 2020-12 implementation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RELATIONSHIPS = {"exact", "equivalent", "broader", "narrower", "derived", "transformed", "lossy", "unsupported"}
MATURITY_STATES = {"DISCOVERED", "RESEARCH", "EVALUATED", "EXPERIMENTAL", "PREVIEW", "STABLE", "REJECTED", "SUPERSEDED", "DEPRECATED"}
AUTHORITY_KINDS = {"source_authority", "human_authority", "system_authority", "model_inference", "none"}
APPROVAL_STATES = {"approved", "rejected", "not_asserted"}


class ContractValidationError(ValueError):
    pass


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractValidationError(f"{label} must be an object")
    return value


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractValidationError(f"{label} must be a non-empty string")
    return value


def reject_extra(obj: dict[str, Any], allowed: set[str], label: str) -> None:
    extra = set(obj) - allowed
    if extra:
        raise ContractValidationError(f"{label} contains unsupported keys: {sorted(extra)}")


def validate_reference(value: Any, label: str = "reference") -> None:
    obj = require_object(value, label)
    reject_extra(obj, {"namespace", "id", "version"}, label)
    require_string(obj.get("namespace"), f"{label}.namespace")
    require_string(obj.get("id"), f"{label}.id")
    if "version" in obj:
        require_string(obj["version"], f"{label}.version")


def validate_authority(value: Any) -> None:
    obj = require_object(value, "authority")
    reject_extra(obj, {"kind", "actor", "scope", "approval", "basis", "confidence"}, "authority")
    kind, approval = obj.get("kind"), obj.get("approval")
    if kind not in AUTHORITY_KINDS:
        raise ContractValidationError("authority.kind is not recognized")
    if approval not in APPROVAL_STATES:
        raise ContractValidationError("authority.approval is not recognized")
    if kind != "human_authority" and approval != "not_asserted":
        raise ContractValidationError("non-human authority cannot assert approval")
    if kind == "human_authority" and "actor" not in obj:
        raise ContractValidationError("human authority requires actor")
    if "actor" in obj:
        validate_reference(obj["actor"], "authority.actor")
    if kind == "model_inference":
        confidence = obj.get("confidence")
        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
            raise ContractValidationError("model_inference requires numeric confidence")
        if not 0 <= float(confidence) <= 1:
            raise ContractValidationError("authority.confidence must be between 0 and 1")
    if "scope" in obj:
        scope = obj["scope"]
        if not isinstance(scope, list) or not scope:
            raise ContractValidationError("authority.scope must be a non-empty array when present")
        if any(not isinstance(item, str) or not item.strip() for item in scope) or len(scope) != len(set(scope)):
            raise ContractValidationError("authority.scope items must be non-empty and unique")
    if "basis" in obj:
        require_string(obj["basis"], "authority.basis")


def validate_provenance(value: Any) -> None:
    obj = require_object(value, "provenance")
    reject_extra(obj, {"source", "source_version", "observed_at", "transformations"}, "provenance")
    if "source" not in obj:
        raise ContractValidationError("provenance.source is required")
    validate_reference(obj["source"], "provenance.source")
    if "source_version" in obj:
        require_string(obj["source_version"], "provenance.source_version")
    if "observed_at" in obj:
        require_string(obj["observed_at"], "provenance.observed_at")
    transformations = obj.get("transformations", [])
    if not isinstance(transformations, list):
        raise ContractValidationError("provenance.transformations must be an array")
    for index, value in enumerate(transformations):
        tx = require_object(value, f"provenance.transformations[{index}]")
        reject_extra(tx, {"operation", "mapping", "performed_by", "performed_at", "notes"}, f"provenance.transformations[{index}]")
        require_string(tx.get("operation"), f"provenance.transformations[{index}].operation")
        if "mapping" in tx:
            validate_reference(tx["mapping"], f"provenance.transformations[{index}].mapping")
        if "performed_by" in tx:
            validate_reference(tx["performed_by"], f"provenance.transformations[{index}].performed_by")
        if "performed_at" in tx:
            require_string(tx["performed_at"], f"provenance.transformations[{index}].performed_at")


def validate_envelope(value: Any) -> None:
    obj = require_object(value, "envelope")
    allowed = {"contract", "record", "data", "provenance", "authority", "maturity"}
    reject_extra(obj, allowed, "envelope")
    missing = allowed - set(obj)
    if missing:
        raise ContractValidationError(f"envelope missing required keys: {sorted(missing)}")
    validate_reference(obj["contract"], "envelope.contract")
    validate_reference(obj["record"], "envelope.record")
    require_object(obj["data"], "envelope.data")
    validate_provenance(obj["provenance"])
    validate_authority(obj["authority"])
    if obj["maturity"] not in MATURITY_STATES:
        raise ContractValidationError("envelope.maturity is not recognized")


def validate_endpoint(value: Any, label: str) -> None:
    obj = require_object(value, label)
    reject_extra(obj, {"contract", "path"}, label)
    if "contract" not in obj or "path" not in obj:
        raise ContractValidationError(f"{label} requires contract and path")
    validate_reference(obj["contract"], f"{label}.contract")
    require_string(obj["path"], f"{label}.path")


def validate_mapping(value: Any) -> None:
    obj = require_object(value, "mapping")
    allowed = {"mapping_id", "version", "source", "target", "relationship", "transform", "loss_notes", "maturity", "provenance"}
    reject_extra(obj, allowed, "mapping")
    required = {"mapping_id", "version", "source", "target", "relationship", "maturity", "provenance"}
    missing = required - set(obj)
    if missing:
        raise ContractValidationError(f"mapping missing required keys: {sorted(missing)}")
    validate_reference(obj["mapping_id"], "mapping.mapping_id")
    require_string(obj["version"], "mapping.version")
    validate_endpoint(obj["source"], "mapping.source")
    validate_endpoint(obj["target"], "mapping.target")
    if obj["relationship"] not in RELATIONSHIPS:
        raise ContractValidationError("mapping.relationship is not recognized")
    if obj["relationship"] == "lossy" and not (isinstance(obj.get("loss_notes"), str) and obj["loss_notes"].strip()):
        raise ContractValidationError("lossy mapping requires loss_notes")
    if obj["maturity"] not in MATURITY_STATES:
        raise ContractValidationError("mapping.maturity is not recognized")
    if "transform" in obj:
        transform = require_object(obj["transform"], "mapping.transform")
        reject_extra(transform, {"kind", "description"}, "mapping.transform")
        if transform.get("kind") not in {"identity", "expression", "lookup", "code", "manual"}:
            raise ContractValidationError("mapping.transform.kind is not recognized")
        if "description" in transform:
            require_string(transform["description"], "mapping.transform.description")
    validate_provenance(obj["provenance"])


def validate_registry() -> int:
    registry = require_object(load_json(ROOT / "schemas" / "registry.json"), "schema registry")
    entries = registry.get("schemas")
    if not isinstance(entries, list) or not entries:
        raise ContractValidationError("schema registry must contain schemas")
    seen_ids, seen_paths = set(), set()
    for index, entry_value in enumerate(entries):
        entry = require_object(entry_value, f"registry[{index}]")
        schema_id = require_string(entry.get("id"), f"registry[{index}].id")
        relative_path = require_string(entry.get("path"), f"registry[{index}].path")
        version = require_string(entry.get("version"), f"registry[{index}].version")
        if schema_id in seen_ids or relative_path in seen_paths:
            raise ContractValidationError("schema registry IDs and paths must be unique")
        seen_ids.add(schema_id); seen_paths.add(relative_path)
        path = ROOT / relative_path
        if not path.is_file():
            raise ContractValidationError(f"registered schema path does not exist: {relative_path}")
        schema = require_object(load_json(path), f"schema {relative_path}")
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            raise ContractValidationError(f"{relative_path} must declare JSON Schema Draft 2020-12")
        if schema.get("$id") != schema_id:
            raise ContractValidationError(f"{relative_path} $id does not match registry")
        if schema.get("x-meaningwire-contract-version") != version:
            raise ContractValidationError(f"{relative_path} version does not match registry")
        if schema.get("x-meaningwire-maturity") != "EXPERIMENTAL":
            raise ContractValidationError(f"{relative_path} must be marked EXPERIMENTAL")
    return len(entries)


def validate_fixture_manifest() -> tuple[int, int]:
    manifest = load_json(ROOT / "tests" / "fixtures" / "manifest.json")
    entries = manifest.get("fixtures", [])
    if not isinstance(entries, list) or not entries:
        raise ContractValidationError("fixture manifest must contain fixtures")
    validators = {"envelope": validate_envelope, "mapping": validate_mapping}
    valid_count = invalid_count = 0
    for entry in entries:
        validator = validators.get(entry["kind"])
        if validator is None:
            raise ContractValidationError(f"unknown fixture kind: {entry['kind']}")
        value = load_json(ROOT / entry["path"])
        try:
            validator(value)
        except ContractValidationError as exc:
            if entry["valid"]:
                raise ContractValidationError(f"{entry['path']} unexpectedly failed: {exc}") from exc
            if entry.get("error_contains") and entry["error_contains"] not in str(exc):
                raise ContractValidationError(f"{entry['path']} failed for unexpected reason: {exc}") from exc
            invalid_count += 1
        else:
            if not entry["valid"]:
                raise ContractValidationError(f"{entry['path']} unexpectedly passed")
            valid_count += 1
    return valid_count, invalid_count


def main() -> int:
    schema_count = validate_registry()
    valid_count, invalid_count = validate_fixture_manifest()
    print(f"PASS: {schema_count} schemas registered; {valid_count} valid fixtures accepted; {invalid_count} invalid fixtures rejected as expected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
