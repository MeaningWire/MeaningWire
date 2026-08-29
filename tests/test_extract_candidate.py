from __future__ import annotations

import io
import json
import os
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import extract_candidate  # noqa: E402
import release_builder  # noqa: E402


class CandidateExtractionTests(unittest.TestCase):
    def test_verified_builder_candidate_extracts_to_new_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            result = release_builder.build_release_candidate(base / "candidate")
            evidence = json.loads(result["evidence"].read_text(encoding="utf-8"))
            destination = base / "extracted"
            root = extract_candidate.extract_candidate(
                result["archive"],
                result["evidence"],
                destination,
                expected_source_commit=evidence["source_commit"],
            )
            self.assertEqual(root, destination / f"MeaningWire-{evidence['version']}")
            self.assertTrue((root / "README.md").is_file())
            self.assertTrue((root / "RELEASE-MANIFEST.json").is_file())
            self.assertFalse(any(path.is_symlink() for path in root.rglob("*")))

    def test_extraction_directory_modes_are_controlled_under_permissive_umask(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            result = release_builder.build_release_candidate(base / "candidate")
            destination = base / "extracted"
            previous_umask = os.umask(0)
            try:
                root = extract_candidate.extract_candidate(
                    result["archive"], result["evidence"], destination
                )
            finally:
                os.umask(previous_umask)

            directories = [destination, root]
            directories.extend(path for path in root.rglob("*") if path.is_dir())
            self.assertGreater(len(directories), 2)
            for directory in directories:
                self.assertEqual(
                    directory.stat().st_mode & 0o777,
                    0o755,
                    f"unexpected extraction directory mode: {directory}",
                )

    def test_existing_destination_is_rejected_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            result = release_builder.build_release_candidate(base / "candidate")
            destination = base / "extracted"
            destination.mkdir()
            sentinel = destination / "sentinel.txt"
            sentinel.write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(extract_candidate.CandidateExtractionError, "already exists"):
                extract_candidate.extract_candidate(
                    result["archive"], result["evidence"], destination
                )
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

    def test_source_commit_mismatch_is_rejected_before_destination_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            result = release_builder.build_release_candidate(base / "candidate")
            destination = base / "extracted"
            with self.assertRaisesRegex(extract_candidate.CandidateExtractionError, "does not match expected"):
                extract_candidate.extract_candidate(
                    result["archive"],
                    result["evidence"],
                    destination,
                    expected_source_commit="0" * 40,
                )
            self.assertFalse(destination.exists())

    def test_tampered_archive_is_rejected_before_destination_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            result = release_builder.build_release_candidate(base / "candidate")
            archive = result["archive"]
            archive.write_bytes(archive.read_bytes() + b"tamper")
            destination = base / "extracted"
            with self.assertRaises(extract_candidate.CandidateExtractionError):
                extract_candidate.extract_candidate(
                    archive, result["evidence"], destination
                )
            self.assertFalse(destination.exists())

    def test_unsafe_archive_member_is_rejected_before_any_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            candidate_dir = base / "candidate"
            result = release_builder.build_release_candidate(candidate_dir)
            evidence = json.loads(result["evidence"].read_text(encoding="utf-8"))
            malicious = candidate_dir / result["archive"].name
            prefix = f"MeaningWire-{evidence['version']}"
            with tarfile.open(malicious, "w:gz") as archive:
                info = tarfile.TarInfo(f"{prefix}/../escape.txt")
                payload = b"escape"
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))
            destination = base / "extracted"
            outside = base / "escape.txt"
            with self.assertRaises(extract_candidate.CandidateExtractionError):
                extract_candidate.extract_candidate(
                    malicious, result["evidence"], destination
                )
            self.assertFalse(destination.exists())
            self.assertFalse(outside.exists())


if __name__ == "__main__":
    unittest.main()
