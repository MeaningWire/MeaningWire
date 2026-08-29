from __future__ import annotations

import hashlib
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import candidate_archive_integrity as integrity  # noqa: E402
import release_builder  # noqa: E402


class ReleaseBuilderTests(unittest.TestCase):
    def test_version_is_explicit_semver_prerelease(self) -> None:
        version = release_builder.load_version()
        self.assertIn("-", version)
        self.assertTrue(version.startswith("0."))

    def test_candidate_build_is_byte_reproducible(self) -> None:
        commit = release_builder.current_commit()
        version = release_builder.load_version()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = release_builder.build_release_candidate(
                root / "first", expected_source_commit=commit
            )
            second = release_builder.build_release_candidate(
                root / "second", expected_source_commit=commit
            )

            first_bytes = first["archive"].read_bytes()
            second_bytes = second["archive"].read_bytes()
            self.assertEqual(first_bytes, second_bytes)
            self.assertEqual(first["sbom"].read_bytes(), second["sbom"].read_bytes())
            self.assertEqual(first["checksums"].read_bytes(), second["checksums"].read_bytes())
            self.assertEqual(first["evidence"].read_bytes(), second["evidence"].read_bytes())

            archive_digest = hashlib.sha256(first_bytes).hexdigest()
            sbom_digest = hashlib.sha256(first["sbom"].read_bytes()).hexdigest()
            self.assertEqual(first["evidence_data"]["artifact_sha256"], archive_digest)
            self.assertEqual(first["evidence_data"]["sbom"]["sha256"], sbom_digest)
            self.assertEqual(first["evidence_data"]["sbom"]["validation"]["status"], "PENDING")
            self.assertEqual(
                first["checksums"].read_text(encoding="utf-8"),
                "".join(
                    [
                        f"{archive_digest}  MeaningWire-{version}.tar.gz\n",
                        f"{sbom_digest}  MeaningWire-{version}.spdx.json\n",
                    ]
                ),
            )

            root_package = next(
                package
                for package in first["sbom_document"]["packages"]
                if package["SPDXID"] == "SPDXRef-Package-MeaningWire"
            )
            self.assertEqual(
                root_package["checksums"],
                [{"algorithm": "SHA256", "checksumValue": archive_digest}],
            )

    def test_archive_contains_normalized_manifest_and_public_source(self) -> None:
        commit = release_builder.current_commit()
        version = release_builder.load_version()
        with tempfile.TemporaryDirectory() as directory:
            result = release_builder.build_release_candidate(
                directory, expected_source_commit=commit
            )
            prefix = f"MeaningWire-{version}/"
            manifest_name = f"{prefix}RELEASE-MANIFEST.json"

            with tarfile.open(result["archive"], "r:gz") as archive:
                members = archive.getmembers()
                names = [member.name for member in members]
                self.assertIn(manifest_name, names)
                self.assertTrue(all(name.startswith(prefix) for name in names))
                self.assertTrue(all(".." not in Path(name).parts for name in names))
                self.assertTrue(all(not Path(name).is_absolute() for name in names))

                for member in members:
                    self.assertEqual(member.mtime, 0)
                    self.assertEqual(member.uid, 0)
                    self.assertEqual(member.gid, 0)
                    self.assertEqual(member.uname, "")
                    self.assertEqual(member.gname, "")

                extracted = archive.extractfile(manifest_name)
                self.assertIsNotNone(extracted)
                assert extracted is not None
                manifest = json.loads(extracted.read().decode("utf-8"))

            self.assertEqual(manifest["version"], version)
            self.assertEqual(manifest["source_commit"], commit)
            self.assertEqual(manifest["maturity"], "EXPERIMENTAL")
            self.assertFalse(manifest["publication_performed"])
            self.assertFalse(manifest["runtime_network_access"])

            paths = [entry["path"] for entry in manifest["files"]]
            self.assertEqual(paths, sorted(paths))
            for required in (
                "VERSION",
                "LICENSE",
                "README.md",
                "requirements-validation.txt",
                "requirements-validation.lock",
                "docs/quickstart.md",
                "tools/meaningwire.py",
                "tools/release_builder.py",
                "tools/validate_dependency_lock.py",
                "tools/generate_spdx_sbom.py",
                "tools/fetch_spdx_schema.py",
                "tools/validate_spdx_sbom.py",
                "schemas/registry.json",
                "mappings/registry.json",
                "tests/fixtures/proofs/json-object-crm-email-target.json",
            ):
                self.assertIn(required, paths)
                self.assertIn(f"{prefix}{required}", names)

    def test_tracked_blob_size_limit_fails_before_blob_load(self) -> None:
        object_sha = "a" * 40
        tree = f"100644 blob {object_sha}\tlarge.bin\0".encode()

        def git_bytes(*args: str) -> bytes:
            if args[:2] == ("ls-tree", "-r"):
                return tree
            if args == ("cat-file", "-s", object_sha):
                return b"5\n"
            if args == ("cat-file", "blob", object_sha):
                raise AssertionError("over-limit blob must not be loaded")
            raise AssertionError(f"unexpected git call: {args}")

        with mock.patch.object(release_builder, "_git_bytes", side_effect=git_bytes):
            with mock.patch.object(integrity, "MAX_MEMBER_BYTES", 4):
                with self.assertRaisesRegex(release_builder.ReleaseBuildError, "member safety limit"):
                    release_builder.tracked_blobs()

    def test_tracked_total_limit_fails_before_blob_load(self) -> None:
        object_sha = "b" * 40
        tree = f"100644 blob {object_sha}\tlarge.bin\0".encode()

        def git_bytes(*args: str) -> bytes:
            if args[:2] == ("ls-tree", "-r"):
                return tree
            if args == ("cat-file", "-s", object_sha):
                return b"5\n"
            if args == ("cat-file", "blob", object_sha):
                raise AssertionError("over-limit blob must not be loaded")
            raise AssertionError(f"unexpected git call: {args}")

        with mock.patch.object(release_builder, "_git_bytes", side_effect=git_bytes):
            with mock.patch.object(integrity, "MAX_MEMBER_BYTES", 10):
                with mock.patch.object(integrity, "MAX_TOTAL_FILE_BYTES", 4):
                    with self.assertRaisesRegex(release_builder.ReleaseBuildError, "before loading"):
                        release_builder.tracked_blobs()

    def test_tracked_member_count_reserves_manifest_slot(self) -> None:
        object_sha = "c" * 40
        tree = f"100644 blob {object_sha}\tone.txt\0".encode()
        with mock.patch.object(release_builder, "_git_bytes", return_value=tree):
            with mock.patch.object(integrity, "MAX_MEMBER_COUNT", 1):
                with self.assertRaisesRegex(release_builder.ReleaseBuildError, "member safety limit"):
                    release_builder.tracked_blobs()

    def test_generated_manifest_counts_toward_total_limit(self) -> None:
        blob = release_builder.TrackedBlob(
            path="one.txt", mode=0o644, object_sha="d" * 40, data=b"x"
        )
        with mock.patch.object(integrity, "MAX_MEMBER_COUNT", 10):
            with mock.patch.object(integrity, "MAX_MEMBER_BYTES", 10):
                with mock.patch.object(integrity, "MAX_TOTAL_FILE_BYTES", 4):
                    with self.assertRaisesRegex(release_builder.ReleaseBuildError, "release manifest"):
                        release_builder._validate_generated_manifest_limits([blob], b"1234")

    def test_oversized_generated_archive_is_removed_before_evidence_promotion(self) -> None:
        commit = release_builder.current_commit()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with mock.patch.object(integrity, "MAX_ARCHIVE_BYTES", 1):
                with self.assertRaisesRegex(release_builder.ReleaseBuildError, "archive safety envelope"):
                    release_builder.build_release_candidate(root, expected_source_commit=commit)
            self.assertFalse(any(root.glob("*.tar.gz")))
            self.assertFalse((root / "release-evidence.json").exists())
            self.assertFalse((root / "SHA256SUMS").exists())

    def test_expected_commit_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(
                release_builder.ReleaseBuildError,
                "expected source commit",
            ):
                release_builder.build_release_candidate(
                    directory,
                    expected_source_commit="0" * 40,
                )


if __name__ == "__main__":
    unittest.main()
