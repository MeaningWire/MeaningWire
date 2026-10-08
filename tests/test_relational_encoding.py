from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import relational_encoding  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "proofs" / "case-004b-bridge.json"


class RelationalEncodingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with FIXTURE.open("r", encoding="utf-8") as handle:
            cls.artifact = json.load(handle)

    def test_relational_encoding_reconstructs_exact_fixture(self) -> None:
        encoded = relational_encoding.encode_relational(self.artifact)
        reconstructed = relational_encoding.decode_relational(encoded)
        self.assertEqual(
            relational_encoding.canonical_bytes(self.artifact),
            relational_encoding.canonical_bytes(reconstructed),
        )

    def test_relational_round_trip_preserves_reference_behavior(self) -> None:
        report = relational_encoding.run_experiment(self.artifact)
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["relational_behavior_equal"])
        self.assertTrue(report["named_json_behavior_equal"])
        self.assertEqual(report["reference_behavior_groups"], 9)

    def test_size_comparison_discloses_excluded_costs(self) -> None:
        report = relational_encoding.run_experiment(self.artifact)
        self.assertGreater(report["named_json_bytes"], 0)
        self.assertGreater(report["relational_tuple_json_bytes"], 0)
        self.assertFalse(report["schema_overhead_included"])
        self.assertFalse(report["decoder_cost_included"])
        self.assertFalse(report["network_access"])

    def test_decoder_rejects_unknown_layout_and_wrong_tuple_arity(self) -> None:
        with self.assertRaises(ValueError):
            relational_encoding.decode_relational({"layout": "unknown"})
        encoded = relational_encoding.encode_relational(self.artifact)
        encoded["entities"][0].pop()
        with self.assertRaises(ValueError):
            relational_encoding.decode_relational(encoded)


if __name__ == "__main__":
    unittest.main()
