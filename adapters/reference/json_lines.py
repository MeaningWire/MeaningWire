#!/usr/bin/env python3
"""Repository-local JSON Lines reference adapter for MeaningWire.

The adapter validates a bounded UTF-8 JSON Lines file completely before yielding
any canonical envelopes. It performs no network access and no writes.
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
DEFAULT_MAX_BYTES = 2_097_152
DEFAULT_MAX_RECORDS = 10_000


class JsonLinesAdapterError(ValueError):
    """Raised when the local JSON Lines source violates the adapter boundary."""


class JsonLinesAdapter:
    """Read a bounded local JSON Lines file and emit canonical envelopes."""

    def __init__(
        self,
        path: str | Path,
        *,
        source: dict[str, Any],
        contract: dict[str, Any],
        record_namespace: str,
        record_id_field: str,
        max_bytes: int = DEFAULT_MAX_BYTES,
        max_records: int = DEFAULT_MAX_RECORDS,
    ) -> None:
        self._path = Path(path).expanduser()
        self._source = deepcopy(source)
        self._contract = deepcopy(contract)
        if not isinstance(record_namespace, str) or not record_namespace.strip():
            raise JsonLinesAdapterError("record_namespace must be a non-empty string")
        if not isinstance(record_id_field, str) or not record_id_field.strip():
            raise JsonLinesAdapterError("record_id_field must be a non-empty string")
        if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes <= 0:
            raise JsonLinesAdapterError("max_bytes must be a positive integer")
        if not isinstance(max_records, int) or isinstance(max_records, bool) or max_records <= 0:
            raise JsonLinesAdapterError("max_records must be a positive integer")
        self._record_namespace = record_namespace
        self._record_id_field = record_id_field
        self._max_bytes = max_bytes
        self._max_records = max_records
        adapter_sdk.validate_descriptor(self.describe())

    def describe(self) -> dict[str, Any]:
        return {
            "adapter_id": {
                "namespace": "urn:meaningwire:adapter",
                "id": "reference-json-lines",
                "version": ADAPTER_VERSION,
            },
            "version": ADAPTER_VERSION,
            "source": deepcopy(self._source),
            "capabilities": ["read_records"],
            "maturity": "EXPERIMENTAL",
        }

    def _load_records(self) -> list[tuple[str, dict[str, Any]]]:
        if not self._path.is_file():
            raise JsonLinesAdapterError(f"source file does not exist: {self._path}")
        size = self._path.stat().st_size
        if size > self._max_bytes:
            raise JsonLinesAdapterError(
                f"source file exceeds max_bytes ({size} > {self._max_bytes})"
            )

        records: list[tuple[str, dict[str, Any]]] = []
        seen_ids: set[str] = set()
        try:
            with self._path.open("r", encoding="utf-8") as handle:
                for line_number, raw_line in enumerate(handle, start=1):
                    line = raw_line.rstrip("\r\n")
                    if not line.strip():
                        raise JsonLinesAdapterError(
                            f"line {line_number} is blank; every line must be a JSON object"
                        )
                    try:
                        value = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise JsonLinesAdapterError(
                            f"line {line_number} is not valid JSON: column {exc.colno}"
                        ) from exc
                    if not isinstance(value, dict):
                        raise JsonLinesAdapterError(
                            f"line {line_number} JSON root must be an object"
                        )
                    record_id = value.get(self._record_id_field)
                    if not isinstance(record_id, str) or not record_id.strip():
                        raise JsonLinesAdapterError(
                            f"line {line_number} field {self._record_id_field!r} must be a non-empty string"
                        )
                    if record_id in seen_ids:
                        raise JsonLinesAdapterError(f"duplicate record id: {record_id}")
                    records.append((record_id, value))
                    seen_ids.add(record_id)
                    if len(records) > self._max_records:
                        raise JsonLinesAdapterError(
                            f"source exceeds max_records ({len(records)} > {self._max_records})"
                        )
        except UnicodeDecodeError as exc:
            raise JsonLinesAdapterError("source file must be UTF-8 JSON Lines") from exc

        if not records:
            raise JsonLinesAdapterError("source file must contain at least one record")
        return records

    def read(self) -> Iterable[dict[str, Any]]:
        records = self._load_records()
        descriptor = self.describe()
        envelopes: list[dict[str, Any]] = []
        for record_id, data in records:
            envelope = adapter_sdk.build_read_envelope(
                descriptor,
                contract=self._contract,
                record={"namespace": self._record_namespace, "id": record_id},
                data=data,
            )
            envelopes.append(adapter_sdk.validate_emitted_envelope(descriptor, envelope))
        yield from envelopes


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1:
        print("usage: json_lines.py <local-json-lines-file>", file=sys.stderr)
        return 2
    adapter = JsonLinesAdapter(
        argv[0],
        source={
            "namespace": "urn:meaningwire:example-source",
            "id": "json-lines-smoke",
            "version": "1",
        },
        contract={
            "namespace": "urn:example:contract",
            "id": "party",
            "version": "0.0.1",
        },
        record_namespace="urn:example:record",
        record_id_field="record_id",
    )
    envelopes = list(adapter.read())
    if len(envelopes) < 1:
        raise JsonLinesAdapterError("JSON Lines adapter must emit at least one envelope")
    print(f"PASS: JSON Lines reference adapter emitted {len(envelopes)} validated envelopes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
