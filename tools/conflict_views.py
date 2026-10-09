#!/usr/bin/env python3
"""CASE-004L: explicit historical and active conflict views.

Counts represent conflicting (subject, predicate, scope) groups, not pairwise
claim combinations. Historical disagreement is never erased by supersession.
"""
from __future__ import annotations

from typing import Any


CONTRACT_VERSION = "case-004l-both-views-v1"
ACTIVE_CONFLICT_STATUS = "conflicting_verified_claims"


def build_conflict_views(
    raw_claim_analysis: dict[str, Any],
    temporal_analysis: dict[str, Any],
) -> dict[str, Any]:
    """Return separate historical and active conflict measures without conflation."""
    historical = list(raw_claim_analysis.get("conflicts", []))
    active = [
        {
            "subject": group.get("subject"),
            "predicate": group.get("predicate"),
            "scope": group.get("scope"),
            "claim_ids": list(group.get("active_verified_claim_ids", [])),
            "active_values": list(group.get("active_values", [])),
            "status": group.get("status"),
        }
        for group in temporal_analysis.get("groups", [])
        if group.get("status") == ACTIVE_CONFLICT_STATUS
    ]

    return {
        "contract_version": CONTRACT_VERSION,
        "count_unit": "conflicting_subject_predicate_scope_group",
        "historical_disagreement_count": len(historical),
        "historical_disagreements": historical,
        "active_unresolved_conflict_count": len(active),
        "active_unresolved_conflicts": active,
        "semantic_rules": {
            "historical_disagreement_survives_supersession": True,
            "active_conflict_requires_multiple_distinct_active_verified_values": True,
            "supersession_must_be_explicit_valid_and_temporally_later": True,
            "historical_count_is_not_active_count": True,
            "counts_are_group_counts_not_pair_counts": True,
        },
    }


if __name__ == "__main__":
    raise SystemExit("Import build_conflict_views() from the test harness; no CLI is defined.")
