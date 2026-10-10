from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from case_006b_resolution_sweep import (  # noqa: E402
    quantize,
    reconstruct,
    size_comparison,
    sweep,
    theoretical_max_error,
)


class ResolutionSweepTests(unittest.TestCase):
    def test_error_bound_holds_for_multiple_resolutions(self) -> None:
        for levels in (2, 4, 8, 16, 256):
            bound = theoretical_max_error(levels)
            for i in range(1001):
                value = i / 1000
                decoded = reconstruct(quantize(value, levels), levels)
                self.assertLessEqual(abs(value - decoded), bound + 1e-12)

    def test_higher_resolution_does_not_increase_theoretical_bound(self) -> None:
        bounds = [theoretical_max_error(levels) for levels in (2, 4, 8, 16, 256)]
        self.assertEqual(bounds, sorted(bounds, reverse=True))

    def test_low_resolution_can_collapse_a_task_defined_pair(self) -> None:
        self.assertEqual(quantize(0.49, 2), quantize(0.51, 2))
        self.assertNotEqual(quantize(0.49, 256), quantize(0.51, 256))

    def test_sweep_reports_collisions_and_error_separately(self) -> None:
        rows = sweep()
        self.assertEqual([row["levels"] for row in rows], [2, 4, 8, 16, 256])
        self.assertGreater(rows[0]["critical_pair_collisions"], 0)
        self.assertLessEqual(rows[-1]["critical_pair_collisions"], rows[0]["critical_pair_collisions"])
        for row in rows:
            self.assertIn("mean_abs_error_on_1001_point_grid", row)
            self.assertIn("theoretical_max_abs_error", row)

    def test_size_comparison_is_explicitly_json_not_bit_packing(self) -> None:
        result = size_comparison()
        self.assertGreater(result["explicit_json_bytes"], 0)
        self.assertGreater(result["positional_quantized_json_bytes"], 0)
        self.assertIn("Not bit-packed", result["warning"])


if __name__ == "__main__":
    unittest.main()
