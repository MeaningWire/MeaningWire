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


class EventIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with FIXTURE.open("r", encoding="utf-8") as handle:
            cls.base = json.load(handle)

    def escalation(self) -> dict:
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

    def test_duplicate_event_id_is_reported_globally(self) -> None:
        artifact = self.escalation()
        duplicate = copy.deepcopy(artifact["events"][-1])
        duplicate["claim_ref"] = "unrelated-claim"
        artifact["events"].append(duplicate)
        result = resolution_escalation_contract.check_contract(artifact)
        self.assertFalse(result["event_integrity"]["contract_valid"])
        duplicate_errors = [
            error for error in result["event_integrity"]["errors"]
            if error["code"] == "duplicate_event_id"
        ]
        self.assertEqual(len(duplicate_errors), 1)
        self.assertEqual(duplicate_errors[0]["event_id"], "event-X2")
        self.assertFalse(result["escalation"]["contract_valid"])

    def test_duplicate_resolution_event_ids_invalidate_resolution(self) -> None:
        artifact = copy.deepcopy(self.base)
        artifact["claims"][0]["resolution"] = "resolved"
        event = {
            "id": "event-R1", "type": "resolution_confirmed",
            "occurred_at": "2026-10-08T11:00:00-05:00",
            "actor_ref": "inspector-I", "claim_ref": "claim-C1",
        }
        artifact["events"].extend([event, copy.deepcopy(event)])
        result = resolution_escalation_contract.check_contract(artifact)
        self.assertFalse(result["event_integrity"]["contract_valid"])
        self.assertFalse(result["resolution"]["contract_valid"])
        self.assertIn("resolution_event_id_must_be_unique", result["resolution"]["errors"])

    def test_missing_event_id_is_reported(self) -> None:
        artifact = self.escalation()
        artifact["events"][-1].pop("id")
        result = resolution_escalation_contract.check_contract(artifact)
        self.assertFalse(result["event_integrity"]["contract_valid"])
        self.assertEqual(result["event_integrity"]["errors"][0]["code"],
                         "event_ids_must_be_nonempty_strings")
        self.assertFalse(result["escalation"]["contract_valid"])

    def test_valid_distinct_event_ids_remain_valid(self) -> None:
        result = resolution_escalation_contract.check_contract(self.escalation())
        self.assertTrue(result["event_integrity"]["contract_valid"])
        self.assertTrue(result["escalation"]["contract_valid"])


if __name__ == "__main__":
    unittest.main()
