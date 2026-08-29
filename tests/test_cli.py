from __future__ import annotations

import contextlib
import io
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import meaningwire  # noqa: E402


class MeaningWireCLITests(unittest.TestCase):
    def run_cli(self, argv: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = meaningwire.main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_doctor_json_reports_public_state(self) -> None:
        code, stdout, stderr = self.run_cli(["doctor", "--json"])
        self.assertEqual(code, 0, stderr)
        payload = json.loads(stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["schemas"]["bootstrap_registered"], 6)
        self.assertEqual(payload["schemas"]["draft_2020_12_registered"], 6)
        self.assertEqual(payload["mappings"]["registered"], 2)
        self.assertFalse(payload["network_access"])

    def test_schemas_list_is_deterministic(self) -> None:
        code, stdout, stderr = self.run_cli(["schemas", "list", "--json"])
        self.assertEqual(code, 0, stderr)
        payload = json.loads(stdout)
        schema_ids = [entry["id"] for entry in payload["schemas"]]
        self.assertEqual(schema_ids, sorted(schema_ids))
        self.assertEqual(len(schema_ids), 6)
        self.assertIn("urn:meaningwire:schema:identity:party:0.1.0", schema_ids)

    def test_schema_validate_accepts_valid_fixture(self) -> None:
        code, stdout, stderr = self.run_cli(
            [
                "schema",
                "validate",
                "urn:meaningwire:schema:core:envelope:0.1.0",
                str(ROOT / "tests" / "fixtures" / "valid" / "envelope-source.json"),
                "--json",
            ]
        )
        self.assertEqual(code, 0, stderr)
        payload = json.loads(stdout)
        self.assertEqual(payload["status"], "VALID")

    def test_schema_validate_rejects_invalid_fixture(self) -> None:
        code, stdout, stderr = self.run_cli(
            [
                "schema",
                "validate",
                "urn:meaningwire:schema:core:envelope:0.1.0",
                str(ROOT / "tests" / "fixtures" / "invalid" / "envelope-model-approved.json"),
                "--json",
            ]
        )
        self.assertEqual(code, 2)
        self.assertEqual(stderr, "")
        payload = json.loads(stdout)
        self.assertEqual(payload["status"], "INVALID")
        self.assertTrue(payload["errors"])

    def test_mappings_list_exposes_only_registered_examples(self) -> None:
        code, stdout, stderr = self.run_cli(["mappings", "list", "--json"])
        self.assertEqual(code, 0, stderr)
        payload = json.loads(stdout)
        identifiers = [item["mapping_id"]["id"] for item in payload["mappings"]]
        self.assertEqual(identifiers, ["example-crm-email", "example-erp-email"])

    def test_mappings_inspect_resolves_exact_mapping(self) -> None:
        code, stdout, stderr = self.run_cli(
            ["mappings", "inspect", "example-crm-email", "--version", "0.1.0", "--json"]
        )
        self.assertEqual(code, 0, stderr)
        payload = json.loads(stdout)
        self.assertEqual(payload["mapping_id"]["id"], "example-crm-email")

    def test_mappings_inspect_missing_identity_fails(self) -> None:
        code, stdout, stderr = self.run_cli(
            ["mappings", "inspect", "does-not-exist", "--version", "0.1.0", "--json"]
        )
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        payload = json.loads(stderr)
        self.assertEqual(payload["status"], "ERROR")
        self.assertIn("no mapping matches", payload["error"])

    def test_proof_run_json_matches_pinned_target(self) -> None:
        code, stdout, stderr = self.run_cli(["proof", "run", "--json"])
        self.assertEqual(code, 0, stderr)
        self.assertEqual(stderr, "")
        payload = json.loads(stdout)
        expected = json.loads(
            (
                ROOT
                / "tests"
                / "fixtures"
                / "proofs"
                / "json-object-crm-email-target.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(payload["status"], "PASS")
        self.assertFalse(payload["network_access"])
        self.assertEqual(payload["proof"]["target_envelope"], expected)
        self.assertEqual(
            payload["proof"]["mapping"]["mapping_id"]["id"],
            "example-crm-email",
        )

    def test_proof_run_text_is_explicitly_experimental(self) -> None:
        code, stdout, stderr = self.run_cli(["proof", "run"])
        self.assertEqual(code, 0, stderr)
        self.assertEqual(stderr, "")
        self.assertIn("PASS: EXPERIMENTAL synthetic interoperability proof", stdout)
        self.assertIn("target approval not asserted", stdout)
        self.assertIn("network access disabled", stdout)


if __name__ == "__main__":
    unittest.main()
