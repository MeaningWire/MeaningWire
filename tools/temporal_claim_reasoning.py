#!/usr/bin/env python3
"""CASE-004F: bounded time-aware claim supersession experiment."""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from typing import Any

VERIFIED = "verified"


def _value_key(value: Any) -> str:
    """Use the same canonical JSON equality rule as raw claim analysis."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def analyze_temporal_claims(artifact: dict[str, Any]) -> dict[str, Any]:
    """Resolve only explicit, same-scope, later verified supersession links."""
    claims = artifact.get("claims", [])
    by_id: dict[str, dict[str, Any]] = {}
    group_key: dict[str, tuple[Any, Any, Any]] = {}
    for index, claim in enumerate(claims):
        claim_id = claim.get("id")
        if not isinstance(claim_id, str) or not claim_id:
            raise ValueError(f"claims[{index}] has no valid id")
        if claim_id in by_id:
            raise ValueError(f"duplicate claim id: {claim_id}")
        by_id[claim_id] = claim
        group_key[claim_id] = (
            claim.get("subject"), claim.get("predicate"), claim.get("scope")
        )

    superseded: set[str] = set()
    accepted_edges: list[dict[str, str]] = []
    rejected_edges: list[dict[str, str]] = []
    for relation in artifact.get("relations", []):
        if relation.get("predicate") != "supersedes":
            continue
        newer_id, older_id = relation.get("subject"), relation.get("object")
        newer, older = by_id.get(newer_id), by_id.get(older_id)
        reason = None
        if newer is None or older is None:
            reason = "unknown_claim_reference"
        elif group_key[newer_id] != group_key[older_id]:
            reason = "scope_or_subject_mismatch"
        elif newer.get("epistemic_status") != VERIFIED or older.get("epistemic_status") != VERIFIED:
            reason = "both_claims_must_be_verified"
        else:
            newer_time = _parse_time(newer.get("observed_at"))
            older_time = _parse_time(older.get("observed_at"))
            if newer_time is None or older_time is None:
                reason = "missing_or_unzoned_time"
            elif newer_time <= older_time:
                reason = "superseding_claim_not_later"
        if reason:
            rejected_edges.append({
                "newer_claim_id": str(newer_id),
                "older_claim_id": str(older_id),
                "reason": reason,
            })
        else:
            superseded.add(older_id)
            accepted_edges.append({
                "newer_claim_id": newer_id,
                "older_claim_id": older_id,
            })

    grouped: dict[tuple[Any, Any, Any], list[dict[str, Any]]] = defaultdict(list)
    for claim in claims:
        grouped[group_key[claim["id"]]].append(claim)

    groups = []
    for (subject, predicate, scope), members in sorted(
        grouped.items(), key=lambda item: tuple(str(part) for part in item[0])
    ):
        active = [
            claim for claim in members
            if claim["id"] not in superseded and claim.get("epistemic_status") == VERIFIED
        ]
        values: dict[str, list[str]] = defaultdict(list)
        display_values: dict[str, Any] = {}
        for claim in active:
            key = _value_key(claim.get("object"))
            values[key].append(claim["id"])
            display_values[key] = claim.get("object")
        if len(values) > 1:
            status = "conflicting_verified_claims"
        elif any(claim["id"] in superseded for claim in members):
            status = "resolved_by_explicit_later_supersession" if active else "supersession_without_active_verified_claim"
        else:
            status = "no_verified_conflict"
        groups.append({
            "subject": subject,
            "predicate": predicate,
            "scope": scope,
            "claim_ids": sorted(claim["id"] for claim in members),
            "active_verified_claim_ids": sorted(claim["id"] for claim in active),
            "status": status,
            "active_values": [
                {"value": display_values[key], "claim_ids": sorted(ids)}
                for key, ids in sorted(values.items())
            ],
        })

    return {
        "claim_count": len(claims),
        "claims_preserved": sorted(by_id),
        "accepted_supersessions": sorted(
            accepted_edges, key=lambda edge: (edge["newer_claim_id"], edge["older_claim_id"])
        ),
        "rejected_supersessions": sorted(
            rejected_edges, key=lambda edge: (edge["newer_claim_id"], edge["older_claim_id"], edge["reason"])
        ),
        "groups": groups,
        "decision_boundary": {
            "automatic_truth_selection": False,
            "whole_bridge_unsafe_established": False,
            "explicit_supersession_only": True,
        },
    }
