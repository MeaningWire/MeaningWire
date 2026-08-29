#!/usr/bin/env python3
"""Safely extract a verified MeaningWire candidate without trusting tar extraction."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import candidate_archive_integrity

PROJECT = "MeaningWire"


class CandidateExtractionError(ValueError):
    """Raised when verified candidate extraction cannot proceed safely."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CandidateExtractionError(f"cannot read release evidence {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CandidateExtractionError("release evidence root must be an object")
    return value


def _mode_map(manifest: dict[str, Any]) -> dict[str, int]:
    records = manifest.get("files")
    if not isinstance(records, list):
        raise CandidateExtractionError("release manifest files must be an array")
    modes: dict[str, int] = {}
    for record in records:
        if not isinstance(record, dict):
            raise CandidateExtractionError("release manifest file record is invalid")
        path = record.get("path")
        mode = record.get("mode")
        if not isinstance(path, str) or mode not in {"0644", "0755"}:
            raise CandidateExtractionError("release manifest path/mode is invalid")
        modes[path] = 0o755 if mode == "0755" else 0o644
    return modes


def extract_candidate(
    archive_path: str | Path,
    release_evidence_path: str | Path,
    destination: str | Path,
    *,
    expected_source_commit: str | None = None,
) -> Path:
    """Validate the complete archive first, then write it into a new destination."""

    archive = Path(archive_path).resolve()
    evidence_path = Path(release_evidence_path).resolve()
    destination_path = Path(destination).resolve()
    evidence = _read_json(evidence_path)

    version = evidence.get("version")
    source_commit = evidence.get("source_commit")
    archive_name = evidence.get("artifact")
    manifest_sha256 = evidence.get("content_manifest_sha256")
    if not isinstance(version, str) or not version:
        raise CandidateExtractionError("release evidence version is invalid")
    if not isinstance(source_commit, str):
        raise CandidateExtractionError("release evidence source_commit is invalid")
    if expected_source_commit is not None and source_commit != expected_source_commit:
        raise CandidateExtractionError(
            f"candidate source commit {source_commit} does not match expected {expected_source_commit}"
        )
    if archive.name != archive_name:
        raise CandidateExtractionError(
            f"archive filename {archive.name!r} does not match release evidence {archive_name!r}"
        )

    try:
        files, manifest, _validation = candidate_archive_integrity.inspect_candidate(
            archive,
            version=version,
            source_commit=source_commit,
            expected_manifest_sha256=manifest_sha256,
        )
    except candidate_archive_integrity.CandidateArchiveError as exc:
        raise CandidateExtractionError(f"candidate archive integrity failure: {exc}") from exc

    if destination_path.exists():
        raise CandidateExtractionError(
            f"extraction destination already exists; refusing overwrite: {destination_path}"
        )

    modes = _mode_map(manifest)
    root = destination_path / f"{PROJECT}-{version}"
    try:
        destination_path.mkdir(parents=True, exist_ok=False)
        root.mkdir(mode=0o755)
        for relative in sorted(files):
            output = root / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            if output.exists() or output.is_symlink():
                raise CandidateExtractionError(f"refusing extraction overwrite: {relative}")
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            mode = 0o644 if relative == "RELEASE-MANIFEST.json" else modes[relative]
            fd = os.open(output, flags, mode)
            try:
                with os.fdopen(fd, "wb", closefd=True) as handle:
                    handle.write(files[relative])
            except Exception:
                try:
                    os.close(fd)
                except OSError:
                    pass
                raise
            os.chmod(output, mode)
    except CandidateExtractionError:
        raise
    except OSError as exc:
        raise CandidateExtractionError(f"candidate extraction failed: {exc}") from exc

    return root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and safely extract a MeaningWire release candidate"
    )
    parser.add_argument("--archive", required=True, help="candidate .tar.gz path")
    parser.add_argument(
        "--release-evidence", required=True, help="release-evidence.json path"
    )
    parser.add_argument("--destination", required=True, help="new extraction directory")
    parser.add_argument(
        "--source-commit", help="require release evidence to match this exact source commit"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = extract_candidate(
            args.archive,
            args.release_evidence,
            args.destination,
            expected_source_commit=args.source_commit,
        )
    except CandidateExtractionError as exc:
        print(f"ERROR: {exc}")
        return 2
    print(f"PASS: safely extracted verified candidate to {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
