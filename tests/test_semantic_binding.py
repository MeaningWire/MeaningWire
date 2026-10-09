from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import relational_encoding  # noqa: E402
from semantic_roundtrip import canonical_bytes  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "proofs" / "case-004b-bridge.json"
SCENE_PREDICATES = {"color", "motion"}


def make_scene() -> dict:
    with FIXTURE.open("r", encoding="utf-8") as handle:
        artifact = json.load(handle)
    artifact = copy.deepcopy(artifact)
    artifact["entities"].extend([
        {"id": "scene-1", "type": "scene", "label": "Scene 1"},
        {"id": "vehicle-A", "type": "vehicle", "label": "Vehicle A"},
        {"id": "vehicle-B", "type": "vehicle", "label": "Vehicle B"},
    ])
    artifact["relations"].extend([
        {"subject": "scene-1", "predicate": "contains", "object": "vehicle-A"},
        {"subject": "scene-1", "predicate": "contains", "object": "vehicle-B"},
    ])
    claims = [
        ("claim-A-color", "vehicle-A", "color", "red"),
        ("claim-A-motion", "vehicle-A", "motion", "stopped"),
        ("claim-B-color", "vehicle-B", "color", "blue"),
        ("claim-B-motion", "vehicle-B", "motion", "moving_left"),
    ]
    for claim_id, subject, predicate, value in claims:
        artifact["claims"].append({
            "id": claim_id,
            "subject": subject,
            "predicate": predicate,
            "object": value,
            "epistemic_status": "verified",
            "confidence": 1.0,
            "scope": "scene-1",
            "observed_at": "2026-10-08T12:00:00-05:00",
            "source_ref": "inspector-I",
            "resolution": "unresolved",
            "significance": "scene_description",
        })
    return artifact


def binding_signature(artifact: dict) -> tuple[tuple[str, str, str], ...]:
    """Capture which attribute value belongs to which entity."""
    rows = [
        (claim["subject"], claim["predicate"], claim["object"])
        for claim in artifact["claims"]
        if claim.get("predicate") in SCENE_PREDICATES
    ]
    return tuple(sorted(rows))


class SemanticBindingTests(unittest.TestCase):
    def test_entity_attribute_bindings_survive_json_and_relational_round_trips(self) -> None:
        artifact = make_scene()
        expected = binding_signature(artifact)
        json_round_trip = json.loads(canonical_bytes(artifact).decode("utf-8"))
        relational_round_trip = relational_encoding.decode_relational(
            json.loads(canonical_bytes(relational_encoding.encode_relational(artifact)).decode("utf-8"))
        )

        self.assertEqual(binding_signature(json_round_trip), expected)
        self.assertEqual(binding_signature(relational_round_trip), expected)
        self.assertEqual(canonical_bytes(artifact), canonical_bytes(json_round_trip))
        self.assertEqual(canonical_bytes(artifact), canonical_bytes(relational_round_trip))

    def test_same_values_with_wrong_entity_binding_are_not_semantically_equivalent(self) -> None:
        artifact = make_scene()
        original = binding_signature(artifact)
        changed = copy.deepcopy(artifact)
        claim = next(item for item in changed["claims"] if item["id"] == "claim-A-motion")
        claim["subject"] = "vehicle-B"

        original_values = sorted(value for _, _, value in original)
        changed_values = sorted(value for _, _, value in binding_signature(changed))
        self.assertEqual(original_values, changed_values)
        self.assertNotEqual(binding_signature(changed), original)

    def test_part_whole_frame_survives_round_trip(self) -> None:
        artifact = make_scene()
        encoded = relational_encoding.encode_relational(artifact)
        reconstructed = relational_encoding.decode_relational(
            json.loads(canonical_bytes(encoded).decode("utf-8"))
        )
        relations = {
            (item["subject"], item["predicate"], item["object"])
            for item in reconstructed["relations"]
        }
        self.assertIn(("scene-1", "contains", "vehicle-A"), relations)
        self.assertIn(("scene-1", "contains", "vehicle-B"), relations)
        self.assertEqual(
            {subject for subject, predicate, _ in binding_signature(reconstructed)
             if predicate == "motion"},
            {"vehicle-A", "vehicle-B"},
        )


if __name__ == "__main__":
    unittest.main()
