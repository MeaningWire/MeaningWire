from __future__ import annotations

import sys
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import candidate_archive_integrity as integrity  # noqa: E402
import release_builder  # noqa: E402


class ExactVersionSourceBindingTests(unittest.TestCase):
    def test_load_version_reads_exact_git_source_ref(self) -> None:
        source = "a" * 40
        with mock.patch.object(
            release_builder,
            "_git_bytes",
            return_value=b"0.1.0-alpha.0\n",
        ) as git_bytes:
            version = release_builder.load_version(source)
        self.assertEqual(version, "0.1.0-alpha.0")
        git_bytes.assert_called_once_with("show", f"{source}:VERSION")

    def test_committed_version_requires_one_exact_semver_line(self) -> None:
        with mock.patch.object(
            release_builder,
            "_git_bytes",
            return_value=b"0.1.0-alpha.0\nextra\n",
        ):
            with self.assertRaisesRegex(
                release_builder.ReleaseBuildError,
                "exactly one SemVer line|valid SemVer",
            ):
                release_builder.load_version("b" * 40)

    def test_packaged_version_must_equal_declared_version(self) -> None:
        manifest = {
            "project": "MeaningWire",
            "version": "0.1.0-alpha.0",
            "source_commit": "b" * 40,
            "publication_performed": False,
            "runtime_network_access": False,
            "files": [],
        }
        with self.assertRaisesRegex(
            integrity.CandidateArchiveError,
            "packaged VERSION does not match declared release version",
        ):
            integrity.validate_manifest(
                manifest,
                {"VERSION": b"0.1.0-alpha.99\n", "RELEASE-MANIFEST.json": b"{}"},
                version="0.1.0-alpha.0",
                source_commit="b" * 40,
            )


if __name__ == "__main__":
    unittest.main()
