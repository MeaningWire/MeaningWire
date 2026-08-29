# Schemas

MeaningWire schemas are public, versioned semantic contracts represented with JSON Schema Draft 2020-12.

Current requirements include:

- vendor-independent identifiers and namespaces;
- explicit versioning and maturity metadata;
- repository-local schema registration and reference resolution;
- provenance and authority kept in the canonical envelope rather than duplicated into every domain payload;
- domain boundaries that do not import any one external standard wholesale;
- deterministic validation fixtures;
- documented compatibility and deprecation rules before stable release.

## Canonical domains

Initial domain families are Identity / Parties, Products / Services, Commerce, Finance, Operations, Communications, Content, Governance, and Integration.

The first experimental domain contract is:

- `urn:meaningwire:schema:identity:party:0.1.0` — `schemas/domains/identity/party.schema.json`

The Party payload separates canonical envelope record identity from source/business identifiers and models only a deliberately small common denominator: party type, typed names, scheme-aware identifiers, and typed contact points.

See `docs/architecture/domain-contract-conventions.md` for the domain boundary and standards-research rationale.

## Registry

`schemas/registry.json` is the public schema index used by both the dependency-free bootstrap validator and the standards-compliant Draft 2020-12 validation layer.

Adding a schema requires a versioned `$id`, `x-meaningwire-contract-version`, `x-meaningwire-maturity`, a registry entry, deterministic validation coverage, and documentation of its semantic boundary.

Schema design remains pre-release and EXPERIMENTAL. Substantial semantic changes should remain explicit and use the RFC process when they become consequential to public compatibility.
