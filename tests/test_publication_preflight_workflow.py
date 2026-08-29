from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import validate_publication_preflight_workflow as validator  # noqa: E402


class PublicationPreflightWorkflowTests(unittest.TestCase):
    def test_repository_preflight_workflow_is_nonpublishing(self) -> None:
        self.assertEqual(validator.validate_workflow(), [])

    def test_automatic_trigger_is_rejected(self) -> None:
        text = validator.WORKFLOW.read_text(encoding="utf-8") + "\npush:\n"
        self.assertTrue(any("manual-only" in error for error in validator.validate_text(text)))

    def test_write_permission_is_rejected(self) -> None:
        text = validator.WORKFLOW.read_text(encoding="utf-8").replace("contents: read", "contents: write")
        errors = validator.validate_text(text)
        self.assertTrue(any("required preflight guard" in error for error in errors))
        self.assertTrue(any("forbidden" in error for error in errors))

    def test_release_or_attestation_operations_are_rejected(self) -> None:
        base = validator.WORKFLOW.read_text(encoding="utf-8")
        for fragment in ("gh release create v1", "git tag v1", "npm publish", "id-token: write"):
            with self.subTest(fragment=fragment):
                self.assertTrue(any("forbidden" in error for error in validator.validate_text(base + "\n" + fragment)))


if __name__ == "__main__":
    unittest.main()
