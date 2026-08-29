from __future__ import annotations

import json
import os
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import release_builder  # noqa: E402
import release_publication_preflight as preflight  # noqa: E402
import release_readiness  # noqa: E402
import validate_spdx_sbom  # noqa: E402


class PublicationPreflightTests(unittest.TestCase):
    def _candidate(self, directory: Path) -> tuple[Path, str, str]:
        commit = release_builder.current_commit()
        version = release_builder.load_version()
        result = release_builder.build_release_candidate(directory, expected_source_commit=commit)
        release_path = result["evidence"]
        release_evidence = json.loads(release_path.read_text(encoding="utf-8"))
        validation = validate_spdx_sbom.validation_evidence(
            sbom_path=result["sbom"],
            sbom_sha256=release_evidence["sbom"]["sha256"],
            schema_sha256="c" * 64,
            policy={
                "scope": "candidate archive plus governed validation dependency environment",
                "locked_dependency_count": 6,
                "package_count": 7,
                "relationship_count": 6,
            },
        )
        validation_path = directory / "spdx-validation-evidence.json"
        validation_bytes = validate_spdx_sbom.write_json(validation_path, validation)
        validate_spdx_sbom.promote_release_evidence(
            release_path,
            release_evidence,
            validation_evidence_path=validation_path,
            validation_evidence_bytes=validation_bytes,
        )
        readiness = release_readiness.evaluate_readiness(
            directory,
            expected_source_commit=commit,
            fresh_environment_verified=True,
            documentation_build_verified=True,
        )
        (directory / "release-readiness.json").write_text(
            json.dumps(readiness, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return directory, commit, version

    def _evaluate(self, directory: Path, commit: str, version: str, **overrides):
        args = {
            "source_commit": commit,
            "requested_version": version,
            "tag_name": f"v{version}",
            "release_title": f"MeaningWire {version}",
            "prerelease": True,
            "release_notes_source": f"docs/releases/{version}.md",
            "fresh_environment_verified": True,
            "documentation_build_verified": True,
        }
        args.update(overrides)
        return preflight.evaluate_preflight(directory, **args)

    def test_exact_candidate_metadata_renders_nonpublishing_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory, commit, version = self._candidate(Path(temp))
            report, notes = self._evaluate(directory, commit, version)
        self.assertEqual(report["source_commit"], commit)
        self.assertEqual(report["tag_name"], f"v{version}")
        self.assertFalse(report["publication_performed"])
        self.assertFalse(report["attestation_performed"])
        self.assertEqual(report["human_boundary"]["status"], "PENDING")
        self.assertIn(b"Prepublication evidence", notes)
        self.assertIn(commit.encode(), notes)

    def test_dirty_workspace_version_cannot_change_preflight_identity(self) -> None:
        with tempfile.TemporaryDirectory() as candidate_temp, tempfile.TemporaryDirectory() as workspace_temp:
            directory, commit, version = self._candidate(Path(candidate_temp))
            workspace = Path(workspace_temp)
            (workspace / "VERSION").write_text("9.9.9-dirty\n", encoding="utf-8")
            original_cwd = Path.cwd()
            try:
                os.chdir(workspace)
                report, _notes = self._evaluate(directory, commit, version)
            finally:
                os.chdir(original_cwd)
        self.assertEqual(report["version"], version)
        self.assertEqual(report["tag_name"], f"v{version}")
        self.assertEqual(report["release_title"], f"MeaningWire {version}")
        self.assertTrue(report["prerelease"])

    def test_preflight_does_not_use_raw_tar_member_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory, commit, version = self._candidate(Path(temp))
            with mock.patch.object(
                tarfile.TarFile,
                "getmember",
                side_effect=AssertionError("raw tar member lookup must not be used"),
            ):
                report, _notes = self._evaluate(directory, commit, version)
        self.assertEqual(report["source_commit"], commit)

    def test_candidate_mutation_during_note_inspection_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory, _commit, version = self._candidate(Path(temp))
            release_evidence = json.loads(
                (directory / "release-evidence.json").read_text(encoding="utf-8")
            )
            archive = directory / release_evidence["artifact"]
            original_inspect = preflight.candidate_archive_integrity.inspect_candidate

            def inspect_then_mutate(*args, **kwargs):
                result = original_inspect(*args, **kwargs)
                archive.write_bytes(archive.read_bytes() + b"changed-after-inspection")
                return result

            with mock.patch.object(
                preflight.candidate_archive_integrity,
                "inspect_candidate",
                side_effect=inspect_then_mutate,
            ):
                with self.assertRaisesRegex(
                    preflight.PublicationPreflightError,
                    "changed during stable bounded inspection",
                ):
                    preflight._candidate_member(
                        directory,
                        release_evidence,
                        f"docs/releases/{version}.md",
                    )

    def test_candidate_digest_change_after_readiness_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory, _commit, version = self._candidate(Path(temp))
            release_evidence = json.loads(
                (directory / "release-evidence.json").read_text(encoding="utf-8")
            )
            archive = directory / release_evidence["artifact"]
            archive.write_bytes(archive.read_bytes() + b"changed-before-inspection")
            with self.assertRaisesRegex(
                preflight.PublicationPreflightError,
                "SHA-256 does not match release evidence",
            ):
                preflight._candidate_member(
                    directory,
                    release_evidence,
                    f"docs/releases/{version}.md",
                )

    def test_version_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory, commit, version = self._candidate(Path(temp))
            with self.assertRaisesRegex(preflight.PublicationPreflightError, "exact candidate VERSION"):
                self._evaluate(directory, commit, version, requested_version="0.1.0-alpha.99")

    def test_tag_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory, commit, version = self._candidate(Path(temp))
            with self.assertRaisesRegex(preflight.PublicationPreflightError, "tag name"):
                self._evaluate(directory, commit, version, tag_name="wrong-tag")

    def test_title_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory, commit, version = self._candidate(Path(temp))
            with self.assertRaisesRegex(preflight.PublicationPreflightError, "release title"):
                self._evaluate(directory, commit, version, release_title="MeaningWire")

    def test_prerelease_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory, commit, version = self._candidate(Path(temp))
            with self.assertRaisesRegex(preflight.PublicationPreflightError, "prerelease classification"):
                self._evaluate(directory, commit, version, prerelease=False)

    def test_unsafe_release_notes_path_fails_closed(self) -> None:
        with self.assertRaises(preflight.PublicationPreflightError):
            preflight._safe_repo_path("../release.md")
        with self.assertRaises(preflight.PublicationPreflightError):
            preflight._safe_repo_path("/release.md")
        with self.assertRaises(preflight.PublicationPreflightError):
            preflight._safe_repo_path("docs\\release.md")


if __name__ == "__main__":
    unittest.main()
