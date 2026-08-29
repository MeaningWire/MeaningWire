---
title: Builder
description: Work with MeaningWire's current experimental schemas, mappings, adapters, and CLI boundaries.
---

Use this path when you want to build against MeaningWire's public contracts rather than only inspect the project.

## Start with the contracts

Canonical schemas live under `schemas/` and are registered in `schemas/registry.json`. Mapping definitions live under `mappings/` with deterministic registry lookup and explicit relationship types.

The current public contracts are marked **EXPERIMENTAL**. Treat their version identifiers as real compatibility boundaries, but do not assume pre-1.0 stability.

## Keep authority separate from data

MeaningWire models provenance and authority explicitly. An adapter or model-generated transformation must not manufacture human approval. Mapping a value into a canonical representation does not transfer the source system's approval or authority to the target representation.

## Prefer the read-only adapter boundary first

The Adapter SDK and reference adapters are intentionally read-only. New adapters should prove deterministic reads, source identity, envelope construction, bounded input handling, and fail-closed behavior before any write capability is considered.

## Validate locally

Useful checks include:

```bash
python tools/validate_contracts.py
python tools/mapping_registry.py
python tools/validate_jsonschema.py
python -m unittest discover -s tests -v
```

The governed CI path performs additional candidate, dependency-lock, SBOM, extracted-environment, documentation-build, and release-readiness checks.

## Public implementation rule

A supported MeaningWire release must remain understandable, buildable, testable, validatable, and releasable without access to private MeaningWire code or hidden infrastructure.
