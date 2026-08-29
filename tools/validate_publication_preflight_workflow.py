#!/usr/bin/env python3
"""Fail-closed static guard for the non-publishing publication preflight workflow."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "release-publication-preflight.yml"

REQUIRED_SNIPPETS = (
    "workflow_dispatch:",
    "permissions:\n  contents: read",
    "persist-credentials: false",
    "ref: ${{ inputs.source_sha }}",
    "python tools/validate_workflow_pins.py",
    "python tools/release_publication_preflight.py",
    "python tools/release_readiness.py",
    "--require-ready",
    "Publication preflight only.",
)

FORBIDDEN_PATTERNS = (
    r"\bgh\s+release\b",
    r"\bgit\s+tag\b",
    r"\bgit\s+push\b",
    r"actions/create-release@",
    r"softprops/action-gh-release@",
    r"ncipollo/release-action@",
    r"actions/attest@",
    r"attest-build-provenance@",
    r"attest-sbom@",
    r"id-token:\s*write",
    r"attestations:\s*write",
    r"packages:\s*write",
    r"contents:\s*write",
    r"pages:\s*write",
    r"deployments?:\s*write",
    r"npm\s+publish",
    r"twine\s+upload",
    r"docker\s+push",
    r"ghcr\.io",
)


class PreflightWorkflowError(ValueError):
    pass


def validate_text(text: str) -> list[str]:
    errors: list[str] = []
    if re.search(r"(?m)^\s*(push|pull_request|schedule|release):\s*$", text):
        errors.append("workflow must remain manual-only; automatic trigger detected")
    for snippet in REQUIRED_SNIPPETS:
        if snippet not in text:
            errors.append(f"required preflight guard is missing: {snippet}")
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(f"publishing-capable construct is forbidden in preflight: {pattern}")
    return errors


def validate_workflow(path: Path = WORKFLOW) -> list[str]:
    if not path.is_file():
        raise PreflightWorkflowError(f"preflight workflow is missing: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise PreflightWorkflowError(f"cannot read preflight workflow: {exc}") from exc
    return validate_text(text)


def main() -> int:
    try:
        errors = validate_workflow()
    except PreflightWorkflowError as exc:
        print(f"ERROR: {exc}")
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 2
    print("PASS: publication preflight remains manual-only, read-only, exact-source-bound, readiness-gated, and non-publishing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
