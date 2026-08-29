from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import interoperability_pipeline  # noqa: E402
import mapping_registry  # noqa: E402
from adapters.reference.json_object import JsonObjectAdapter  # noqa: E402


class InteroperabilityPipelineTests(unittest.TestCase):
    def source_envelope(self) -> dict:
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
        return list(adapter.read())[0]

    def mapping(self) -> dict:
        return mapping_registry.get_mapping(
            "urn:meaningwire:mapping", "example-crm-email", "0.1.0"
        )

    def target_record(self) -> dict:
        return {"namespace": "urn:example:record", "id": "party-CUST-001"}

    def test_complete_synthetic_proof_matches_pinned_expected_target(self) -> None:
        proof = interoperability_pipeline.run_synthetic_proof()
        expected_path = (
            ROOT / "tests" / "fixtures" / "proofs" / "json-object-crm-email-target.json"
        )
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        self.assertEqual(proof["target_envelope"], expected)
        self.assertEqual(
            proof["source_envelope"]["data"]["email"], "person@example.invalid"
        )

    def test_source_contract_must_match_mapping_exactly(self) -> None:
        source = self.source_envelope()
        source["contract"]["version"] = "different"
        with self.assertRaisesRegex(
            interoperability_pipeline.InteroperabilityPipelineError,
            "must exactly match",
        ):
            interoperability_pipeline.transform_envelope(
                source, self.mapping(), target_record=self.target_record()
            )

    def test_source_envelope_is_not_mutated(self) -> None:
        source = self.source_envelope()
        before = copy.deepcopy(source)
        interoperability_pipeline.transform_envelope(
            source, self.mapping(), target_record=self.target_record()
        )
        self.assertEqual(source, before)

    def test_existing_provenance_transformations_are_preserved(self) -> None:
        source = self.source_envelope()
        source["provenance"]["transformations"] = [
            {
                "operation": "synthetic.previous",
                "mapping": {
                    "namespace": "urn:meaningwire:mapping",
                    "id": "previous",
                    "version": "0.0.1",
                },
            }
        ]
        target = interoperability_pipeline.transform_envelope(
            source, self.mapping(), target_record=self.target_record()
        )
        operations = [item["operation"] for item in target["provenance"]["transformations"]]
        self.assertEqual(operations, ["synthetic.previous", "meaningwire.mapping.apply"])

    def test_human_source_approval_is_not_transferred(self) -> None:
        source = self.source_envelope()
        source["authority"] = {
            "kind": "human_authority",
            "actor": {"namespace": "urn:example:actor", "id": "reviewer-1"},
            "approval": "approved",
        }
        target = interoperability_pipeline.transform_envelope(
            source, self.mapping(), target_record=self.target_record()
        )
        self.assertEqual(target["authority"]["kind"], "none")
        self.assertEqual(target["authority"]["approval"], "not_asserted")
        self.assertIn("does not transfer", target["authority"]["basis"])

    def test_target_record_must_be_valid_reference(self) -> None:
        with self.assertRaises(interoperability_pipeline.InteroperabilityPipelineError):
            interoperability_pipeline.transform_envelope(
                self.source_envelope(), self.mapping(), target_record={"id": "missing-namespace"}
            )

    def test_non_identity_transform_still_fails_closed(self) -> None:
        mapping = copy.deepcopy(self.mapping())
        mapping["transform"] = {
            "kind": "expression",
            "description": "Synthetic unimplemented expression.",
        }
        with self.assertRaisesRegex(
            interoperability_pipeline.InteroperabilityPipelineError,
            "not implemented",
        ):
            interoperability_pipeline.transform_envelope(
                self.source_envelope(), mapping, target_record=self.target_record()
            )


if __name__ == "__main__":
    unittest.main()
