from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from adapters.reference.json_lines import JsonLinesAdapter, JsonLinesAdapterError  # noqa: E402


class JsonLinesAdapterTests(unittest.TestCase):
    def adapter(
        self,
        path: Path,
        *,
        max_bytes: int = 2_097_152,
        max_records: int = 10_000,
    ) -> JsonLinesAdapter:
        return JsonLinesAdapter(
            path,
            source={
                "namespace": "urn:meaningwire:example-source",
                "id": "synthetic-json-lines",
                "version": "1",
            },
            contract={
                "namespace": "urn:example:contract",
                "id": "party",
                "version": "0.0.1",
            },
            record_namespace="urn:example:record",
            record_id_field="record_id",
            max_bytes=max_bytes,
            max_records=max_records,
        )

    def test_fixture_emits_two_validated_envelopes(self) -> None:
        path = ROOT / "tests" / "fixtures" / "adapters" / "json-lines-records.jsonl"
        envelopes = list(self.adapter(path).read())
        self.assertEqual([item["record"]["id"] for item in envelopes], ["REC-001", "REC-002"])
        self.assertEqual(envelopes[0]["data"]["email"], "one@example.invalid")
        self.assertEqual(envelopes[1]["data"]["email"], "two@example.invalid")
        self.assertTrue(all(item["authority"]["approval"] == "not_asserted" for item in envelopes))
        self.assertTrue(
            all(item["provenance"]["source"]["id"] == "synthetic-json-lines" for item in envelopes)
        )

    def test_blank_line_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "blank.jsonl"
            path.write_text('{"record_id":"A"}\n\n{"record_id":"B"}\n', encoding="utf-8")
            with self.assertRaisesRegex(JsonLinesAdapterError, "line 2 is blank"):
                list(self.adapter(path).read())

    def test_invalid_later_line_yields_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "partial.jsonl"
            path.write_text('{"record_id":"A"}\n{"record_id":\n', encoding="utf-8")
            iterator = self.adapter(path).read()
            with self.assertRaisesRegex(JsonLinesAdapterError, "line 2 is not valid JSON"):
                next(iterator)

    def test_non_object_line_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "array.jsonl"
            path.write_text('[1,2,3]\n', encoding="utf-8")
            with self.assertRaisesRegex(JsonLinesAdapterError, "root must be an object"):
                list(self.adapter(path).read())

    def test_missing_record_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing-id.jsonl"
            path.write_text('{"email":"person@example.invalid"}\n', encoding="utf-8")
            with self.assertRaisesRegex(JsonLinesAdapterError, "must be a non-empty string"):
                list(self.adapter(path).read())

    def test_duplicate_record_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.jsonl"
            path.write_text('{"record_id":"A"}\n{"record_id":"A"}\n', encoding="utf-8")
            with self.assertRaisesRegex(JsonLinesAdapterError, "duplicate record id: A"):
                list(self.adapter(path).read())

    def test_empty_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.jsonl"
            path.write_text("", encoding="utf-8")
            with self.assertRaisesRegex(JsonLinesAdapterError, "at least one record"):
                list(self.adapter(path).read())

    def test_max_records_is_enforced_before_yield(self) -> None:
        path = ROOT / "tests" / "fixtures" / "adapters" / "json-lines-records.jsonl"
        iterator = self.adapter(path, max_records=1).read()
        with self.assertRaisesRegex(JsonLinesAdapterError, "exceeds max_records"):
            next(iterator)

    def test_max_bytes_is_enforced(self) -> None:
        path = ROOT / "tests" / "fixtures" / "adapters" / "json-lines-records.jsonl"
        with self.assertRaisesRegex(JsonLinesAdapterError, "exceeds max_bytes"):
            list(self.adapter(path, max_bytes=8).read())


if __name__ == "__main__":
    unittest.main()
