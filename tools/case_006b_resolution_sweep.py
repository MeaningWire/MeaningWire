"""CASE-006B: resolution, collision, and serialized-size sweep for scalar quantization.

Synthetic engineering experiment only; it does not validate psychological scales.
"""
from __future__ import annotations

import json
from typing import Iterable


def quantize(value: float, levels: int) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 1:
        raise ValueError("value must be numeric and in [0, 1]")
    if isinstance(levels, bool) or not isinstance(levels, int) or levels < 2:
        raise ValueError("levels must be an integer >= 2")
    return int(round(float(value) * (levels - 1)))


def reconstruct(code: int, levels: int) -> float:
    if isinstance(code, bool) or not isinstance(code, int) or not 0 <= code < levels:
        raise ValueError("code outside quantizer range")
    return code / (levels - 1)


def theoretical_max_error(levels: int) -> float:
    if isinstance(levels, bool) or not isinstance(levels, int) or levels < 2:
        raise ValueError("levels must be an integer >= 2")
    return 1 / (2 * (levels - 1))


def sweep(level_counts: Iterable[int] = (2, 4, 8, 16, 256)) -> list[dict]:
    # Pairs represent synthetic values that a downstream task says must remain distinct.
    # These are deliberately not asserted to be psychologically valid thresholds.
    critical_pairs = ((0.49, 0.51), (0.24, 0.26), (0.74, 0.76), (0.10, 0.90))
    samples = [i / 1000 for i in range(1001)]
    result = []
    for levels in level_counts:
        errors = [abs(x - reconstruct(quantize(x, levels), levels)) for x in samples]
        collisions = [
            {"pair": [left, right], "codes": [quantize(left, levels), quantize(right, levels)]}
            for left, right in critical_pairs
            if quantize(left, levels) == quantize(right, levels)
        ]
        result.append({
            "levels": levels,
            "nominal_bits_per_scalar_lower_bound": (levels - 1).bit_length(),
            "theoretical_max_abs_error": theoretical_max_error(levels),
            "observed_max_abs_error_on_1001_point_grid": max(errors),
            "mean_abs_error_on_1001_point_grid": sum(errors) / len(errors),
            "critical_pair_count": len(critical_pairs),
            "critical_pair_collisions": len(collisions),
            "collisions": collisions,
        })
    return result


def size_comparison(levels: int = 8) -> dict:
    # A synthetic single state, comparing verbose explicit JSON to a positional
    # compact JSON representation. This is serialized UTF-8 size, not bit packing.
    dimensions = {
        "goal_importance": 0.91,
        "perceived_possibility": 0.68,
        "personal_agency": 0.54,
        "expectation_confidence": 0.42,
    }
    names = tuple(dimensions)
    explicit = {
        "codebook": "human-experience-v0.1",
        "state_id": "state-hope-001",
        "subject_ref": "person:synthetic-01",
        "state_type": "hope",
        "target_ref": "goal:synthetic-01",
        "context_ref": "event:synthetic-01",
        "dimensions": dimensions,
        "source_kind": "self_report",
        "confidence": 0.83,
        "observed_at": "2026-10-09T12:00:00Z",
    }
    positional = {
        "c": "human-experience-v0.1",
        "i": "state-hope-001",
        "s": "person:synthetic-01",
        "t": "hope",
        "g": "goal:synthetic-01",
        "x": "event:synthetic-01",
        "d": [quantize(dimensions[name], levels) for name in names],
        "p": "self_report",
        "q": quantize(0.83, levels),
        "at": "2026-10-09T12:00:00Z",
    }
    explicit_bytes = len(json.dumps(explicit, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    positional_bytes = len(json.dumps(positional, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
    return {
        "levels": levels,
        "explicit_json_bytes": explicit_bytes,
        "positional_quantized_json_bytes": positional_bytes,
        "difference_bytes": explicit_bytes - positional_bytes,
        "percent_reduction": round((explicit_bytes - positional_bytes) / explicit_bytes * 100, 2),
        "warning": "Synthetic one-record JSON size only; excludes schema distribution, framing, escaping variance, and sync/update costs. Not bit-packed and not a general compression claim.",
    }


def report() -> dict:
    return {
        "experiment": "CASE-006B",
        "purpose": "resolution vs numeric error and task-defined pair collisions",
        "synthetic_only": True,
        "resolution_sweep": sweep(),
        "single_record_size_comparison": size_comparison(),
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2, sort_keys=True))
