from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import validate_jsonschema  # noqa: E402

SCHEMA_ID = "urn:meaningwire:schema:identity:party:0.1.0"


class IdentityPartyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry, cls.schemas = validate_jsonschema.build_registry()
        cls.validator = validate_jsonschema.validator_for(
            SCHEMA_ID, cls.registry, cls.schemas
        )

    def assertValid(self, value: dict) -> None:
        errors = list(self.validator.iter_errors(value))
        self.assertEqual(errors, [], [error.message for error in errors])

    def assertInvalid(self, value: dict) -> None:
        self.assertTrue(list(self.validator.iter_errors(value)))

    def test_synthetic_person_fixture_is_valid(self) -> None:
        value = json.loads(
            (
                ROOT
                / "tests"
                / "fixtures"
                / "domains"
                / "identity"
                / "party-person.json"
            ).read_text(encoding="utf-8")
        )
        self.assertValid(value)

    def test_synthetic_organization_fixture_is_valid(self) -> None:
        value = json.loads(
            (
                ROOT
                / "tests"
                / "fixtures"
                / "domains"
                / "identity"
                / "party-organization.json"
            ).read_text(encoding="utf-8")
        )
        self.assertValid(value)

    def test_party_requires_meaningful_attributes_beyond_type(self) -> None:
        self.assertInvalid({"party_type": "person"})

    def test_unknown_party_type_is_rejected(self) -> None:
        self.assertInvalid(
            {
                "party_type": "customer",
                "names": [{"kind": "display", "value": "Synthetic Customer"}],
            }
        )

    def test_source_system_identifier_metadata_requires_scheme(self) -> None:
        self.assertInvalid(
            {
                "party_type": "organization",
                "identifiers": [{"value": "ABC", "scheme_version": "2"}],
            }
        )
        self.assertInvalid(
            {
                "party_type": "organization",
                "identifiers": [{"value": "ABC", "scheme_agency": "issuer"}],
            }
        )

    def test_contact_kind_is_explicit_and_bounded(self) -> None:
        self.assertInvalid(
            {
                "party_type": "person",
                "contact_points": [{"kind": "fax", "value": "+1-555-0100"}],
            }
        )

    def test_domain_data_does_not_duplicate_envelope_record_identity(self) -> None:
        self.assertInvalid(
            {
                "party_type": "person",
                "names": [{"kind": "display", "value": "Synthetic Person"}],
                "party_id": "canonical-id-does-not-belong-here",
            }
        )

    def test_vendor_or_business_role_fields_are_not_implicit_party_properties(self) -> None:
        self.assertInvalid(
            {
                "party_type": "organization",
                "names": [{"kind": "display", "value": "Synthetic Supplier"}],
                "supplier_id": "SUP-1",
            }
        )
        self.assertInvalid(
            {
                "party_type": "organization",
                "names": [{"kind": "display", "value": "Synthetic Buyer"}],
                "role": "buyer",
            }
        )


if __name__ == "__main__":
    unittest.main()
