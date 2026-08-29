from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import release_builder  # noqa: E402
import release_readiness  # noqa: E402
import validate_spdx_sbom  # noqa: E402


class ReleaseReadinessTests(unittest.TestCase):
    def _validated_candidate(self, directory: Path) -> tuple[Path, str]:
        commit = release_builder.current_commit()
        result = release_builder.build_release_candidate(
            directory, expected_source_commit=commit
        )
        release_path = result["evidence"]
        release_evidence = json.loads(release_path.read_text(encoding="utf-8"))
        sbom_path = result["sbom"]
        validation = validate_spdx_sbom.validation_evidence(
            sbom_path=sbom_path,
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
        return directory, commit

    def test_current_candidate_passes_mechanical_threshold_but_not_launch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate_dir, commit = self._validated_candidate(Path(directory))
            report = release_readiness.evaluate_readiness(
                candidate_dir,
                expected_source_commit=commit,
                fresh_environment_verified=True,
            )

        self.assertEqual(report["release_threshold"]["status"], "PASS")
        self.assertEqual(report["overall_status"], "BLOCKED")
        self.assertIn("documentation_site_build_not_ready", report["blockers"])
        self.assertIn("governed_publication_path_not_ready", report["blockers"])
        self.assertIn("public_attestation_path_not_ready", report["blockers"])
        self.assertTrue(report["human_boundary"]["required"])
        self.assertFalse(report["publication_performed"])

    def test_fresh_environment_proof_is_required_for_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate_dir, commit = self._validated_candidate(Path(directory))
            report = release_readiness.evaluate_readiness(
                candidate_dir,
                expected_source_commit=commit,
                fresh_environment_verified=False,
            )

        self.assertEqual(report["release_threshold"]["status"], "FAIL")
        self.assertIn(
            "release_threshold:fresh_environment_verification",
            report["blockers"],
        )

    def test_source_commit_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate_dir, _commit = self._validated_candidate(Path(directory))
            with self.assertRaisesRegex(
                release_readiness.ReleaseReadinessError,
                "does not match expected",
            ):
                release_readiness.evaluate_readiness(
                    candidate_dir,
                    expected_source_commit="0" * 40,
                    fresh_environment_verified=True,
                )

    def test_sbom_tamper_blocks_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate_dir, commit = self._validated_candidate(Path(directory))
            sbom_path = candidate_dir / f"MeaningWire-{release_builder.load_version()}.spdx.json"
            sbom_path.write_bytes(sbom_path.read_bytes() + b"\n")
            report = release_readiness.evaluate_readiness(
                candidate_dir,
                expected_source_commit=commit,
                fresh_environment_verified=True,
            )

        self.assertEqual(report["release_threshold"]["status"], "FAIL")
        failing = {
            check["name"]
            for check in report["release_threshold"]["checks"]
            if check["status"] == "FAIL"
        }
        self.assertIn("candidate_sbom_digest", failing)
        self.assertIn("checksum_manifest", failing)
        self.assertIn("sbom_validation_state", failing)


if __name__ == "__main__":
    unittest.main()
