"""CASE-006A: deterministic, LLM-free quantization of human-experience states.

This is an isolated research harness, not a clinical or psychological instrument.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

CODEBOOK_VERSION = "human-experience-v0.1"
LEVELS = 8
DIMENSIONS: dict[str, tuple[str, ...]] = {
    "hope": (
        "goal_importance",
        "perceived_possibility",
        "personal_agency",
        "expectation_confidence",
    ),
    "shame": (
        "negative_self_evaluation",
        "perceived_exposure",
        "belonging_threat",
        "norm_violation_belief",
    ),
    "trust": (
        "perceived_reliability",
        "perceived_benevolence",
        "willingness_to_be_vulnerable",
        "evidence_confidence",
    ),
}
SOURCE_KINDS = {"self_report", "observation", "inference"}


def _unit_interval(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number in [0, 1]")
    if not 0 <= value <= 1:
        raise ValueError(f"{field} must be in [0, 1]")
    return float(value)


def validate_state(state: dict[str, Any]) -> None:
    required = {
        "state_id", "subject_ref", "state_type", "target_ref", "context_ref",
        "dimensions", "source_kind", "confidence", "observed_at",
    }
    if not isinstance(state, dict) or set(state) != required:
        raise ValueError("state fields do not match CASE-006A contract")
    if state["state_type"] not in DIMENSIONS:
        raise ValueError("unsupported state_type")
    if state["source_kind"] not in SOURCE_KINDS:
        raise ValueError("source_kind must be self_report, observation, or inference")
    for field in ("state_id", "subject_ref", "target_ref", "context_ref", "observed_at"):
        if not isinstance(state[field], str) or not state[field]:
            raise ValueError(f"{field} must be a non-empty string")
    if not isinstance(state["dimensions"], dict):
        raise ValueError("dimensions must be an object")
    expected = set(DIMENSIONS[state["state_type"]])
    if set(state["dimensions"]) != expected:
        raise ValueError("dimension names do not match the versioned state codebook")
    for name, value in state["dimensions"].items():
        _unit_interval(value, f"dimensions.{name}")
    _unit_interval(state["confidence"], "confidence")


def quantize(value: float) -> int:
    """Map [0, 1] to eight ordinal levels; level 0..7 is not a probability."""
    return int(round(_unit_interval(value, "value") * (LEVELS - 1)))


def dequantize(level: int) -> float:
    if isinstance(level, bool) or not isinstance(level, int) or not 0 <= level < LEVELS:
        raise ValueError("quantized level must be an integer from 0 through 7")
    return level / (LEVELS - 1)


def encode_state(state: dict[str, Any]) -> dict[str, Any]:
    """Encode dimensions positionally; retain provenance and relational context."""
    validate_state(state)
    names = DIMENSIONS[state["state_type"]]
    return {
        "codebook": CODEBOOK_VERSION,
        "state_id": state["state_id"],
        "subject_ref": state["subject_ref"],
        "state_type": state["state_type"],
        "target_ref": state["target_ref"],
        "context_ref": state["context_ref"],
        "dimension_levels": [quantize(state["dimensions"][name]) for name in names],
        "source_kind": state["source_kind"],
        "confidence_level": quantize(state["confidence"]),
        "observed_at": state["observed_at"],
    }


def decode_state(encoded: dict[str, Any]) -> dict[str, Any]:
    required = {
        "codebook", "state_id", "subject_ref", "state_type", "target_ref",
        "context_ref", "dimension_levels", "source_kind", "confidence_level",
        "observed_at",
    }
    if not isinstance(encoded, dict) or set(encoded) != required:
        raise ValueError("encoded state fields do not match CASE-006A contract")
    if encoded["codebook"] != CODEBOOK_VERSION:
        raise ValueError("unknown codebook version")
    state_type = encoded["state_type"]
    if state_type not in DIMENSIONS:
        raise ValueError("unknown state_type")
    names = DIMENSIONS[state_type]
    levels = encoded["dimension_levels"]
    if not isinstance(levels, list) or len(levels) != len(names):
        raise ValueError("dimension level count does not match codebook")
    dimensions = {name: dequantize(level) for name, level in zip(names, levels)}
    decoded = {
        "state_id": encoded["state_id"],
        "subject_ref": encoded["subject_ref"],
        "state_type": state_type,
        "target_ref": encoded["target_ref"],
        "context_ref": encoded["context_ref"],
        "dimensions": dimensions,
        "source_kind": encoded["source_kind"],
        "confidence": dequantize(encoded["confidence_level"]),
        "observed_at": encoded["observed_at"],
    }
    validate_state(decoded)
    return decoded


def encode_experience(states: list[dict[str, Any]]) -> dict[str, Any]:
    """Preserve concurrent states as separate records; never collapse to one label."""
    if not isinstance(states, list) or not states:
        raise ValueError("experience must contain at least one state")
    ids: set[str] = set()
    encoded = []
    for state in states:
        validate_state(state)
        if state["state_id"] in ids:
            raise ValueError("state_id values must be unique within an experience")
        ids.add(state["state_id"])
        encoded.append(encode_state(state))
    return {"codebook": CODEBOOK_VERSION, "states": encoded}


def decode_experience(experience: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(experience, dict) or set(experience) != {"codebook", "states"}:
        raise ValueError("experience envelope mismatch")
    if experience["codebook"] != CODEBOOK_VERSION:
        raise ValueError("unknown experience codebook")
    states = experience["states"]
    if not isinstance(states, list) or not states:
        raise ValueError("experience must contain at least one state")
    decoded = [decode_state(state) for state in states]
    ids = [state["state_id"] for state in decoded]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate state_id in encoded experience")
    return decoded


def maximum_absolute_error() -> float:
    """Theoretical maximum scalar error for nearest-level quantization."""
    return 1 / (2 * (LEVELS - 1))


def distortion(original: dict[str, Any], decoded: dict[str, Any]) -> dict[str, Any]:
    """Report per-dimension absolute errors without pretending dimensions are interchangeable."""
    validate_state(original)
    validate_state(decoded)
    if any(original[key] != decoded[key] for key in (
        "state_id", "subject_ref", "state_type", "target_ref", "context_ref",
        "source_kind", "observed_at",
    )):
        raise ValueError("non-numeric semantic metadata changed")
    errors = {
        name: abs(original["dimensions"][name] - decoded["dimensions"][name])
        for name in DIMENSIONS[original["state_type"]]
    }
    return {
        "dimension_absolute_errors": errors,
        "max_dimension_error": max(errors.values()),
        "confidence_absolute_error": abs(original["confidence"] - decoded["confidence"]),
        "non_numeric_metadata_preserved": True,
    }
