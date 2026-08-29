#!/usr/bin/env python3
"""Build deterministic, non-publishing MeaningWire release-candidate evidence.

The builder reads tracked blob contents and release identity from the exact
checked-out Git commit, not from mutable working-tree files. It creates a
normalized tar.gz archive, a content manifest, a transitional SPDX 2.3
candidate SBOM, SHA-256 checksums, and release evidence. It does not tag,
publish, attest, upload, announce, or contact a package registry.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import re
import subprocess
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import candidate_archive_integrity
import generate_spdx_sbom

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "MeaningWire"
MATURITY = "EXPERIMENTAL"
_VERSION_RE = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


class ReleaseBuildError(ValueError):
    """Raised when a release candidate cannot be built safely."""


@dataclass(frozen=True)
class TrackedBlob:
    path: str
    mode: int
    object_sha: str
    data: bytes


def _git_bytes(*args: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise ReleaseBuildError("git is required to build a release candidate") from exc
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.decode("utf-8", errors="replace").strip()
        raise ReleaseBuildError(f"git {' '.join(args)} failed: {message}") from exc
    return result.stdout


def current_commit() -> str:
    value = _git_bytes("rev-parse", "HEAD").decode("ascii", errors="strict").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ReleaseBuildError("HEAD did not resolve to a full 40-character commit SHA")
    return value


def load_version(source_ref: str = "HEAD") -> str:
    """Read VERSION from an exact Git source ref, never from the working tree."""

    try:
        raw = _git_bytes("show", f"{source_ref}:VERSION")
        version = raw.decode("utf-8", errors="strict").strip()
    except UnicodeDecodeError as exc:
        raise ReleaseBuildError("committed VERSION is not valid UTF-8") from exc
    if not _VERSION_RE.fullmatch(version):
        raise ReleaseBuildError(f"committed VERSION is not valid SemVer: {version!r}")
    if raw != f"{version}\n".encode("utf-8"):
        raise ReleaseBuildError("committed VERSION must contain exactly one SemVer line")
    return version


def _safe_repo_path(path: str) -> str:
    if not path or path.startswith("/") or "\\" in path:
        raise ReleaseBuildError(f"unsafe tracked path: {path!r}")
    parts = path.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ReleaseBuildError(f"unsafe tracked path: {path!r}")
    return path


def _git_blob_size(object_sha: str, path: str) -> int:
    try:
        raw = _git_bytes("cat-file", "-s", object_sha).decode("ascii", errors="strict").strip()
        size = int(raw)
    except (UnicodeDecodeError, ValueError) as exc:
        raise ReleaseBuildError(f"could not determine tracked blob size for {path}") from exc
    if size < 0:
        raise ReleaseBuildError(f"invalid tracked blob size for {path}")
    return size


def tracked_blobs() -> list[TrackedBlob]:
    """Return bounded regular tracked blobs from HEAD in deterministic path order."""

    raw = _git_bytes("ls-tree", "-r", "-z", "--full-tree", "HEAD")
    blobs: list[TrackedBlob] = []
    total_bytes = 0
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        try:
            metadata, path_bytes = entry.split(b"\t", 1)
            mode_bytes, object_type, object_sha_bytes = metadata.split(b" ", 2)
            path = path_bytes.decode("utf-8", errors="strict")
            mode_text = mode_bytes.decode("ascii", errors="strict")
            object_sha = object_sha_bytes.decode("ascii", errors="strict")
        except (ValueError, UnicodeDecodeError) as exc:
            raise ReleaseBuildError("could not parse git ls-tree output") from exc

        _safe_repo_path(path)
        if object_type != b"blob":
            raise ReleaseBuildError(f"unsupported tracked object type for {path}: {object_type!r}")
        if mode_text not in {"100644", "100755"}:
            raise ReleaseBuildError(
                f"release candidates reject symlinks and special file modes: {path} ({mode_text})"
            )
        if not re.fullmatch(r"[0-9a-f]{40}", object_sha):
            raise ReleaseBuildError(f"invalid Git object SHA for {path}")
        if len(blobs) + 2 > candidate_archive_integrity.MAX_MEMBER_COUNT:
            raise ReleaseBuildError(
                "tracked file count plus release manifest exceeds candidate member safety limit "
                f"({candidate_archive_integrity.MAX_MEMBER_COUNT})"
            )

        size = _git_blob_size(object_sha, path)
        if size > candidate_archive_integrity.MAX_MEMBER_BYTES:
            raise ReleaseBuildError(
                f"tracked file exceeds candidate member safety limit: {path} "
                f"({candidate_archive_integrity.MAX_MEMBER_BYTES} bytes)"
            )
        if total_bytes + size > candidate_archive_integrity.MAX_TOTAL_FILE_BYTES:
            raise ReleaseBuildError(
                "tracked source bytes exceed candidate total-file safety limit before loading "
                f"({candidate_archive_integrity.MAX_TOTAL_FILE_BYTES} bytes)"
            )

        data = _git_bytes("cat-file", "blob", object_sha)
        if len(data) != size:
            raise ReleaseBuildError(f"tracked blob size changed unexpectedly for {path}")
        mode = 0o755 if mode_text == "100755" else 0o644
        blobs.append(TrackedBlob(path=path, mode=mode, object_sha=object_sha, data=data))
        total_bytes += size

    if not blobs:
        raise ReleaseBuildError("HEAD contains no releasable tracked files")
    return sorted(blobs, key=lambda item: item.path)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def build_content_manifest(
    blobs: list[TrackedBlob], *, version: str, source_commit: str
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "project": PROJECT,
        "version": version,
        "maturity": MATURITY,
        "source_commit": source_commit,
        "publication_performed": False,
        "runtime_network_access": False,
        "files": [
            {
                "path": blob.path,
                "size": len(blob.data),
                "sha256": _sha256(blob.data),
                "git_object": blob.object_sha,
                "mode": format(blob.mode, "04o"),
            }
            for blob in blobs
        ],
    }


def _validate_generated_manifest_limits(blobs: list[TrackedBlob], manifest_bytes: bytes) -> None:
    if len(blobs) + 1 > candidate_archive_integrity.MAX_MEMBER_COUNT:
        raise ReleaseBuildError(
            "candidate member count exceeds safety limit after adding release manifest "
            f"({candidate_archive_integrity.MAX_MEMBER_COUNT})"
        )
    if len(manifest_bytes) > candidate_archive_integrity.MAX_MEMBER_BYTES:
        raise ReleaseBuildError(
            "release manifest exceeds candidate member safety limit "
            f"({candidate_archive_integrity.MAX_MEMBER_BYTES} bytes)"
        )
    total_bytes = sum(len(blob.data) for blob in blobs) + len(manifest_bytes)
    if total_bytes > candidate_archive_integrity.MAX_TOTAL_FILE_BYTES:
        raise ReleaseBuildError(
            "tracked source plus release manifest exceeds candidate total-file safety limit "
            f"({candidate_archive_integrity.MAX_TOTAL_FILE_BYTES} bytes)"
        )


def _add_bytes(
    archive: tarfile.TarFile,
    *,
    name: str,
    data: bytes,
    mode: int,
) -> None:
    info = tarfile.TarInfo(name=name)
    info.size = len(data)
    info.mode = mode
    info.mtime = 0
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    archive.addfile(info, io.BytesIO(data))


def write_archive(
    output_path: Path,
    blobs: list[TrackedBlob],
    *,
    version: str,
    manifest_bytes: bytes,
) -> None:
    prefix = f"{PROJECT}-{version}"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as raw:
        with gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=raw,
            compresslevel=9,
            mtime=0,
        ) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.GNU_FORMAT) as archive:
                for blob in blobs:
                    _add_bytes(
                        archive,
                        name=f"{prefix}/{blob.path}",
                        data=blob.data,
                        mode=blob.mode,
                    )
                _add_bytes(
                    archive,
                    name=f"{prefix}/RELEASE-MANIFEST.json",
                    data=manifest_bytes,
                    mode=0o644,
                )


def build_release_candidate(
    output_dir: str | Path,
    *,
    expected_source_commit: str | None = None,
) -> dict[str, Any]:
    source_commit = current_commit()
    if expected_source_commit is not None and expected_source_commit != source_commit:
        raise ReleaseBuildError(
            f"expected source commit {expected_source_commit} but HEAD is {source_commit}"
        )

    version = load_version(source_commit)
    blobs = tracked_blobs()
    version_blob = next((blob for blob in blobs if blob.path == "VERSION"), None)
    if version_blob is None or version_blob.data != f"{version}\n".encode("utf-8"):
        raise ReleaseBuildError("tracked VERSION does not match exact committed release identity")
    manifest = build_content_manifest(blobs, version=version, source_commit=source_commit)
    manifest_bytes = _json_bytes(manifest)
    _validate_generated_manifest_limits(blobs, manifest_bytes)
    manifest_sha256 = _sha256(manifest_bytes)

    destination = Path(output_dir).expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    archive_name = f"{PROJECT}-{version}.tar.gz"
    archive_path = destination / archive_name
    write_archive(
        archive_path,
        blobs,
        version=version,
        manifest_bytes=manifest_bytes,
    )
    try:
        archive_sha256 = candidate_archive_integrity.archive_sha256(archive_path)
    except candidate_archive_integrity.CandidateArchiveError as exc:
        try:
            archive_path.unlink()
        except OSError:
            pass
        raise ReleaseBuildError(f"generated candidate exceeds archive safety envelope: {exc}") from exc

    sbom_name = f"{PROJECT}-{version}.spdx.json"
    sbom_path = destination / sbom_name
    try:
        sbom_result = generate_spdx_sbom.write_spdx_document(
            sbom_path,
            version=version,
            source_commit=source_commit,
            created=generate_spdx_sbom.commit_created_at(source_commit),
            archive_name=archive_name,
            archive_sha256=archive_sha256,
        )
    except (generate_spdx_sbom.SPDXGenerationError, ValueError, OSError) as exc:
        raise ReleaseBuildError(f"could not generate candidate SBOM: {exc}") from exc
    sbom_sha256 = sbom_result["sha256"]

    checksums_path = destination / "SHA256SUMS"
    checksums_path.write_text(
        "".join(
            [
                f"{archive_sha256}  {archive_name}\n",
                f"{sbom_sha256}  {sbom_name}\n",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )

    evidence = {
        "schema_version": 2,
        "project": PROJECT,
        "version": version,
        "maturity": MATURITY,
        "source_commit": source_commit,
        "artifact": archive_name,
        "artifact_sha256": archive_sha256,
        "content_manifest_sha256": manifest_sha256,
        "tracked_file_count": len(blobs),
        "sbom": {
            "filename": sbom_name,
            "sha256": sbom_sha256,
            "format": "SPDX",
            "version": "2.3",
            "transitional": True,
            "scope": "candidate archive plus governed validation dependency environment",
            "validation": {
                "status": "PENDING",
                "evidence_filename": "spdx-validation-evidence.json",
            },
        },
        "deterministic_archive": True,
        "deterministic_sbom": True,
        "attestation_performed": False,
        "publication_performed": False,
        "runtime_network_access": False,
    }
    evidence_path = destination / "release-evidence.json"
    evidence_path.write_bytes(_json_bytes(evidence))

    return {
        "archive": archive_path,
        "sbom": sbom_path,
        "checksums": checksums_path,
        "evidence": evidence_path,
        "evidence_data": evidence,
        "manifest": manifest,
        "sbom_document": sbom_result["document"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build deterministic, non-publishing MeaningWire candidate evidence"
    )
    parser.add_argument(
        "--output-dir",
        default="dist",
        help="directory for candidate artifacts (default: dist)",
    )
    parser.add_argument(
        "--source-commit",
        help="require HEAD to equal this exact 40-character commit SHA",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = build_release_candidate(
            args.output_dir,
            expected_source_commit=args.source_commit,
        )
    except (ReleaseBuildError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 2

    evidence = result["evidence_data"]
    print(
        "PASS: deterministic non-publishing release candidate built; "
        f"version={evidence['version']}; "
        f"source_commit={evidence['source_commit']}; "
        f"artifact_sha256={evidence['artifact_sha256']}; "
        f"sbom_sha256={evidence['sbom']['sha256']}; "
        "sbom_validation=PENDING; publication_performed=false; attestation_performed=false."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
