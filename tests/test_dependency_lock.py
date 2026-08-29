from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import validate_dependency_lock  # noqa: E402


class ValidationDependencyLockTests(unittest.TestCase):
    def test_lock_is_exact_hashed_and_represents_direct_requirements(self) -> None:
        direct, locked = validate_dependency_lock.validate_static()
        self.assertEqual(direct, {"jsonschema": "4.26.0"})
        self.assertEqual(len(locked), 6)
        self.assertEqual(locked["jsonschema"][0], "4.26.0")
        for _name, (_version, hashes) in locked.items():
            self.assertTrue(hashes)
            self.assertTrue(all(len(digest) == 64 for digest in hashes))

    def test_locked_graph_contains_python_312_referencing_backport(self) -> None:
        _direct, locked = validate_dependency_lock.validate_static()
        self.assertEqual(locked["referencing"][0], "0.37.0")
        self.assertEqual(locked["typing-extensions"][0], "4.16.0")

    def test_lock_target_is_explicitly_linux_cpython_312(self) -> None:
        text = validate_dependency_lock.LOCK.read_text(encoding="utf-8")
        self.assertIn(validate_dependency_lock.TARGET_LINE, text)
        self.assertIn("binary wheels only", text)


if __name__ == "__main__":
    unittest.main()
