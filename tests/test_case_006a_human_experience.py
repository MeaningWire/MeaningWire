from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from case_006a_human_experience import (  # noqa: E402
    CODEBOOK_VERSION,
    decode_experience,
    decode_state,
    distortion,
    encode_experience,
    encode_state,
    maximum_absolute_error,
    quantize,
)


def state(state_id: str, state_type: str, source_kind: str = "self_report") -> dict:
    values = {
        "hope": {
            "goal_importance": 0.91,
            "perceived_possibility": 0.68,
            "personal_agency": 0.54,
            "expectation_confidence": 0.42,
        },
        "shame": {
            "negative_self_evaluation": 0.81,
            "perceived_exposure": 0.62,
            "belonging_threat": 0.77,
            "norm_violation_belief": 0.73,
        },
        "trust": {
            "perceived_reliability": 0.72,
            "perceived_benevolence": 0.65,
            "willingness_to_be_vulnerable": 0.49,
            "evidence_confidence": 0.58,
        },
    }
    return {
        "state_id": state_id,
        "subject_ref": "person:synthetic-01",
        "state_type": state_type,
        "target_ref": "goal:synthetic-01" if state_type == "hope" else "person:synthetic-02",
        "context_ref": "event:synthetic-01",
        "dimensions": values[state_type],
        "source_kind": source_kind,
        "confidence": 0.83,
        "observed_at": "2026-10-09T12:00:00Z",
    }


class HumanExperienceQuantizationTests(unittest.TestCase):
    def test_numeric_quantization_has_bounded_scalar_error(self) -> None:
        for i in range(1001):
            value = i / 1000
            reconstructed = quantize(value) / 7
            self.assertLessEqual(abs(value - reconstructed), maximum_absolute_error() + 1e-12)

    def test_state_round_trip_preserves_type_target_context_and_provenance(self) -> None:
        for kind in ("hope", "shame", "trust"):
            original = state(f"state-{kind}", kind)
            decoded = decode_state(encode_state(original))
            report = distortion(original, decoded)
            self.assertTrue(report["non_numeric_metadata_preserved"])
            self.assertLessEqual(report["max_dimension_error"], maximum_absolute_error() + 1e-12)
            self.assertLessEqual(report["confidence_absolute_error"], maximum_absolute_error() + 1e-12)
            for key in ("state_id", "subject_ref", "state_type", "target_ref", "context_ref",
                        "source_kind", "observed_at"):
                self.assertEqual(decoded[key], original[key])

    def test_self_report_is_not_silently_changed_to_inference(self) -> None:
        original = state("state-hope", "hope", "self_report")
        decoded = decode_state(encode_state(original))
        self.assertEqual(decoded["source_kind"], "self_report")
        inferred = state("state-hope-inferred", "hope", "inference")
        self.assertNotEqual(
            decode_state(encode_state(inferred))["source_kind"],
            decoded["source_kind"],
        )

    def test_hope_and_shame_can_coexist_without_being_collapsed(self) -> None:
        original = [state("state-hope", "hope"), state("state-shame", "shame")]
        encoded = encode_experience(original)
        decoded = decode_experience(encoded)
        self.assertEqual([item["state_type"] for item in decoded], ["hope", "shame"])
        self.assertEqual([item["state_id"] for item in decoded], ["state-hope", "state-shame"])

    def test_unknown_codebook_fails_closed(self) -> None:
        encoded = encode_state(state("state-hope", "hope"))
        encoded["codebook"] = "unknown-v9"
        with self.assertRaises(ValueError):
            decode_state(encoded)

    def test_missing_or_reordered_dimensions_are_not_guessed(self) -> None:
        original = state("state-hope", "hope")
        original["dimensions"].pop("personal_agency")
        with self.assertRaises(ValueError):
            encode_state(original)

    def test_duplicate_state_ids_fail_closed(self) -> None:
        repeated = state("same-id", "hope")
        with self.assertRaises(ValueError):
            encode_experience([repeated, dict(repeated)])

    def test_quantized_values_are_levels_not_claims_of_probability(self) -> None:
        encoded = encode_state(state("state-trust", "trust"))
        self.assertEqual(encoded["codebook"], CODEBOOK_VERSION)
        self.assertTrue(all(isinstance(level, int) and 0 <= level <= 7
                            for level in encoded["dimension_levels"]))


if __name__ == "__main__":
    unittest.main()
