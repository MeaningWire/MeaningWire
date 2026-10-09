from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import cross_interpreter_consistency  # noqa: E402
import relational_encoding  # noqa: E402
from semantic_roundtrip import canonical_bytes  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "proofs" / "case-004b-bridge.json"


class CrossInterpreterConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with FIXTURE.open("r", encoding="utf-8") as handle:
            cls.base = json.load(handle)

    def conflicting_artifact(self) -> dict:
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

    def test_raw_and_temporal_views_agree_when_no_supersession_exists(self) -> None:
        view = cross_interpreter_consistency.integrated_view(self.conflicting_artifact())
        self.assertEqual(view["raw_claim_analysis"]["conflict_count"], 1)
        self.assertEqual(
            view["cross_interpreter_comparisons"][0]["relationship"],
            "raw_and_active_conflict",
        )

    def test_temporal_resolution_preserves_raw_conflict_as_history(self) -> None:
        artifact = self.conflicting_artifact()
        artifact["relations"].append({
            "subject": "claim-C2", "predicate": "supersedes", "object": "claim-C1"
        })
        view = cross_interpreter_consistency.integrated_view(artifact)
        self.assertEqual(view["raw_claim_analysis"]["conflict_count"], 1)
        self.assertEqual(
            view["temporal_analysis"]["groups"][0]["status"],
            "resolved_by_explicit_later_supersession",
        )
        self.assertEqual(
            view["cross_interpreter_comparisons"][0]["relationship"],
            "raw_evidence_conflict_but_temporally_superseded",
        )
        self.assertTrue(view["semantic_boundary"]["raw_claim_history_is_preserved"])
        self.assertTrue(view["semantic_boundary"]["temporal_supersession_does_not_delete_history"])
        self.assertEqual(
            view["semantic_boundary"]["whether_raw_conflicts_should_be_named_active_conflicts"],
            "requires_contract_decision",
        )

    def test_combined_outputs_survive_json_and_relational_round_trips(self) -> None:
        artifact = self.conflicting_artifact()
        artifact["relations"].append({
            "subject": "claim-C2", "predicate": "supersedes", "object": "claim-C1"
        })
        expected = cross_interpreter_consistency.integrated_view(artifact)
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
                canonical_bytes(cross_interpreter_consistency.integrated_view(value)),
            )

    def test_significance_remains_judgment_in_composed_view(self) -> None:
        artifact = self.conflicting_artifact()
        view = cross_interpreter_consistency.integrated_view(artifact)
        self.assertFalse(view["field_semantics"]["significance"]["action_inferred_from_judgment"])
        self.assertFalse(view["resolution_escalation_contract"]["significance"]["causes_automatic_action"])


if __name__ == "__main__":
    unittest.main()
