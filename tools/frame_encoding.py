"""CASE-005B frame-reference encoding for a controlled synthetic scene.

This lab codec is deliberately small and explicit. Its size comparison includes
the shared frame definition once across a batch of scene instances.
"""
from __future__ import annotations

from typing import Any


def encode_scene(scene: dict[str, Any], frame: dict[str, Any]) -> dict[str, Any]:
    required_frame = {"frame_id", "entity_type", "attributes"}
    if set(frame) != required_frame:
        raise ValueError("frame schema mismatch")
    if not isinstance(frame["attributes"], list) or not frame["attributes"]:
        raise ValueError("frame attributes must be a non-empty list")
    if len(set(frame["attributes"])) != len(frame["attributes"]):
        raise ValueError("frame attributes must be unique")
    if set(scene) != {"scene_id", "entities", "relations"}:
        raise ValueError("scene schema mismatch")

    rows = []
    for entity in scene["entities"]:
        if entity.get("type") != frame["entity_type"]:
            raise ValueError("entity type does not match frame")
        if set(entity) != {"id", "type", "attributes"}:
            raise ValueError("entity schema mismatch")
        attrs = entity["attributes"]
        if set(attrs) != set(frame["attributes"]):
            raise ValueError("entity attributes do not match frame")
        values = []
        for name in frame["attributes"]:
            item = attrs[name]
            if not isinstance(item, dict) or set(item) != {"value", "status", "confidence"}:
                raise ValueError(f"attribute {name} must preserve value, status, and confidence")
            values.append([item["value"], item["status"], item["confidence"]])
        rows.append([entity["id"], values])

    relations = []
    for relation in scene["relations"]:
        if set(relation) != {"subject", "predicate", "object"}:
            raise ValueError("relation schema mismatch")
        relations.append([relation["subject"], relation["predicate"], relation["object"]])

    return {
        "frame_ref": frame["frame_id"],
        "scene_id": scene["scene_id"],
        "entities": rows,
        "relations": relations,
    }


def decode_scene(encoded: dict[str, Any], frame: dict[str, Any]) -> dict[str, Any]:
    if set(encoded) != {"frame_ref", "scene_id", "entities", "relations"}:
        raise ValueError("encoded scene schema mismatch")
    if encoded["frame_ref"] != frame.get("frame_id"):
        raise ValueError("unknown or mismatched frame reference")

    entities = []
    for row in encoded["entities"]:
        if not isinstance(row, list) or len(row) != 2:
            raise ValueError("entity tuple arity mismatch")
        entity_id, values = row
        if not isinstance(values, list) or len(values) != len(frame["attributes"]):
            raise ValueError("attribute tuple arity mismatch")
        attributes = {}
        for name, item in zip(frame["attributes"], values):
            if not isinstance(item, list) or len(item) != 3:
                raise ValueError("attribute state tuple arity mismatch")
            value, status, confidence = item
            attributes[name] = {
                "value": value,
                "status": status,
                "confidence": confidence,
            }
        entities.append({"id": entity_id, "type": frame["entity_type"], "attributes": attributes})

    relations = []
    for row in encoded["relations"]:
        if not isinstance(row, list) or len(row) != 3:
            raise ValueError("relation tuple arity mismatch")
        subject, predicate, obj = row
        relations.append({"subject": subject, "predicate": predicate, "object": obj})

    return {"scene_id": encoded["scene_id"], "entities": entities, "relations": relations}
