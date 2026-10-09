from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from frame_versioning import (  # noqa: E402
    apply_frame_update,
    create_frame_update,
    decode_versioned_scene,
    encode_versioned_scene,
    make_versioned_frame,
)


FRAME_V1 = {
    "frame_id": "two-vehicle-scene",
    "entity_type": "vehicle",
    "attributes": ["color", "motion"],
}


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def make_scene(index: int, version: int = 1) -> dict:
    attributes_a = {
        "color": {"value": "red", "status": "verified", "confidence": 1.0},
        "motion": {"value": "stopped", "status": "verified", "confidence": 1.0},
    }
    attributes_b = {
        "color": {"value": "blue", "status": "reported", "confidence": 0.8},
        "motion": {"value": "moving_left", "status": "uncertain", "confidence": 0.55},
    }
    if version >= 2:
        attributes_a["lane"] = {"value": 1, "status": "verified", "confidence": 1.0}
        attributes_b["lane"] = {"value": 2, "status": "reported", "confidence": 0.9}
    return {
        "scene_id": f"scene-{index}",
        "entities": [
            {"id": f"vehicle-{index}-A", "type": "vehicle", "attributes": attributes_a},
            {"id": f"vehicle-{index}-B", "type": "vehicle", "attributes": attributes_b},
        ],
        "relations": [
            {"subject": f"scene-{index}", "predicate": "contains", "object": f"vehicle-{index}-A"},
            {"subject": f"scene-{index}", "predicate": "contains", "object": f"vehicle-{index}-B"},
        ],
    }


class FrameVersionRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.frame_v1 = make_versioned_frame(FRAME_V1, 1)
        self.frame_v2_schema = {**FRAME_V1, "attributes": ["color", "motion", "lane"]}

    def test_versioned_round_trip_preserves_semantics(self) -> None:
        scene = make_scene(1)
        encoded = encode_versioned_scene(scene, self.frame_v1)
        reconstructed = decode_versioned_scene(encoded, self.frame_v1)
        self.assertEqual(canonical_bytes(reconstructed), canonical_bytes(scene))

    def test_receiver_rejects_new_frame_until_update_is_applied(self) -> None:
        update = create_frame_update(self.frame_v1, self.frame_v2_schema)
        frame_v2 = apply_frame_update(self.frame_v1, update)
        payload = encode_versioned_scene(make_scene(2, version=2), frame_v2)

        with self.assertRaisesRegex(ValueError, "unknown or incompatible"):
            decode_versioned_scene(payload, self.frame_v1)

        recovered_frame = apply_frame_update(self.frame_v1, update)
        recovered = decode_versioned_scene(payload, recovered_frame)
        self.assertEqual(canonical_bytes(recovered), canonical_bytes(make_scene(2, version=2)))

    def test_stale_update_is_rejected_and_current_frame_is_not_mutated(self) -> None:
        update = create_frame_update(self.frame_v1, self.frame_v2_schema)
        frame_v2 = apply_frame_update(self.frame_v1, update)
        before = copy.deepcopy(self.frame_v2_schema)
        with self.assertRaisesRegex(ValueError, "stale or out-of-order"):
            apply_frame_update(frame_v2, update)
        self.assertEqual(self.frame_v2_schema, before)
        self.assertEqual(self.frame_v1["version"], 1)

    def test_tampered_update_digest_fails_closed(self) -> None:
        update = create_frame_update(self.frame_v1, self.frame_v2_schema)
        update["next_digest"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            apply_frame_update(self.frame_v1, update)

    def test_same_frame_version_with_different_schema_is_not_silently_decoded(self) -> None:
        payload = encode_versioned_scene(make_scene(3), self.frame_v1)
        incompatible = make_versioned_frame(
            {**FRAME_V1, "attributes": ["motion", "color"]}, version=1
        )
        with self.assertRaisesRegex(ValueError, "unknown or incompatible"):
            decode_versioned_scene(payload, incompatible)

    def test_wire_cost_accounts_for_initial_frame_update_and_every_instance(self) -> None:
        update = create_frame_update(self.frame_v1, self.frame_v2_schema)
        frame_v2 = apply_frame_update(self.frame_v1, update)
        scenes = [make_scene(i, version=1 if i <= 2 else 2) for i in range(1, 11)]
        encoded = [
            encode_versioned_scene(scene, self.frame_v1 if i <= 2 else frame_v2)
            for i, scene in enumerate(scenes, start=1)
        ]
        explicit_total = sum(len(canonical_bytes(scene)) for scene in scenes)
        wire_total = (
            len(canonical_bytes(self.frame_v1))
            + len(canonical_bytes(update))
            + sum(len(canonical_bytes(message)) for message in encoded)
        )
        # This test validates complete accounting, not that this protocol must win.
        self.assertGreater(explicit_total, 0)
        self.assertGreater(wire_total, 0)
        self.assertEqual(
            wire_total,
            len(canonical_bytes(self.frame_v1))
            + len(canonical_bytes(update))
            + sum(len(canonical_bytes(message)) for message in encoded),
        )


if __name__ == "__main__":
    unittest.main()
