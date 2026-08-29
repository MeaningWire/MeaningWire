#!/usr/bin/env python3
"""Repository-local JSON object reference adapter for MeaningWire.

The adapter reads exactly one UTF-8 JSON object from a local file and emits one
validated MeaningWire envelope. It performs no network access and no writes.
"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import adapter_sdk  # noqa: E402

ADAPTER_VERSION = "0.1.0"
DEFAULT_MAX_BYTES = 1_048_576


class JsonObjectAdapterError(ValueError):
    """Raised when the local JSON object source cannot be read safely."""


class JsonObjectAdapter:
    """Read one local JSON object and emit one canonical MeaningWire envelope."""

    def __init__(
        self,
        path: str | Path,
        *,
        source: dict[str, Any],
        contract: dict[str, Any],
        record: dict[str, Any],
        max_bytes: int = DEFAULT_MAX_BYTES,
    ) -> None:
        self._path = Path(path).expanduser()
        self._source = deepcopy(source)
        self._contract = deepcopy(contract)
        self._record = deepcopy(record)
        if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes <= 0:
            raise JsonObjectAdapterError("max_bytes must be a positive integer")
        self._max_bytes = max_bytes
        adapter_sdk.validate_descriptor(self.describe())

    def describe(self) -> dict[str, Any]:
        return {
            "adapter_id": {
                "namespace": "urn:meaningwire:adapter",
                "id": "reference-json-object",
                "version": ADAPTER_VERSION,
            },
            "version": ADAPTER_VERSION,
            "source": deepcopy(self._source),
            "capabilities": ["read_records"],
            "maturity": "EXPERIMENTAL",
        }

    def _load_object(self) -> dict[str, Any]:
        if not self._path.is_file():
            raise JsonObjectAdapterError(f"source file does not exist: {self._path}")
        size = self._path.stat().st_size
        if size > self._max_bytes:
            raise JsonObjectAdapterError(
                f"source file exceeds max_bytes ({size} > {self._max_bytes})"
            )
        try:
            with self._path.open("r", encoding="utf-8") as handle:
                value = json.load(handle)
        except UnicodeDecodeError as exc:
            raise JsonObjectAdapterError("source file must be UTF-8 JSON") from exc
        except json.JSONDecodeError as exc:
            raise JsonObjectAdapterError(
                f"source file is not valid JSON: line {exc.lineno} column {exc.colno}"
            ) from exc
        if not isinstance(value, dict):
            raise JsonObjectAdapterError("source JSON root must be an object")
        return value

    def read(self) -> Iterable[dict[str, Any]]:
        envelope = adapter_sdk.build_read_envelope(
            self.describe(),
            contract=self._contract,
            record=self._record,
            data=self._load_object(),
        )
        yield adapter_sdk.validate_emitted_envelope(self.describe(), envelope)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1:
        print("usage: json_object.py <local-json-object-file>", file=sys.stderr)
        return 2
    adapter = JsonObjectAdapter(
        argv[0],
        source={
            "namespace": "urn:meaningwire:example-source",
            "id": "json-object-smoke",
            "version": "1",
        },
        contract={
            "namespace": "urn:example:contract",
            "id": "party",
            "version": "0.0.1",
        },
        record={"namespace": "urn:example:record", "id": "json-object-smoke-1"},
    )
    envelopes = list(adapter.read())
    if len(envelopes) != 1:
        raise JsonObjectAdapterError("JSON object adapter must emit exactly one envelope")
    print("PASS: JSON object reference adapter emitted one validated envelope.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
