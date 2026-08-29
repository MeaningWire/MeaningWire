from __future__ import annotations

import hashlib
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

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
            self.assertEqual(first["checksums"].read_bytes(), second["checksums"].read_bytes())
            self.assertEqual(first["evidence"].read_bytes(), second["evidence"].read_bytes())

            digest = hashlib.sha256(first_bytes).hexdigest()
            self.assertEqual(first["evidence_data"]["artifact_sha256"], digest)
            self.assertEqual(
                first["checksums"].read_text(encoding="utf-8"),
                f"{digest}  MeaningWire-{version}.tar.gz\n",
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
                "schemas/registry.json",
                "mappings/registry.json",
                "tests/fixtures/proofs/json-object-crm-email-target.json",
            ):
                self.assertIn(required, paths)
                self.assertIn(f"{prefix}{required}", names)

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
