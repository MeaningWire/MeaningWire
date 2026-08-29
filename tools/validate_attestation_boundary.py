#!/usr/bin/env python3
"""Fail closed if ordinary MeaningWire workflows gain public attestation capability.

During quiet pre-release engineering no checked-in workflow may request OIDC or
attestation write authority or invoke GitHub/Sigstore attestation/signing tools.
The future governed publication workflow must deliberately replace this policy
at the human-authorized implementation boundary rather than bypass it.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

FORBIDDEN = (
    (re.compile(r"(?im)^\s*id-token:\s*write\s*$"), "OIDC id-token write permission"),
    (re.compile(r"(?im)^\s*attestations:\s*write\s*$"), "attestations write permission"),
    (re.compile(r"(?im)^\s*uses:\s*actions/attest(?:-[^@\s]+)?@"), "GitHub attestation action"),
    (re.compile(r"(?im)\bcosign\s+(?:sign|attest)\b"), "Sigstore cosign signing/attestation command"),
    (re.compile(r"(?im)\bsigstore\b.*\b(?:sign|attest)\b"), "Sigstore signing/attestation command"),
)


class AttestationBoundaryError(ValueError):
    pass


def workflow_files() -> list[Path]:
    if not WORKFLOWS.is_dir():
        raise AttestationBoundaryError("workflow directory is missing")
    return sorted([*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")])


def validate_text(text: str, label: str = "workflow") -> list[str]:
    errors: list[str] = []
    for pattern, description in FORBIDDEN:
        if pattern.search(text):
            errors.append(f"{label}: quiet pre-release forbids {description}")
    return errors


def validate_repository() -> list[str]:
    errors: list[str] = []
    for path in workflow_files():
        relative = path.relative_to(ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise AttestationBoundaryError(f"cannot read {relative}: {exc}") from exc
        errors.extend(validate_text(text, relative))
    return errors


def main() -> int:
    try:
        errors = validate_repository()
    except AttestationBoundaryError as exc:
        print(f"ERROR: {exc}")
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 2
    print("PASS: checked-in workflows cannot mint public attestations during quiet pre-release.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
