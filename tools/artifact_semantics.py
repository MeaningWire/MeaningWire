#!/usr/bin/env python3
"""CASE-004H: expose selected artifact fields as explicit observable semantics."""
from __future__ import annotations

from typing import Any


def interpret_artifact(artifact: dict[str, Any], claim_id: str = "claim-C1") -> dict[str, Any]:
    """Return bounded observations without inventing actions from judgments."""
    matches = [claim for claim in artifact.get("claims", []) if claim.get("id") == claim_id]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one claim with id {claim_id!r}")
    claim = matches[0]

    events = artifact.get("events", [])
    escalation_events = [
        {
            "id": event.get("id"),
            "type": event.get("type"),
            "occurred_at": event.get("occurred_at"),
            "actor_ref": event.get("actor_ref"),
            "claim_ref": event.get("claim_ref"),
        }
        for event in events
        if isinstance(event.get("type"), str)
        and event["type"].startswith("escalation_")
        and event.get("claim_ref") in (None, claim_id)
    ]

    return {
        "claim_dimensions": {
            "subject": claim.get("subject"),
            "predicate": claim.get("predicate"),
            "object": claim.get("object"),
            "scope": claim.get("scope"),
            "observed_at": claim.get("observed_at"),
            "epistemic_status": claim.get("epistemic_status"),
            "confidence": claim.get("confidence"),
        },
        "resolution": {
            "state": claim.get("resolution"),
            "is_explicitly_resolved": claim.get("resolution") == "resolved",
        },
        "significance": {
            "judgment": claim.get("significance"),
            "judgment_present": claim.get("significance") not in (None, ""),
            "action_inferred_from_judgment": False,
        },
        "escalation_history": {
            "count": len(escalation_events),
            "events_in_artifact_order": escalation_events,
        },
    }
