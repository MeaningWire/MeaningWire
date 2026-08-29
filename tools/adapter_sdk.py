#!/usr/bin/env python3
"""Experimental read-only Adapter SDK foundation for MeaningWire.

This public reference interface defines how an adapter identifies itself and
emits MeaningWire envelopes without introducing vendor-specific semantics,
write-back behavior, hidden credentials, or a second contract system.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable, Protocol, runtime_checkable

import validate_contracts

READ_ONLY_CAPABILITIES = {"discover_contracts", "read_records"}


class AdapterContractError(ValueError):
    """Raised when adapter metadata or emitted data violates the SDK boundary."""


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AdapterContractError(f"{label} must be a non-empty string")
    return value


def _reference_key(value: Any, label: str, *, require_version: bool = False) -> tuple[str, str, str]:
    try:
        validate_contracts.validate_reference(value, label)
    except validate_contracts.ContractValidationError as exc:
        raise AdapterContractError(str(exc)) from exc
    namespace = value["namespace"]
    identifier = value["id"]
    version = value.get("version", "")
    if require_version and not version:
        raise AdapterContractError(f"{label}.version is required")
    return namespace, identifier, version


def validate_descriptor(value: Any) -> dict[str, Any]:
    """Validate and return a defensive copy of an adapter descriptor."""

    if not isinstance(value, dict):
        raise AdapterContractError("adapter descriptor must be an object")
    allowed = {"adapter_id", "version", "source", "capabilities", "maturity"}
    extra = set(value) - allowed
    if extra:
        raise AdapterContractError(f"adapter descriptor contains unsupported keys: {sorted(extra)}")
    missing = allowed - set(value)
    if missing:
        raise AdapterContractError(f"adapter descriptor missing required keys: {sorted(missing)}")

    adapter_key = _reference_key(value["adapter_id"], "adapter.adapter_id", require_version=True)
    version = _require_string(value["version"], "adapter.version")
    if adapter_key[2] != version:
        raise AdapterContractError("adapter.adapter_id.version must equal adapter.version")

    _reference_key(value["source"], "adapter.source")

    capabilities = value["capabilities"]
    if not isinstance(capabilities, list) or not capabilities:
        raise AdapterContractError("adapter.capabilities must be a non-empty array")
    if any(not isinstance(item, str) or not item.strip() for item in capabilities):
        raise AdapterContractError("adapter.capabilities items must be non-empty strings")
    if capabilities != sorted(set(capabilities)):
        raise AdapterContractError("adapter.capabilities must be unique and sorted")
    unsupported = set(capabilities) - READ_ONLY_CAPABILITIES
    if unsupported:
        raise AdapterContractError(
            f"adapter capabilities are not permitted by the read-only foundation: {sorted(unsupported)}"
        )
    if "read_records" not in capabilities:
        raise AdapterContractError("read-only adapters must declare read_records")

    maturity = _require_string(value["maturity"], "adapter.maturity")
    if maturity not in validate_contracts.MATURITY_STATES:
        raise AdapterContractError("adapter.maturity is not recognized")

    return deepcopy(value)


@runtime_checkable
class ReadOnlyAdapter(Protocol):
    """Minimal behavioral protocol for pre-release read-only adapters."""

    def describe(self) -> dict[str, Any]:
        """Return adapter metadata satisfying ``validate_descriptor``."""

    def read(self) -> Iterable[dict[str, Any]]:
        """Yield MeaningWire envelopes without mutating the source system."""


def validate_adapter(adapter: Any) -> dict[str, Any]:
    """Validate the structural protocol and descriptor without reading data."""

    if not isinstance(adapter, ReadOnlyAdapter):
        raise AdapterContractError("adapter must implement describe() and read()")
    return validate_descriptor(adapter.describe())


def build_read_envelope(
    descriptor: dict[str, Any],
    *,
    contract: dict[str, Any],
    record: dict[str, Any],
    data: dict[str, Any],
) -> dict[str, Any]:
    """Build a validated canonical envelope for one read-only adapter record."""

    descriptor = validate_descriptor(descriptor)
    if not isinstance(data, dict):
        raise AdapterContractError("adapter record data must be an object")

    source = deepcopy(descriptor["source"])
    provenance: dict[str, Any] = {"source": source}
    if source.get("version"):
        provenance["source_version"] = source["version"]

    envelope = {
        "contract": deepcopy(contract),
        "record": deepcopy(record),
        "data": deepcopy(data),
        "provenance": provenance,
        "authority": {
            "kind": "source_authority",
            "approval": "not_asserted",
            "basis": "Read through a MeaningWire adapter; no human approval asserted.",
        },
        "maturity": descriptor["maturity"],
    }

    try:
        validate_contracts.validate_envelope(envelope)
    except validate_contracts.ContractValidationError as exc:
        raise AdapterContractError(f"adapter emitted invalid envelope: {exc}") from exc
    return envelope


def validate_emitted_envelope(descriptor: dict[str, Any], envelope: Any) -> dict[str, Any]:
    """Validate an emitted envelope and bind its provenance to the adapter source."""

    descriptor = validate_descriptor(descriptor)
    try:
        validate_contracts.validate_envelope(envelope)
    except validate_contracts.ContractValidationError as exc:
        raise AdapterContractError(f"adapter emitted invalid envelope: {exc}") from exc

    expected = _reference_key(descriptor["source"], "adapter.source")
    actual = _reference_key(envelope["provenance"]["source"], "envelope.provenance.source")
    if actual != expected:
        raise AdapterContractError("envelope provenance.source must match adapter.source")

    if envelope["authority"]["approval"] != "not_asserted":
        raise AdapterContractError("read-only adapters cannot assert human approval")

    return deepcopy(envelope)


def main() -> int:
    descriptor = {
        "adapter_id": {
            "namespace": "urn:meaningwire:adapter",
            "id": "synthetic-smoke",
            "version": "0.1.0",
        },
        "version": "0.1.0",
        "source": {
            "namespace": "urn:meaningwire:example-source",
            "id": "synthetic-smoke",
            "version": "1",
        },
        "capabilities": ["read_records"],
        "maturity": "EXPERIMENTAL",
    }
    envelope = build_read_envelope(
        descriptor,
        contract={"namespace": "urn:example:contract", "id": "party", "version": "0.0.1"},
        record={"namespace": "urn:example:record", "id": "smoke-1"},
        data={"email": "person@example.invalid"},
    )
    validate_emitted_envelope(descriptor, envelope)
    print("PASS: read-only Adapter SDK descriptor and envelope boundary validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
