from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "github_repository_adapter.py"
SPEC = importlib.util.spec_from_file_location("github_repository_adapter", MODULE_PATH)
assert SPEC and SPEC.loader
adapter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adapter)


class GitHubRepositoryAdapterTests(unittest.TestCase):
    def test_build_repository_url_accepts_owner_name(self) -> None:
        self.assertEqual(
            adapter.build_repository_url("MeaningWire/MeaningWire"),
            "https://api.github.com/repos/MeaningWire/MeaningWire",
        )

    def test_build_repository_url_rejects_invalid_slug(self) -> None:
        with self.assertRaises(adapter.GitHubAdapterError):
            adapter.build_repository_url("https://github.com/MeaningWire/MeaningWire")

    def test_normalize_repository_is_deterministic_with_fixed_timestamp(self) -> None:
        payload = {
            "id": 1349847431,
            "node_id": "R_example",
            "name": "MeaningWire",
            "full_name": "MeaningWire/MeaningWire",
            "private": False,
            "html_url": "https://github.com/MeaningWire/MeaningWire",
            "url": "https://api.github.com/repos/MeaningWire/MeaningWire",
            "description": "Example",
            "visibility": "public",
            "archived": False,
            "default_branch": "main",
            "language": "Python",
            "topics": ["interoperability"],
            "owner": {"login": "MeaningWire"},
            "license": {"spdx_id": "Apache-2.0"},
            "created_at": "2026-08-28T00:00:00Z",
            "updated_at": "2026-08-28T00:00:00Z",
            "pushed_at": "2026-08-28T00:00:00Z",
        }

        first = adapter.normalize_repository(payload, retrieved_at="2026-08-28T21:00:00Z")
        second = adapter.normalize_repository(payload, retrieved_at="2026-08-28T21:00:00Z")

        self.assertEqual(first, second)
        self.assertEqual(first["adapter_output"], "github.repository.snapshot.v0")
        self.assertEqual(first["maturity"], "experimental")
        self.assertEqual(first["source"]["system"], "github")
        self.assertEqual(first["repository"]["full_name"], "MeaningWire/MeaningWire")
        self.assertIsNone(first["mapping"]["canonical_contract"])

    def test_normalize_repository_requires_identity_and_urls(self) -> None:
        with self.assertRaises(adapter.GitHubAdapterError):
            adapter.normalize_repository({"full_name": "MeaningWire/MeaningWire"})


if __name__ == "__main__":
    unittest.main()
