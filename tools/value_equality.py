#!/usr/bin/env python3
"""CASE-004N: explicit, conservative, domain-aware JSON value equality."""
from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from typing import Any

RULES_FIELD = "value_equality_rules"
CONTRACT_VERSION = "case-004n-typed-domain-aware-v1"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _matching_rule(
    artifact: dict[str, Any], *, subject: Any, predicate: Any, scope: Any
) -> dict[str, Any] | None:
    rules = artifact.get(RULES_FIELD, [])
    if not isinstance(rules, list):
        raise ValueError(f"{RULES_FIELD} must be a list")
    matches = []
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            raise ValueError(f"{RULES_FIELD}[{index}] must be an object")
        if not isinstance(rule.get("predicate"), str) or not rule["predicate"]:
            raise ValueError(f"{RULES_FIELD}[{index}] requires a non-empty predicate")
        if rule.get("subject") not in (None, subject):
            continue
        if rule["predicate"] != predicate:
            continue
        if rule.get("scope") not in (None, scope):
            continue
        if rule.get("rule") not in ("canonical_json", "numeric_equivalence"):
            raise ValueError(f"{RULES_FIELD}[{index}] has unsupported rule")
        matches.append(rule)
    if len(matches) > 1:
        raise ValueError(
            f"ambiguous {RULES_FIELD} for subject={subject!r}, "
            f"predicate={predicate!r}, scope={scope!r}"
        )
    return matches[0] if matches else None


def value_key(
    value: Any,
    artifact: dict[str, Any],
    *,
    subject: Any,
    predicate: Any,
    scope: Any,
) -> str:
    """Return a stable equality key; no semantic coercion without a matching rule."""
    rule = _matching_rule(
        artifact, subject=subject, predicate=predicate, scope=scope
    )
    if rule is None or rule["rule"] == "canonical_json":
        return "json:" + _canonical_json(value)

    # Python bool is a subclass of int; reject it explicitly. Strings and numbers
    # remain distinct even when their textual contents look numeric.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "json:" + _canonical_json(value)
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("numeric_equivalence requires a finite JSON number") from exc
    if not number.is_finite():
        raise ValueError("numeric_equivalence requires a finite JSON number")
    if number == 0:
        number = Decimal(0)
    normalized = number.normalize()
    return "number:" + format(normalized, "f")


def equality_policy(
    artifact: dict[str, Any], *, subject: Any, predicate: Any, scope: Any
) -> dict[str, Any]:
    rule = _matching_rule(
        artifact, subject=subject, predicate=predicate, scope=scope
    )
    return {
        "contract_version": CONTRACT_VERSION,
        "applied_rule": rule["rule"] if rule else "canonical_json",
        "source": RULES_FIELD if rule else "conservative_default",
        "numeric_coercion_enabled": bool(rule and rule["rule"] == "numeric_equivalence"),
    }
