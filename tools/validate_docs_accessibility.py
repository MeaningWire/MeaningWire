#!/usr/bin/env python3
"""Validate deterministic, static accessibility invariants in rendered docs.

This intentionally checks only properties that can be established from built HTML.
Passing this validator is not a WCAG conformance claim and does not replace manual,
keyboard, assistive-technology, contrast, zoom/reflow, or browser testing.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


RESOURCE_LINK_RELS = {"stylesheet", "preload", "modulepreload", "icon", "manifest"}


def _attrs(items: list[tuple[str, str | None]]) -> dict[str, str]:
    return {name.lower(): value or "" for name, value in items}


def _is_remote(url: str) -> bool:
    parsed = urlsplit(url.strip())
    return parsed.scheme.lower() in {"http", "https"} or bool(parsed.netloc)


@dataclass
class PageEvidence:
    lang: str = ""
    titles: list[str] = field(default_factory=list)
    descriptions: list[str] = field(default_factory=list)
    main_count: int = 0
    main_ids: set[str] = field(default_factory=set)
    headings: list[int] = field(default_factory=list)
    h1_count: int = 0
    pre_main_fragment_links: list[dict[str, str]] = field(default_factory=list)
    missing_alt: list[str] = field(default_factory=list)
    autoplay_media: list[str] = field(default_factory=list)
    remote_resources: list[str] = field(default_factory=list)


class AccessibilityParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.evidence = PageEvidence()
        self._in_title = False
        self._title_parts: list[str] = []
        self._in_main = False
        self._seen_main = False
        self._active_pre_main_link: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attributes = _attrs(attrs)

        if tag == "html":
            self.evidence.lang = attributes.get("lang", "").strip()
        elif tag == "title":
            self._in_title = True
            self._title_parts = []
        elif tag == "meta" and attributes.get("name", "").lower() == "description":
            self.evidence.descriptions.append(attributes.get("content", "").strip())

        if tag == "main":
            self.evidence.main_count += 1
            self._in_main = True
            self._seen_main = True

        if self._in_main:
            element_id = attributes.get("id", "").strip()
            if element_id:
                self.evidence.main_ids.add(element_id)
            if len(tag) == 2 and tag[0] == "h" and tag[1].isdigit():
                level = int(tag[1])
                if 1 <= level <= 6:
                    self.evidence.headings.append(level)
                    if level == 1:
                        self.evidence.h1_count += 1

        if tag == "a" and not self._seen_main:
            href = attributes.get("href", "").strip()
            if href.startswith("#") and len(href) > 1:
                link = {
                    "href": href,
                    "aria_label": attributes.get("aria-label", "").strip(),
                    "text": "",
                }
                self.evidence.pre_main_fragment_links.append(link)
                self._active_pre_main_link = link

        if tag == "img" and "alt" not in attributes:
            self.evidence.missing_alt.append(attributes.get("src", "<missing src>"))

        if tag in {"audio", "video"} and "autoplay" in attributes:
            self.evidence.autoplay_media.append(attributes.get("src", tag))

        candidate_url = ""
        if tag == "script":
            candidate_url = attributes.get("src", "")
        elif tag == "link":
            rels = {part.lower() for part in attributes.get("rel", "").split()}
            if rels & RESOURCE_LINK_RELS:
                candidate_url = attributes.get("href", "")
        elif tag in {"img", "source", "iframe", "audio", "video"}:
            candidate_url = attributes.get("src", "")
        if tag == "video" and not candidate_url:
            candidate_url = attributes.get("poster", "")

        if candidate_url and _is_remote(candidate_url):
            self.evidence.remote_resources.append(f"<{tag}> {candidate_url}")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
            self.evidence.titles.append("".join(self._title_parts).strip())
            self._title_parts = []
        if tag == "a":
            self._active_pre_main_link = None
        if tag == "main":
            self._in_main = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)
        if self._active_pre_main_link is not None:
            self._active_pre_main_link["text"] += data


def audit_html(path: Path) -> PageEvidence:
    parser = AccessibilityParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser.evidence


def validate_page(relative: str, evidence: PageEvidence) -> list[str]:
    errors: list[str] = []

    if not evidence.lang:
        errors.append(f"{relative}: <html> is missing a non-empty lang attribute")

    if len(evidence.titles) != 1 or not evidence.titles[0]:
        errors.append(f"{relative}: expected exactly one non-empty <title>")

    if len(evidence.descriptions) != 1 or not evidence.descriptions[0]:
        errors.append(f"{relative}: expected exactly one non-empty meta description")

    if evidence.main_count != 1:
        errors.append(f"{relative}: expected exactly one <main>, found {evidence.main_count}")

    if evidence.h1_count != 1:
        errors.append(f"{relative}: expected exactly one <h1> inside <main>, found {evidence.h1_count}")

    valid_skip_links = []
    for link in evidence.pre_main_fragment_links:
        target = link["href"][1:]
        name = link["aria_label"] or link["text"].strip()
        if target in evidence.main_ids and name:
            valid_skip_links.append(link)
    if not valid_skip_links:
        errors.append(
            f"{relative}: expected a named pre-main fragment link targeting content inside <main>"
        )

    previous = None
    for level in evidence.headings:
        if previous is not None and level > previous + 1:
            errors.append(
                f"{relative}: heading hierarchy jumps from h{previous} to h{level} inside <main>"
            )
        previous = level

    for src in evidence.missing_alt:
        errors.append(f"{relative}: <img> is missing alt attribute: {src}")
    for src in evidence.autoplay_media:
        errors.append(f"{relative}: autoplay media is not allowed: {src}")
    for resource in evidence.remote_resources:
        errors.append(f"{relative}: unexpected remote subresource: {resource}")

    return errors


def validate(root: Path) -> list[str]:
    html_files = sorted(root.rglob("*.html"))
    if not html_files:
        return [f"no rendered HTML files found under {root}"]

    errors: list[str] = []
    titles: dict[str, list[str]] = {}
    for html_file in html_files:
        relative = html_file.relative_to(root).as_posix()
        try:
            evidence = audit_html(html_file)
        except (OSError, UnicodeError) as exc:
            errors.append(f"{relative}: cannot parse rendered HTML: {exc}")
            continue

        errors.extend(validate_page(relative, evidence))
        if len(evidence.titles) == 1 and evidence.titles[0]:
            titles.setdefault(evidence.titles[0], []).append(relative)

    for title, paths in sorted(titles.items()):
        if len(paths) > 1:
            errors.append(f"duplicate rendered page title {title!r}: {', '.join(paths)}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate static accessibility and documentation-integrity invariants."
    )
    parser.add_argument("root", nargs="?", default="dist", help="Rendered documentation root")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: documentation root does not exist: {root}", file=sys.stderr)
        return 1

    errors = validate(root)
    if errors:
        print("ERROR: rendered documentation accessibility/integrity checks failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "PASS: rendered documentation has language, titles/descriptions, semantic main/heading structure, "
        "a named skip target, image alt attributes, no autoplay media, and no remote subresources."
    )
    print("NOTE: this static check is not a WCAG conformance claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
