from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

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

    def test_version_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory, commit, version = self._candidate(Path(temp))
            with self.assertRaisesRegex(preflight.PublicationPreflightError, "canonical VERSION"):
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
