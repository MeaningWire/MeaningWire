#!/usr/bin/env python3
"""CASE-004I: validate explicit resolution and typed escalation transitions.

This is a narrow experiment contract, not a safety or domain-authority engine.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

ESCALATION_TRANSITIONS = {
    None: {"escalation_requested"},
    "escalation_requested": {"escalation_acknowledged", "escalation_withdrawn"},
    "escalation_acknowledged": {"escalation_resolved", "escalation_withdrawn"},
    "escalation_resolved": set(),
    "escalation_withdrawn": set(),
}


def _zoned_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def check_contract(artifact: dict[str, Any], claim_id: str = "claim-C1") -> dict[str, Any]:
    claims = [claim for claim in artifact.get("claims", []) if claim.get("id") == claim_id]
    if len(claims) != 1:
        raise ValueError(f"expected exactly one claim with id {claim_id!r}")
    claim = claims[0]
    entities = {
        entity.get("id")
        for entity in artifact.get("entities", [])
        if isinstance(entity.get("id"), str)
    }
    events = artifact.get("events", [])

    resolution_events = [
        event for event in events
        if event.get("type") == "resolution_confirmed" and event.get("claim_ref") == claim_id
    ]
    resolution_errors: list[str] = []
    if claim.get("resolution") == "resolved":
        if len(resolution_events) != 1:
            resolution_errors.append("resolved_state_requires_exactly_one_resolution_confirmed_event")
        for event in resolution_events:
            if not isinstance(event.get("id"), str) or not event["id"]:
                resolution_errors.append("resolution_event_missing_id")
            if not isinstance(event.get("actor_ref"), str) or event.get("actor_ref") not in entities:
                resolution_errors.append("resolution_event_actor_must_reference_known_entity")
            if _zoned_datetime(event.get("occurred_at")) is None:
                resolution_errors.append("resolution_event_requires_timezone_aware_timestamp")
    elif resolution_events:
        resolution_errors.append("resolution_confirmed_event_conflicts_with_non_resolved_state")

    escalation_events = [
        event for event in events
        if isinstance(event.get("type"), str)
        and event["type"].startswith("escalation_")
        and event.get("claim_ref") == claim_id
    ]
    escalation_errors: list[dict[str, str]] = []
    current_state: str | None = None
    previous_time: datetime | None = None
    for index, event in enumerate(escalation_events):
        event_id = event.get("id")
        event_type = event.get("type")
        actor_ref = event.get("actor_ref")
        occurred_at = _zoned_datetime(event.get("occurred_at"))
        problems: list[str] = []
        if not isinstance(event_id, str) or not event_id:
            problems.append("missing_event_id")
        if actor_ref not in entities:
            problems.append("actor_must_reference_known_entity")
        if occurred_at is None:
            problems.append("missing_or_unzoned_timestamp")
        elif previous_time is not None and occurred_at < previous_time:
            problems.append("event_time_regresses")
        if event_type not in ESCALATION_TRANSITIONS.get(current_state, set()):
            problems.append("invalid_escalation_state_transition")
        if problems:
            escalation_errors.append({
                "event_id": str(event_id),
                "event_type": str(event_type),
                "problems": ",".join(problems),
            })
        else:
            current_state = event_type
            previous_time = occurred_at

    return {
        "claim_id": claim_id,
        "resolution": {
            "recorded_state": claim.get("resolution"),
            "contract_valid": not resolution_errors,
            "errors": sorted(set(resolution_errors)),
            "confirmed_event_ids": sorted(
                str(event.get("id")) for event in resolution_events
                if isinstance(event.get("id"), str)
            ),
        },
        "escalation": {
            "recorded_event_ids_in_order": [
                str(event.get("id")) for event in escalation_events
            ],
            "derived_state": current_state,
            "contract_valid": not escalation_errors,
            "errors": escalation_errors,
        },
        "significance": {
            "recorded_judgment": claim.get("significance"),
            "causes_automatic_action": False,
        },
        "decision_boundary": {
            "physical_repair_established": False,
            "whole_bridge_safety_established": False,
            "judgment_promoted_to_action": False,
        },
    }
