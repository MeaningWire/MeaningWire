from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import validate_attestation_boundary as boundary  # noqa: E402


class AttestationBoundaryTests(unittest.TestCase):
    def test_current_repository_has_no_attestation_capable_workflow(self) -> None:
        self.assertEqual(boundary.validate_repository(), [])

    def test_oidc_write_permission_is_rejected(self) -> None:
        errors = boundary.validate_text("permissions:\n  contents: read\n  id-token: write\n")
        self.assertTrue(any("OIDC" in error for error in errors))

    def test_attestation_write_permission_is_rejected(self) -> None:
        errors = boundary.validate_text("permissions:\n  attestations: write\n")
        self.assertTrue(any("attestations write" in error for error in errors))

    def test_github_attest_action_is_rejected(self) -> None:
        errors = boundary.validate_text("- uses: actions/attest@0123456789012345678901234567890123456789\n")
        self.assertTrue(any("GitHub attestation action" in error for error in errors))

    def test_cosign_signing_is_rejected(self) -> None:
        errors = boundary.validate_text("run: cosign sign artifact.tar.gz\n")
        self.assertTrue(any("cosign" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
