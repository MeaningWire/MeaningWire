from __future__ import annotations

import gzip
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import candidate_archive_integrity as integrity  # noqa: E402
import extract_candidate  # noqa: E402
import release_builder  # noqa: E402
import release_publication_preflight as preflight  # noqa: E402
import release_readiness  # noqa: E402
import validate_spdx_sbom  # noqa: E402


class _GrowingReader:
    def __init__(self, descriptor, payload: bytes) -> None:
        self._descriptor = descriptor
        self._payload = io.BytesIO(payload)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._descriptor.close()

    def fileno(self) -> int:
        return self._descriptor.fileno()

    def read(self, size: int = -1) -> bytes:
        return self._payload.read(size)


class BoundedCandidateHashingTests(unittest.TestCase):
    def _validated_candidate(self, directory: Path) -> tuple[dict[str, Path], dict[str, object]]:
        commit = release_builder.current_commit()
        result = release_builder.build_release_candidate(
            directory, expected_source_commit=commit
        )
        release_path = result["evidence"]
        release_evidence = json.loads(release_path.read_text(encoding="utf-8"))
        validation = validate_spdx_sbom.validation_evidence(
            sbom_path=result["sbom"],
            sbom_sha256=release_evidence["sbom"]["sha256"],
            schema_sha256="c" * 64,
            policy={
                "scope": "candidate archive plus governed validation dependency environment",
                "locked_dependency_count": 6,
                "package_count": 7,
                "relationship_count": 6,
            },
        )
        validation_path = directory / "spdx-validation-evidence.json"
        validation_bytes = validate_spdx_sbom.write_json(validation_path, validation)
        validate_spdx_sbom.promote_release_evidence(
            release_path,
            release_evidence,
            validation_evidence_path=validation_path,
            validation_evidence_bytes=validation_bytes,
        )
        return result, json.loads(release_path.read_text(encoding="utf-8"))

    def test_bounded_hash_matches_exact_candidate_sha256(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = release_builder.build_release_candidate(Path(temp))
            expected = hashlib.sha256(result["archive"].read_bytes()).hexdigest()
            self.assertEqual(integrity.archive_sha256(result["archive"]), expected)

    def test_archive_size_limit_fails_before_archive_open(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = release_builder.build_release_candidate(Path(temp))
            with mock.patch.object(integrity, "MAX_ARCHIVE_BYTES", 1):
                with mock.patch.object(
                    Path,
                    "open",
                    side_effect=AssertionError("over-limit archive must not be opened"),
                ):
                    with self.assertRaisesRegex(
                        integrity.CandidateArchiveError, "compressed size"
                    ):
                        integrity.archive_sha256(result["archive"])

    def test_archive_replacement_after_path_stat_is_rejected_after_open(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = release_builder.build_release_candidate(Path(temp))
            with mock.patch.object(integrity, "MAX_ARCHIVE_BYTES", 1):
                with mock.patch.object(integrity, "_archive_size", return_value=1):
                    with self.assertRaisesRegex(
                        integrity.CandidateArchiveError, "after open"
                    ):
                        integrity.archive_sha256(result["archive"])

    def test_archive_growth_during_hashing_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            descriptor_path = Path(temp) / "descriptor.bin"
            descriptor_path.write_bytes(b"1234")
            descriptor = open(descriptor_path, "rb")
            growing = _GrowingReader(descriptor, b"12345")
            with mock.patch.object(integrity, "MAX_ARCHIVE_BYTES", 4):
                with mock.patch.object(integrity, "_archive_size", return_value=4):
                    with mock.patch.object(Path, "open", return_value=growing):
                        with self.assertRaisesRegex(
                            integrity.CandidateArchiveError, "during hashing"
                        ):
                            integrity.archive_sha256(Path("candidate.tar.gz"))

    def test_raw_compressed_growth_during_inspection_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            descriptor_path = Path(temp) / "descriptor.bin"
            descriptor_path.write_bytes(b"1234")
            descriptor = open(descriptor_path, "rb")
            payload = gzip.compress(b"x" * 1024)
            growing = _GrowingReader(descriptor, payload)
            with mock.patch.object(integrity, "MAX_ARCHIVE_BYTES", 12):
                with mock.patch.object(integrity, "_archive_size", return_value=4):
                    with mock.patch.object(integrity, "_opened_archive_size", return_value=4):
                        with mock.patch.object(Path, "open", return_value=growing):
                            with self.assertRaisesRegex(
                                integrity.CandidateArchiveError, "compressed stream"
                            ):
                                integrity.read_archive(Path("candidate.tar.gz"), "0.1.0-alpha.0")

    def test_stable_inspection_rejects_mutation_after_parsing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            result = release_builder.build_release_candidate(directory)
            evidence = json.loads(result["evidence"].read_text(encoding="utf-8"))
            original = integrity.inspect_candidate

            def mutate_after_parse(*args, **kwargs):
                parsed = original(*args, **kwargs)
                with result["archive"].open("ab") as handle:
                    handle.write(b"mutation")
                return parsed

            with mock.patch.object(integrity, "inspect_candidate", side_effect=mutate_after_parse):
                with self.assertRaisesRegex(
                    integrity.CandidateArchiveError, "changed during stable bounded inspection"
                ):
                    integrity.inspect_candidate_stable(
                        result["archive"],
                        version=evidence["version"],
                        source_commit=evidence["source_commit"],
                        expected_artifact_sha256=evidence["artifact_sha256"],
                        expected_manifest_sha256=evidence["content_manifest_sha256"],
                    )

    def test_extraction_rejects_over_limit_candidate_before_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            result = release_builder.build_release_candidate(base / "candidate")
            destination = base / "extracted"
            with mock.patch.object(integrity, "MAX_ARCHIVE_BYTES", 1):
                with self.assertRaisesRegex(
                    extract_candidate.CandidateExtractionError, "compressed size"
                ):
                    extract_candidate.extract_candidate(
                        result["archive"], result["evidence"], destination
                    )
            self.assertFalse(destination.exists())

    def test_extraction_uses_stable_inspection_before_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            result = release_builder.build_release_candidate(base / "candidate")
            destination = base / "extracted"
            with mock.patch.object(
                integrity,
                "inspect_candidate_stable",
                side_effect=integrity.CandidateArchiveError("stable snapshot rejected"),
            ) as stable:
                with self.assertRaisesRegex(
                    extract_candidate.CandidateExtractionError, "stable snapshot rejected"
                ):
                    extract_candidate.extract_candidate(
                        result["archive"], result["evidence"], destination
                    )
            stable.assert_called_once()
            self.assertFalse(destination.exists())

    def test_readiness_rejects_over_limit_candidate_before_archive_inspection(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            result, evidence = self._validated_candidate(directory)
            with mock.patch.object(integrity, "MAX_ARCHIVE_BYTES", 1):
                with self.assertRaisesRegex(
                    release_readiness.ReleaseReadinessError, "compressed size"
                ):
                    release_readiness.evaluate_readiness(
                        directory,
                        expected_source_commit=evidence["source_commit"],
                        fresh_environment_verified=True,
                        documentation_build_verified=True,
                    )
            self.assertTrue(result["archive"].is_file())

    def test_readiness_uses_stable_candidate_inspection(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            _result, evidence = self._validated_candidate(directory)
            with mock.patch.object(
                integrity,
                "inspect_candidate_stable",
                side_effect=integrity.CandidateArchiveError("stable snapshot rejected"),
            ) as stable:
                with self.assertRaisesRegex(
                    release_readiness.ReleaseReadinessError, "stable snapshot rejected"
                ):
                    release_readiness.evaluate_readiness(
                        directory,
                        expected_source_commit=evidence["source_commit"],
                        fresh_environment_verified=True,
                        documentation_build_verified=True,
                    )
            stable.assert_called_once()

    def test_preflight_note_reader_rejects_over_limit_candidate_before_inspection(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            result = release_builder.build_release_candidate(directory)
            evidence = json.loads(result["evidence"].read_text(encoding="utf-8"))
            with mock.patch.object(integrity, "MAX_ARCHIVE_BYTES", 1):
                with self.assertRaisesRegex(
                    preflight.PublicationPreflightError, "compressed size"
                ):
                    preflight._candidate_member(
                        directory,
                        evidence,
                        f"docs/releases/{evidence['version']}.md",
                    )

    def test_preflight_note_reader_uses_stable_candidate_inspection(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            result = release_builder.build_release_candidate(directory)
            evidence = json.loads(result["evidence"].read_text(encoding="utf-8"))
            with mock.patch.object(
                integrity,
                "inspect_candidate_stable",
                side_effect=integrity.CandidateArchiveError("stable snapshot rejected"),
            ) as stable:
                with self.assertRaisesRegex(
                    preflight.PublicationPreflightError, "stable snapshot rejected"
                ):
                    preflight._candidate_member(
                        directory,
                        evidence,
                        f"docs/releases/{evidence['version']}.md",
                    )
            stable.assert_called_once()


if __name__ == "__main__":
    unittest.main()
