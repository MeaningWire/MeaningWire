#!/usr/bin/env python3
"""CASE-004C: compare named JSON with a compact relational tuple encoding.

Research fixture only. The tuple layout is a versioned, external schema; its
schema/decoder cost is deliberately reported as excluded, not hidden.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from semantic_roundtrip import canonical_bytes, reason, round_trip

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "tests" / "fixtures" / "proofs" / "case-004b-bridge.json"

ROOT_FIELDS = ("artifact_id", "artifact_kind", "schema_version")
ENTITY_FIELDS = ("id", "type", "label")
RELATION_FIELDS = ("subject", "predicate", "object")
CLAIM_FIELDS = (
    "id", "subject", "predicate", "object", "epistemic_status", "confidence",
    "scope", "observed_at", "source_ref", "resolution", "significance",
)
EVENT_FIELDS = ("id", "type", "occurred_at", "actor_ref", "claim_ref")
POLICY_FIELDS = (
    "id", "version", "rule", "reported_defect_action", "verified_defect_action",
    "whole_bridge_unsafe_requires",
)


def require_exact_keys(record: dict[str, Any], fields: tuple[str, ...], where: str) -> None:
    actual = set(record)
    expected = set(fields)
    if actual != expected:
        raise ValueError(
            f"{where} schema mismatch: missing={sorted(expected - actual)}, "
            f"unexpected={sorted(actual - expected)}"
        )


def encode_relational(artifact: dict[str, Any]) -> dict[str, Any]:
    """Encode the fixture as tables of positional tuples under a shared schema."""
    require_exact_keys(artifact, ROOT_FIELDS + ("entities", "relations", "claims", "events", "policy"), "root")
    for name, fields in (
        ("entities", ENTITY_FIELDS),
        ("relations", RELATION_FIELDS),
        ("claims", CLAIM_FIELDS),
        ("events", EVENT_FIELDS),
    ):
        for index, record in enumerate(artifact[name]):
            require_exact_keys(record, fields, f"{name}[{index}]")
    require_exact_keys(artifact["policy"], POLICY_FIELDS, "policy")
    return {
        "layout": "case-004c-v1",
        "root": [artifact[key] for key in ROOT_FIELDS],
        "entities": [[record[key] for key in ENTITY_FIELDS] for record in artifact["entities"]],
        "relations": [[record[key] for key in RELATION_FIELDS] for record in artifact["relations"]],
        "claims": [[record[key] for key in CLAIM_FIELDS] for record in artifact["claims"]],
        "events": [[record[key] for key in EVENT_FIELDS] for record in artifact["events"]],
        "policy": [artifact["policy"][key] for key in POLICY_FIELDS],
    }


def decode_relational(encoded: dict[str, Any]) -> dict[str, Any]:
    """Reconstruct named JSON using the same external tuple-layout contract."""
    if encoded.get("layout") != "case-004c-v1":
        raise ValueError("unsupported relational layout")
    def records(rows: list[list[Any]], fields: tuple[str, ...], where: str) -> list[dict[str, Any]]:
        output = []
        for index, row in enumerate(rows):
            if not isinstance(row, list) or len(row) != len(fields):
                raise ValueError(f"{where}[{index}] tuple arity mismatch")
            output.append(dict(zip(fields, row)))
        return output

    root = encoded["root"]
    if not isinstance(root, list) or len(root) != len(ROOT_FIELDS):
        raise ValueError("root tuple arity mismatch")
    policy = encoded["policy"]
    if not isinstance(policy, list) or len(policy) != len(POLICY_FIELDS):
        raise ValueError("policy tuple arity mismatch")
    return {
        **dict(zip(ROOT_FIELDS, root)),
        "entities": records(encoded["entities"], ENTITY_FIELDS, "entities"),
        "relations": records(encoded["relations"], RELATION_FIELDS, "relations"),
        "claims": records(encoded["claims"], CLAIM_FIELDS, "claims"),
        "events": records(encoded["events"], EVENT_FIELDS, "events"),
        "policy": dict(zip(POLICY_FIELDS, policy)),
    }


def run_experiment(artifact: dict[str, Any]) -> dict[str, Any]:
    named_round_trip = round_trip(artifact)
    relational = encode_relational(artifact)
    reconstructed = decode_relational(round_trip(relational))
    named_bytes = len(canonical_bytes(artifact))
    relational_bytes = len(canonical_bytes(relational))
    behavior_original = reason(artifact)
    behavior_named = reason(named_round_trip)
    behavior_relational = reason(reconstructed)
    structural_equal = canonical_bytes(artifact) == canonical_bytes(reconstructed)
    behavior_equal = canonical_bytes(behavior_original) == canonical_bytes(behavior_relational)
    return {
        "experiment": "CASE-004C",
        "status": "PASS" if structural_equal and behavior_equal else "FAIL",
        "artifact_id": artifact.get("artifact_id"),
        "named_json_bytes": named_bytes,
        "relational_tuple_json_bytes": relational_bytes,
        "bytes_saved": named_bytes - relational_bytes,
        "percent_size_reduction": round((named_bytes - relational_bytes) * 100 / named_bytes, 2) if named_bytes else 0,
        "named_json_behavior_equal": canonical_bytes(behavior_original) == canonical_bytes(reason(named_round_trip)),
        "relational_structure_reconstructed_equal": structural_equal,
        "relational_behavior_equal": behavior_equal,
        "reference_behavior_groups": len(behavior_original),
        "schema_overhead_included": False,
        "decoder_cost_included": False,
        "network_access": False,
        "interpretation": (
            "PASS means this declared positional tuple encoding reconstructs this fixture and preserves "
            "the CASE-004B observable behavior groups. The byte comparison excludes the shared schema, "
            "decoder, and any version-negotiation overhead; it is not a fair total-cost comparison or "
            "proof that a general relational substrate is minimal."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    with args.artifact.open("r", encoding="utf-8") as handle:
        report = run_experiment(json.load(handle))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            f"{report['status']}: {report['experiment']} "
            f"named={report['named_json_bytes']}B relational={report['relational_tuple_json_bytes']}B "
            f"saved={report['bytes_saved']}B ({report['percent_size_reduction']}%) "
            f"behavior_equal={report['relational_behavior_equal']}"
        )
        print("Schema and decoder overhead excluded; see report interpretation.")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
