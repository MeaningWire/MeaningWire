from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import relational_encoding  # noqa: E402
from semantic_roundtrip import canonical_bytes, reason  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "proofs" / "case-004b-bridge.json"


class EpistemicDifferentialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with FIXTURE.open("r", encoding="utf-8") as handle:
            cls.reported = json.load(handle)

    def verified_variant(self) -> dict:
        artifact = copy.deepcopy(self.reported)
        artifact["claims"][0]["epistemic_status"] = "verified"
        artifact["events"].append({
            "id": "event-E2",
            "type": "inspection_verified",
            "occurred_at": "2026-10-08T11:00:00-05:00",
            "actor_ref": "inspector-I",
            "claim_ref": "claim-C1",
        })
        return artifact

    def test_reported_and_verified_are_semantically_distinct(self) -> None:
        reported_behavior = reason(self.reported)
        verified = self.verified_variant()
        verified_behavior = reason(verified)

        self.assertEqual(reported_behavior["T2_evidence"]["status"], "reported_not_verified")
        self.assertEqual(verified_behavior["T2_evidence"]["status"], "verified")
        self.assertFalse(reported_behavior["T4_uncertainty"]["is_verified"])
        self.assertTrue(verified_behavior["T4_uncertainty"]["is_verified"])
        self.assertTrue(reported_behavior["T4_uncertainty"]["must_not_treat_as_certain"])
        self.assertFalse(verified_behavior["T4_uncertainty"]["must_not_treat_as_certain"])
        self.assertFalse(reported_behavior["T5_time"]["current_condition_established"])
        self.assertTrue(verified_behavior["T5_time"]["current_condition_established"])
        self.assertEqual(reported_behavior["T9_decision"]["recommended_action"], "manual_review")
        self.assertEqual(verified_behavior["T9_decision"]["recommended_action"], "assess_risk")
        self.assertFalse(verified_behavior["T6_scope"]["whole_bridge_unsafe_established"])
        self.assertFalse(verified_behavior["T9_decision"]["human_approval_asserted"])

        changed_groups = [
            group for group in reported_behavior
            if canonical_bytes(reported_behavior[group]) != canonical_bytes(verified_behavior[group])
        ]
        self.assertEqual(changed_groups, ["T2_evidence", "T4_uncertainty", "T5_time", "T9_decision"])

    def test_both_meanings_survive_json_and_relational_round_trips(self) -> None:
        for artifact in (self.reported, self.verified_variant()):
            with self.subTest(status=artifact["claims"][0]["epistemic_status"]):
                expected = reason(artifact)
                json_reconstructed = json.loads(canonical_bytes(artifact).decode("utf-8"))
                tuple_encoded = relational_encoding.encode_relational(artifact)
                tuple_reconstructed = relational_encoding.decode_relational(
                    json.loads(canonical_bytes(tuple_encoded).decode("utf-8"))
                )
                self.assertEqual(canonical_bytes(artifact), canonical_bytes(json_reconstructed))
                self.assertEqual(canonical_bytes(artifact), canonical_bytes(tuple_reconstructed))
                self.assertEqual(canonical_bytes(expected), canonical_bytes(reason(json_reconstructed)))
                self.assertEqual(canonical_bytes(expected), canonical_bytes(reason(tuple_reconstructed)))

    def test_verification_event_is_additive_not_a_replacement_for_report_history(self) -> None:
        verified = self.verified_variant()
        event_types = [event["type"] for event in verified["events"]]
        self.assertIn("inspection_reported", event_types)
        self.assertIn("inspection_verified", event_types)
        behavior = reason(verified)
        self.assertTrue(behavior["T8_provenance"]["report_event_present"])


if __name__ == "__main__":
    unittest.main()
