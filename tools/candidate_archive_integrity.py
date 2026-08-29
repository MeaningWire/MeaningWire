#!/usr/bin/env python3
"""Strict structural validation for MeaningWire release-candidate archives."""

from __future__ import annotations

import gzip
import hashlib
import json
import re
import tarfile
from pathlib import Path
from typing import Any, BinaryIO

PROJECT = "MeaningWire"
_SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA64_RE = re.compile(r"^[0-9a-f]{64}$")
_ALLOWED_MODES = {"0644", "0755"}

# These ceilings are deliberately much larger than the current preview candidate while
# remaining finite enough to fail closed on unreasonable or adversarial archive input.
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_MEMBER_COUNT = 4096
MAX_MEMBER_BYTES = 32 * 1024 * 1024
MAX_TOTAL_FILE_BYTES = 256 * 1024 * 1024
MAX_DECOMPRESSED_STREAM_BYTES = 320 * 1024 * 1024


class CandidateArchiveError(ValueError):
    """Raised when candidate archive structure or manifest evidence is ambiguous."""


class _BoundedReader:
    """Expose a read-only stream that fails before decompression can grow without bound."""

    def __init__(self, source: BinaryIO, limit: int) -> None:
        self._source = source
        self._limit = limit
        self._read = 0

    def read(self, size: int = -1) -> bytes:
        remaining = self._limit - self._read
        request = remaining + 1 if size < 0 else min(size, remaining + 1)
        data = self._source.read(request)
        self._read += len(data)
        if self._read > self._limit:
            raise CandidateArchiveError(
                "candidate archive decompressed stream exceeds safety limit "
                f"({MAX_DECOMPRESSED_STREAM_BYTES} bytes)"
            )
        return data


def _safe_relative(path: str, *, label: str) -> str:
    if not path or path.startswith("/") or "\\" in path:
        raise CandidateArchiveError(f"unsafe {label}: {path!r}")
    parts = path.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise CandidateArchiveError(f"unsafe {label}: {path!r}")
    return path


def _archive_size(path: Path) -> int:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise CandidateArchiveError(f"cannot inspect candidate archive: {exc}") from exc
    if size > MAX_ARCHIVE_BYTES:
        raise CandidateArchiveError(
            "candidate archive compressed size exceeds safety limit "
            f"({MAX_ARCHIVE_BYTES} bytes)"
        )
    return size


def archive_sha256(archive_path: str | Path) -> str:
    """Hash a candidate archive while enforcing the compressed-size ceiling."""

    path = Path(archive_path)
    _archive_size(path)
    digest = hashlib.sha256()
    hashed_bytes = 0
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                hashed_bytes += len(chunk)
                if hashed_bytes > MAX_ARCHIVE_BYTES:
                    raise CandidateArchiveError(
                        "candidate archive compressed size exceeds safety limit during hashing "
                        f"({MAX_ARCHIVE_BYTES} bytes)"
                    )
                digest.update(chunk)
    except CandidateArchiveError:
        raise
    except OSError as exc:
        raise CandidateArchiveError(f"cannot hash candidate archive: {exc}") from exc
    return digest.hexdigest()


def read_archive(archive_path: str | Path, version: str) -> dict[str, bytes]:
    """Return bounded unique regular-file contents after strict archive checks."""

    path = Path(archive_path)
    _archive_size(path)
    prefix = f"{PROJECT}-{version}/"
    files: dict[str, bytes] = {}
    member_count = 0
    total_file_bytes = 0
    try:
        with path.open("rb") as raw:
            with gzip.GzipFile(fileobj=raw, mode="rb") as compressed:
                bounded = _BoundedReader(compressed, MAX_DECOMPRESSED_STREAM_BYTES)
                # Stream the tar sequentially so validation can enforce member and byte
                # ceilings before an unbounded member list or payload set is materialized.
                with tarfile.open(fileobj=bounded, mode="r|") as archive:
                    for member in archive:
                        member_count += 1
                        if member_count > MAX_MEMBER_COUNT:
                            raise CandidateArchiveError(
                                "candidate archive member count exceeds safety limit "
                                f"({MAX_MEMBER_COUNT})"
                            )
                        if not member.isfile():
                            raise CandidateArchiveError(
                                f"candidate archive contains non-regular member: {member.name}"
                            )
                        if member.size < 0 or member.size > MAX_MEMBER_BYTES:
                            raise CandidateArchiveError(
                                "candidate archive member exceeds safety limit: "
                                f"{member.name} ({MAX_MEMBER_BYTES} bytes)"
                            )
                        if total_file_bytes + member.size > MAX_TOTAL_FILE_BYTES:
                            raise CandidateArchiveError(
                                "candidate archive total uncompressed file size exceeds safety limit "
                                f"({MAX_TOTAL_FILE_BYTES} bytes)"
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
                        data = extracted.read(member.size + 1)
                        if len(data) != member.size:
                            raise CandidateArchiveError(
                                f"candidate archive member size is inconsistent: {member.name}"
                            )
                        files[relative] = data
                        total_file_bytes += len(data)
    except CandidateArchiveError:
        raise
    except (OSError, EOFError, gzip.BadGzipFile, tarfile.TarError) as exc:
        raise CandidateArchiveError(f"cannot inspect candidate archive: {exc}") from exc
    if member_count == 0:
        raise CandidateArchiveError("candidate archive contains no members")
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
