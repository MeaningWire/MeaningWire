#!/usr/bin/env python3
"""Compare repeated documentation builds without overstating Pagefind byte stability.

MeaningWire requires all project-authored documentation and deterministic Pagefind
index outputs to be byte-identical across repeated builds. Two upstream Pagefind
runtime assets have been observed to vary under an otherwise pinned identical
build: ``pagefind-ui.js`` and ``wasm.*.pagefind``. Those exact runtime assets are
structurally validated instead of byte-compared; any other differing file fails
closed.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

_PAGEFIND_UI = "pagefind/pagefind-ui.js"
_PAGEFIND_WASM_RE = re.compile(r"^pagefind/wasm\.[A-Za-z0-9_-]+\.pagefind$")


class DocsBuildComparisonError(ValueError):
    """Raised when repeated documentation builds violate the reproducibility contract."""


def _files(root: Path) -> dict[str, Path]:
    if not root.is_dir():
        raise DocsBuildComparisonError(f"documentation build directory is missing: {root}")
    result: dict[str, Path] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise DocsBuildComparisonError(f"documentation output contains symbolic link: {relative}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise DocsBuildComparisonError(f"documentation output contains non-regular file: {relative}")
        result[relative] = path
    if not result:
        raise DocsBuildComparisonError(f"documentation build contains no files: {root}")
    return result


def _is_volatile_pagefind_runtime(path: str) -> bool:
    return path == _PAGEFIND_UI or _PAGEFIND_WASM_RE.fullmatch(path) is not None


def _validate_pagefind_runtime(path: str, data: bytes) -> None:
    if path == _PAGEFIND_UI:
        if len(data) < 1000:
            raise DocsBuildComparisonError("Pagefind UI runtime is unexpectedly small")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise DocsBuildComparisonError("Pagefind UI runtime is not UTF-8 JavaScript") from exc
        if "PagefindUI" not in text:
            raise DocsBuildComparisonError("Pagefind UI runtime does not expose expected PagefindUI marker")
        return
    if _PAGEFIND_WASM_RE.fullmatch(path):
        if len(data) < 8 or not data.startswith(b"\x00asm"):
            raise DocsBuildComparisonError(f"Pagefind WASM runtime is not a valid WebAssembly header: {path}")
        return
    raise DocsBuildComparisonError(f"unrecognized volatile Pagefind runtime path: {path}")


def compare_builds(first: str | Path, second: str | Path) -> dict[str, object]:
    first_root = Path(first).resolve()
    second_root = Path(second).resolve()
    first_files = _files(first_root)
    second_files = _files(second_root)

    if set(first_files) != set(second_files):
        missing = sorted(set(first_files) - set(second_files))
        extra = sorted(set(second_files) - set(first_files))
        details: list[str] = []
        if missing:
            details.append("missing from second build: " + ", ".join(missing))
        if extra:
            details.append("extra in second build: " + ", ".join(extra))
        raise DocsBuildComparisonError("documentation file set differs: " + "; ".join(details))

    exact_count = 0
    volatile_count = 0
    volatile_digests: dict[str, tuple[str, str]] = {}
    for relative in sorted(first_files):
        first_bytes = first_files[relative].read_bytes()
        second_bytes = second_files[relative].read_bytes()
        if _is_volatile_pagefind_runtime(relative):
            _validate_pagefind_runtime(relative, first_bytes)
            _validate_pagefind_runtime(relative, second_bytes)
            volatile_count += 1
            volatile_digests[relative] = (
                hashlib.sha256(first_bytes).hexdigest(),
                hashlib.sha256(second_bytes).hexdigest(),
            )
            continue
        if first_bytes != second_bytes:
            raise DocsBuildComparisonError(
                f"deterministic documentation output differs across repeated builds: {relative}"
            )
        exact_count += 1

    if _PAGEFIND_UI not in first_files:
        raise DocsBuildComparisonError("Pagefind UI runtime is missing")
    wasm_paths = sorted(path for path in first_files if _PAGEFIND_WASM_RE.fullmatch(path))
    if len(wasm_paths) != 1:
        raise DocsBuildComparisonError(
            f"expected exactly one Pagefind WASM runtime, found {len(wasm_paths)}"
        )

    return {
        "exact_file_count": exact_count,
        "volatile_runtime_count": volatile_count,
        "volatile_runtime_sha256": volatile_digests,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare repeated MeaningWire documentation builds with a narrow Pagefind runtime boundary"
    )
    parser.add_argument("first")
    parser.add_argument("second")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = compare_builds(args.first, args.second)
    except (DocsBuildComparisonError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 2
    print(
        "PASS: repeated documentation builds preserve identical file sets; "
        f"{result['exact_file_count']} files are byte-identical and "
        f"{result['volatile_runtime_count']} explicitly bounded Pagefind runtime assets are structurally valid."
    )
    for path, digests in sorted(result["volatile_runtime_sha256"].items()):
        print(f"NOTE: {path} sha256 first={digests[0]} second={digests[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
