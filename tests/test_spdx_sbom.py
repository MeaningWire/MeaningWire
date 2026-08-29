from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import fetch_spdx_schema  # noqa: E402
import generate_spdx_sbom  # noqa: E402
import validate_spdx_sbom  # noqa: E402


class SPDXCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.version = generate_spdx_sbom.load_version()
        self.commit = generate_spdx_sbom.current_commit()
        self.archive_name = f"MeaningWire-{self.version}.tar.gz"
        self.archive_sha256 = "a" * 64
        self.created = generate_spdx_sbom.commit_created_at(self.commit)
        self.sbom = generate_spdx_sbom.build_spdx_document(
            version=self.version,
            source_commit=self.commit,
            created=self.created,
            archive_name=self.archive_name,
            archive_sha256=self.archive_sha256,
        )
        self.release_evidence = {
            "version": self.version,
            "source_commit": self.commit,
            "artifact": self.archive_name,
            "artifact_sha256": self.archive_sha256,
        }

    def test_generation_is_deterministic(self) -> None:
        second = generate_spdx_sbom.build_spdx_document(
            version=self.version,
            source_commit=self.commit,
            created=self.created,
            archive_name=self.archive_name,
            archive_sha256=self.archive_sha256,
        )
        self.assertEqual(
            generate_spdx_sbom.json_bytes(self.sbom),
            generate_spdx_sbom.json_bytes(second),
        )

    def test_scope_is_root_plus_exact_locked_dependency_set(self) -> None:
        packages = {package["SPDXID"]: package for package in self.sbom["packages"]}
        self.assertEqual(len(packages), 7)
        self.assertEqual(self.sbom["spdxVersion"], "SPDX-2.3")
        self.assertEqual(self.sbom["dataLicense"], "CC0-1.0")
        self.assertEqual(self.sbom["documentDescribes"], ["SPDXRef-Package-MeaningWire"])
        self.assertEqual(
            packages["SPDXRef-Package-MeaningWire"]["checksums"][0]["checksumValue"],
            self.archive_sha256,
        )
        self.assertIn("SPDXRef-Package-jsonschema", packages)
        self.assertIn("SPDXRef-Package-jsonschema-specifications", packages)
        self.assertIn("SPDXRef-Package-referencing", packages)
        self.assertIn("SPDXRef-Package-rpds-py", packages)
        self.assertIn("SPDXRef-Package-typing-extensions", packages)
        self.assertIn("SPDXRef-Package-attrs", packages)

    def test_project_policy_accepts_generated_document(self) -> None:
        policy = validate_spdx_sbom.validate_meaningwire_policy(
            self.sbom,
            self.release_evidence,
        )
        self.assertEqual(policy["locked_dependency_count"], 6)
        self.assertEqual(policy["package_count"], 7)

    def test_project_policy_rejects_missing_locked_dependency(self) -> None:
        broken = copy.deepcopy(self.sbom)
        broken["packages"] = [
            package
            for package in broken["packages"]
            if package["SPDXID"] != "SPDXRef-Package-jsonschema"
        ]
        with self.assertRaisesRegex(
            validate_spdx_sbom.SPDXValidationError,
            "locked dependency missing",
        ):
            validate_spdx_sbom.validate_meaningwire_policy(
                broken,
                self.release_evidence,
            )

    def test_project_policy_rejects_wrong_candidate_digest(self) -> None:
        broken = copy.deepcopy(self.sbom)
        broken["packages"][0]["checksums"][0]["checksumValue"] = "b" * 64
        with self.assertRaisesRegex(
            validate_spdx_sbom.SPDXValidationError,
            "root package SHA-256",
        ):
            validate_spdx_sbom.validate_meaningwire_policy(
                broken,
                self.release_evidence,
            )

    def test_upstream_schema_identity_is_pinned(self) -> None:
        self.assertEqual(
            fetch_spdx_schema.SPDX_SPEC_COMMIT,
            "44ab76293754df4af5af700fd4abd5453b866c86",
        )
        self.assertEqual(
            fetch_spdx_schema.SPDX_SCHEMA_BLOB_SHA1,
            "0ca1c7b56bebb10fb637285698e401342b4910d6",
        )
        self.assertEqual(fetch_spdx_schema.SPDX_SCHEMA_LICENSE, "CC-BY-3.0")
        with self.assertRaises(fetch_spdx_schema.SPDXSchemaFetchError):
            fetch_spdx_schema.verify_schema_bytes(b"not the official schema")


if __name__ == "__main__":
    unittest.main()
