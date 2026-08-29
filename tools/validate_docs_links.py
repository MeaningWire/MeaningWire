#!/usr/bin/env python3
"""Fail closed when rendered documentation links target missing local files."""

from __future__ import annotations

import argparse
import posixpath
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


SKIPPED_SCHEMES = {"data", "javascript", "mailto", "tel"}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for name, value in attrs:
            if name == "href" and value:
                self.links.append(value)


def page_url(root: Path, html_file: Path) -> str:
    relative = html_file.relative_to(root).as_posix()
    if relative == "index.html":
        return "/"
    if relative.endswith("/index.html"):
        return f"/{relative[:-10]}"
    return f"/{relative}"


def local_target(root: Path, source_url: str, href: str) -> Path | None:
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc:
        return None
    if parsed.scheme.lower() in SKIPPED_SCHEMES:
        return None
    if not parsed.path:
        return None

    resolved = unquote(urlsplit(urljoin(source_url, parsed.path)).path)
    normalized = posixpath.normpath(resolved)
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"

    target = root / normalized.lstrip("/")
    if resolved.endswith("/"):
        return target / "index.html"
    if target.exists():
        return target
    if target.suffix:
        return target
    return target / "index.html"


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    html_files = sorted(root.rglob("*.html"))
    if not html_files:
        return [f"no rendered HTML files found under {root}"]

    for html_file in html_files:
        parser = LinkParser()
        try:
            parser.feed(html_file.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            errors.append(f"{html_file}: cannot parse rendered HTML: {exc}")
            continue

        source_url = page_url(root, html_file)
        for href in sorted(set(parser.links)):
            target = local_target(root, source_url, href)
            if target is None:
                continue
            try:
                target.relative_to(root)
            except ValueError:
                errors.append(f"{source_url}: internal link escapes documentation root: {href}")
                continue
            if not target.exists():
                expected = target.relative_to(root).as_posix()
                errors.append(f"{source_url}: {href} -> missing {expected}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that rendered internal documentation links resolve locally."
    )
    parser.add_argument("root", nargs="?", default="dist", help="Rendered documentation root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: documentation root does not exist: {root}", file=sys.stderr)
        return 1

    errors = validate(root)
    if errors:
        print("ERROR: rendered documentation contains invalid internal links:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("PASS: rendered internal documentation links resolve to local files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
