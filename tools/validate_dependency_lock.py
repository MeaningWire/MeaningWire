#!/usr/bin/env python3
"""Validate MeaningWire's target-specific Python dependency lock.

The lock is used by governed CI/release-candidate verification for CPython 3.12
on Linux x86_64. This tool performs dependency-free static validation and can
also verify a clean installed environment against the exact locked versions.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECT = ROOT / "requirements-validation.txt"
LOCK = ROOT / "requirements-validation.lock"
TARGET_LINE = "# Target: CPython 3.12, Linux x86_64, binary wheels only"
PIN_RE = re.compile(r"^([A-Za-z0-9_.-]+)==([^\s\\]+)\s*\\?$", re.IGNORECASE)
HASH_RE = re.compile(r"^--hash=sha256:([0-9a-f]{64})$")


class DependencyLockError(ValueError):
    """Raised when the dependency lock is malformed or inconsistent."""


def canonical_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def direct_requirements() -> dict[str, str]:
    requirements: dict[str, str] = {}
    for raw in DIRECT.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = PIN_RE.fullmatch(line)
        if not match:
            raise DependencyLockError(
                f"direct requirement must be an exact == pin: {line!r}"
            )
        name, version = match.groups()
        requirements[canonical_name(name)] = version
    if not requirements:
        raise DependencyLockError("requirements-validation.txt has no requirements")
    return requirements


def locked_requirements() -> dict[str, tuple[str, tuple[str, ...]]]:
    lines = LOCK.read_text(encoding="utf-8").splitlines()
    if TARGET_LINE not in lines:
        raise DependencyLockError(f"lock target declaration is missing: {TARGET_LINE}")

    entries: dict[str, tuple[str, tuple[str, ...]]] = {}
    current_name: str | None = None
    current_version: str | None = None
    hashes: list[str] = []

    def finish() -> None:
        nonlocal current_name, current_version, hashes
        if current_name is None:
            return
        if not hashes:
            raise DependencyLockError(f"locked requirement {current_name} has no SHA-256 hash")
        key = canonical_name(current_name)
        if key in entries:
            raise DependencyLockError(f"duplicate locked requirement: {current_name}")
        entries[key] = (current_version or "", tuple(sorted(set(hashes))))
        current_name = None
        current_version = None
        hashes = []

    for raw in lines:
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        pin = PIN_RE.fullmatch(stripped)
        if pin:
            finish()
            current_name, current_version = pin.groups()
            continue
        hash_match = HASH_RE.fullmatch(stripped.rstrip("\\").strip())
        if hash_match and current_name is not None:
            hashes.append(hash_match.group(1))
            continue
        raise DependencyLockError(f"unsupported lock syntax: {stripped!r}")
    finish()

    if not entries:
        raise DependencyLockError("requirements-validation.lock has no packages")
    if list(entries) != sorted(entries):
        raise DependencyLockError("locked package entries must be sorted by canonical name")
    return entries


def validate_static() -> tuple[dict[str, str], dict[str, tuple[str, tuple[str, ...]]]]:
    direct = direct_requirements()
    locked = locked_requirements()
    missing = sorted(set(direct) - set(locked))
    if missing:
        raise DependencyLockError(
            "direct requirements missing from lock: " + ", ".join(missing)
        )
    mismatched = [
        name
        for name, version in direct.items()
        if locked[name][0] != version
    ]
    if mismatched:
        details = ", ".join(
            f"{name}: direct={direct[name]} lock={locked[name][0]}" for name in mismatched
        )
        raise DependencyLockError("direct/lock version mismatch: " + details)
    return direct, locked


def verify_installed(locked: dict[str, tuple[str, tuple[str, ...]]]) -> None:
    installed = {
        canonical_name(dist.metadata["Name"]): dist.version
        for dist in importlib.metadata.distributions()
        if dist.metadata.get("Name")
    }
    missing = sorted(set(locked) - set(installed))
    mismatched = sorted(
        name
        for name, (version, _hashes) in locked.items()
        if installed.get(name) != version
    )
    if missing:
        raise DependencyLockError("locked packages not installed: " + ", ".join(missing))
    if mismatched:
        details = ", ".join(
            f"{name}: lock={locked[name][0]} installed={installed.get(name)}"
            for name in mismatched
        )
        raise DependencyLockError("installed version mismatch: " + details)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate MeaningWire validation dependency lock")
    parser.add_argument(
        "--verify-installed",
        action="store_true",
        help="also verify that all locked packages are installed at the exact locked versions",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        direct, locked = validate_static()
        if args.verify_installed:
            verify_installed(locked)
    except (DependencyLockError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}")
        return 2

    suffix = "; installed versions match" if args.verify_installed else ""
    print(
        f"PASS: validation dependency lock contains {len(locked)} exact hashed packages; "
        f"{len(direct)} direct requirement(s) represented{suffix}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
