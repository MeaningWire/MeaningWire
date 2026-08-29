#!/usr/bin/env python3
"""Strict structural validation for MeaningWire release-candidate archives."""

from __future__ import annotations

import hashlib
import json
import re
import tarfile
from pathlib import Path
from typing import Any

PROJECT = "MeaningWire"
_SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA64_RE = re.compile(r"^[0-9a-f]{64}$")
_ALLOWED_MODES = {"0644", "0755"}


class CandidateArchiveError(ValueError):
    """Raised when candidate archive structure or manifest evidence is ambiguous."""


def _safe_relative(path: str, *, label: str) -> str:
    if not path or path.startswith("/") or "\\" in path:
        raise CandidateArchiveError(f"unsafe {label}: {path!r}")
    parts = path.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise CandidateArchiveError(f"unsafe {label}: {path!r}")
    return path


def read_archive(archive_path: str | Path, version: str) -> dict[str, bytes]:
    """Return unique regular-file contents after strict archive-structure checks."""

    path = Path(archive_path)
    prefix = f"{PROJECT}-{version}/"
    files: dict[str, bytes] = {}
    try:
        with tarfile.open(path, "r:gz") as archive:
            members = archive.getmembers()
            if not members:
                raise CandidateArchiveError("candidate archive contains no members")
            for member in members:
                if not member.isfile():
                    raise CandidateArchiveError(
                        f"candidate archive contains non-regular member: {member.name}"
                    )
                if not member.name.startswith(prefix):
                    raise CandidateArchiveError(
                        f"candidate archive member is outside expected prefix: {member.name}"
                    )
                relative = _safe_relative(
                    member.name[len(prefix) :], label="candidate archive member"
                )
                if relative in files:
                    raise CandidateArchiveError(
                        f"duplicate candidate archive member: {relative}"
                    )
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise CandidateArchiveError(
                        f"could not read candidate archive member: {member.name}"
                    )
                files[relative] = extracted.read()
    except CandidateArchiveError:
        raise
    except (OSError, tarfile.TarError) as exc:
        raise CandidateArchiveError(f"cannot inspect candidate archive: {exc}") from exc
    if not files:
        raise CandidateArchiveError("candidate archive contains no regular files")
    return files


def parse_manifest(data: bytes) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CandidateArchiveError(f"cannot parse RELEASE-MANIFEST.json: {exc}") from exc
    if not isinstance(value, dict):
        raise CandidateArchiveError("RELEASE-MANIFEST.json root must be an object")
    return value


def validate_manifest(
    manifest: dict[str, Any],
    archive_files: dict[str, bytes],
    *,
    version: str,
    source_commit: str,
) -> dict[str, Any]:
    """Validate manifest identity and exact per-file correspondence."""

    if manifest.get("project") != PROJECT:
        raise CandidateArchiveError("release manifest project identity is invalid")
    if manifest.get("version") != version:
        raise CandidateArchiveError("release manifest version is inconsistent")
    if manifest.get("source_commit") != source_commit or not _SHA40_RE.fullmatch(source_commit):
        raise CandidateArchiveError("release manifest source commit is inconsistent")
    if manifest.get("publication_performed") is not False:
        raise CandidateArchiveError("release manifest publication boundary is invalid")
    if manifest.get("runtime_network_access") is not False:
        raise CandidateArchiveError("release manifest runtime network boundary is invalid")

    records = manifest.get("files")
    if not isinstance(records, list) or not records:
        raise CandidateArchiveError("release manifest files must be a non-empty array")

    expected_files = set(archive_files) - {"RELEASE-MANIFEST.json"}
    seen: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise CandidateArchiveError(f"release manifest file record {index} is not an object")
        raw_path = record.get("path")
        if not isinstance(raw_path, str):
            raise CandidateArchiveError(f"release manifest file record {index} has no valid path")
        relative = _safe_relative(raw_path, label="release manifest path")
        if relative == "RELEASE-MANIFEST.json":
            raise CandidateArchiveError("release manifest must not recursively list itself")
        if relative in seen:
            raise CandidateArchiveError(f"duplicate release manifest path: {relative}")
        seen.add(relative)
        data = archive_files.get(relative)
        if data is None:
            raise CandidateArchiveError(
                f"release manifest references missing archive file: {relative}"
            )
        digest = record.get("sha256")
        if not isinstance(digest, str) or not _SHA64_RE.fullmatch(digest):
            raise CandidateArchiveError(f"release manifest SHA-256 is invalid: {relative}")
        if hashlib.sha256(data).hexdigest() != digest:
            raise CandidateArchiveError(f"release manifest SHA-256 mismatch: {relative}")
        size = record.get("size")
        if not isinstance(size, int) or isinstance(size, bool) or size != len(data):
            raise CandidateArchiveError(f"release manifest size mismatch: {relative}")
        git_object = record.get("git_object")
        if not isinstance(git_object, str) or not _SHA40_RE.fullmatch(git_object):
            raise CandidateArchiveError(f"release manifest Git object is invalid: {relative}")
        if record.get("mode") not in _ALLOWED_MODES:
            raise CandidateArchiveError(f"release manifest mode is invalid: {relative}")

    if seen != expected_files:
        missing = sorted(expected_files - seen)
        extra = sorted(seen - expected_files)
        details: list[str] = []
        if missing:
            details.append("unlisted archive files: " + ", ".join(missing))
        if extra:
            details.append("manifest-only files: " + ", ".join(extra))
        raise CandidateArchiveError("release manifest/archive mismatch: " + "; ".join(details))

    return {
        "file_count": len(seen),
        "paths": seen,
    }


def inspect_candidate(
    archive_path: str | Path,
    *,
    version: str,
    source_commit: str,
    expected_manifest_sha256: str,
) -> tuple[dict[str, bytes], dict[str, Any], dict[str, Any]]:
    if not isinstance(expected_manifest_sha256, str) or not _SHA64_RE.fullmatch(
        expected_manifest_sha256
    ):
        raise CandidateArchiveError("release evidence content_manifest_sha256 is invalid")
    files = read_archive(archive_path, version)
    manifest_bytes = files.get("RELEASE-MANIFEST.json")
    if manifest_bytes is None:
        raise CandidateArchiveError("candidate archive is missing RELEASE-MANIFEST.json")
    if hashlib.sha256(manifest_bytes).hexdigest() != expected_manifest_sha256:
        raise CandidateArchiveError("embedded release manifest digest does not match release evidence")
    manifest = parse_manifest(manifest_bytes)
    validation = validate_manifest(
        manifest,
        files,
        version=version,
        source_commit=source_commit,
    )
    return files, manifest, validation
