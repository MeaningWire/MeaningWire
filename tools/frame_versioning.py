"""CASE-005C versioned frame references and fail-closed recovery."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from frame_encoding import decode_scene, encode_scene


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def frame_digest(schema: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(schema)).hexdigest()


def make_versioned_frame(schema: dict[str, Any], version: int) -> dict[str, Any]:
    _validate_schema(schema)
    if isinstance(version, bool) or not isinstance(version, int) or version < 1:
        raise ValueError("frame version must be a positive integer")
    return {
        "frame_id": schema["frame_id"],
        "version": version,
        "schema": schema,
        "digest": frame_digest(schema),
    }


def _validate_schema(schema: dict[str, Any]) -> None:
    if not isinstance(schema, dict) or set(schema) != {"frame_id", "entity_type", "attributes"}:
        raise ValueError("frame schema mismatch")
    if not isinstance(schema["frame_id"], str) or not schema["frame_id"]:
        raise ValueError("frame_id must be a non-empty string")
    if not isinstance(schema["entity_type"], str) or not schema["entity_type"]:
        raise ValueError("entity_type must be a non-empty string")
    attrs = schema["attributes"]
    if not isinstance(attrs, list) or not attrs or any(not isinstance(x, str) or not x for x in attrs):
        raise ValueError("frame attributes must be a non-empty list of names")
    if len(set(attrs)) != len(attrs):
        raise ValueError("frame attributes must be unique")


def _validate_versioned_frame(frame: dict[str, Any]) -> None:
    if not isinstance(frame, dict) or set(frame) != {"frame_id", "version", "schema", "digest"}:
        raise ValueError("versioned frame schema mismatch")
    _validate_schema(frame["schema"])
    if frame["frame_id"] != frame["schema"]["frame_id"]:
        raise ValueError("frame identity mismatch")
    if isinstance(frame["version"], bool) or not isinstance(frame["version"], int) or frame["version"] < 1:
        raise ValueError("frame version must be a positive integer")
    if frame["digest"] != frame_digest(frame["schema"]):
        raise ValueError("frame digest mismatch")


def encode_versioned_scene(scene: dict[str, Any], frame: dict[str, Any]) -> dict[str, Any]:
    _validate_versioned_frame(frame)
    payload = encode_scene(scene, frame["schema"])
    return {
        "frame_ref": frame["frame_id"],
        "frame_version": frame["version"],
        "frame_digest": frame["digest"],
        "payload": payload,
    }


def decode_versioned_scene(encoded: dict[str, Any], frame: dict[str, Any]) -> dict[str, Any]:
    _validate_versioned_frame(frame)
    if not isinstance(encoded, dict) or set(encoded) != {
        "frame_ref", "frame_version", "frame_digest", "payload"
    }:
        raise ValueError("versioned scene envelope mismatch")
    if (
        encoded["frame_ref"] != frame["frame_id"]
        or encoded["frame_version"] != frame["version"]
        or encoded["frame_digest"] != frame["digest"]
    ):
        raise ValueError("unknown or incompatible frame version")
    return decode_scene(encoded["payload"], frame["schema"])


def create_frame_update(current: dict[str, Any], next_schema: dict[str, Any]) -> dict[str, Any]:
    _validate_versioned_frame(current)
    _validate_schema(next_schema)
    if next_schema["frame_id"] != current["frame_id"]:
        raise ValueError("frame update cannot change frame identity")
    if next_schema == current["schema"]:
        raise ValueError("frame update must change the schema")
    return {
        "frame_id": current["frame_id"],
        "from_version": current["version"],
        "to_version": current["version"] + 1,
        "previous_digest": current["digest"],
        "schema": next_schema,
        "next_digest": frame_digest(next_schema),
    }


def apply_frame_update(current: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    """Validate all preconditions before returning a new frame; never mutates current."""
    _validate_versioned_frame(current)
    required = {
        "frame_id", "from_version", "to_version", "previous_digest", "schema", "next_digest"
    }
    if not isinstance(update, dict) or set(update) != required:
        raise ValueError("frame update schema mismatch")
    if update["frame_id"] != current["frame_id"]:
        raise ValueError("frame update identity mismatch")
    if update["from_version"] != current["version"] or update["previous_digest"] != current["digest"]:
        raise ValueError("stale or out-of-order frame update")
    if update["to_version"] != current["version"] + 1:
        raise ValueError("frame versions must advance by exactly one")
    _validate_schema(update["schema"])
    if update["schema"]["frame_id"] != current["frame_id"]:
        raise ValueError("frame update cannot change frame identity")
    if update["next_digest"] != frame_digest(update["schema"]):
        raise ValueError("frame update digest mismatch")
    return make_versioned_frame(update["schema"], update["to_version"])
