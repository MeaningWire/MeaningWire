from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import semantic_roundtrip  # noqa: E402


FIXTURE = ROOT / "tests" / "fixtures" / "proofs" / "case-004b-bridge.json"


class SemanticRoundTripTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with FIXTURE.open("r", encoding="utf-8") as handle:
            cls.artifact = json.load(handle)

    def test_json_round_trip_preserves_structure(self) -> None:
        reconstructed = semantic_roundtrip.round_trip(self.artifact)
        self.assertEqual(
            semantic_roundtrip.canonical_bytes(self.artifact),
            semantic_roundtrip.canonical_bytes(reconstructed),
        )

    def test_json_round_trip_preserves_all_reference_behaviors(self) -> None:
        report = semantic_roundtrip.run_battery(self.artifact)
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["round_trip_behavior_equal"])
        self.assertTrue(all(item["pass"] for item in report["reference_tests"].values()))
        self.assertEqual(len(report["reference_tests"]), 9)

    def test_targeted_ablations_expose_expected_information_loss(self) -> None:
        report = semantic_roundtrip.run_battery(self.artifact)
        ablations = {item["name"]: item for item in report["ablations"]}
        expected_to_diverge = {
            "remove_temporal_value",
            "remove_scope",
            "remove_epistemic_status",
            "remove_confidence",
            "remove_provenance_reference",
            "remove_relations",
            "remove_policy_version",
            "remove_escalation_event",
        }
        for name in expected_to_diverge:
            with self.subTest(ablated=name):
                self.assertTrue(ablations[name]["behavior_changed"], name)

    def test_resolution_and_significance_are_redundant_only_for_this_battery(self) -> None:
        report = semantic_roundtrip.run_battery(self.artifact)
        ablations = {item["name"]: item for item in report["ablations"]}
        self.assertFalse(ablations["remove_resolution"]["behavior_changed"])
        self.assertFalse(ablations["remove_significance"]["behavior_changed"])

    def test_cli_report_is_machine_readable_and_has_no_network_dependency(self) -> None:
        report = semantic_roundtrip.run_battery(self.artifact)
        self.assertFalse(report["network_access"])
        self.assertGreater(report["serialized_bytes"], 0)
        self.assertEqual(report["experiment"], "CASE-004B")


if __name__ == "__main__":
    unittest.main()
