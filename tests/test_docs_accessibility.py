from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import validate_docs_accessibility  # noqa: E402


GOOD_HTML = """<!doctype html>
<html lang="en">
<head>
  <title>Example | MeaningWire</title>
  <meta name="description" content="Example page">
  <link rel="stylesheet" href="/_astro/site.css">
</head>
<body>
  <a href="#page-title">Skip to content</a>
  <main>
    <h1 id="page-title">Example</h1>
    <h2>Details</h2>
    <img src="/diagram.svg" alt="">
  </main>
</body>
</html>
"""


class DocsAccessibilityTests(unittest.TestCase):
    def _validate(self, pages: dict[str, str]) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative, html in pages.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(html, encoding="utf-8")
            return validate_docs_accessibility.validate(root)

    def test_good_static_page_passes(self) -> None:
        self.assertEqual(self._validate({"index.html": GOOD_HTML}), [])

    def test_missing_language_and_skip_target_fail_closed(self) -> None:
        broken = GOOD_HTML.replace(' lang="en"', "").replace('id="page-title"', 'id="other"')
        errors = self._validate({"index.html": broken})
        self.assertTrue(any("lang attribute" in error for error in errors))
        self.assertTrue(any("pre-main fragment link" in error for error in errors))

    def test_heading_jump_and_missing_alt_fail_closed(self) -> None:
        broken = GOOD_HTML.replace("<h2>Details</h2>", "<h3>Details</h3>").replace(
            ' alt=""', ""
        )
        errors = self._validate({"index.html": broken})
        self.assertTrue(any("jumps from h1 to h3" in error for error in errors))
        self.assertTrue(any("missing alt attribute" in error for error in errors))

    def test_remote_subresource_and_autoplay_fail_closed(self) -> None:
        broken = GOOD_HTML.replace(
            '<link rel="stylesheet" href="/_astro/site.css">',
            '<link rel="stylesheet" href="https://example.invalid/site.css">',
        ).replace(
            "</main>", '<video src="/demo.mp4" autoplay></video>\n  </main>'
        )
        errors = self._validate({"index.html": broken})
        self.assertTrue(any("remote subresource" in error for error in errors))
        self.assertTrue(any("autoplay media" in error for error in errors))

    def test_duplicate_titles_fail_closed(self) -> None:
        errors = self._validate({"index.html": GOOD_HTML, "second/index.html": GOOD_HTML})
        self.assertTrue(any("duplicate rendered page title" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
