from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import adapter_sdk  # noqa: E402


class SyntheticAdapter:
    def __init__(self, descriptor: dict, envelopes: list[dict] | None = None) -> None:
        self._descriptor = descriptor
        self._envelopes = envelopes or []

    def describe(self) -> dict:
        return copy.deepcopy(self._descriptor)

    def read(self):
        yield from copy.deepcopy(self._envelopes)


class AdapterSDKTests(unittest.TestCase):
    def descriptor(self) -> dict:
        return {
            "adapter_id": {
                "namespace": "urn:meaningwire:adapter",
                "id": "synthetic-memory",
                "version": "0.1.0",
            },
            "version": "0.1.0",
            "source": {
                "namespace": "urn:meaningwire:example-source",
                "id": "synthetic-memory",
                "version": "1",
            },
            "capabilities": ["read_records"],
            "maturity": "EXPERIMENTAL",
        }

    def test_descriptor_validates_and_is_copied(self) -> None:
        descriptor = self.descriptor()
        validated = adapter_sdk.validate_descriptor(descriptor)
        self.assertEqual(validated, descriptor)
        self.assertIsNot(validated, descriptor)
        self.assertIsNot(validated["adapter_id"], descriptor["adapter_id"])

    def test_descriptor_version_must_match_identity_version(self) -> None:
        descriptor = self.descriptor()
        descriptor["version"] = "9.9.9"
        with self.assertRaisesRegex(
            adapter_sdk.AdapterContractError,
            "adapter.adapter_id.version must equal adapter.version",
        ):
            adapter_sdk.validate_descriptor(descriptor)

    def test_capabilities_must_be_unique_sorted_and_read_only(self) -> None:
        descriptor = self.descriptor()
        descriptor["capabilities"] = ["read_records", "discover_contracts"]
        with self.assertRaisesRegex(adapter_sdk.AdapterContractError, "unique and sorted"):
            adapter_sdk.validate_descriptor(descriptor)

        descriptor = self.descriptor()
        descriptor["capabilities"] = ["read_records", "write_records"]
        with self.assertRaisesRegex(adapter_sdk.AdapterContractError, "not permitted"):
            adapter_sdk.validate_descriptor(descriptor)

    def test_adapter_protocol_validation_does_not_read_data(self) -> None:
        class NoReadDuringValidation(SyntheticAdapter):
            def read(self):
                raise AssertionError("validate_adapter must not consume records")
                yield  # pragma: no cover

        descriptor = adapter_sdk.validate_adapter(NoReadDuringValidation(self.descriptor()))
        self.assertEqual(descriptor["adapter_id"]["id"], "synthetic-memory")

    def test_build_read_envelope_preserves_source_provenance(self) -> None:
        descriptor = self.descriptor()
        data = {"email": "person@example.invalid", "nested": {"x": 1}}
        envelope = adapter_sdk.build_read_envelope(
            descriptor,
            contract={"namespace": "urn:example:contract", "id": "party", "version": "0.0.1"},
            record={"namespace": "urn:example:record", "id": "record-1"},
            data=data,
        )
        self.assertEqual(envelope["provenance"]["source"], descriptor["source"])
        self.assertEqual(envelope["authority"]["approval"], "not_asserted")
        self.assertEqual(envelope["data"], data)
        self.assertIsNot(envelope["data"], data)

    def test_emitted_envelope_source_must_match_adapter_source(self) -> None:
        descriptor = self.descriptor()
        envelope = adapter_sdk.build_read_envelope(
            descriptor,
            contract={"namespace": "urn:example:contract", "id": "party", "version": "0.0.1"},
            record={"namespace": "urn:example:record", "id": "record-1"},
            data={"email": "person@example.invalid"},
        )
        envelope["provenance"]["source"]["id"] = "different-source"
        with self.assertRaisesRegex(adapter_sdk.AdapterContractError, "must match adapter.source"):
            adapter_sdk.validate_emitted_envelope(descriptor, envelope)

    def test_adapter_cannot_assert_human_approval(self) -> None:
        descriptor = self.descriptor()
        envelope = adapter_sdk.build_read_envelope(
            descriptor,
            contract={"namespace": "urn:example:contract", "id": "party", "version": "0.0.1"},
            record={"namespace": "urn:example:record", "id": "record-1"},
            data={"email": "person@example.invalid"},
        )
        envelope["authority"] = {
            "kind": "human_authority",
            "actor": {"namespace": "urn:example:actor", "id": "human-1"},
            "approval": "approved",
        }
        with self.assertRaisesRegex(adapter_sdk.AdapterContractError, "cannot assert human approval"):
            adapter_sdk.validate_emitted_envelope(descriptor, envelope)


if __name__ == "__main__":
    unittest.main()
