#!/usr/bin/env python3
"""Generate a deterministic transitional SPDX 2.3 SBOM for a MeaningWire candidate.

The SBOM scope is deliberately narrow: the MeaningWire release-candidate archive
and the target-specific locked Python validation environment. It does not claim
to inventory the operating system, GitHub-hosted runner, or unrelated tooling.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

import validate_dependency_lock

ROOT = Path(__file__).resolve().parents[1]
VERSION_PATH = ROOT / "VERSION"
PROJECT = "MeaningWire"
SPDX_VERSION = "SPDX-2.3"
DATA_LICENSE = "CC0-1.0"
ROOT_PACKAGE_ID = "SPDXRef-Package-MeaningWire"
_VERSION_RE = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


class SPDXGenerationError(ValueError):
    """Raised when deterministic SPDX candidate data cannot be generated."""


def _git_text(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as exc:
        raise SPDXGenerationError("git is required to generate candidate SBOM data") from exc
    except subprocess.CalledProcessError as exc:
        raise SPDXGenerationError(
            f"git {' '.join(args)} failed: {exc.stderr.strip()}"
        ) from exc
    return result.stdout.strip()


def current_commit() -> str:
    value = _git_text("rev-parse", "HEAD")
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise SPDXGenerationError("HEAD did not resolve to a full commit SHA")
    return value


def commit_created_at(source_commit: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise SPDXGenerationError("source commit must be a full lowercase SHA")
    raw = _git_text("show", "-s", "--format=%ct", source_commit)
    try:
        timestamp = int(raw)
    except ValueError as exc:
        raise SPDXGenerationError("Git commit timestamp was not an integer") from exc
    return dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def load_version() -> str:
    version = VERSION_PATH.read_text(encoding="utf-8").strip()
    if not _VERSION_RE.fullmatch(version):
        raise SPDXGenerationError(f"VERSION is not valid SemVer: {version!r}")
    return version


def _spdx_id_for_dependency(name: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9.-]+", "-", name).strip("-")
    if not safe:
        raise SPDXGenerationError(f"cannot create SPDX ID for dependency {name!r}")
    return f"SPDXRef-Package-{safe}"


def _dependency_package(
    name: str,
    version: str,
    hashes: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "SPDXID": _spdx_id_for_dependency(name),
        "name": name,
        "versionInfo": version,
        "downloadLocation": "NOASSERTION",
        "filesAnalyzed": False,
        "licenseConcluded": "NOASSERTION",
        "licenseDeclared": "NOASSERTION",
        "copyrightText": "NOASSERTION",
        "checksums": [
            {"algorithm": "SHA256", "checksumValue": digest}
            for digest in sorted(hashes)
        ],
        "externalRefs": [
            {
                "referenceCategory": "PACKAGE-MANAGER",
                "referenceType": "purl",
                "referenceLocator": f"pkg:pypi/{name}@{version}",
            }
        ],
        "comment": (
            "Governed validation-environment dependency from "
            "requirements-validation.lock; checksum identifies an accepted "
            "binary wheel for the documented candidate target."
        ),
    }


def build_spdx_document(
    *,
    version: str,
    source_commit: str,
    created: str,
    archive_name: str,
    archive_sha256: str,
) -> dict[str, Any]:
    if not _VERSION_RE.fullmatch(version):
        raise SPDXGenerationError(f"invalid candidate version: {version!r}")
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise SPDXGenerationError("source commit must be a full lowercase SHA")
    if not re.fullmatch(r"[0-9a-f]{64}", archive_sha256):
        raise SPDXGenerationError("archive SHA-256 must be 64 lowercase hex characters")
    if not archive_name or "/" in archive_name or "\\" in archive_name:
        raise SPDXGenerationError("archive name must be a simple filename")

    _direct, locked = validate_dependency_lock.validate_static()
    dependency_packages = [
        _dependency_package(name, locked[name][0], locked[name][1])
        for name in sorted(locked)
    ]

    root_package = {
        "SPDXID": ROOT_PACKAGE_ID,
        "name": PROJECT,
        "versionInfo": version,
        "packageFileName": archive_name,
        "downloadLocation": "NOASSERTION",
        "filesAnalyzed": False,
        "licenseConcluded": "Apache-2.0",
        "licenseDeclared": "Apache-2.0",
        "copyrightText": "NOASSERTION",
        "checksums": [{"algorithm": "SHA256", "checksumValue": archive_sha256}],
        "homepage": "https://github.com/MeaningWire/MeaningWire",
        "sourceInfo": f"Built from exact public Git commit {source_commit}.",
        "comment": (
            "Transitional SPDX 2.3 candidate package record. This SBOM is "
            "pre-release evidence and is not a production-readiness claim."
        ),
    }

    relationships = [
        {
            "spdxElementId": ROOT_PACKAGE_ID,
            "relationshipType": "DEPENDS_ON",
            "relatedSpdxElement": package["SPDXID"],
            "comment": (
                "Flattened governed validation-environment dependency; this "
                "relationship does not distinguish direct from transitive Python dependencies."
            ),
        }
        for package in dependency_packages
    ]

    return {
        "SPDXID": "SPDXRef-DOCUMENT",
        "spdxVersion": SPDX_VERSION,
        "dataLicense": DATA_LICENSE,
        "name": f"MeaningWire-{version}-candidate-sbom",
        "documentNamespace": (
            f"urn:meaningwire:spdx:release-candidate:{version}:{source_commit}"
        ),
        "creationInfo": {
            "created": created,
            "creators": [f"Tool: MeaningWire-SBOM-generator-{version}"],
            "comment": (
                "Generated deterministically from the exact candidate archive "
                "digest and requirements-validation.lock."
            ),
        },
        "documentDescribes": [ROOT_PACKAGE_ID],
        "packages": [root_package, *dependency_packages],
        "relationships": relationships,
        "comment": (
            "Scope: MeaningWire candidate archive plus the locked CPython 3.12 / "
            "Linux x86-64 validation dependency environment. Operating-system, "
            "runner, and unrelated build-tool inventories are out of scope."
        ),
    }


def json_bytes(document: dict[str, Any]) -> bytes:
    return (json.dumps(document, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_spdx_document(
    output_path: str | Path,
    *,
    version: str,
    source_commit: str,
    created: str,
    archive_name: str,
    archive_sha256: str,
) -> dict[str, Any]:
    document = build_spdx_document(
        version=version,
        source_commit=source_commit,
        created=created,
        archive_name=archive_name,
        archive_sha256=archive_sha256,
    )
    data = json_bytes(document)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return {
        "path": destination,
        "document": document,
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a deterministic transitional SPDX 2.3 MeaningWire candidate SBOM"
    )
    parser.add_argument("--archive", required=True, help="candidate archive path")
    parser.add_argument("--output", required=True, help="SPDX JSON output path")
    parser.add_argument(
        "--source-commit",
        help="exact source commit; defaults to HEAD",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        archive = Path(args.archive)
        if not archive.is_file():
            raise SPDXGenerationError(f"candidate archive does not exist: {archive}")
        source_commit = args.source_commit or current_commit()
        if source_commit != current_commit():
            raise SPDXGenerationError(
                f"source commit {source_commit} does not match checked-out HEAD {current_commit()}"
            )
        version = load_version()
        archive_sha256 = hashlib.sha256(archive.read_bytes()).hexdigest()
        result = write_spdx_document(
            args.output,
            version=version,
            source_commit=source_commit,
            created=commit_created_at(source_commit),
            archive_name=archive.name,
            archive_sha256=archive_sha256,
        )
    except (SPDXGenerationError, validate_dependency_lock.DependencyLockError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 2

    print(
        "PASS: transitional SPDX 2.3 candidate SBOM generated; "
        f"sha256={result['sha256']}; scope=candidate+locked-validation-environment."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
