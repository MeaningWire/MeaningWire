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

    def test_both_views_report_conflict_when_no_supersession_exists(self) -> None:
        view = cross_interpreter_consistency.integrated_view(self.conflicting_artifact())
        self.assertEqual(view["raw_claim_analysis"]["conflict_count"], 1)
        self.assertEqual(view["conflict_views"]["historical_disagreement_count"], 1)
        self.assertEqual(view["conflict_views"]["active_unresolved_conflict_count"], 1)
        self.assertEqual(
            view["cross_interpreter_comparisons"][0]["relationship"],
            "raw_and_active_conflict",
        )

    def test_supersession_preserves_history_but_clears_active_conflict(self) -> None:
        artifact = self.conflicting_artifact()
        artifact["relations"].append({
            "subject": "claim-C2", "predicate": "supersedes", "object": "claim-C1"
        })
        view = cross_interpreter_consistency.integrated_view(artifact)
        self.assertEqual(view["raw_claim_analysis"]["conflict_count"], 1)
        self.assertEqual(view["conflict_views"]["historical_disagreement_count"], 1)
        self.assertEqual(view["conflict_views"]["active_unresolved_conflict_count"], 0)
        self.assertEqual(
            view["conflict_views"]["historical_disagreements"][0]["claim_ids"],
            ["claim-C1", "claim-C2"],
        )
        self.assertEqual(view["conflict_views"]["active_unresolved_conflicts"], [])
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
        self.assertEqual(view["semantic_boundary"]["conflict_semantics"], "both_views_separately")

    def test_invalid_supersession_does_not_hide_active_conflict(self) -> None:
        artifact = self.conflicting_artifact()
        for claim in artifact["claims"]:
            if claim.get("id") == "claim-C1":
                claim["observed_at"] = "2026-10-08T11:00:00-05:00"
            elif claim.get("id") == "claim-C2":
                claim["observed_at"] = "2026-10-08T12:00:00-05:00"
        artifact["relations"].append({
            "subject": "claim-C1", "predicate": "supersedes", "object": "claim-C2"
        })
        view = cross_interpreter_consistency.integrated_view(artifact)
        self.assertEqual(view["temporal_analysis"]["rejected_supersessions"][0]["reason"],
                         "superseding_claim_not_later")
        self.assertEqual(view["conflict_views"]["historical_disagreement_count"], 1)
        self.assertEqual(view["conflict_views"]["active_unresolved_conflict_count"], 1)

    def test_counts_are_group_counts_not_pair_counts(self) -> None:
        artifact = self.conflicting_artifact()
        artifact["claims"].append({
            "id": "claim-C3", "subject": "crack-C", "predicate": "condition",
            "object": "uncertain", "epistemic_status": "verified", "confidence": 0.7,
            "scope": "member-M", "observed_at": "2026-10-08T13:00:00-05:00",
            "source_ref": "inspector-J", "resolution": "unresolved",
            "significance": "follow_up_inspection",
        })
        view = cross_interpreter_consistency.integrated_view(artifact)
        self.assertEqual(view["conflict_views"]["historical_disagreement_count"], 1)
        self.assertEqual(view["conflict_views"]["active_unresolved_conflict_count"], 1)
        self.assertEqual(
            view["conflict_views"]["count_unit"],
            "conflicting_subject_predicate_scope_group",
        )

    def test_structured_values_with_different_key_order_are_semantically_equal(self) -> None:
        artifact = self.conflicting_artifact()
        for claim in artifact["claims"]:
            if claim.get("id") == "claim-C1":
                claim["object"] = {"surface": "crack", "depth_mm": 2}
            elif claim.get("id") == "claim-C2":
                claim["object"] = {"depth_mm": 2, "surface": "crack"}

        view = cross_interpreter_consistency.integrated_view(artifact)
        self.assertEqual(view["raw_claim_analysis"]["conflict_count"], 0)
        self.assertEqual(view["conflict_views"]["historical_disagreement_count"], 0)
        self.assertEqual(view["conflict_views"]["active_unresolved_conflict_count"], 0)
        self.assertEqual(
            view["temporal_analysis"]["groups"][0]["status"],
            "no_verified_conflict",
        )
        self.assertEqual(
            len(view["temporal_analysis"]["groups"][0]["active_values"]),
            1,
        )

    def test_numeric_values_remain_distinct_without_explicit_domain_rule(self) -> None:
        artifact = self.conflicting_artifact()
        for claim in artifact["claims"]:
            if claim.get("id") == "claim-C1":
                claim["object"] = 1
            elif claim.get("id") == "claim-C2":
                claim["object"] = 1.0

        view = cross_interpreter_consistency.integrated_view(artifact)
        self.assertEqual(view["conflict_views"]["historical_disagreement_count"], 1)
        self.assertEqual(view["conflict_views"]["active_unresolved_conflict_count"], 1)
        self.assertEqual(view["temporal_analysis"]["groups"][0]["status"],
                         "conflicting_verified_claims")

    def test_explicit_numeric_rule_normalizes_equal_numbers_in_both_views(self) -> None:
        artifact = self.conflicting_artifact()
        for claim in artifact["claims"]:
            if claim.get("id") == "claim-C1":
                claim["object"] = 1
            elif claim.get("id") == "claim-C2":
                claim["object"] = 1.0
        artifact["value_equality_rules"] = [{
            "predicate": "condition",
            "rule": "numeric_equivalence",
        }]

        view = cross_interpreter_consistency.integrated_view(artifact)
        self.assertEqual(view["conflict_views"]["historical_disagreement_count"], 0)
        self.assertEqual(view["conflict_views"]["active_unresolved_conflict_count"], 0)
        self.assertEqual(view["temporal_analysis"]["groups"][0]["status"],
                         "no_verified_conflict")
        self.assertEqual(view["temporal_analysis"]["value_equality_contract"]["rule_count"], 1)

    def test_numeric_rule_does_not_coerce_strings_or_booleans(self) -> None:
        artifact = self.conflicting_artifact()
        for claim in artifact["claims"]:
            if claim.get("id") == "claim-C1":
                claim["object"] = 1
            elif claim.get("id") == "claim-C2":
                claim["object"] = "1"
        artifact["value_equality_rules"] = [{
            "predicate": "condition",
            "rule": "numeric_equivalence",
        }]

        view = cross_interpreter_consistency.integrated_view(artifact)
        self.assertEqual(view["conflict_views"]["historical_disagreement_count"], 1)
        self.assertEqual(view["conflict_views"]["active_unresolved_conflict_count"], 1)

    def test_overlapping_equality_rules_are_rejected_as_ambiguous(self) -> None:
        artifact = self.conflicting_artifact()
        artifact["value_equality_rules"] = [
            {"predicate": "condition", "rule": "canonical_json"},
            {"predicate": "condition", "rule": "numeric_equivalence"},
        ]
        with self.assertRaisesRegex(ValueError, "ambiguous value_equality_rules"):
            cross_interpreter_consistency.integrated_view(artifact)

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


    def _round_trip_variants(self, artifact: dict) -> list[tuple[str, dict]]:
        json_reconstructed = json.loads(canonical_bytes(artifact).decode("utf-8"))
        relational_reconstructed = relational_encoding.decode_relational(
            json.loads(canonical_bytes(relational_encoding.encode_relational(artifact)).decode("utf-8"))
        )
        return [("json", json_reconstructed), ("relational", relational_reconstructed)]

    def _numeric_disagreement(self) -> dict:
        artifact = self.conflicting_artifact()
        artifact["claims"][0]["object"] = 1
        artifact["claims"][1]["object"] = 1.0
        return artifact

    def test_equality_rules_survive_json_and_relational_round_trips(self) -> None:
        artifact = self._numeric_disagreement()
        artifact["value_equality_rules"] = [{
            "predicate": "condition",
            "scope": "member-M",
            "rule": "numeric_equivalence",
        }]
        for path, reconstructed in self._round_trip_variants(artifact):
            with self.subTest(path=path):
                self.assertEqual(canonical_bytes(artifact), canonical_bytes(reconstructed))
                self.assertEqual(artifact["value_equality_rules"], reconstructed["value_equality_rules"])
                view = cross_interpreter_consistency.integrated_view(reconstructed)
                self.assertEqual(view["conflict_views"]["historical_disagreement_count"], 0)
                self.assertEqual(view["conflict_views"]["active_unresolved_conflict_count"], 0)

    def test_absent_rule_survives_round_trips_and_keeps_conservative_default(self) -> None:
        artifact = self._numeric_disagreement()
        self.assertNotIn("value_equality_rules", artifact)
        for path, reconstructed in self._round_trip_variants(artifact):
            with self.subTest(path=path):
                self.assertNotIn("value_equality_rules", reconstructed)
                view = cross_interpreter_consistency.integrated_view(reconstructed)
                self.assertEqual(view["conflict_views"]["historical_disagreement_count"], 1)
                self.assertEqual(view["conflict_views"]["active_unresolved_conflict_count"], 1)

    def test_ambiguous_rules_survive_round_trips_and_fail_closed(self) -> None:
        artifact = self._numeric_disagreement()
        artifact["value_equality_rules"] = [
            {"predicate": "condition", "scope": "member-M", "rule": "numeric_equivalence"},
            {"predicate": "condition", "rule": "canonical_json"},
        ]
        for path, reconstructed in self._round_trip_variants(artifact):
            with self.subTest(path=path):
                self.assertEqual(canonical_bytes(artifact), canonical_bytes(reconstructed))
                with self.assertRaisesRegex(ValueError, "ambiguous value_equality_rules"):
                    cross_interpreter_consistency.integrated_view(reconstructed)



if __name__ == "__main__":
    unittest.main()
