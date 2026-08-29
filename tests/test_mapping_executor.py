from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mapping_executor  # noqa: E402
import mapping_registry  # noqa: E402


class MappingExecutorTests(unittest.TestCase):
    def registered_mapping(self) -> dict:
        return mapping_registry.get_mapping(
            "urn:meaningwire:mapping", "example-crm-email", "0.1.0"
        )

    def test_registered_identity_mapping_preserves_scalar(self) -> None:
        result = mapping_executor.execute_registered_value(
            "urn:meaningwire:mapping",
            "example-crm-email",
            "person@example.invalid",
            version="0.1.0",
        )
        self.assertEqual(result["value"], "person@example.invalid")
        self.assertEqual(result["transform_kind"], "identity")
        self.assertEqual(result["mapping_id"]["id"], "example-crm-email")

    def test_identity_returns_deep_copy_for_mutable_value(self) -> None:
        source = {"nested": ["a", {"b": 2}]}
        result = mapping_executor.execute_value(self.registered_mapping(), source)
        self.assertEqual(result["value"], source)
        self.assertIsNot(result["value"], source)
        self.assertIsNot(result["value"]["nested"], source["nested"])
        result["value"]["nested"].append("changed")
        self.assertEqual(source, {"nested": ["a", {"b": 2}]})

    def test_expression_transform_fails_closed(self) -> None:
        mapping = copy.deepcopy(self.registered_mapping())
        mapping["transform"] = {
            "kind": "expression",
            "description": "Synthetic unimplemented expression for fail-closed testing.",
        }
        with self.assertRaisesRegex(
            mapping_executor.MappingExecutionError,
            "transform kind 'expression' is not implemented",
        ):
            mapping_executor.execute_value(mapping, "value")

    def test_lookup_transform_fails_closed(self) -> None:
        mapping = copy.deepcopy(self.registered_mapping())
        mapping["transform"] = {
            "kind": "lookup",
            "description": "Synthetic unimplemented lookup for fail-closed testing.",
        }
        with self.assertRaisesRegex(
            mapping_executor.MappingExecutionError,
            "transform kind 'lookup' is not implemented",
        ):
            mapping_executor.execute_value(mapping, "value")

    def test_code_transform_fails_closed(self) -> None:
        mapping = copy.deepcopy(self.registered_mapping())
        mapping["transform"] = {
            "kind": "code",
            "description": "Synthetic unimplemented code transform for fail-closed testing.",
        }
        with self.assertRaisesRegex(
            mapping_executor.MappingExecutionError,
            "transform kind 'code' is not implemented",
        ):
            mapping_executor.execute_value(mapping, "value")

    def test_manual_transform_fails_closed(self) -> None:
        mapping = copy.deepcopy(self.registered_mapping())
        mapping["transform"] = {
            "kind": "manual",
            "description": "Synthetic manual transform for fail-closed testing.",
        }
        with self.assertRaisesRegex(
            mapping_executor.MappingExecutionError,
            "transform kind 'manual' is not implemented",
        ):
            mapping_executor.execute_value(mapping, "value")

    def test_missing_transform_fails_closed(self) -> None:
        mapping = copy.deepcopy(self.registered_mapping())
        del mapping["transform"]
        with self.assertRaisesRegex(
            mapping_executor.MappingExecutionError,
            "has no executable transform",
        ):
            mapping_executor.execute_value(mapping, "value")

    def test_invalid_mapping_is_rejected_before_execution(self) -> None:
        mapping = copy.deepcopy(self.registered_mapping())
        mapping["relationship"] = "invented"
        with self.assertRaisesRegex(
            mapping_executor.MappingExecutionError,
            "mapping is invalid",
        ):
            mapping_executor.execute_value(mapping, "value")


if __name__ == "__main__":
    unittest.main()
