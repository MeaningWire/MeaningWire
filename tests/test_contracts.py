from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import validate_contracts  # noqa: E402


class ContractValidationTests(unittest.TestCase):
    def test_schema_registry_is_consistent(self) -> None:
        self.assertEqual(validate_contracts.validate_registry(), 5)

    def test_fixture_manifest(self) -> None:
        self.assertEqual(validate_contracts.validate_fixture_manifest(), (2, 2))


if __name__ == "__main__":
    unittest.main()
