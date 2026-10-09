from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import artifact_semantics  # noqa: E402
import relational_encoding  # noqa: E402
from semantic_roundtrip import canonical_bytes  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "proofs" / "case-004b-bridge.json"


class ArtifactSemanticSensitivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with FIXTURE.open("r", encoding="utf-8") as handle:
            cls.base = json.load(handle)

    def test_resolution_significance_and_escalation_each_change_observable_output(self) -> None:
        original = artifact_semantics.interpret_artifact(self.base)

        resolution_variant = copy.deepcopy(self.base)
        resolution_variant["claims"][0]["resolution"] = "resolved"
        resolution_result = artifact_semantics.interpret_artifact(resolution_variant)
        self.assertNotEqual(original["resolution"], resolution_result["resolution"])
        for group in ("claim_dimensions", "significance", "escalation_history"):
            self.assertEqual(original[group], resolution_result[group])

        significance_variant = copy.deepcopy(self.base)
        significance_variant["claims"][0]["significance"] = "critical_review"
        significance_result = artifact_semantics.interpret_artifact(significance_variant)
        self.assertNotEqual(original["significance"], significance_result["significance"])
        for group in ("claim_dimensions", "resolution", "escalation_history"):
            self.assertEqual(original[group], significance_result[group])
        self.assertFalse(significance_result["significance"]["action_inferred_from_judgment"])

        escalation_variant = copy.deepcopy(self.base)
        escalation_variant["events"].append({
            "id": "event-E2",
            "type": "escalation_requested",
            "occurred_at": "2026-10-08T12:00:00-05:00",
            "actor_ref": "inspector-I",
            "claim_ref": "claim-C1",
        })
        escalation_result = artifact_semantics.interpret_artifact(escalation_variant)
        self.assertNotEqual(original["escalation_history"], escalation_result["escalation_history"])
        for group in ("claim_dimensions", "resolution", "significance"):
            self.assertEqual(original[group], escalation_result[group])
        self.assertEqual(escalation_result["escalation_history"]["count"], 1)

    def test_unrelated_claim_escalation_is_not_attributed_to_selected_claim(self) -> None:
        artifact = copy.deepcopy(self.base)
        artifact["events"].append({
            "id": "event-E2",
            "type": "escalation_requested",
            "occurred_at": "2026-10-08T12:00:00-05:00",
            "actor_ref": "inspector-I",
            "claim_ref": "claim-C-other",
        })
        result = artifact_semantics.interpret_artifact(artifact)
        self.assertEqual(result["escalation_history"]["count"], 0)

    def test_selected_semantics_survive_json_and_relational_round_trips(self) -> None:
        artifact = copy.deepcopy(self.base)
        artifact["claims"][0]["resolution"] = "resolved"
        artifact["claims"][0]["significance"] = "critical_review"
        artifact["events"].extend([
            {
                "id": "event-E2", "type": "escalation_requested",
                "occurred_at": "2026-10-08T11:00:00-05:00",
                "actor_ref": "inspector-I", "claim_ref": "claim-C1",
            },
            {
                "id": "event-E3", "type": "escalation_acknowledged",
                "occurred_at": "2026-10-08T11:05:00-05:00",
                "actor_ref": "inspector-I", "claim_ref": "claim-C1",
            },
        ])
        expected = artifact_semantics.interpret_artifact(artifact)
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
                canonical_bytes(artifact_semantics.interpret_artifact(value)),
            )

    def test_missing_or_duplicate_selected_claim_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "expected exactly one claim"):
            artifact_semantics.interpret_artifact(self.base, "missing")
        duplicate = copy.deepcopy(self.base)
        duplicate["claims"].append(copy.deepcopy(duplicate["claims"][0]))
        with self.assertRaisesRegex(ValueError, "expected exactly one claim"):
            artifact_semantics.interpret_artifact(duplicate)


if __name__ == "__main__":
    unittest.main()
