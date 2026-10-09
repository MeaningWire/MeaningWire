from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from frame_cost_model import benchmark_matrix, run_cost_case  # noqa: E402


class FrameCostModelTests(unittest.TestCase):
    def test_total_includes_initial_frame_updates_and_all_instance_bytes(self) -> None:
        row = run_cost_case(12, 4)
        self.assertEqual(row["schema_updates"], 2)
        self.assertEqual(
            row["total_frame_protocol_bytes"],
            row["initial_frame_bytes"]
            + row["frame_update_bytes"]
            + row["instance_envelope_and_payload_bytes"],
        )
        self.assertEqual(
            row["bytes_saved"],
            row["explicit_json_bytes"] - row["total_frame_protocol_bytes"],
        )

    def test_no_schema_change_has_no_update_cost(self) -> None:
        row = run_cost_case(20, None)
        self.assertEqual(row["schema_updates"], 0)
        self.assertEqual(row["frame_update_bytes"], 0)

    def test_more_frequent_changes_never_omit_update_accounting(self) -> None:
        slow = run_cost_case(20, 10)
        frequent = run_cost_case(20, 2)
        self.assertLess(slow["schema_updates"], frequent["schema_updates"])
        self.assertGreater(slow["frame_update_bytes"], 0)
        self.assertGreater(frequent["frame_update_bytes"], slow["frame_update_bytes"])

    def test_invalid_workloads_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            run_cost_case(0, None)
        with self.assertRaises(ValueError):
            run_cost_case(10, 1)

    def test_matrix_covers_batch_sizes_and_change_rates_without_assuming_wins(self) -> None:
        rows = benchmark_matrix()
        self.assertEqual(len(rows), 28)
        self.assertEqual({r["messages"] for r in rows}, {1, 2, 5, 10, 25, 50, 100})
        self.assertEqual({r["change_interval"] for r in rows}, {None, 10, 4, 2})
        self.assertTrue(all(r["explicit_json_bytes"] > 0 for r in rows))
        self.assertTrue(all(r["total_frame_protocol_bytes"] > 0 for r in rows))
        # Deliberately no assertion that frame encoding always wins.


if __name__ == "__main__":
    unittest.main()
