from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import compare_docs_builds as comparator  # noqa: E402


class CompareDocsBuildsTests(unittest.TestCase):
    def _build(self, root: Path, *, ui: bytes, wasm: bytes, index: bytes = b"same") -> None:
        (root / "pagefind").mkdir(parents=True)
        (root / "index.html").write_bytes(b"<html>same</html>")
        (root / "pagefind" / "pagefind.js").write_bytes(index)
        (root / "pagefind" / "pagefind-ui.css").write_bytes(b"same css")
        (root / "pagefind" / "pagefind-ui.js").write_bytes(ui)
        (root / "pagefind" / "wasm.unknown.pagefind").write_bytes(wasm)

    def test_known_runtime_assets_may_differ_when_structurally_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            first, second = base / "first", base / "second"
            valid_js_a = (b"const PagefindUI='a';" + b"x" * 1200)
            valid_js_b = (b"const PagefindUI='b';" + b"y" * 1200)
            valid_wasm_a = b"\x00asm\x01\x00\x00\x00" + b"a" * 32
            valid_wasm_b = b"\x00asm\x01\x00\x00\x00" + b"b" * 32
            self._build(first, ui=valid_js_a, wasm=valid_wasm_a)
            self._build(second, ui=valid_js_b, wasm=valid_wasm_b)
            result = comparator.compare_builds(first, second)
        self.assertEqual(result["volatile_runtime_count"], 2)
        self.assertEqual(result["exact_file_count"], 3)

    def test_non_runtime_difference_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            first, second = base / "first", base / "second"
            ui = b"const PagefindUI='ok';" + b"x" * 1200
            wasm = b"\x00asm\x01\x00\x00\x00" + b"a" * 32
            self._build(first, ui=ui, wasm=wasm, index=b"first")
            self._build(second, ui=ui, wasm=wasm, index=b"second")
            with self.assertRaisesRegex(
                comparator.DocsBuildComparisonError,
                "deterministic documentation output differs",
            ):
                comparator.compare_builds(first, second)

    def test_unexpected_pagefind_difference_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            first, second = base / "first", base / "second"
            ui = b"const PagefindUI='ok';" + b"x" * 1200
            wasm = b"\x00asm\x01\x00\x00\x00" + b"a" * 32
            self._build(first, ui=ui, wasm=wasm)
            self._build(second, ui=ui, wasm=wasm)
            (first / "pagefind" / "unexpected.js").write_bytes(b"one")
            (second / "pagefind" / "unexpected.js").write_bytes(b"two")
            with self.assertRaisesRegex(
                comparator.DocsBuildComparisonError,
                "deterministic documentation output differs",
            ):
                comparator.compare_builds(first, second)

    def test_invalid_runtime_assets_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            first, second = base / "first", base / "second"
            bad_ui = b"tiny"
            wasm = b"\x00asm\x01\x00\x00\x00" + b"a" * 32
            self._build(first, ui=bad_ui, wasm=wasm)
            self._build(second, ui=bad_ui, wasm=wasm)
            with self.assertRaisesRegex(comparator.DocsBuildComparisonError, "unexpectedly small"):
                comparator.compare_builds(first, second)

    def test_file_set_difference_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            first, second = base / "first", base / "second"
            ui = b"const PagefindUI='ok';" + b"x" * 1200
            wasm = b"\x00asm\x01\x00\x00\x00" + b"a" * 32
            self._build(first, ui=ui, wasm=wasm)
            self._build(second, ui=ui, wasm=wasm)
            (second / "extra.txt").write_text("extra", encoding="utf-8")
            with self.assertRaisesRegex(comparator.DocsBuildComparisonError, "file set differs"):
                comparator.compare_builds(first, second)


if __name__ == "__main__":
    unittest.main()
