#!/usr/bin/env python3
"""Evaluate MeaningWire release readiness without publishing anything.

The gate consumes a verified candidate evidence directory and the candidate archive.
It separates mechanical release-threshold evidence from launch-experience and
publication-path readiness. It can report READY_FOR_HUMAN_DECISION, but it can
never authorize or perform publication.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tarfile
from pathlib import Path
from typing import Any

import fetch_spdx_schema

PROJECT = "MeaningWire"
READY = "READY_FOR_HUMAN_DECISION"
BLOCKED = "BLOCKED"
PUBLICATION_WORKFLOW = ".github/workflows/release-publication.yml"
_REQUIRED_ARCHIVE_PATHS = (
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "ROADMAP.md",
    "requirements-validation.lock",
    "docs/quickstart.md",
    "docs/releases/compatibility-and-migrations.md",
    "docs/releases/candidate-sbom.md",
    "docs/releases/release-readiness.md",
    "docs/releases/release-notes-template.md",
    "docs/architecture/public-implementation-boundary.md",
    "docs/architecture/release-agent-foundation.md",
    "docs/architecture/supply-chain-evidence.md",
    "tools/meaningwire.py",
    "tools/release_builder.py",
    "tools/release_readiness.py",
    "schemas/registry.json",
    "mappings/registry.json",
    "adapters/reference/json_object.py",
    "adapters/reference/json_lines.py",
    "tests/fixtures/proofs/json-object-crm-email-target.json",
)
_SEMVER_PRERELEASE_RE = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)-"
    r"[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
_SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA64_RE = re.compile(r"^[0-9a-f]{64}$")


class ReleaseReadinessError(ValueError):
    """Raised when candidate evidence cannot be evaluated safely."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseReadinessError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReleaseReadinessError(f"JSON root must be an object: {path}")
    return value


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise ReleaseReadinessError(f"cannot hash {path}: {exc}") from exc


def _parse_checksums(path: Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ReleaseReadinessError(f"cannot read {path}: {exc}") from exc
    result: dict[str, str] = {}
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  ([^/\\]+)", line)
        if not match:
            raise ReleaseReadinessError(
                f"invalid SHA256SUMS line {line_number}: {line!r}"
            )
        digest, filename = match.groups()
        if filename in result:
            raise ReleaseReadinessError(f"duplicate SHA256SUMS filename: {filename}")
        result[filename] = digest
    if not result:
        raise ReleaseReadinessError("SHA256SUMS contains no entries")
    return result


def _archive_files(archive_path: Path, version: str) -> dict[str, bytes]:
    prefix = f"{PROJECT}-{version}/"
    files: dict[str, bytes] = {}
    try:
        with tarfile.open(archive_path, "r:gz") as archive:
            for member in archive.getmembers():
                if not member.isfile():
                    continue
                if not member.name.startswith(prefix):
                    raise ReleaseReadinessError(
                        f"candidate archive member is outside expected prefix: {member.name}"
                    )
                relative = member.name[len(prefix) :]
                if not relative or relative.startswith("/") or ".." in Path(relative).parts:
                    raise ReleaseReadinessError(
                        f"unsafe candidate archive member: {member.name}"
                    )
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise ReleaseReadinessError(
                        f"could not read candidate archive member: {member.name}"
                    )
                files[relative] = extracted.read()
    except (OSError, tarfile.TarError) as exc:
        raise ReleaseReadinessError(f"cannot inspect candidate archive: {exc}") from exc
    if not files:
        raise ReleaseReadinessError("candidate archive contains no regular files")
    return files


def _json_from_bytes(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReleaseReadinessError(f"cannot parse {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReleaseReadinessError(f"{label} root must be an object")
    return value


def _check(name: str, passed: bool, detail: str) -> dict[str, Any]:
    return {"name": name, "status": "PASS" if passed else "FAIL", "detail": detail}


def _expected_spdx_schema_identity() -> dict[str, str]:
    return {
        "repository": fetch_spdx_schema.SPDX_SPEC_REPOSITORY,
        "commit": fetch_spdx_schema.SPDX_SPEC_COMMIT,
        "path": fetch_spdx_schema.SPDX_SCHEMA_PATH,
        "git_blob_sha1": fetch_spdx_schema.SPDX_SCHEMA_BLOB_SHA1,
    }


def _schema_identity_matches(value: Any) -> bool:
    return isinstance(value, dict) and all(
        value.get(key) == expected
        for key, expected in _expected_spdx_schema_identity().items()
    )


def _detect_documentation_site(files: dict[str, bytes]) -> tuple[bool, str]:
    package_json_paths = sorted(path for path in files if path.endswith("package.json"))
    lock_paths = {path for path in files if path.endswith("package-lock.json")}
    astro_config_paths = {
        path
        for path in files
        if path.endswith("astro.config.mjs")
        or path.endswith("astro.config.ts")
        or path.endswith("astro.config.js")
    }
    for package_path in package_json_paths:
        try:
            package = json.loads(files[package_path].decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(package, dict):
            continue
        dependencies: dict[str, Any] = {}
        for key in ("dependencies", "devDependencies"):
            value = package.get(key)
            if isinstance(value, dict):
                dependencies.update(value)
        if "@astrojs/starlight" not in dependencies:
            continue
        parent = str(Path(package_path).parent)
        parent = "" if parent == "." else parent + "/"
        has_lock = f"{parent}package-lock.json" in lock_paths
        has_config = any(path.startswith(parent) for path in astro_config_paths)
        if has_lock and has_config:
            return True, (
                "Starlight package, lockfile, and Astro config found under "
                f"{parent or 'repository root'}"
            )
    return False, (
        "no pinned Starlight package + package-lock + Astro config set is present "
        "in the candidate"
    )


def _detect_publication_path(files: dict[str, bytes]) -> tuple[bool, bool, str]:
    workflow = files.get(PUBLICATION_WORKFLOW)
    if workflow is None:
        return False, False, f"{PUBLICATION_WORKFLOW} is not implemented"
    try:
        text = workflow.decode("utf-8")
    except UnicodeDecodeError:
        return False, False, f"{PUBLICATION_WORKFLOW} is not UTF-8"

    readiness_gate = (
        "workflow_dispatch:" in text
        and "tools/release_readiness.py" in text
        and "--require-ready" in text
    )
    attestation = (
        re.search(r"actions/attest@[0-9a-f]{40}", text) is not None
        and "id-token: write" in text
        and "attestations: write" in text
    )
    detail = (
        "publication workflow contains manual dispatch and fail-closed readiness gate"
        if readiness_gate
        else "publication workflow exists but lacks the expected manual fail-closed readiness contract"
    )
    return readiness_gate, attestation, detail


def evaluate_readiness(
    candidate_dir: str | Path,
    *,
    expected_source_commit: str | None = None,
    fresh_environment_verified: bool = False,
) -> dict[str, Any]:
    directory = Path(candidate_dir).resolve()
    release_evidence_path = directory / "release-evidence.json"
    release_evidence = _read_json(release_evidence_path)

    version = release_evidence.get("version")
    source_commit = release_evidence.get("source_commit")
    archive_name = release_evidence.get("artifact")
    archive_sha256 = release_evidence.get("artifact_sha256")
    if not isinstance(version, str) or not _SEMVER_PRERELEASE_RE.fullmatch(version):
        raise ReleaseReadinessError("release evidence version must be explicit prerelease SemVer")
    if not isinstance(source_commit, str) or not _SHA40_RE.fullmatch(source_commit):
        raise ReleaseReadinessError("release evidence source_commit must be a full lowercase SHA")
    if expected_source_commit is not None and source_commit != expected_source_commit:
        raise ReleaseReadinessError(
            f"candidate source commit {source_commit} does not match expected {expected_source_commit}"
        )
    if not isinstance(archive_name, str) or archive_name != f"{PROJECT}-{version}.tar.gz":
        raise ReleaseReadinessError("release evidence artifact filename is inconsistent with version")
    if not isinstance(archive_sha256, str) or not _SHA64_RE.fullmatch(archive_sha256):
        raise ReleaseReadinessError("release evidence artifact_sha256 is invalid")

    sbom_evidence = release_evidence.get("sbom")
    if not isinstance(sbom_evidence, dict):
        raise ReleaseReadinessError("release evidence does not contain SBOM evidence")
    sbom_name = sbom_evidence.get("filename")
    sbom_sha256 = sbom_evidence.get("sha256")
    if not isinstance(sbom_name, str) or sbom_name != f"{PROJECT}-{version}.spdx.json":
        raise ReleaseReadinessError("release evidence SBOM filename is inconsistent with version")
    if not isinstance(sbom_sha256, str) or not _SHA64_RE.fullmatch(sbom_sha256):
        raise ReleaseReadinessError("release evidence SBOM sha256 is invalid")

    archive_path = directory / archive_name
    sbom_path = directory / sbom_name
    checksums_path = directory / "SHA256SUMS"
    validation_path = directory / "spdx-validation-evidence.json"
    required_files = (archive_path, sbom_path, checksums_path, validation_path)
    for path in required_files:
        if not path.is_file():
            raise ReleaseReadinessError(f"required candidate evidence file is missing: {path.name}")

    actual_archive_sha256 = _sha256(archive_path)
    actual_sbom_sha256 = _sha256(sbom_path)
    validation_sha256 = _sha256(validation_path)
    checksums = _parse_checksums(checksums_path)
    validation_evidence = _read_json(validation_path)

    archive_files = _archive_files(archive_path, version)
    manifest_bytes = archive_files.get("RELEASE-MANIFEST.json")
    if manifest_bytes is None:
        raise ReleaseReadinessError("candidate archive is missing RELEASE-MANIFEST.json")
    manifest = _json_from_bytes(manifest_bytes, "RELEASE-MANIFEST.json")
    manifest_paths = {
        item.get("path")
        for item in manifest.get("files", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }

    validation_state = sbom_evidence.get("validation")
    validation_pass = (
        isinstance(validation_state, dict)
        and validation_state.get("status") == "PASS"
    )
    validation_digest_bound = (
        validation_pass
        and validation_state.get("evidence_filename") == validation_path.name
        and validation_state.get("evidence_sha256") == validation_sha256
    )
    validation_document_pass = (
        validation_evidence.get("status") == "PASS"
        and isinstance(validation_evidence.get("sbom"), dict)
        and validation_evidence["sbom"].get("filename") == sbom_name
        and validation_evidence["sbom"].get("sha256") == actual_sbom_sha256
        and validation_evidence["sbom"].get("format") == "SPDX"
        and validation_evidence["sbom"].get("version") == "2.3"
        and validation_evidence["sbom"].get("transitional") is True
    )
    validation_schema_identity = (
        isinstance(validation_state, dict)
        and _schema_identity_matches(validation_state.get("official_schema"))
        and _schema_identity_matches(validation_evidence.get("official_schema"))
    )
    release_sbom_identity = (
        sbom_evidence.get("format") == "SPDX"
        and sbom_evidence.get("version") == "2.3"
        and sbom_evidence.get("transitional") is True
    )

    missing_required_paths = sorted(set(_REQUIRED_ARCHIVE_PATHS) - manifest_paths)
    threshold_checks = [
        _check(
            "candidate_archive_digest",
            actual_archive_sha256 == archive_sha256,
            "candidate archive SHA-256 matches release evidence",
        ),
        _check(
            "candidate_sbom_digest",
            actual_sbom_sha256 == sbom_sha256,
            "candidate SBOM SHA-256 matches release evidence",
        ),
        _check(
            "checksum_manifest",
            checksums.get(archive_name) == actual_archive_sha256
            and checksums.get(sbom_name) == actual_sbom_sha256,
            "SHA256SUMS binds the candidate archive and SBOM",
        ),
        _check(
            "sbom_validation_state",
            bool(
                validation_pass
                and validation_digest_bound
                and validation_document_pass
                and release_sbom_identity
            ),
            "SBOM validation is PASS and the deterministic validation evidence digest is bound",
        ),
        _check(
            "sbom_validation_schema_identity",
            bool(validation_schema_identity),
            "release and validation evidence both bind the exact pinned official SPDX schema identity",
        ),
        _check(
            "candidate_manifest_identity",
            manifest.get("version") == version
            and manifest.get("source_commit") == source_commit
            and manifest.get("publication_performed") is False
            and manifest.get("runtime_network_access") is False,
            "embedded release manifest matches candidate identity and non-publication boundary",
        ),
        _check(
            "required_public_release_material",
            not missing_required_paths,
            "all required public implementation, quickstart, compatibility, release, schema, mapping, adapter, and proof paths are packaged"
            if not missing_required_paths
            else "missing from candidate manifest: " + ", ".join(missing_required_paths),
        ),
        _check(
            "candidate_non_publication_state",
            release_evidence.get("publication_performed") is False
            and release_evidence.get("attestation_performed") is False,
            "candidate evidence remains non-published and non-attested",
        ),
        _check(
            "fresh_environment_verification",
            fresh_environment_verified,
            "caller asserts this gate ran only after the workflow's isolated extracted-candidate proof"
            if fresh_environment_verified
            else "fresh-environment proof has not been asserted for this evaluation",
        ),
    ]
    threshold_pass = all(check["status"] == "PASS" for check in threshold_checks)

    docs_ready, docs_detail = _detect_documentation_site(archive_files)
    publication_ready, attestation_ready, publication_detail = _detect_publication_path(
        archive_files
    )

    blockers: list[str] = []
    if not threshold_pass:
        blockers.extend(
            f"release_threshold:{check['name']}"
            for check in threshold_checks
            if check["status"] != "PASS"
        )
    if not docs_ready:
        blockers.append("documentation_site_build_not_ready")
    if not publication_ready:
        blockers.append("governed_publication_path_not_ready")
    if not attestation_ready:
        blockers.append("public_attestation_path_not_ready")

    overall = READY if not blockers else BLOCKED
    return {
        "schema_version": 1,
        "project": PROJECT,
        "version": version,
        "source_commit": source_commit,
        "overall_status": overall,
        "release_threshold": {
            "status": "PASS" if threshold_pass else "FAIL",
            "checks": threshold_checks,
        },
        "launch_experience": {
            "status": "PASS" if docs_ready else "BLOCKED",
            "documentation_site_build": {
                "status": "PASS" if docs_ready else "BLOCKED",
                "detail": docs_detail,
            },
        },
        "publication_capability": {
            "status": "PASS" if publication_ready and attestation_ready else "BLOCKED",
            "governed_publication_path": {
                "status": "PASS" if publication_ready else "BLOCKED",
                "detail": publication_detail,
            },
            "public_attestation_path": {
                "status": "PASS" if attestation_ready else "BLOCKED",
                "detail": (
                    "publication workflow contains immutable actions/attest plus required OIDC/attestation permissions"
                    if attestation_ready
                    else "public build/SBOM attestation path is not yet implemented"
                ),
            },
        },
        "blockers": blockers,
        "human_boundary": {
            "required": True,
            "authority": "explicit public release authorization",
            "status": "PENDING",
            "request_only_when": READY,
        },
        "publication_performed": False,
        "report_deterministic": True,
    }


def _json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate MeaningWire release readiness without publishing"
    )
    parser.add_argument(
        "--candidate-dir", required=True, help="verified candidate evidence directory"
    )
    parser.add_argument(
        "--source-commit", help="require candidate evidence to match this exact commit"
    )
    parser.add_argument(
        "--fresh-environment-verified",
        action="store_true",
        help="assert that the caller runs after the isolated extracted-candidate proof",
    )
    parser.add_argument("--output", help="write machine-readable readiness report JSON")
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="exit nonzero unless the report is READY_FOR_HUMAN_DECISION",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = evaluate_readiness(
            args.candidate_dir,
            expected_source_commit=args.source_commit,
            fresh_environment_verified=args.fresh_environment_verified,
        )
        data = _json_bytes(report)
        if args.output:
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(data)
    except (ReleaseReadinessError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 2

    print(
        f"{report['overall_status']}: release_threshold={report['release_threshold']['status']}; "
        f"launch_experience={report['launch_experience']['status']}; "
        f"publication_capability={report['publication_capability']['status']}; "
        f"blockers={len(report['blockers'])}; publication_performed=false."
    )
    if args.require_ready and report["overall_status"] != READY:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
