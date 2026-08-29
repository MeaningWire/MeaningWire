#!/usr/bin/env python3
"""Fetch the exact upstream SPDX 2.3 JSON Schema used for candidate validation.

The upstream file is not vendored into MeaningWire. This tool downloads the file
from one immutable SPDX specification commit and verifies the Git blob object ID
before writing it locally for validation.
"""

from __future__ import annotations

import argparse
import hashlib
import urllib.error
import urllib.request
from pathlib import Path

SPDX_SPEC_REPOSITORY = "spdx/spdx-spec"
SPDX_SPEC_COMMIT = "44ab76293754df4af5af700fd4abd5453b866c86"
SPDX_SCHEMA_PATH = "schemas/spdx-schema.json"
SPDX_SCHEMA_BLOB_SHA1 = "0ca1c7b56bebb10fb637285698e401342b4910d6"
SPDX_SCHEMA_LICENSE = "CC-BY-3.0"
SPDX_SCHEMA_URL = (
    "https://raw.githubusercontent.com/"
    f"{SPDX_SPEC_REPOSITORY}/{SPDX_SPEC_COMMIT}/{SPDX_SCHEMA_PATH}"
)


class SPDXSchemaFetchError(ValueError):
    """Raised when the pinned upstream SPDX schema cannot be verified."""


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data, usedforsecurity=False).hexdigest()


def verify_schema_bytes(data: bytes) -> str:
    blob_sha1 = git_blob_sha1(data)
    if blob_sha1 != SPDX_SCHEMA_BLOB_SHA1:
        raise SPDXSchemaFetchError(
            "downloaded SPDX schema Git blob mismatch: "
            f"expected {SPDX_SCHEMA_BLOB_SHA1}, got {blob_sha1}"
        )
    return hashlib.sha256(data).hexdigest()


def fetch_schema() -> tuple[bytes, str]:
    request = urllib.request.Request(
        SPDX_SCHEMA_URL,
        headers={"User-Agent": "MeaningWire-release-candidate-validator"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise SPDXSchemaFetchError(f"could not fetch pinned SPDX schema: {exc}") from exc
    if not data:
        raise SPDXSchemaFetchError("pinned SPDX schema download was empty")
    sha256 = verify_schema_bytes(data)
    return data, sha256


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch and verify the immutable official SPDX 2.3 JSON Schema"
    )
    parser.add_argument("--output", required=True, help="local schema output path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data, sha256 = fetch_schema()
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
    except (SPDXSchemaFetchError, OSError) as exc:
        print(f"ERROR: {exc}")
        return 2

    print(
        "PASS: official SPDX 2.3 schema fetched from immutable upstream commit; "
        f"git_blob={SPDX_SCHEMA_BLOB_SHA1}; sha256={sha256}; license={SPDX_SCHEMA_LICENSE}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
