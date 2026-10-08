#!/usr/bin/env python3
"""Experimental CASE-004B semantic round-trip and ablation harness.

This is a deterministic research fixture, not an engineering safety tool and
not a stable MeaningWire contract. It uses only the Python standard library.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "tests" / "fixtures" / "proofs" / "case-004b-bridge.json"


def canonical_bytes(value: Any) -> bytes:
    """Serialize deterministically so byte equality is a reproducible check."""
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def round_trip(value: Any) -> Any:
    """Perform an actual JSON serialization/deserialization round trip."""
    return json.loads(canonical_bytes(value).decode("utf-8"))


def entity_by_id(artifact: dict[str, Any], entity_id: str) -> dict[str, Any] | None:
    return next((e for e in artifact.get("entities", []) if e.get("id") == entity_id), None)


def relation_exists(
    artifact: dict[str, Any], subject: str, predicate: str, obj: str
) -> bool:
    return any(
        r.get("subject") == subject
        and r.get("predicate") == predicate
        and r.get("object") == obj
        for r in artifact.get("relations", [])
    )


def claim_by_id(artifact: dict[str, Any], claim_id: str = "claim-C1") -> dict[str, Any] | None:
    return next((c for c in artifact.get("claims", []) if c.get("id") == claim_id), None)


def reason(artifact: dict[str, Any]) -> dict[str, Any]:
    """Return the required observable reasoning behavior for the test battery."""
    claim = claim_by_id(artifact)
    bridge = entity_by_id(artifact, "bridge-B")
    member = entity_by_id(artifact, "member-M")
    defect = entity_by_id(artifact, "crack-C")
    inspector = entity_by_id(artifact, "inspector-I")
    policy = artifact.get("policy", {})
    source_id = claim.get("source_ref") if claim else None
    source_exists = source_id is not None and entity_by_id(artifact, source_id) is not None
    reported_by_relation = bool(source_id and relation_exists(artifact, source_id, "reported", "crack-C"))
    member_is_in_bridge = relation_exists(artifact, "bridge-B", "contains", "member-M")
    defect_is_on_member = relation_exists(artifact, "member-M", "has_defect", "crack-C")
    load_bearing = relation_exists(artifact, "member-M", "structural_role", "load-bearing")
    epistemic_status = claim.get("epistemic_status") if claim else None
    confidence = claim.get("confidence") if claim else None
    scope = claim.get("scope") if claim else None
    resolution = claim.get("resolution") if claim else None
    observed_at = claim.get("observed_at") if claim else None

    if claim is None:
        evidence_state = "claim_missing"
    elif epistemic_status == "reported_not_verified":
        evidence_state = "reported_not_verified"
    elif epistemic_status == "verified":
        evidence_state = "verified"
    else:
        evidence_state = "unknown_or_changed"

    if evidence_state == "reported_not_verified" and load_bearing and policy.get("reported_defect_action"):
        recommended_action = policy["reported_defect_action"]
    elif evidence_state == "verified" and load_bearing and policy.get("verified_defect_action"):
        recommended_action = policy["verified_defect_action"]
    else:
        recommended_action = "insufficient_basis_for_policy_action"

    return {
        "T1_meaning": {
            "bridge": bridge.get("label") if bridge else None,
            "member": member.get("label") if member else None,
            "defect": defect.get("label") if defect else None,
            "member_belongs_to_bridge": member_is_in_bridge,
            "defect_belongs_to_member": defect_is_on_member,
        },
        "T2_evidence": {
            "status": evidence_state,
            "source_ref": source_id,
            "source_exists": source_exists,
            "source_relation_supports_claim": reported_by_relation,
            "source_entity_type": inspector.get("type") if inspector else None,
        },
        "T3_causality": {
            "member_is_load_bearing": load_bearing,
            "risk_implication": (
                "potential_structural_risk_if_defect_is_confirmed"
                if load_bearing and defect_is_on_member
                else "not_supported_by_current_relations"
            ),
        },
        "T4_uncertainty": {
            "confidence": confidence,
            "is_verified": evidence_state == "verified",
            "must_not_treat_as_certain": evidence_state != "verified",
        },
        "T5_time": {
            "observation_time": observed_at,
            "historical_observation_preserved": observed_at is not None,
            "current_condition_established": evidence_state == "verified",
        },
        "T6_scope": {
            "claim_scope": scope,
            "scope_is_member_level": scope == "member-M",
            "whole_bridge_unsafe_established": False,
        },
        "T7_counterfactual": {
            "if_member_not_load_bearing": "not_supported_by_current_relations",
            "if_repaired": "historical_report_remains_but_current_state_requires_new_evidence",
            "if_source_removed": "claim_provenance_incomplete",
        },
        "T8_provenance": {
            "source_ref": source_id,
            "source_present": source_exists,
            "report_event_present": any(
                e.get("type") == "inspection_reported"
                and e.get("claim_ref") == (claim.get("id") if claim else None)
                for e in artifact.get("events", [])
            ),
        },
        "T9_decision": {
            "policy_id": policy.get("id"),
            "policy_version": policy.get("version"),
            "recommended_action": recommended_action,
            "human_approval_asserted": False,
        },
    }


def remove_path(value: dict[str, Any], path: tuple[str, ...]) -> None:
    """Remove one nested key; missing keys are ignored for mutation experiments."""
    current: Any = value
    for key in path[:-1]:
        if not isinstance(current, dict) or key not in current:
            return
        current = current[key]
    if isinstance(current, dict):
        current.pop(path[-1], None)


def run_battery(artifact: dict[str, Any]) -> dict[str, Any]:
    original_behavior = reason(artifact)
    reconstructed = round_trip(artifact)
    reconstructed_behavior = reason(reconstructed)
    cases: list[dict[str, Any]] = [
        {"name": "dimensions_time", "path": ("claims",), "mutator": "observed_at"},
    ]
    # Explicit mutations below test whether each information class changes an
    # observable behavior when removed. These are targeted counterexamples,
    # not a proof of global minimality.
    ablations: list[dict[str, Any]] = []

    def compare(name: str, mutate: Any) -> None:
        reduced = copy.deepcopy(artifact)
        mutate(reduced)
        before = reason(artifact)
        after = reason(reduced)
        changed = [
            key for key in before
            if canonical_bytes(before[key]) != canonical_bytes(after[key])
        ]
        ablations.append({
            "name": name,
            "behavior_changed": bool(changed),
            "changed_tests": changed,
        })

    compare("remove_temporal_value", lambda a: a["claims"][0].pop("observed_at", None))
    compare("remove_scope", lambda a: a["claims"][0].pop("scope", None))
    compare("remove_epistemic_status", lambda a: a["claims"][0].pop("epistemic_status", None))
    compare("remove_confidence", lambda a: a["claims"][0].pop("confidence", None))
    compare("remove_provenance_reference", lambda a: a["claims"][0].pop("source_ref", None))
    compare("remove_relations", lambda a: a.pop("relations", None))
    compare("remove_policy_version", lambda a: a["policy"].pop("version", None))
    compare("remove_resolution", lambda a: a["claims"][0].pop("resolution", None))
    compare("remove_significance", lambda a: a["claims"][0].pop("significance", None))
    compare("remove_escalation_event", lambda a: a.pop("events", None))

    return {
        "status": "PASS" if canonical_bytes(original_behavior) == canonical_bytes(reconstructed_behavior) else "FAIL",
        "experiment": "CASE-004B",
        "maturity": "EXPERIMENTAL",
        "artifact_id": artifact.get("artifact_id"),
        "serialized_bytes": len(canonical_bytes(artifact)),
        "round_trip_structurally_equal": canonical_bytes(artifact) == canonical_bytes(reconstructed),
        "round_trip_behavior_equal": canonical_bytes(original_behavior) == canonical_bytes(reconstructed_behavior),
        "reference_tests": {
            name: {
                "pass": canonical_bytes(original_behavior[name]) == canonical_bytes(reconstructed_behavior[name]),
                "original": original_behavior[name],
                "reconstructed": reconstructed_behavior[name],
            }
            for name in original_behavior
        },
        "ablations": ablations,
        "interpretation": (
            "PASS means this fixture's required outputs survived JSON round trip. "
            "Ablations show only whether the current test battery detects loss; "
            "they do not prove universal or byte-level minimality."
        ),
        "network_access": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--json", action="store_true", help="emit full machine-readable report")
    args = parser.parse_args()
    with args.artifact.open("r", encoding="utf-8") as handle:
        artifact = json.load(handle)
    report = run_battery(artifact)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            f"{report['status']}: {report['experiment']} "
            f"artifact={report['artifact_id']} "
            f"bytes={report['serialized_bytes']} "
            f"round_trip_behavior_equal={report['round_trip_behavior_equal']}"
        )
        for name, result in report["reference_tests"].items():
            print(f"  {'PASS' if result['pass'] else 'FAIL'} {name}")
        for result in report["ablations"]:
            print(
                f"  {'DIVERGED' if result['behavior_changed'] else 'NO DIVERGENCE'} "
                f"{result['name']}: {','.join(result['changed_tests']) or 'none'}"
            )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
