from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import relational_encoding  # noqa: E402
import resolution_escalation_contract  # noqa: E402
from semantic_roundtrip import canonical_bytes  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "proofs" / "case-004b-bridge.json"


class ResolutionEscalationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with FIXTURE.open("r", encoding="utf-8") as handle:
            cls.base = json.load(handle)

    def resolved_artifact(self) -> dict:
        artifact = copy.deepcopy(self.base)
        artifact["claims"][0]["resolution"] = "resolved"
        artifact["events"].append({
            "id": "event-R1",
            "type": "resolution_confirmed",
            "occurred_at": "2026-10-08T11:00:00-05:00",
            "actor_ref": "inspector-I",
            "claim_ref": "claim-C1",
        })
        return artifact

    def test_resolution_label_alone_is_not_contract_valid(self) -> None:
        artifact = copy.deepcopy(self.base)
        artifact["claims"][0]["resolution"] = "resolved"
        result = resolution_escalation_contract.check_contract(artifact)
        self.assertFalse(result["resolution"]["contract_valid"])
        self.assertIn(
            "resolved_state_requires_exactly_one_resolution_confirmed_event",
            result["resolution"]["errors"],
        )

    def test_resolution_requires_typed_attributable_timestamped_event(self) -> None:
        result = resolution_escalation_contract.check_contract(self.resolved_artifact())
        self.assertTrue(result["resolution"]["contract_valid"])
        self.assertEqual(result["resolution"]["confirmed_event_ids"], ["event-R1"])

        bad = self.resolved_artifact()
        bad["events"][-1]["actor_ref"] = "unknown-actor"
        bad_result = resolution_escalation_contract.check_contract(bad)
        self.assertFalse(bad_result["resolution"]["contract_valid"])
        self.assertIn(
            "resolution_event_actor_must_reference_known_entity",
            bad_result["resolution"]["errors"],
        )

    def test_resolution_event_conflicts_with_unresolved_state(self) -> None:
        artifact = copy.deepcopy(self.base)
        artifact["events"].append({
            "id": "event-R1", "type": "resolution_confirmed",
            "occurred_at": "2026-10-08T11:00:00-05:00",
            "actor_ref": "inspector-I", "claim_ref": "claim-C1",
        })
        result = resolution_escalation_contract.check_contract(artifact)
        self.assertFalse(result["resolution"]["contract_valid"])
        self.assertIn(
            "resolution_confirmed_event_conflicts_with_non_resolved_state",
            result["resolution"]["errors"],
        )

    def test_escalation_requires_valid_explicit_transitions(self) -> None:
        artifact = copy.deepcopy(self.base)
        artifact["events"].extend([
            {"id": "event-X1", "type": "escalation_requested",
             "occurred_at": "2026-10-08T11:00:00-05:00",
             "actor_ref": "inspector-I", "claim_ref": "claim-C1"},
            {"id": "event-X2", "type": "escalation_acknowledged",
             "occurred_at": "2026-10-08T11:05:00-05:00",
             "actor_ref": "inspector-I", "claim_ref": "claim-C1"},
            {"id": "event-X3", "type": "escalation_resolved",
             "occurred_at": "2026-10-08T11:10:00-05:00",
             "actor_ref": "inspector-I", "claim_ref": "claim-C1"},
        ])
        result = resolution_escalation_contract.check_contract(artifact)
        self.assertTrue(result["escalation"]["contract_valid"])
        self.assertEqual(result["escalation"]["derived_state"], "escalation_resolved")

        invalid = copy.deepcopy(self.base)
        invalid["events"].append({
            "id": "event-X1", "type": "escalation_resolved",
            "occurred_at": "2026-10-08T11:00:00-05:00",
            "actor_ref": "inspector-I", "claim_ref": "claim-C1",
        })
        invalid_result = resolution_escalation_contract.check_contract(invalid)
        self.assertFalse(invalid_result["escalation"]["contract_valid"])
        self.assertIn(
            "invalid_escalation_state_transition",
            invalid_result["escalation"]["errors"][0]["problems"],
        )

    def test_escalation_requires_monotonic_timezone_aware_timestamps(self) -> None:
        artifact = copy.deepcopy(self.base)
        artifact["events"].extend([
            {"id": "event-X1", "type": "escalation_requested",
             "occurred_at": "2026-10-08T11:05:00-05:00",
             "actor_ref": "inspector-I", "claim_ref": "claim-C1"},
            {"id": "event-X2", "type": "escalation_acknowledged",
             "occurred_at": "2026-10-08T11:00:00-05:00",
             "actor_ref": "inspector-I", "claim_ref": "claim-C1"},
        ])
        result = resolution_escalation_contract.check_contract(artifact)
        self.assertFalse(result["escalation"]["contract_valid"])
        self.assertIn("event_time_regresses", result["escalation"]["errors"][0]["problems"])

    def test_significance_is_preserved_as_judgment_not_action(self) -> None:
        artifact = copy.deepcopy(self.base)
        artifact["claims"][0]["significance"] = "critical_review"
        result = resolution_escalation_contract.check_contract(artifact)
        self.assertEqual(result["significance"]["recorded_judgment"], "critical_review")
        self.assertFalse(result["significance"]["causes_automatic_action"])
        self.assertFalse(result["decision_boundary"]["judgment_promoted_to_action"])

    def test_contract_outputs_survive_json_and_relational_round_trips(self) -> None:
        artifact = self.resolved_artifact()
        artifact["events"].extend([
            {"id": "event-X1", "type": "escalation_requested",
             "occurred_at": "2026-10-08T11:05:00-05:00",
             "actor_ref": "inspector-I", "claim_ref": "claim-C1"},
            {"id": "event-X2", "type": "escalation_acknowledged",
             "occurred_at": "2026-10-08T11:10:00-05:00",
             "actor_ref": "inspector-I", "claim_ref": "claim-C1"},
        ])
        expected = resolution_escalation_contract.check_contract(artifact)
        reconstructed = [
            json.loads(canonical_bytes(artifact).decode("utf-8")),
            relational_encoding.decode_relational(
                json.loads(canonical_bytes(relational_encoding.encode_relational(artifact)).decode("utf-8"))
            ),
        ]
        for value in reconstructed:
            self.assertEqual(canonical_bytes(artifact), canonical_bytes(value))
            self.assertEqual(
                canonical_bytes(expected),
                canonical_bytes(resolution_escalation_contract.check_contract(value)),
            )


if __name__ == "__main__":
    unittest.main()
