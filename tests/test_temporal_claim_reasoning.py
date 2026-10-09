from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import relational_encoding  # noqa: E402
import temporal_claim_reasoning  # noqa: E402
from semantic_roundtrip import canonical_bytes  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "proofs" / "case-004b-bridge.json"


class TemporalSupersessionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with FIXTURE.open("r", encoding="utf-8") as handle:
            cls.base = json.load(handle)

    def contradictory_variant(self) -> dict:
        artifact = copy.deepcopy(self.base)
        artifact["entities"].append({
            "id": "inspector-J", "type": "source", "label": "Inspector J"
        })
        artifact["claims"][0]["epistemic_status"] = "verified"
        artifact["claims"].append({
            "id": "claim-C2", "subject": "crack-C", "predicate": "condition",
            "object": "absent", "epistemic_status": "verified", "confidence": 0.88,
            "scope": "member-M", "observed_at": "2026-10-08T12:00:00-05:00",
            "source_ref": "inspector-J", "resolution": "unresolved",
            "significance": "follow_up_inspection",
        })
        artifact["relations"].append({
            "subject": "inspector-J", "predicate": "reported", "object": "crack-C"
        })
        artifact["events"].append({
            "id": "event-E2", "type": "inspection_verified",
            "occurred_at": "2026-10-08T12:00:00-05:00",
            "actor_ref": "inspector-J", "claim_ref": "claim-C2",
        })
        return artifact

    def test_conflict_remains_without_explicit_supersession(self) -> None:
        result = temporal_claim_reasoning.analyze_temporal_claims(self.contradictory_variant())
        self.assertEqual(result["groups"][0]["status"], "conflicting_verified_claims")
        self.assertEqual(result["groups"][0]["active_verified_claim_ids"], ["claim-C1", "claim-C2"])

    def test_later_explicit_supersession_resolves_active_conflict_but_preserves_history(self) -> None:
        artifact = self.contradictory_variant()
        artifact["relations"].append({
            "subject": "claim-C2", "predicate": "supersedes", "object": "claim-C1"
        })
        result = temporal_claim_reasoning.analyze_temporal_claims(artifact)
        group = result["groups"][0]
        self.assertEqual(group["status"], "resolved_by_explicit_later_supersession")
        self.assertEqual(group["active_verified_claim_ids"], ["claim-C2"])
        self.assertEqual(result["claims_preserved"], ["claim-C1", "claim-C2"])
        self.assertEqual(len(result["accepted_supersessions"]), 1)
        self.assertFalse(result["decision_boundary"]["automatic_truth_selection"])
        self.assertFalse(result["decision_boundary"]["whole_bridge_unsafe_established"])

    def test_earlier_claim_cannot_supersede_later_claim(self) -> None:
        artifact = self.contradictory_variant()
        artifact["relations"].append({
            "subject": "claim-C1", "predicate": "supersedes", "object": "claim-C2"
        })
        result = temporal_claim_reasoning.analyze_temporal_claims(artifact)
        self.assertEqual(result["groups"][0]["status"], "conflicting_verified_claims")
        self.assertEqual(result["rejected_supersessions"][0]["reason"], "superseding_claim_not_later")

    def test_supersession_cannot_cross_scope(self) -> None:
        artifact = self.contradictory_variant()
        artifact["claims"][1]["scope"] = "bridge-B"
        artifact["relations"].append({
            "subject": "claim-C2", "predicate": "supersedes", "object": "claim-C1"
        })
        result = temporal_claim_reasoning.analyze_temporal_claims(artifact)
        self.assertEqual(result["accepted_supersessions"], [])
        self.assertEqual(result["rejected_supersessions"][0]["reason"], "scope_or_subject_mismatch")

    def test_analysis_survives_json_and_relational_round_trips(self) -> None:
        artifact = self.contradictory_variant()
        artifact["relations"].append({
            "subject": "claim-C2", "predicate": "supersedes", "object": "claim-C1"
        })
        expected = temporal_claim_reasoning.analyze_temporal_claims(artifact)
        reconstructed_values = [
            json.loads(canonical_bytes(artifact).decode("utf-8")),
            relational_encoding.decode_relational(
                json.loads(canonical_bytes(relational_encoding.encode_relational(artifact)).decode("utf-8"))
            ),
        ]
        for reconstructed in reconstructed_values:
            self.assertEqual(canonical_bytes(artifact), canonical_bytes(reconstructed))
            self.assertEqual(
                canonical_bytes(expected),
                canonical_bytes(temporal_claim_reasoning.analyze_temporal_claims(reconstructed)),
            )


if __name__ == "__main__":
    unittest.main()
