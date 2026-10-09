#!/usr/bin/env python3
"""CASE-004E: multi-claim evidence analysis for a bounded synthetic fixture.

This module preserves claims individually and flags narrowly defined conflicts.
It is not a safety assessor or a general-purpose contradiction solver.
"""
from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

VERIFIED = "verified"


def _value_key(value: Any) -> str:
    """Create a deterministic key for arbitrary JSON-compatible claim values."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def analyze_claims(artifact: dict[str, Any]) -> dict[str, Any]:
    """Summarize all claims and detect incompatible verified values in same scope."""
    claims = artifact.get("claims", [])
    seen_ids: set[str] = set()
    grouped: dict[tuple[Any, Any, Any], list[dict[str, Any]]] = defaultdict(list)
    summaries: list[dict[str, Any]] = []

    for index, claim in enumerate(claims):
        claim_id = claim.get("id")
        if not isinstance(claim_id, str) or not claim_id:
            raise ValueError(f"claims[{index}] has no valid id")
        if claim_id in seen_ids:
            raise ValueError(f"duplicate claim id: {claim_id}")
        seen_ids.add(claim_id)
        summary = {
            "claim_id": claim_id,
            "subject": claim.get("subject"),
            "predicate": claim.get("predicate"),
            "object": claim.get("object"),
            "epistemic_status": claim.get("epistemic_status"),
            "confidence": claim.get("confidence"),
            "scope": claim.get("scope"),
            "source_ref": claim.get("source_ref"),
        }
        summaries.append(summary)
        grouped[(claim.get("subject"), claim.get("predicate"), claim.get("scope"))].append(summary)

    conflicts: list[dict[str, Any]] = []
    for (subject, predicate, scope), group in sorted(
        grouped.items(), key=lambda item: tuple(str(part) for part in item[0])
    ):
        verified = [c for c in group if c["epistemic_status"] == VERIFIED]
        values: dict[str, list[str]] = defaultdict(list)
        display_values: dict[str, Any] = {}
        for claim in verified:
            value_key = _value_key(claim["object"])
            values[value_key].append(claim["claim_id"])
            display_values[value_key] = claim["object"]
        if len(values) > 1:
            conflicts.append({
                "subject": subject,
                "predicate": predicate,
                "scope": scope,
                "claim_ids": sorted(c["claim_id"] for c in verified),
                "conflicting_values": [
                    {"value": display_values[key], "claim_ids": sorted(ids)}
                    for key, ids in sorted(values.items())
                ],
                "status": "conflicting_verified_claims",
            })

    return {
        "claim_count": len(summaries),
        "claims": sorted(summaries, key=lambda claim: claim["claim_id"]),
        "conflicts": conflicts,
        "conflict_count": len(conflicts),
        "decision_boundary": {
            "whole_bridge_unsafe_established": False,
            "automatic_resolution_performed": False,
            "human_review_required_for_conflict": bool(conflicts),
        },
    }


if __name__ == "__main__":
    raise SystemExit("Import analyze_claims() from the test harness; no CLI is defined.")
