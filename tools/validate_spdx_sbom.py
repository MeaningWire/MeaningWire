#!/usr/bin/env python3
"""Validate a MeaningWire candidate SBOM against official SPDX 2.3 and policy."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import fetch_spdx_schema
import validate_dependency_lock


class SPDXValidationError(ValueError):
    """Raised when an SPDX candidate document violates schema or project policy."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SPDXValidationError(f"cannot read JSON {path}: {exc}") from exc


def sha256_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise SPDXValidationError(f"cannot read {path}: {exc}") from exc


def validate_official_schema(sbom: dict[str, Any], schema_path: Path) -> str:
    try:
        import jsonschema
    except ModuleNotFoundError as exc:
        raise SPDXValidationError(
            "jsonschema is required; install requirements-validation.lock"
        ) from exc

    try:
        schema_bytes = schema_path.read_bytes()
    except OSError as exc:
        raise SPDXValidationError(f"cannot read SPDX schema {schema_path}: {exc}") from exc
    schema_sha256 = fetch_spdx_schema.verify_schema_bytes(schema_bytes)
    try:
        schema = json.loads(schema_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SPDXValidationError(f"pinned SPDX schema is not valid UTF-8 JSON: {exc}") from exc

    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(
        validator.iter_errors(sbom),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    if errors:
        first = errors[0]
        location = "$"
        for part in first.absolute_path:
            location += f"[{part}]" if isinstance(part, int) else f".{part}"
        raise SPDXValidationError(
            f"official SPDX 2.3 schema validation failed at {location}: {first.message}"
        )
    return schema_sha256


def package_by_id(sbom: dict[str, Any]) -> dict[str, dict[str, Any]]:
    packages = sbom.get("packages")
    if not isinstance(packages, list):
        raise SPDXValidationError("SBOM packages must be an array")
    result: dict[str, dict[str, Any]] = {}
    for package in packages:
        if not isinstance(package, dict) or not isinstance(package.get("SPDXID"), str):
            raise SPDXValidationError("each SBOM package must have a string SPDXID")
        spdx_id = package["SPDXID"]
        if spdx_id in result:
            raise SPDXValidationError(f"duplicate package SPDXID: {spdx_id}")
        result[spdx_id] = package
    return result


def checksum_values(package: dict[str, Any]) -> set[str]:
    values: set[str] = set()
    for checksum in package.get("checksums", []):
        if isinstance(checksum, dict) and checksum.get("algorithm") == "SHA256":
            value = checksum.get("checksumValue")
            if isinstance(value, str):
                values.add(value)
    return values


def validate_meaningwire_policy(
    sbom: dict[str, Any],
    release_evidence: dict[str, Any],
) -> dict[str, Any]:
    if sbom.get("spdxVersion") != "SPDX-2.3":
        raise SPDXValidationError("SBOM must explicitly declare SPDX-2.3")
    if sbom.get("dataLicense") != "CC0-1.0":
        raise SPDXValidationError("SPDX document dataLicense must be CC0-1.0")
    if sbom.get("SPDXID") != "SPDXRef-DOCUMENT":
        raise SPDXValidationError("SPDX document ID must be SPDXRef-DOCUMENT")

    version = release_evidence.get("version")
    source_commit = release_evidence.get("source_commit")
    archive_name = release_evidence.get("artifact")
    archive_sha256 = release_evidence.get("artifact_sha256")
    if not all(isinstance(value, str) and value for value in (version, source_commit, archive_name, archive_sha256)):
        raise SPDXValidationError("release evidence is missing candidate identity fields")

    expected_namespace = f"urn:meaningwire:spdx:release-candidate:{version}:{source_commit}"
    if sbom.get("documentNamespace") != expected_namespace:
        raise SPDXValidationError("SBOM documentNamespace does not bind the exact candidate")
    if sbom.get("documentDescribes") != ["SPDXRef-Package-MeaningWire"]:
        raise SPDXValidationError("SBOM must describe exactly the MeaningWire root package")

    packages = package_by_id(sbom)
    root = packages.get("SPDXRef-Package-MeaningWire")
    if root is None:
        raise SPDXValidationError("MeaningWire root package is missing")
    if root.get("name") != "MeaningWire" or root.get("versionInfo") != version:
        raise SPDXValidationError("MeaningWire root package name/version mismatch")
    if root.get("packageFileName") != archive_name:
        raise SPDXValidationError("MeaningWire root package archive name mismatch")
    if checksum_values(root) != {archive_sha256}:
        raise SPDXValidationError("MeaningWire root package SHA-256 does not match release evidence")
    if root.get("licenseConcluded") != "Apache-2.0" or root.get("licenseDeclared") != "Apache-2.0":
        raise SPDXValidationError("MeaningWire root package license must be Apache-2.0")
    if root.get("filesAnalyzed") is not False:
        raise SPDXValidationError("candidate SBOM must state filesAnalyzed=false for root package")

    _direct, locked = validate_dependency_lock.validate_static()
    expected_dependency_ids: dict[str, str] = {}
    for name in sorted(locked):
        spdx_id = "SPDXRef-Package-" + name
        expected_dependency_ids[spdx_id] = name
        package = packages.get(spdx_id)
        if package is None:
            raise SPDXValidationError(f"locked dependency missing from SBOM: {name}")
        locked_version, locked_hashes = locked[name]
        if package.get("name") != name or package.get("versionInfo") != locked_version:
            raise SPDXValidationError(f"locked dependency name/version mismatch: {name}")
        if checksum_values(package) != set(locked_hashes):
            raise SPDXValidationError(f"locked dependency checksum mismatch: {name}")
        if package.get("filesAnalyzed") is not False:
            raise SPDXValidationError(f"dependency must state filesAnalyzed=false: {name}")
        external_refs = package.get("externalRefs", [])
        expected_purl = f"pkg:pypi/{name}@{locked_version}"
        if not any(
            isinstance(ref, dict)
            and ref.get("referenceCategory") == "PACKAGE-MANAGER"
            and ref.get("referenceType") == "purl"
            and ref.get("referenceLocator") == expected_purl
            for ref in external_refs
        ):
            raise SPDXValidationError(f"locked dependency purl missing: {name}")

    expected_ids = {"SPDXRef-Package-MeaningWire", *expected_dependency_ids}
    if set(packages) != expected_ids:
        unexpected = sorted(set(packages) - expected_ids)
        missing = sorted(expected_ids - set(packages))
        raise SPDXValidationError(
            f"SBOM package scope mismatch; unexpected={unexpected}; missing={missing}"
        )

    relationships = sbom.get("relationships")
    if not isinstance(relationships, list):
        raise SPDXValidationError("SBOM relationships must be an array")
    actual_dependency_targets = {
        relationship.get("relatedSpdxElement")
        for relationship in relationships
        if isinstance(relationship, dict)
        and relationship.get("spdxElementId") == "SPDXRef-Package-MeaningWire"
        and relationship.get("relationshipType") == "DEPENDS_ON"
    }
    if actual_dependency_targets != set(expected_dependency_ids):
        raise SPDXValidationError("root DEPENDS_ON relationships do not match locked dependency set")

    return {
        "scope": "candidate archive plus governed validation dependency environment",
        "locked_dependency_count": len(locked),
        "package_count": len(packages),
        "relationship_count": len(relationships),
    }


def validation_evidence(
    *,
    sbom_path: Path,
    sbom_sha256: str,
    schema_sha256: str,
    policy: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "status": "PASS",
        "sbom": {
            "filename": sbom_path.name,
            "sha256": sbom_sha256,
            "format": "SPDX",
            "version": "2.3",
            "transitional": True,
        },
        "official_schema": {
            "repository": fetch_spdx_schema.SPDX_SPEC_REPOSITORY,
            "commit": fetch_spdx_schema.SPDX_SPEC_COMMIT,
            "path": fetch_spdx_schema.SPDX_SCHEMA_PATH,
            "git_blob_sha1": fetch_spdx_schema.SPDX_SCHEMA_BLOB_SHA1,
            "sha256": schema_sha256,
            "license": fetch_spdx_schema.SPDX_SCHEMA_LICENSE,
        },
        "project_policy": policy,
        "publication_performed": False,
        "attestation_performed": False,
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a MeaningWire candidate SBOM against official SPDX 2.3 and project policy"
    )
    parser.add_argument("sbom", help="candidate SPDX JSON path")
    parser.add_argument("--schema", required=True, help="verified official SPDX 2.3 schema path")
    parser.add_argument("--release-evidence", required=True, help="MeaningWire release-evidence.json path")
    parser.add_argument("--output-evidence", help="write deterministic SBOM validation evidence JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    sbom_path = Path(args.sbom)
    schema_path = Path(args.schema)
    release_evidence_path = Path(args.release_evidence)
    try:
        sbom = load_json(sbom_path)
        if not isinstance(sbom, dict):
            raise SPDXValidationError("SBOM root must be a JSON object")
        release_evidence = load_json(release_evidence_path)
        if not isinstance(release_evidence, dict):
            raise SPDXValidationError("release evidence root must be a JSON object")
        sbom_sha256 = sha256_file(sbom_path)
        expected_sbom = release_evidence.get("sbom")
        if not isinstance(expected_sbom, dict):
            raise SPDXValidationError("release evidence does not describe an SBOM")
        if expected_sbom.get("filename") != sbom_path.name or expected_sbom.get("sha256") != sbom_sha256:
            raise SPDXValidationError("SBOM identity does not match release evidence")
        schema_sha256 = validate_official_schema(sbom, schema_path)
        policy = validate_meaningwire_policy(sbom, release_evidence)
        evidence = validation_evidence(
            sbom_path=sbom_path,
            sbom_sha256=sbom_sha256,
            schema_sha256=schema_sha256,
            policy=policy,
        )
        if args.output_evidence:
            write_json(Path(args.output_evidence), evidence)
    except (
        SPDXValidationError,
        fetch_spdx_schema.SPDXSchemaFetchError,
        validate_dependency_lock.DependencyLockError,
        OSError,
    ) as exc:
        print(f"ERROR: {exc}")
        return 2

    print(
        "PASS: transitional SPDX 2.3 candidate SBOM validated against the exact "
        "official schema and MeaningWire scope policy; publication_performed=false."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
