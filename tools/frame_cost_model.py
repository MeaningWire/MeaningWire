"""Deterministic byte-cost model for CASE-005D frame reuse and schema drift."""
from __future__ import annotations

import json
from typing import Any

from frame_versioning import (
    apply_frame_update,
    create_frame_update,
    encode_versioned_scene,
    make_versioned_frame,
)


BASE_ATTRIBUTES = ["color", "motion"]
EXTRA_ATTRIBUTES = ["lane", "signal", "heading", "speed", "occupancy"]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def make_scene(index: int, schema: dict[str, Any]) -> dict[str, Any]:
    attrs: dict[str, dict[str, Any]] = {}
    for name in schema["attributes"]:
        if name == "color":
            value, status, confidence = ("red" if index % 2 else "blue"), "verified", 1.0
        elif name == "motion":
            value, status, confidence = ("moving" if index % 3 else "stopped"), "reported", 0.9
        elif name == "lane":
            value, status, confidence = index % 4 + 1, "verified", 1.0
        elif name == "signal":
            value, status, confidence = ("green" if index % 2 else "red"), "reported", 0.8
        elif name == "heading":
            value, status, confidence = (index * 15) % 360, "estimated", 0.7
        elif name == "speed":
            value, status, confidence = index * 1.25, "measured", 0.95
        else:
            value, status, confidence = (index % 5 != 0), "reported", 0.8
        attrs[name] = {"value": value, "status": status, "confidence": confidence}
    return {
        "scene_id": f"scene-{index}",
        "entities": [
            {"id": f"vehicle-{index}", "type": schema["entity_type"], "attributes": attrs}
        ],
        "relations": [],
    }


def run_cost_case(message_count: int, change_interval: int | None) -> dict[str, Any]:
    """Each schema change adds one new attribute; interval is message count between changes."""
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
    initial_frame_bytes = len(canonical_bytes(frame))
    update_bytes = 0
    explicit_bytes = 0
    instance_bytes = 0
    updates = 0
    all_scenes: list[dict[str, Any]] = []

    for index in range(1, message_count + 1):
        if (
            change_interval is not None
            and index > 1
            and (index - 1) % change_interval == 0
            and len(schema["attributes"]) < len(BASE_ATTRIBUTES) + len(EXTRA_ATTRIBUTES)
        ):
            next_attribute = EXTRA_ATTRIBUTES[len(schema["attributes"]) - len(BASE_ATTRIBUTES)]
            next_schema = {**schema, "attributes": [*schema["attributes"], next_attribute]}
            update = create_frame_update(frame, next_schema)
            update_bytes += len(canonical_bytes(update))
            frame = apply_frame_update(frame, update)
            schema = next_schema
            updates += 1

        scene = make_scene(index, schema)
        all_scenes.append(scene)
        explicit_bytes += len(canonical_bytes(scene))
        message = encode_versioned_scene(scene, frame)
        instance_bytes += len(canonical_bytes(message))

    total_wire_bytes = initial_frame_bytes + update_bytes + instance_bytes
    return {
        "messages": message_count,
        "change_interval": change_interval,
        "schema_updates": updates,
        "explicit_json_bytes": explicit_bytes,
        "initial_frame_bytes": initial_frame_bytes,
        "frame_update_bytes": update_bytes,
        "instance_envelope_and_payload_bytes": instance_bytes,
        "total_frame_protocol_bytes": total_wire_bytes,
        "bytes_saved": explicit_bytes - total_wire_bytes,
        "percent_saved": round((explicit_bytes - total_wire_bytes) / explicit_bytes * 100, 2),
    }


def benchmark_matrix() -> list[dict[str, Any]]:
    rows = []
    for count in (1, 2, 5, 10, 25, 50, 100):
        for interval in (None, 10, 4, 2):
            rows.append(run_cost_case(count, interval))
    return rows


if __name__ == "__main__":
    print(json.dumps(benchmark_matrix(), indent=2, sort_keys=True))
