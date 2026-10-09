#!/usr/bin/env python3
"""CASE-004K: compare raw evidence conflicts with temporal active-claim state."""
from __future__ import annotations

from typing import Any

import artifact_semantics
import multi_claim_reasoning
import resolution_escalation_contract
import temporal_claim_reasoning
from semantic_roundtrip import reason


def integrated_view(artifact: dict[str, Any], claim_id: str = "claim-C1") -> dict[str, Any]:
    """Keep distinct interpreter outputs visible and flag their semantic relationship."""
    raw_claims = multi_claim_reasoning.analyze_claims(artifact)
    temporal = temporal_claim_reasoning.analyze_temporal_claims(artifact)
    field_semantics = artifact_semantics.interpret_artifact(artifact, claim_id)
    contract = resolution_escalation_contract.check_contract(artifact, claim_id)
    base_reasoning = reason(artifact)

    temporal_by_key = {
        (group.get("subject"), group.get("predicate"), group.get("scope")): group
        for group in temporal["groups"]
    }
    comparisons = []
    for conflict in raw_claims["conflicts"]:
        key = (conflict.get("subject"), conflict.get("predicate"), conflict.get("scope"))
        temporal_group = temporal_by_key.get(key)
        if temporal_group and temporal_group.get("status") == "resolved_by_explicit_later_supersession":
            relationship = "raw_evidence_conflict_but_temporally_superseded"
        elif temporal_group and temporal_group.get("status") == "conflicting_verified_claims":
            relationship = "raw_and_active_conflict"
        else:
            relationship = "raw_conflict_without_matching_temporal_resolution"
        comparisons.append({
            "subject": conflict.get("subject"),
            "predicate": conflict.get("predicate"),
            "scope": conflict.get("scope"),
            "raw_conflict_status": conflict.get("status"),
            "temporal_status": temporal_group.get("status") if temporal_group else "no_matching_temporal_group",
            "relationship": relationship,
        })

    return {
        "base_reasoning": base_reasoning,
        "raw_claim_analysis": raw_claims,
        "temporal_analysis": temporal,
        "field_semantics": field_semantics,
        "resolution_escalation_contract": contract,
        "cross_interpreter_comparisons": comparisons,
        "semantic_boundary": {
            "raw_claim_history_is_preserved": True,
            "temporal_supersession_does_not_delete_history": True,
            "whether_raw_conflicts_should_be_named_active_conflicts": "requires_contract_decision",
        },
    }
