from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mapping_application  # noqa: E402
import mapping_registry  # noqa: E402


class MappingApplicationTests(unittest.TestCase):
    def mapping(self) -> dict:
        return mapping_registry.get_mapping(
            "urn:meaningwire:mapping", "example-crm-email", "0.1.0"
        )

    def test_parse_supported_paths(self) -> None:
        self.assertEqual(mapping_application.parse_simple_member_path("$"), ())
        self.assertEqual(mapping_application.parse_simple_member_path("$.email"), ("email",))
        self.assertEqual(
            mapping_application.parse_simple_member_path("$.contact.email"),
            ("contact", "email"),
        )

    def test_rich_jsonpath_syntax_is_rejected(self) -> None:
        for path in (
            "$['email']",
            "$.items[0]",
            "$.*",
            "$..email",
            "$.items[*]",
            "$.items[?@.active]",
            "$.hyphen-name",
            "$.contact.",
        ):
            with self.subTest(path=path):
                with self.assertRaises(mapping_application.MappingApplicationError):
                    mapping_application.parse_simple_member_path(path)

    def test_get_value_returns_deep_copy(self) -> None:
        source = {"contact": {"email": {"value": "person@example.invalid"}}}
        value = mapping_application.get_value(source, "$.contact.email")
        self.assertEqual(value, {"value": "person@example.invalid"})
        self.assertIsNot(value, source["contact"]["email"])

    def test_missing_source_path_fails(self) -> None:
        with self.assertRaisesRegex(
            mapping_application.MappingApplicationError, "source path does not exist"
        ):
            mapping_application.get_value({}, "$.email")

    def test_source_path_cannot_cross_scalar(self) -> None:
        with self.assertRaisesRegex(
            mapping_application.MappingApplicationError, "crosses a non-object"
        ):
            mapping_application.get_value({"contact": "not-object"}, "$.contact.email")

    def test_set_value_creates_nested_object_without_mutating_input(self) -> None:
        target = {"existing": 1}
        result = mapping_application.set_value(target, "$.contact.email", "x@example.invalid")
        self.assertEqual(
            result,
            {"existing": 1, "contact": {"email": "x@example.invalid"}},
        )
        self.assertEqual(target, {"existing": 1})

    def test_target_collision_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            mapping_application.MappingApplicationError, "collides with non-object"
        ):
            mapping_application.set_value({"contact": "occupied"}, "$.contact.email", "x")
        with self.assertRaisesRegex(
            mapping_application.MappingApplicationError, "already contains a value"
        ):
            mapping_application.set_value(
                {"contact": {"email": "occupied"}}, "$.contact.email", "x"
            )

    def test_apply_registered_mapping_creates_expected_target(self) -> None:
        source = {"email": "person@example.invalid", "untouched": {"x": 1}}
        original = copy.deepcopy(source)
        result = mapping_application.apply_mapping(self.mapping(), source)
        self.assertEqual(
            result["target_data"],
            {"contact": {"email": "person@example.invalid"}},
        )
        self.assertEqual(result["transform_kind"], "identity")
        self.assertEqual(source, original)

    def test_unimplemented_transform_fails_closed(self) -> None:
        mapping = copy.deepcopy(self.mapping())
        mapping["transform"] = {
            "kind": "expression",
            "description": "Synthetic unimplemented expression.",
        }
        with self.assertRaisesRegex(
            mapping_application.MappingApplicationError,
            "transform kind 'expression' is not implemented",
        ):
            mapping_application.apply_mapping(mapping, {"email": "x@example.invalid"})


if __name__ == "__main__":
    unittest.main()
