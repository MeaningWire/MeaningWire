# JSON Schema Validation Boundary

MeaningWire uses JSON Schema Draft 2020-12 as a public contract format. The project keeps two complementary validation layers during pre-release development.

## Layer 1 — dependency-free bootstrap checks

`tools/validate_contracts.py` validates project-specific invariants, registry consistency, deterministic fixtures, and conservative authority rules using only the Python standard library.

This layer exists so core contract sanity checks remain runnable in minimal environments.

## Layer 2 — standards-compliant JSON Schema validation

`tools/validate_jsonschema.py` uses the public Python `jsonschema` package to:

- verify that every registered schema is a valid Draft 2020-12 schema;
- build an in-memory registry for MeaningWire schema URNs;
- resolve cross-schema `$ref` values from `schemas/registry.json`;
- validate the deterministic fixture corpus with a real Draft 2020-12 validator.

The initial pinned top-level dependency is documented in `requirements-validation.txt`.

## No remote schema retrieval

MeaningWire schema identifiers are project-scoped URNs such as:

`urn:meaningwire:schema:core:reference:0.1.0`

The standards validator resolves those URNs only from the repository's public registry. It does not fetch schemas over HTTP or depend on a private registry, private package, private API, custom domain, or undocumented service.

This is both a security boundary and a public-implementation-boundary requirement: validation results should not change because an external URL becomes unavailable or because a private service contains hidden schema state.

## Formats

Draft 2020-12 treats `format` as annotation unless the format-assertion vocabulary is explicitly enabled. This slice therefore does not claim additional format-assertion behavior beyond what is tested. Structural schema validation and local `$ref` resolution are the intended scope.

## Dependency policy

The validator dependency is public, open source, and used as tooling rather than as a hidden project service. Before a release is represented as reproducible, the project should strengthen dependency locking and provenance evidence beyond the current pre-release top-level pin.

## Failure behavior

A registered schema that is invalid Draft 2020-12, cannot be found at its declared public repository path, has a mismatched `$id`, or cannot resolve its MeaningWire references is a validation failure.

The existing semantic bootstrap checks remain authoritative for MeaningWire-specific rules that are intentionally stronger or more explicit than generic JSON Schema validation.
