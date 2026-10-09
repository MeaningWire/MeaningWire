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
import temporal_claim_reasoning  # noqa: E402
from semantic_roundtrip import canonical_bytes, reason  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "proofs" / "case-004b-bridge.json"


class SemanticPermutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with FIXTURE.open("r", encoding="utf-8") as handle:
            cls.base = json.load(handle)

    def multi_claim_artifact(self) -> dict:
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
        artifact["claims"].append({
            "id": "claim-C3", "subject": "member-M", "predicate": "maintenance_state",
            "object": "inspected", "epistemic_status": "verified", "confidence": 0.99,
            "scope": "member-M", "observed_at": "2026-10-08T12:30:00-05:00",
            "source_ref": "inspector-I", "resolution": "resolved",
            "significance": "routine_record",
        })
        artifact["relations"].append({
            "subject": "inspector-J", "predicate": "reported", "object": "crack-C"
        })
        artifact["events"].append({
            "id": "event-E2", "type": "inspection_verified",
            "occurred_at": "2026-10-08T12:00:00-05:00",
            "actor_ref": "inspector-J", "claim_ref": "claim-C2",
        })
        artifact["events"].append({
            "id": "event-E3", "type": "inspection_verified",
            "occurred_at": "2026-10-08T12:30:00-05:00",
            "actor_ref": "inspector-I", "claim_ref": "claim-C3",
        })
        return artifact

    def test_claim_entity_and_relation_permutations_do_not_change_reasoning(self) -> None:
        original = self.multi_claim_artifact()
        permuted = copy.deepcopy(original)
        for field in ("claims", "entities", "relations"):
            permuted[field] = list(reversed(permuted[field]))

        self.assertEqual(
            canonical_bytes(multi_claim_reasoning.analyze_claims(original)),
            canonical_bytes(multi_claim_reasoning.analyze_claims(permuted)),
        )
        self.assertEqual(
            canonical_bytes(temporal_claim_reasoning.analyze_temporal_claims(original)),
            canonical_bytes(temporal_claim_reasoning.analyze_temporal_claims(permuted)),
        )
        self.assertEqual(canonical_bytes(reason(original)), canonical_bytes(reason(permuted)))

    def test_event_history_order_is_preserved_not_normalized_away(self) -> None:
        artifact = self.multi_claim_artifact()
        reversed_events = copy.deepcopy(artifact)
        reversed_events["events"] = list(reversed(reversed_events["events"]))
        self.assertNotEqual(canonical_bytes(artifact), canonical_bytes(reversed_events))
        self.assertEqual(
            canonical_bytes(multi_claim_reasoning.analyze_claims(artifact)),
            canonical_bytes(multi_claim_reasoning.analyze_claims(reversed_events)),
        )

    def test_permuted_artifact_still_round_trips_structurally(self) -> None:
        artifact = self.multi_claim_artifact()
        artifact["claims"].reverse()
        artifact["relations"].reverse()
        encoded = relational_encoding.encode_relational(artifact)
        reconstructed = relational_encoding.decode_relational(
            json.loads(canonical_bytes(encoded).decode("utf-8"))
        )
        self.assertEqual(canonical_bytes(artifact), canonical_bytes(reconstructed))
        self.assertEqual(
            canonical_bytes(multi_claim_reasoning.analyze_claims(artifact)),
            canonical_bytes(multi_claim_reasoning.analyze_claims(reconstructed)),
        )
        self.assertEqual(
            canonical_bytes(temporal_claim_reasoning.analyze_temporal_claims(artifact)),
            canonical_bytes(temporal_claim_reasoning.analyze_temporal_claims(reconstructed)),
        )


if __name__ == "__main__":
    unittest.main()
