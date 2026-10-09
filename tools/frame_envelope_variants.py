"""Compare the existing versioned frame envelope with a compact cached-frame envelope."""
from __future__ import annotations

from typing import Any

from frame_cost_model import BASE_ATTRIBUTES, EXTRA_ATTRIBUTES, canonical_bytes, make_scene
from frame_encoding import decode_scene, encode_scene
from frame_versioning import (
    apply_frame_update,
    create_frame_update,
    encode_versioned_scene,
    make_versioned_frame,
)


def _checked_frame(frame: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(frame, dict) or set(frame) != {"frame_id", "version", "schema", "digest"}:
        raise ValueError("versioned frame schema mismatch")
    expected = make_versioned_frame(frame["schema"], frame["version"])
    if frame != expected:
        raise ValueError("versioned frame digest or metadata mismatch")
    return expected


def encode_compact_scene(scene: dict[str, Any], frame: dict[str, Any]) -> dict[str, Any]:
    """Encode against a receiver-cached frame; send frame reference/version, not digest twice."""
    checked = _checked_frame(frame)
    explicit = encode_scene(scene, checked["schema"])
    payload = {key: value for key, value in explicit.items() if key != "frame_ref"}
    return {
        "frame_ref": checked["frame_id"],
        "frame_version": checked["version"],
        "payload": payload,
    }


def decode_compact_scene(encoded: dict[str, Any], frame: dict[str, Any]) -> dict[str, Any]:
    checked = _checked_frame(frame)
    if not isinstance(encoded, dict) or set(encoded) != {"frame_ref", "frame_version", "payload"}:
        raise ValueError("compact scene envelope mismatch")
    if (
        encoded["frame_ref"] != checked["frame_id"]
        or isinstance(encoded["frame_version"], bool)
        or encoded["frame_version"] != checked["version"]
    ):
        raise ValueError("unknown or incompatible cached frame")
    payload = encoded["payload"]
    if not isinstance(payload, dict) or set(payload) != {"scene_id", "entities", "relations"}:
        raise ValueError("compact scene payload mismatch")
    return decode_scene({"frame_ref": encoded["frame_ref"], **payload}, checked["schema"])


def compare_envelope_costs(message_count: int, change_interval: int | None) -> dict[str, Any]:
    """Charge frame setup, updates, and all instances for both envelope variants."""
    if message_count < 1:
        raise ValueError("message_count must be positive")
    if change_interval is not None and change_interval < 2:
        raise ValueError("change_interval must be at least 2")

    schema: dict[str, Any] = {
        "frame_id": "vehicle-observation",
        "entity_type": "vehicle",
        "attributes": list(BASE_ATTRIBUTES),
    }
    frame = make_versioned_frame(schema, 1)
    initial_bytes = len(canonical_bytes(frame))
    update_bytes = explicit_bytes = current_bytes = compact_bytes = 0
    updates = 0

    for index in range(1, message_count + 1):
        if (
            change_interval is not None
            and index > 1
            and (index - 1) % change_interval == 0
            and len(schema["attributes"]) < len(BASE_ATTRIBUTES) + len(EXTRA_ATTRIBUTES)
        ):
            next_schema = {
                **schema,
                "attributes": [
                    *schema["attributes"],
                    EXTRA_ATTRIBUTES[len(schema["attributes"]) - len(BASE_ATTRIBUTES)],
                ],
            }
            update = create_frame_update(frame, next_schema)
            update_bytes += len(canonical_bytes(update))
            frame = apply_frame_update(frame, update)
            schema = next_schema
            updates += 1

        scene = make_scene(index, schema)
        explicit_bytes += len(canonical_bytes(scene))
        current_bytes += len(canonical_bytes(encode_versioned_scene(scene, frame)))
        compact_bytes += len(canonical_bytes(encode_compact_scene(scene, frame)))

    current_total = initial_bytes + update_bytes + current_bytes
    compact_total = initial_bytes + update_bytes + compact_bytes
    return {
        "messages": message_count,
        "change_interval": change_interval,
        "schema_updates": updates,
        "explicit_json_bytes": explicit_bytes,
        "initial_frame_bytes": initial_bytes,
        "frame_update_bytes": update_bytes,
        "existing_instance_bytes": current_bytes,
        "existing_total_bytes": current_total,
        "existing_bytes_saved": explicit_bytes - current_total,
        "compact_instance_bytes": compact_bytes,
        "compact_total_bytes": compact_total,
        "compact_bytes_saved": explicit_bytes - compact_total,
        "compact_percent_saved": round((explicit_bytes - compact_total) / explicit_bytes * 100, 2),
    }
