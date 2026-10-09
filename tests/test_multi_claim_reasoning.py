from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import multi_claim_reasoning  # noqa: E402
import relational_encoding  # noqa: E402
from semantic_roundtrip import canonical_bytes, reason  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "proofs" / "case-004b-bridge.json"


class MultiClaimConflictTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with FIXTURE.open("r", encoding="utf-8") as handle:
            cls.base = json.load(handle)

    def contradictory_variant(self) -> dict:
        artifact = copy.deepcopy(self.base)
        artifact["entities"].append({
            "id": "inspector-J",
            "type": "source",
            "label": "Inspector J",
        })
        artifact["claims"].append({
            "id": "claim-C2",
            "subject": "crack-C",
            "predicate": "condition",
            "object": "absent",
            "epistemic_status": "verified",
            "confidence": 0.88,
            "scope": "member-M",
            "observed_at": "2026-10-08T12:00:00-05:00",
            "source_ref": "inspector-J",
            "resolution": "unresolved",
            "significance": "conflicts_with_claim-C1",
        })
        artifact["relations"].append({
            "subject": "inspector-J",
            "predicate": "reported",
            "object": "crack-C",
        })
        artifact["events"].append({
            "id": "event-E2",
            "type": "inspection_verified",
            "occurred_at": "2026-10-08T12:00:00-05:00",
            "actor_ref": "inspector-J",
            "claim_ref": "claim-C2",
        })
        # Make both claims verified so the test exercises contradictory
        # verified observations rather than a simple reported/verified pair.
        artifact["claims"][0]["epistemic_status"] = "verified"
        artifact["events"].append({
            "id": "event-E3",
            "type": "inspection_verified",
            "occurred_at": "2026-10-08T11:00:00-05:00",
            "actor_ref": "inspector-I",
            "claim_ref": "claim-C1",
        })
        return artifact

    def test_detects_conflicting_verified_claims_without_erasing_either(self) -> None:
        artifact = self.contradictory_variant()
        result = multi_claim_reasoning.analyze_claims(artifact)
        self.assertEqual(result["claim_count"], 2)
        self.assertEqual(result["conflict_count"], 1)
        conflict = result["conflicts"][0]
        self.assertEqual(conflict["status"], "conflicting_verified_claims")
        self.assertEqual(conflict["claim_ids"], ["claim-C1", "claim-C2"])
        self.assertTrue(result["decision_boundary"]["human_review_required_for_conflict"])
        self.assertFalse(result["decision_boundary"]["automatic_resolution_performed"])
        self.assertFalse(result["decision_boundary"]["whole_bridge_unsafe_established"])
        self.assertEqual(
            {claim["object"] for claim in result["claims"]},
            {"present", "absent"},
        )

    def test_unverified_disagreement_is_not_promoted_to_verified_conflict(self) -> None:
        artifact = self.contradictory_variant()
        artifact["claims"][0]["epistemic_status"] = "reported_not_verified"
        result = multi_claim_reasoning.analyze_claims(artifact)
        self.assertEqual(result["conflict_count"], 0)
        self.assertEqual(result["claim_count"], 2)

    def test_same_claim_set_survives_json_and_relational_round_trips(self) -> None:
        artifact = self.contradictory_variant()
        expected_analysis = multi_claim_reasoning.analyze_claims(artifact)
        expected_legacy_behavior = reason(artifact)
        json_reconstructed = json.loads(canonical_bytes(artifact).decode("utf-8"))
        tuple_reconstructed = relational_encoding.decode_relational(
            json.loads(canonical_bytes(relational_encoding.encode_relational(artifact)).decode("utf-8"))
        )
        for reconstructed in (json_reconstructed, tuple_reconstructed):
            with self.subTest(path="json" if reconstructed is json_reconstructed else "relational"):
                self.assertEqual(canonical_bytes(artifact), canonical_bytes(reconstructed))
                self.assertEqual(
                    canonical_bytes(expected_analysis),
                    canonical_bytes(multi_claim_reasoning.analyze_claims(reconstructed)),
                )
                self.assertEqual(
                    canonical_bytes(expected_legacy_behavior),
                    canonical_bytes(reason(reconstructed)),
                )

    def test_duplicate_claim_ids_are_rejected(self) -> None:
        artifact = self.contradictory_variant()
        artifact["claims"][1]["id"] = artifact["claims"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate claim id"):
            multi_claim_reasoning.analyze_claims(artifact)


if __name__ == "__main__":
    unittest.main()
