from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import validate_jsonschema  # noqa: E402


class StandardsValidationTests(unittest.TestCase):
    def test_registered_schemas_are_valid_draft_2020_12(self) -> None:
        self.assertEqual(validate_jsonschema.validate_registered_schemas(), 5)

    def test_fixture_manifest_with_real_json_schema_engine(self) -> None:
        self.assertEqual(validate_jsonschema.validate_fixture_manifest(), (2, 2))

    def test_cross_schema_urn_resolution_is_local(self) -> None:
        registry, schemas = validate_jsonschema.build_registry()
        validator = validate_jsonschema.validator_for(
            "urn:meaningwire:schema:core:envelope:0.1.0",
            registry,
            schemas,
        )
        with (ROOT / "tests" / "fixtures" / "valid" / "envelope-source.json").open(
            "r", encoding="utf-8"
        ) as handle:
            instance = json.load(handle)
        validator.validate(instance)

    def test_unregistered_schema_is_rejected(self) -> None:
        registry, schemas = validate_jsonschema.build_registry()
        with self.assertRaisesRegex(
            validate_jsonschema.StandardsValidationError,
            "schema is not registered",
        ):
            validate_jsonschema.validator_for(
                "urn:meaningwire:schema:missing:0.1.0",
                registry,
                schemas,
            )


if __name__ == "__main__":
    unittest.main()
