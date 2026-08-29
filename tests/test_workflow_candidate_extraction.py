from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


class WorkflowCandidateExtractionTests(unittest.TestCase):
    def test_workflows_do_not_use_raw_tar_extraction(self) -> None:
        offenders: list[str] = []
        for path in sorted([*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")]):
            text = path.read_text(encoding="utf-8")
            if re.search(r"(?m)\btar\s+[^\n]*-[^\n]*x|\btar\s+-x", text):
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(offenders, [], f"raw tar extraction is forbidden: {offenders}")

    def test_candidate_verification_workflows_use_validated_extractor(self) -> None:
        required = {
            "contract-validation.yml",
            "release-candidate.yml",
            "release-publication-preflight.yml",
        }
        missing: list[str] = []
        for name in sorted(required):
            path = WORKFLOWS / name
            text = path.read_text(encoding="utf-8")
            if "python tools/extract_candidate.py" not in text:
                missing.append(name)
        self.assertEqual(missing, [], f"validated candidate extractor missing from: {missing}")


if __name__ == "__main__":
    unittest.main()
