from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from frame_encoding import decode_scene, encode_scene  # noqa: E402
from semantic_roundtrip import canonical_bytes  # noqa: E402

FRAME = {
    "frame_id": "two-vehicle-scene-v1",
    "entity_type": "vehicle",
    "attributes": ["color", "motion"],
}


def make_scene(index: int = 1) -> dict:
    return {
        "scene_id": f"scene-{index}",
        "entities": [
            {
                "id": f"vehicle-{index}-A",
                "type": "vehicle",
                "attributes": {
                    "color": {"value": "red", "status": "verified", "confidence": 1.0},
                    "motion": {"value": "stopped", "status": "verified", "confidence": 1.0},
                },
            },
            {
                "id": f"vehicle-{index}-B",
                "type": "vehicle",
                "attributes": {
                    "color": {"value": "blue", "status": "reported", "confidence": 0.8},
                    "motion": {"value": "moving_left", "status": "uncertain", "confidence": 0.55},
                },
            },
        ],
        "relations": [
            {"subject": f"scene-{index}", "predicate": "contains", "object": f"vehicle-{index}-A"},
            {"subject": f"scene-{index}", "predicate": "contains", "object": f"vehicle-{index}-B"},
        ],
    }


class FrameReconstructionTests(unittest.TestCase):
    def test_frame_reference_round_trip_preserves_bindings_and_uncertainty(self) -> None:
        scene = make_scene()
        encoded = encode_scene(scene, FRAME)
        reconstructed = decode_scene(json.loads(canonical_bytes(encoded).decode("utf-8")), FRAME)
        self.assertEqual(canonical_bytes(reconstructed), canonical_bytes(scene))
        self.assertEqual(
            reconstructed["entities"][1]["attributes"]["motion"],
            {"value": "moving_left", "status": "uncertain", "confidence": 0.55},
        )

    def test_wrong_or_missing_frame_reference_fails_closed(self) -> None:
        encoded = encode_scene(make_scene(), FRAME)
        encoded["frame_ref"] = "unknown-frame"
        with self.assertRaisesRegex(ValueError, "unknown or mismatched"):
            decode_scene(encoded, FRAME)

    def test_frame_attribute_order_mismatch_is_detected_by_round_trip(self) -> None:
        encoded = encode_scene(make_scene(), FRAME)
        reversed_frame = {**FRAME, "attributes": ["motion", "color"]}
        reconstructed = decode_scene(encoded, reversed_frame)
        self.assertNotEqual(canonical_bytes(reconstructed), canonical_bytes(make_scene()))

    def test_amortized_total_cost_includes_shared_frame_once(self) -> None:
        scenes = [make_scene(i) for i in range(1, 11)]
        explicit_total = sum(len(canonical_bytes(scene)) for scene in scenes)
        frame_total = len(canonical_bytes(FRAME)) + sum(
            len(canonical_bytes(encode_scene(scene, FRAME))) for scene in scenes
        )
        self.assertLess(frame_total, explicit_total)
        self.assertGreater(explicit_total - frame_total, 0)

    def test_frame_encoder_rejects_unrepresented_attributes(self) -> None:
        scene = make_scene()
        scene["entities"][0]["attributes"]["temperature"] = {
            "value": 20, "status": "verified", "confidence": 1.0
        }
        with self.assertRaisesRegex(ValueError, "attributes do not match"):
            encode_scene(scene, FRAME)


if __name__ == "__main__":
    unittest.main()
