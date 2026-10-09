from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import resolution_escalation_contract  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "proofs" / "case-004b-bridge.json"


class EventIdentityIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with FIXTURE.open("r", encoding="utf-8") as handle:
            cls.base = json.load(handle)

    def with_valid_escalation(self) -> dict:
        artifact = copy.deepcopy(self.base)
        artifact["events"].extend([
            {"id": "event-X1", "type": "escalation_requested",
             "occurred_at": "2026-10-08T11:00:00-05:00",
             "actor_ref": "inspector-I", "claim_ref": "claim-C1"},
            {"id": "event-X2", "type": "escalation_acknowledged",
             "occurred_at": "2026-10-08T11:05:00-05:00",
             "actor_ref": "inspector-I", "claim_ref": "claim-C1"},
        ])
        return artifact

    def test_event_ids_must_be_globally_unique(self) -> None:
        artifact = self.with_valid_escalation()
        artifact["events"][-1]["id"] = "event-E1"
        result = resolution_escalation_contract.check_contract(artifact)
        self.assertFalse(result["event_integrity"]["contract_valid"])
        self.assertEqual(result["event_integrity"]["duplicate_event_ids"], ["event-E1"])
        self.assertFalse(result["escalation"]["contract_valid"])
        self.assertIn(
            "event_ids_must_be_globally_unique",
            result["escalation"]["errors"][-1]["problems"],
        )

    def test_missing_event_id_is_rejected(self) -> None:
        artifact = copy.deepcopy(self.base)
        artifact["events"][0].pop("id")
        result = resolution_escalation_contract.check_contract(artifact)
        self.assertFalse(result["event_integrity"]["contract_valid"])
        self.assertEqual(result["event_integrity"]["missing_event_positions"], [0])

    def test_duplicate_resolution_confirmations_are_rejected(self) -> None:
        artifact = copy.deepcopy(self.base)
        artifact["claims"][0]["resolution"] = "resolved"
        confirmation = {
            "id": "event-R1", "type": "resolution_confirmed",
            "occurred_at": "2026-10-08T11:00:00-05:00",
            "actor_ref": "inspector-I", "claim_ref": "claim-C1",
        }
        artifact["events"].extend([copy.deepcopy(confirmation), copy.deepcopy(confirmation)])
        result = resolution_escalation_contract.check_contract(artifact)
        self.assertFalse(result["resolution"]["contract_valid"])
        self.assertIn(
            "resolved_state_requires_exactly_one_resolution_confirmed_event",
            result["resolution"]["errors"],
        )
        self.assertFalse(result["event_integrity"]["contract_valid"])

    def test_duplicate_elsewhere_does_not_mislabel_resolution_event(self) -> None:
        artifact = copy.deepcopy(self.base)
        artifact["events"].append(copy.deepcopy(artifact["events"][0]))
        result = resolution_escalation_contract.check_contract(artifact)
        self.assertFalse(result["event_integrity"]["contract_valid"])
        self.assertEqual(result["resolution"]["errors"], [])
        self.assertFalse(result["resolution"]["contract_valid"])

    def test_other_claim_escalation_is_not_part_of_selected_claim_sequence(self) -> None:
        artifact = self.with_valid_escalation()
        artifact["events"].append({
            "id": "event-OTHER", "type": "escalation_requested",
            "occurred_at": "2026-10-08T11:00:00-05:00",
            "actor_ref": "inspector-I", "claim_ref": "claim-C-other",
        })
        result = resolution_escalation_contract.check_contract(artifact)
        self.assertTrue(result["escalation"]["contract_valid"])
        self.assertEqual(result["escalation"]["recorded_event_ids_in_order"], ["event-X1", "event-X2"])


if __name__ == "__main__":
    unittest.main()
