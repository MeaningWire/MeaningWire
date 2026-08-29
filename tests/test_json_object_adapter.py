from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from adapters.reference.json_object import JsonObjectAdapter, JsonObjectAdapterError  # noqa: E402


class JsonObjectAdapterTests(unittest.TestCase):
    def adapter(self, path: Path, *, max_bytes: int = 1_048_576) -> JsonObjectAdapter:
        return JsonObjectAdapter(
            path,
            source={
                "namespace": "urn:meaningwire:example-source",
                "id": "synthetic-json-object",
                "version": "1",
            },
            contract={
                "namespace": "urn:example:contract",
                "id": "party",
                "version": "0.0.1",
            },
            record={"namespace": "urn:example:record", "id": "json-object-1"},
            max_bytes=max_bytes,
        )

    def test_fixture_emits_one_validated_envelope(self) -> None:
        path = ROOT / "tests" / "fixtures" / "adapters" / "json-object-record.json"
        envelopes = list(self.adapter(path).read())
        self.assertEqual(len(envelopes), 1)
        envelope = envelopes[0]
        self.assertEqual(envelope["data"]["customer_id"], "CUST-001")
        self.assertEqual(envelope["data"]["email"], "person@example.invalid")
        self.assertEqual(
            envelope["provenance"]["source"]["id"], "synthetic-json-object"
        )
        self.assertEqual(envelope["authority"]["approval"], "not_asserted")

    def test_non_object_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "array.json"
            path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
            with self.assertRaisesRegex(JsonObjectAdapterError, "root must be an object"):
                list(self.adapter(path).read())

    def test_invalid_json_is_rejected_with_deterministic_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "broken.json"
            path.write_text('{"broken": ', encoding="utf-8")
            with self.assertRaisesRegex(JsonObjectAdapterError, "not valid JSON"):
                list(self.adapter(path).read())

    def test_size_limit_is_enforced_before_parse(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "large.json"
            path.write_text('{"value":"1234567890"}', encoding="utf-8")
            with self.assertRaisesRegex(JsonObjectAdapterError, "exceeds max_bytes"):
                list(self.adapter(path, max_bytes=8).read())

    def test_missing_source_file_is_rejected(self) -> None:
        path = ROOT / "tests" / "fixtures" / "adapters" / "does-not-exist.json"
        with self.assertRaisesRegex(JsonObjectAdapterError, "source file does not exist"):
            list(self.adapter(path).read())

    def test_max_bytes_must_be_positive_integer(self) -> None:
        path = ROOT / "tests" / "fixtures" / "adapters" / "json-object-record.json"
        with self.assertRaisesRegex(JsonObjectAdapterError, "positive integer"):
            self.adapter(path, max_bytes=0)


if __name__ == "__main__":
    unittest.main()
