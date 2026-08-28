from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mapping_registry  # noqa: E402
import validate_jsonschema  # noqa: E402


class MappingRegistryTests(unittest.TestCase):
    def test_registry_loads_in_deterministic_identity_order(self) -> None:
        mappings = mapping_registry.list_mappings()
        self.assertEqual(len(mappings), 2)
        self.assertEqual(
            [mapping["mapping_id"]["id"] for mapping in mappings],
            ["example-crm-email", "example-erp-email"],
        )

    def test_registered_definitions_pass_draft_2020_12_mapping_schema(self) -> None:
        schema_registry, schemas = validate_jsonschema.build_registry()
        validator = validate_jsonschema.validator_for(
            "urn:meaningwire:schema:mapping:definition:0.1.0",
            schema_registry,
            schemas,
        )
        for mapping in mapping_registry.list_mappings():
            validator.validate(mapping)

    def test_source_contract_filter_resolves_one_candidate(self) -> None:
        mapping = mapping_registry.select_unique(
            source_contract={
                "namespace": "urn:example:contract",
                "id": "crm-customer",
                "version": "1",
            },
            target_contract={
                "namespace": "urn:example:contract",
                "id": "party",
                "version": "0.0.1",
            },
            target_path="$.contact.email",
        )
        self.assertEqual(mapping["mapping_id"]["id"], "example-crm-email")

    def test_broad_target_query_returns_candidates_without_guessing(self) -> None:
        candidates = mapping_registry.find_mappings(
            target_contract={
                "namespace": "urn:example:contract",
                "id": "party",
                "version": "0.0.1",
            },
            target_path="$.contact.email",
        )
        self.assertEqual(len(candidates), 2)
        with self.assertRaisesRegex(
            mapping_registry.MappingRegistryError,
            "mapping selection is ambiguous",
        ):
            mapping_registry.require_unique(candidates)

    def test_exact_identity_lookup(self) -> None:
        mapping = mapping_registry.get_mapping(
            "urn:meaningwire:mapping",
            "example-erp-email",
            "0.1.0",
        )
        self.assertEqual(mapping["source"]["contract"]["id"], "erp-account")

    def test_missing_identity_fails_explicitly(self) -> None:
        with self.assertRaisesRegex(
            mapping_registry.MappingRegistryError,
            "no mapping matches",
        ):
            mapping_registry.get_mapping(
                "urn:meaningwire:mapping",
                "does-not-exist",
                "0.1.0",
            )


if __name__ == "__main__":
    unittest.main()
