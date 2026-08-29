#!/usr/bin/env python3
"""Require immutable commit-SHA pins for external GitHub Actions workflow uses.

Local actions (./path) and docker:// references are not GitHub repository action
references and are excluded. Every other `uses:` reference in .github/workflows
must end in a full 40-character lowercase hexadecimal commit SHA.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
USES_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)")
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class WorkflowPinError(ValueError):
    """Raised when an external workflow action is not immutably pinned."""


def workflow_files() -> list[Path]:
    if not WORKFLOWS.is_dir():
        raise WorkflowPinError(".github/workflows directory is missing")
    files = sorted(
        [*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")],
        key=lambda path: path.as_posix(),
    )
    if not files:
        raise WorkflowPinError("no workflow files found")
    return files


def external_uses(path: Path) -> list[tuple[int, str]]:
    references: list[tuple[int, str]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = USES_RE.match(line)
        if not match:
            continue
        reference = match.group(1).strip('"\'')
        if reference.startswith("./") or reference.startswith("docker://"):
            continue
        references.append((line_number, reference))
    return references


def validate_reference(reference: str) -> bool:
    if "@" not in reference:
        return False
    _action, revision = reference.rsplit("@", 1)
    return bool(FULL_SHA_RE.fullmatch(revision))


def validate_workflows() -> tuple[int, list[str]]:
    checked = 0
    errors: list[str] = []
    for path in workflow_files():
        relative = path.relative_to(ROOT).as_posix()
        for line_number, reference in external_uses(path):
            checked += 1
            if not validate_reference(reference):
                errors.append(
                    f"{relative}:{line_number}: external action must use a full 40-character commit SHA: {reference}"
                )
    return checked, errors


def main() -> int:
    try:
        checked, errors = validate_workflows()
    except (WorkflowPinError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}")
        return 2

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 2

    print(f"PASS: {checked} external GitHub Actions references are immutably pinned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
