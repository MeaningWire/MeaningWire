#!/usr/bin/env python3
"""Explicit pre-release envelope-to-envelope interoperability pipeline.

This module connects already-public MeaningWire boundaries:

adapter/source envelope -> explicit mapping -> mapping application -> target envelope

It performs no implicit mapping selection and deliberately does not transfer
source approval/authority to the transformed representation.
"""

from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import mapping_application
import validate_contracts

ROOT = Path(__file__).resolve().parents[1]
PIPELINE_MATURITY = "EXPERIMENTAL"


class InteroperabilityPipelineError(ValueError):
    """Raised when an envelope cannot be transformed safely and explicitly."""


def _reference_key(value: Any, label: str) -> tuple[str, str, str]:
    try:
        validate_contracts.validate_reference(value, label)
    except validate_contracts.ContractValidationError as exc:
        raise InteroperabilityPipelineError(str(exc)) from exc
    return value["namespace"], value["id"], value.get("version", "")


def transform_envelope(
    source_envelope: dict[str, Any],
    mapping: dict[str, Any],
    *,
    target_record: dict[str, Any],
) -> dict[str, Any]:
    """Transform one validated source envelope through one explicit mapping."""

    try:
        validate_contracts.validate_envelope(source_envelope)
        validate_contracts.validate_mapping(mapping)
        validate_contracts.validate_reference(target_record, "target_record")
    except validate_contracts.ContractValidationError as exc:
        raise InteroperabilityPipelineError(str(exc)) from exc

    source_contract = _reference_key(source_envelope["contract"], "source_envelope.contract")
    mapping_source_contract = _reference_key(mapping["source"]["contract"], "mapping.source.contract")
    if source_contract != mapping_source_contract:
        raise InteroperabilityPipelineError(
            "source envelope contract must exactly match mapping.source.contract"
        )

    try:
        application = mapping_application.apply_mapping(mapping, source_envelope["data"])
    except mapping_application.MappingApplicationError as exc:
        raise InteroperabilityPipelineError(str(exc)) from exc

    provenance = deepcopy(source_envelope["provenance"])
    transformations = list(provenance.get("transformations", []))
    transformations.append(
        {
            "operation": "meaningwire.mapping.apply",
            "mapping": deepcopy(mapping["mapping_id"]),
        }
    )
    provenance["transformations"] = transformations

    target_envelope = {
        "contract": deepcopy(mapping["target"]["contract"]),
        "record": deepcopy(target_record),
        "data": deepcopy(application["target_data"]),
        "provenance": provenance,
        "authority": {
            "kind": "none",
            "approval": "not_asserted",
            "basis": "MeaningWire mapping application does not transfer source approval or authority to the target representation.",
        },
        "maturity": PIPELINE_MATURITY,
    }

    try:
        validate_contracts.validate_envelope(target_envelope)
    except validate_contracts.ContractValidationError as exc:
        raise InteroperabilityPipelineError(
            f"mapping produced invalid target envelope: {exc}"
        ) from exc
    return target_envelope


def run_synthetic_proof() -> dict[str, Any]:
    """Run the repository-local adapter -> mapping -> target-envelope proof."""

    adapters_root = ROOT / "adapters" / "reference"
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    if str(ROOT / "tools") not in sys.path:
        sys.path.insert(0, str(ROOT / "tools"))

    from adapters.reference.json_object import JsonObjectAdapter
    import mapping_registry

    adapter = JsonObjectAdapter(
        ROOT / "tests" / "fixtures" / "adapters" / "json-object-record.json",
        source={
            "namespace": "urn:meaningwire:example-source",
            "id": "synthetic-crm-json-object",
            "version": "1",
        },
        contract={
            "namespace": "urn:example:contract",
            "id": "crm-customer",
            "version": "1",
        },
        record={
            "namespace": "urn:example:record",
            "id": "crm-customer-CUST-001",
        },
    )
    source_envelopes = list(adapter.read())
    if len(source_envelopes) != 1:
        raise InteroperabilityPipelineError("synthetic source adapter did not emit one envelope")

    mapping = mapping_registry.get_mapping(
        "urn:meaningwire:mapping", "example-crm-email", "0.1.0"
    )
    target = transform_envelope(
        source_envelopes[0],
        mapping,
        target_record={
            "namespace": "urn:example:record",
            "id": "party-CUST-001",
        },
    )
    return {"source_envelope": source_envelopes[0], "mapping": mapping, "target_envelope": target}


def main() -> int:
    proof = run_synthetic_proof()
    target = proof["target_envelope"]
    expected = {"contact": {"email": "person@example.invalid"}}
    if target["data"] != expected:
        raise InteroperabilityPipelineError("synthetic proof produced unexpected target data")
    if target["authority"]["approval"] != "not_asserted":
        raise InteroperabilityPipelineError("synthetic proof transferred approval unexpectedly")
    transformations = target["provenance"].get("transformations", [])
    if len(transformations) != 1:
        raise InteroperabilityPipelineError("synthetic proof did not retain mapping provenance")
    print(
        "PASS: JSON object adapter -> source envelope -> registered mapping -> "
        "target envelope completed with explicit provenance and no transferred approval."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
