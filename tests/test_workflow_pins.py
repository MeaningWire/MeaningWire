from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import validate_workflow_pins  # noqa: E402


class WorkflowPinTests(unittest.TestCase):
    def test_full_commit_sha_is_accepted(self) -> None:
        self.assertTrue(
            validate_workflow_pins.validate_reference(
                "actions/checkout@11d5960a326750d5838078e36cf38b85af677262"
            )
        )

    def test_floating_tag_is_rejected(self) -> None:
        self.assertFalse(validate_workflow_pins.validate_reference("actions/checkout@v4"))

    def test_short_sha_is_rejected(self) -> None:
        self.assertFalse(validate_workflow_pins.validate_reference("actions/checkout@11d5960"))

    def test_committed_workflows_have_only_immutable_external_action_pins(self) -> None:
        checked, errors = validate_workflow_pins.validate_workflows()
        self.assertGreater(checked, 0)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
