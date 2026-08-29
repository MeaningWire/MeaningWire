from __future__ import annotations

import io
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import candidate_archive_integrity as integrity  # noqa: E402
import release_builder  # noqa: E402


class CandidateArchiveIntegrityTests(unittest.TestCase):
    def _write_tar(self, path: Path, members: list[tuple[tarfile.TarInfo, bytes | None]]) -> None:
        with tarfile.open(path, "w:gz") as archive:
            for info, data in members:
                if data is None:
                    archive.addfile(info)
                else:
                    info.size = len(data)
                    archive.addfile(info, io.BytesIO(data))

    def test_current_builder_output_passes_strict_integrity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = release_builder.build_release_candidate(directory)
            evidence = json.loads(result["evidence"].read_text(encoding="utf-8"))
            files, manifest, validation = integrity.inspect_candidate(
                result["archive"],
                version=evidence["version"],
                source_commit=evidence["source_commit"],
                expected_manifest_sha256=evidence["content_manifest_sha256"],
            )
        self.assertEqual(manifest["version"], evidence["version"])
        self.assertEqual(validation["file_count"], len(files) - 1)
        self.assertIn("RELEASE-MANIFEST.json", files)

    def test_duplicate_archive_member_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.tar.gz"
            name = "MeaningWire-0.1.0-alpha.0/README.md"
            self._write_tar(
                path,
                [(tarfile.TarInfo(name), b"first"), (tarfile.TarInfo(name), b"second")],
            )
            with self.assertRaisesRegex(integrity.CandidateArchiveError, "duplicate candidate archive member"):
                integrity.read_archive(path, "0.1.0-alpha.0")

    def test_symlink_archive_member_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.tar.gz"
            info = tarfile.TarInfo("MeaningWire-0.1.0-alpha.0/link")
            info.type = tarfile.SYMTYPE
            info.linkname = "README.md"
            self._write_tar(path, [(info, None)])
            with self.assertRaisesRegex(integrity.CandidateArchiveError, "non-regular member"):
                integrity.read_archive(path, "0.1.0-alpha.0")

    def test_traversal_and_backslash_archive_paths_are_rejected(self) -> None:
        for member_name in (
            "MeaningWire-0.1.0-alpha.0/../escape",
            "MeaningWire-0.1.0-alpha.0/docs\\escape",
            "MeaningWire-0.1.0-alpha.0/docs//escape",
            "MeaningWire-0.1.0-alpha.0/./escape",
        ):
            with self.subTest(member_name=member_name), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "candidate.tar.gz"
                self._write_tar(path, [(tarfile.TarInfo(member_name), b"x")])
                with self.assertRaises(integrity.CandidateArchiveError):
                    integrity.read_archive(path, "0.1.0-alpha.0")

    def test_duplicate_manifest_path_is_rejected(self) -> None:
        data = b"hello"
        digest = __import__("hashlib").sha256(data).hexdigest()
        record = {
            "path": "README.md",
            "size": len(data),
            "sha256": digest,
            "git_object": "a" * 40,
            "mode": "0644",
        }
        manifest = {
            "project": "MeaningWire",
            "version": "0.1.0-alpha.0",
            "source_commit": "b" * 40,
            "publication_performed": False,
            "runtime_network_access": False,
            "files": [record, dict(record)],
        }
        with self.assertRaisesRegex(integrity.CandidateArchiveError, "duplicate release manifest path"):
            integrity.validate_manifest(
                manifest,
                {"README.md": data, "RELEASE-MANIFEST.json": b"{}"},
                version="0.1.0-alpha.0",
                source_commit="b" * 40,
            )

    def test_manifest_hash_size_and_unlisted_file_mismatches_are_rejected(self) -> None:
        data = b"hello"
        base_record = {
            "path": "README.md",
            "size": len(data),
            "sha256": __import__("hashlib").sha256(data).hexdigest(),
            "git_object": "a" * 40,
            "mode": "0644",
        }
        base_manifest = {
            "project": "MeaningWire",
            "version": "0.1.0-alpha.0",
            "source_commit": "b" * 40,
            "publication_performed": False,
            "runtime_network_access": False,
            "files": [base_record],
        }
        archive_files = {"README.md": data, "RELEASE-MANIFEST.json": b"{}"}

        wrong_hash = json.loads(json.dumps(base_manifest))
        wrong_hash["files"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(integrity.CandidateArchiveError, "SHA-256 mismatch"):
            integrity.validate_manifest(wrong_hash, archive_files, version="0.1.0-alpha.0", source_commit="b" * 40)

        wrong_size = json.loads(json.dumps(base_manifest))
        wrong_size["files"][0]["size"] += 1
        with self.assertRaisesRegex(integrity.CandidateArchiveError, "size mismatch"):
            integrity.validate_manifest(wrong_size, archive_files, version="0.1.0-alpha.0", source_commit="b" * 40)

        with self.assertRaisesRegex(integrity.CandidateArchiveError, "unlisted archive files"):
            integrity.validate_manifest(
                base_manifest,
                {**archive_files, "extra.txt": b"surprise"},
                version="0.1.0-alpha.0",
                source_commit="b" * 40,
            )

    def test_embedded_manifest_digest_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = release_builder.build_release_candidate(directory)
            evidence = json.loads(result["evidence"].read_text(encoding="utf-8"))
            with self.assertRaisesRegex(integrity.CandidateArchiveError, "manifest digest"):
                integrity.inspect_candidate(
                    result["archive"],
                    version=evidence["version"],
                    source_commit=evidence["source_commit"],
                    expected_manifest_sha256="0" * 64,
                )


if __name__ == "__main__":
    unittest.main()
