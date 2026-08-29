#!/usr/bin/env python3
"""Prepare deterministic publication preflight evidence without publishing.

This module validates exact source/version/release metadata, re-evaluates the
candidate readiness report, verifies release-note source content from the exact
candidate archive, and renders a release-note evidence header. It never creates
a tag, GitHub Release, package, deployment, signature, or attestation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import candidate_archive_integrity
import release_readiness

PROJECT = "MeaningWire"
READY = release_readiness.READY
_SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA64_RE = re.compile(r"^[0-9a-f]{64}$")
_VERSION_RE = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
_TEMPLATE_TOKEN_RE = re.compile(r"<[^>\n]+>")
_REQUIRED_NOTE_SECTIONS = (
    "What this release is",
    "Supported in this release",
    "Added",
    "Changed",
    "Fixed",
    "Breaking changes",
    "Migration guide",
    "Security-relevant changes",
    "Compatibility statement",
    "Known limitations",
    "Explicit non-claims",
    "Public implementation boundary",
    "Upgrade / rollback notes",
    "Changelog",
)


class PublicationPreflightError(ValueError):
    """Raised when publication preflight evidence is inconsistent or incomplete."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PublicationPreflightError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PublicationPreflightError(f"JSON root must be an object: {path}")
    return value


def _safe_repo_path(value: str) -> str:
    if not value or value.startswith("/") or "\\" in value:
        raise PublicationPreflightError(f"unsafe release-notes source path: {value!r}")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise PublicationPreflightError(f"unsafe release-notes source path: {value!r}")
    return value


def _is_prerelease(version: str) -> bool:
    core = version.split("+", 1)[0]
    return "-" in core


def _release_status(version: str) -> str:
    if not _is_prerelease(version):
        return "stable"
    prerelease = version.split("+", 1)[0].split("-", 1)[1].lower()
    if prerelease.startswith("alpha"):
        return "alpha"
    if prerelease.startswith("beta"):
        return "beta"
    if prerelease.startswith("rc"):
        return "rc"
    return "preview"


def _candidate_member(candidate_dir: Path, release_evidence: dict[str, Any], path: str) -> bytes:
    """Read one file only from a bounded, digest-stable validated candidate snapshot."""

    archive_name = release_evidence.get("artifact")
    version = release_evidence.get("version")
    source_commit = release_evidence.get("source_commit")
    artifact_sha256 = release_evidence.get("artifact_sha256")
    manifest_sha256 = release_evidence.get("content_manifest_sha256")
    if not isinstance(archive_name, str) or not isinstance(version, str):
        raise PublicationPreflightError("release evidence is missing artifact/version identity")
    if not isinstance(source_commit, str) or not _SHA40_RE.fullmatch(source_commit):
        raise PublicationPreflightError("release evidence source commit is invalid")
    if not isinstance(artifact_sha256, str) or not _SHA64_RE.fullmatch(artifact_sha256):
        raise PublicationPreflightError("release evidence artifact SHA-256 is invalid")
    if not isinstance(manifest_sha256, str) or not _SHA64_RE.fullmatch(manifest_sha256):
        raise PublicationPreflightError("release evidence manifest SHA-256 is invalid")

    archive_path = candidate_dir / archive_name
    try:
        files, _manifest, _validation = candidate_archive_integrity.inspect_candidate_stable(
            archive_path,
            version=version,
            source_commit=source_commit,
            expected_artifact_sha256=artifact_sha256,
            expected_manifest_sha256=manifest_sha256,
        )
    except candidate_archive_integrity.CandidateArchiveError as exc:
        raise PublicationPreflightError(f"candidate archive integrity failure: {exc}") from exc

    data = files.get(path)
    if data is None:
        raise PublicationPreflightError(
            f"release-notes source is not packaged in the exact candidate: {path}"
        )
    return data


def _parse_note_sections(text: str, version: str) -> dict[str, str]:
    lines = text.splitlines()
    expected_h1 = f"# {PROJECT} {version}"
    if not lines or lines[0].strip() != expected_h1:
        raise PublicationPreflightError(
            f"release-notes source must begin with exact heading {expected_h1!r}"
        )
    if _TEMPLATE_TOKEN_RE.search(text):
        raise PublicationPreflightError("release-notes source contains unresolved <...> template token")

    headings: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        if line.startswith("## "):
            headings.append((index, line[3:].strip()))

    names = [name for _index, name in headings]
    missing = [name for name in _REQUIRED_NOTE_SECTIONS if name not in names]
    if missing:
        raise PublicationPreflightError(
            "release-notes source is missing required sections: " + ", ".join(missing)
        )
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise PublicationPreflightError(
            "release-notes source has duplicate section headings: " + ", ".join(duplicates)
        )

    sections: dict[str, str] = {}
    for position, (line_index, name) in enumerate(headings):
        end = headings[position + 1][0] if position + 1 < len(headings) else len(lines)
        body = "\n".join(lines[line_index + 1 : end]).strip()
        sections[name] = body

    empty = [name for name in _REQUIRED_NOTE_SECTIONS if not sections.get(name, "").strip()]
    if empty:
        raise PublicationPreflightError(
            "release-notes source has empty required sections: " + ", ".join(empty)
        )
    return sections


def _render_release_notes(
    source_text: str,
    *,
    version: str,
    source_commit: str,
    tag_name: str,
    release_title: str,
    prerelease: bool,
    release_evidence: dict[str, Any],
    readiness: dict[str, Any],
) -> bytes:
    lines = source_text.splitlines()
    sbom = release_evidence["sbom"]
    header = [
        lines[0],
        "",
        "> **Prepublication evidence — this is not a published release.**",
        ">",
        f"> **Release status:** `{_release_status(version)}`  ",
        f"> **Source commit:** `{source_commit}`  ",
        f"> **Proposed tag:** `{tag_name}`  ",
        f"> **Proposed release title:** `{release_title}`  ",
        f"> **GitHub prerelease classification:** `{'true' if prerelease else 'false'}`  ",
        f"> **Candidate artifact:** `{release_evidence['artifact']}`  ",
        f"> **Artifact SHA-256:** `{release_evidence['artifact_sha256']}`  ",
        f"> **SBOM artifact:** `{sbom['filename']}`  ",
        f"> **SBOM SHA-256:** `{sbom['sha256']}`  ",
        f"> **Release-readiness:** `{readiness['overall_status']}`  ",
        "> **Human release authorization:** `PENDING`  ",
        "> **Public attestation:** `PENDING`  ",
        "> **Publication performed:** `false`",
        "",
    ]
    return ("\n".join(header + lines[1:]).rstrip() + "\n").encode("utf-8")


def evaluate_preflight(
    candidate_dir: str | Path,
    *,
    source_commit: str,
    requested_version: str,
    tag_name: str,
    release_title: str,
    prerelease: bool,
    release_notes_source: str,
    fresh_environment_verified: bool,
    documentation_build_verified: bool,
) -> tuple[dict[str, Any], bytes]:
    directory = Path(candidate_dir).resolve()
    if not directory.is_dir():
        raise PublicationPreflightError(f"candidate directory does not exist: {directory}")
    if not _SHA40_RE.fullmatch(source_commit):
        raise PublicationPreflightError("source commit must be a full lowercase 40-character SHA")
    if not _VERSION_RE.fullmatch(requested_version):
        raise PublicationPreflightError("requested version must be valid SemVer")

    release_evidence_path = directory / "release-evidence.json"
    readiness_path = directory / "release-readiness.json"
    release_evidence = _read_json(release_evidence_path)
    stored_readiness = _read_json(readiness_path)

    canonical_version = release_evidence.get("version")
    if not isinstance(canonical_version, str) or not _VERSION_RE.fullmatch(canonical_version):
        raise PublicationPreflightError("release evidence version is not valid SemVer")
    if release_evidence.get("source_commit") != source_commit:
        raise PublicationPreflightError("release evidence source commit does not match requested source SHA")
    if release_evidence.get("publication_performed") is not False:
        raise PublicationPreflightError("candidate release evidence does not preserve non-publication state")
    if release_evidence.get("attestation_performed") is not False:
        raise PublicationPreflightError("candidate release evidence does not preserve non-attestation state")

    if requested_version != canonical_version:
        raise PublicationPreflightError(
            f"requested version {requested_version!r} does not match exact candidate VERSION {canonical_version!r}"
        )
    expected_tag = f"v{canonical_version}"
    if tag_name != expected_tag:
        raise PublicationPreflightError(
            f"tag name {tag_name!r} does not match required {expected_tag!r}"
        )
    expected_title = f"{PROJECT} {canonical_version}"
    if release_title != expected_title:
        raise PublicationPreflightError(
            f"release title {release_title!r} does not match required {expected_title!r}"
        )
    expected_prerelease = _is_prerelease(canonical_version)
    if prerelease is not expected_prerelease:
        raise PublicationPreflightError(
            "GitHub prerelease classification does not match exact candidate version semantics"
        )

    try:
        recomputed_readiness = release_readiness.evaluate_readiness(
            directory,
            expected_source_commit=source_commit,
            fresh_environment_verified=fresh_environment_verified,
            documentation_build_verified=documentation_build_verified,
        )
    except release_readiness.ReleaseReadinessError as exc:
        raise PublicationPreflightError(f"candidate readiness evaluation failed: {exc}") from exc
    if stored_readiness != recomputed_readiness:
        raise PublicationPreflightError(
            "stored release-readiness.json is stale or inconsistent with exact candidate evidence"
        )
    if stored_readiness.get("version") != canonical_version:
        raise PublicationPreflightError("readiness report version does not match exact candidate VERSION")
    if stored_readiness.get("source_commit") != source_commit:
        raise PublicationPreflightError("readiness report source commit does not match requested source SHA")

    notes_path = _safe_repo_path(release_notes_source)
    notes_bytes = _candidate_member(directory, release_evidence, notes_path)
    try:
        notes_text = notes_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PublicationPreflightError("release-notes source must be UTF-8") from exc
    _parse_note_sections(notes_text, canonical_version)

    rendered_notes = _render_release_notes(
        notes_text,
        version=canonical_version,
        source_commit=source_commit,
        tag_name=tag_name,
        release_title=release_title,
        prerelease=prerelease,
        release_evidence=release_evidence,
        readiness=stored_readiness,
    )
    sbom = release_evidence["sbom"]
    report = {
        "schema_version": 1,
        "project": PROJECT,
        "version": canonical_version,
        "source_commit": source_commit,
        "tag_name": tag_name,
        "release_title": release_title,
        "prerelease": prerelease,
        "release_status": _release_status(canonical_version),
        "candidate": {
            "artifact": release_evidence["artifact"],
            "artifact_sha256": release_evidence["artifact_sha256"],
            "sbom": sbom["filename"],
            "sbom_sha256": sbom["sha256"],
            "checksums": "SHA256SUMS",
            "sbom_validation_evidence": "spdx-validation-evidence.json",
            "readiness_report": "release-readiness.json",
            "readiness_report_sha256": _sha256(readiness_path.read_bytes()),
            "readiness_status": stored_readiness["overall_status"],
            "readiness_blockers": stored_readiness["blockers"],
        },
        "release_notes": {
            "source_path": notes_path,
            "source_sha256": _sha256(notes_bytes),
            "rendered_sha256": _sha256(rendered_notes),
        },
        "human_boundary": {
            "required": True,
            "authority": "explicit public release authorization",
            "status": "PENDING",
        },
        "publication_performed": False,
        "attestation_performed": False,
    }
    return report, rendered_notes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare fail-closed MeaningWire publication preflight evidence without publishing"
    )
    parser.add_argument("--candidate-dir", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--tag-name", required=True)
    parser.add_argument("--release-title", required=True)
    parser.add_argument("--release-notes-source", required=True)
    prerelease = parser.add_mutually_exclusive_group(required=True)
    prerelease.add_argument("--prerelease", action="store_true", dest="prerelease")
    prerelease.add_argument("--not-prerelease", action="store_false", dest="prerelease")
    parser.add_argument("--fresh-environment-verified", action="store_true")
    parser.add_argument("--documentation-build-verified", action="store_true")
    parser.add_argument("--output", required=True, help="write deterministic preflight JSON")
    parser.add_argument("--rendered-release-notes", required=True)
    parser.add_argument(
        "--require-ready",
        action="store_true",
        help="exit nonzero unless the exact candidate is READY_FOR_HUMAN_DECISION",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report, rendered_notes = evaluate_preflight(
            args.candidate_dir,
            source_commit=args.source_commit,
            requested_version=args.version,
            tag_name=args.tag_name,
            release_title=args.release_title,
            prerelease=args.prerelease,
            release_notes_source=args.release_notes_source,
            fresh_environment_verified=args.fresh_environment_verified,
            documentation_build_verified=args.documentation_build_verified,
        )
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(_json_bytes(report))
        notes_output = Path(args.rendered_release_notes)
        notes_output.parent.mkdir(parents=True, exist_ok=True)
        notes_output.write_bytes(rendered_notes)
    except (PublicationPreflightError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 2

    print(
        "PASS: publication preflight evidence prepared without publishing; "
        f"version={report['version']}; source_commit={report['source_commit']}; "
        f"readiness={report['candidate']['readiness_status']}; "
        f"blockers={len(report['candidate']['readiness_blockers'])}; "
        "human_authorization=PENDING; publication_performed=false; attestation_performed=false."
    )
    if args.require_ready and report["candidate"]["readiness_status"] != READY:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())