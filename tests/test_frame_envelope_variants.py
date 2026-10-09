from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from frame_cost_model import make_scene  # noqa: E402
from frame_envelope_variants import (  # noqa: E402
    compare_envelope_costs,
    decode_compact_scene,
    encode_compact_scene,
)
from frame_versioning import make_versioned_frame  # noqa: E402


class CompactFrameEnvelopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = {
            "frame_id": "vehicle-observation",
            "entity_type": "vehicle",
            "attributes": ["color", "motion"],
        }
        self.frame = make_versioned_frame(self.schema, 1)
        self.scene = make_scene(3, self.schema)

    def test_compact_envelope_round_trips_exact_semantics(self) -> None:
        encoded = encode_compact_scene(self.scene, self.frame)
        self.assertEqual(decode_compact_scene(encoded, self.frame), self.scene)
        self.assertEqual(set(encoded), {"frame_ref", "frame_version", "payload"})
        self.assertNotIn("frame_ref", encoded["payload"])
        self.assertNotIn("frame_digest", encoded)

    def test_unknown_frame_reference_or_version_fails_closed(self) -> None:
        encoded = encode_compact_scene(self.scene, self.frame)
        bad_ref = {**encoded, "frame_ref": "unknown-frame"}
        bad_version = {**encoded, "frame_version": 2}
        bad_float_version = {**encoded, "frame_version": 1.0}
        with self.assertRaises(ValueError):
            decode_compact_scene(bad_ref, self.frame)
        with self.assertRaises(ValueError):
            decode_compact_scene(bad_version, self.frame)
        with self.assertRaises(ValueError):
            decode_compact_scene(bad_float_version, self.frame)

    def test_tampered_cached_frame_digest_fails_closed(self) -> None:
        encoded = encode_compact_scene(self.scene, self.frame)
        bad_frame = {**self.frame, "digest": "0" * 64}
        with self.assertRaises(ValueError):
            decode_compact_scene(encoded, bad_frame)

    def test_compact_variant_reduces_stable_batch_cost_after_amortization(self) -> None:
        single = compare_envelope_costs(1, None)
        batch = compare_envelope_costs(100, None)
        self.assertLess(single["compact_bytes_saved"], 0)
        self.assertGreater(batch["compact_bytes_saved"], 0)
        self.assertGreater(
            batch["compact_bytes_saved"],
            batch["existing_bytes_saved"],
        )
        self.assertEqual(
            batch["compact_total_bytes"],
            batch["initial_frame_bytes"]
            + batch["frame_update_bytes"]
            + batch["compact_instance_bytes"],
        )

    def test_observed_break_even_boundaries(self) -> None:
        for interval, expected_first_win in ((None, 5), (10, 5), (4, 25), (2, 25)):
            first_win = None
            for count in (1, 2, 5, 10, 25, 50, 100):
                row = compare_envelope_costs(count, interval)
                if row["compact_bytes_saved"] >= 0:
                    first_win = count
                    break
            self.assertEqual(first_win, expected_first_win)

    def test_schema_update_cost_is_charged_to_both_variants(self) -> None:
        row = compare_envelope_costs(20, 4)
        self.assertEqual(row["schema_updates"], 4)
        self.assertEqual(
            row["existing_total_bytes"] - row["existing_instance_bytes"],
            row["initial_frame_bytes"] + row["frame_update_bytes"],
        )
        self.assertEqual(
            row["compact_total_bytes"] - row["compact_instance_bytes"],
            row["initial_frame_bytes"] + row["frame_update_bytes"],
        )


if __name__ == "__main__":
    unittest.main()
