# Mapping Registry Behavior

MeaningWire mappings are explicit, versioned semantic relationships. The mapping registry makes those relationships discoverable without turning discovery into implicit transformation or policy.

## Registry role

`mappings/registry.json` is the public repository index for mapping definitions. Each registry entry identifies one versioned mapping and its repository-relative definition path.

A registered mapping must:

- have a unique mapping identity;
- have a unique registry path;
- remain under `mappings/definitions/`;
- match the identity and version declared by its registry entry;
- satisfy the MeaningWire mapping semantic checks;
- satisfy the Draft 2020-12 mapping schema in CI.

The registry itself does not execute a transformation.

## Deterministic discovery

`tools/mapping_registry.py` returns mappings in deterministic identity order and supports filtering by source contract, target contract, source path, target path, relationship, and maturity.

A query may legitimately return more than one mapping. This can happen when multiple source systems map to the same canonical field, multiple versions coexist, or several semantically different relationships are available.

MeaningWire therefore distinguishes **candidate discovery** from **selection**:

- `find_mappings(...)` returns every matching candidate in deterministic order;
- `select_unique(...)` succeeds only when exactly one candidate matches;
- `get_mapping(...)` resolves a mapping by mapping identity and requires version when omitting it would be ambiguous.

The registry never silently scores or guesses a preferred mapping.

## Why ambiguity is explicit

Choosing the wrong semantic mapping can be more damaging than failing to choose one. A broad match must not become an implicit claim that two concepts are equivalent or that one transformation is authoritative.

Future ranking, policy, adapter preference, or AI-assisted recommendation may help a caller decide among candidates, but those mechanisms must remain separate from the deterministic registry and must not rewrite mapping meaning or human authority.

## Path boundary

Registered mapping files must be repository-relative files under `mappings/definitions/`. Absolute paths and path traversal outside that directory are rejected.

This keeps the public implementation self-contained and prevents registry entries from depending on private filesystem locations or hidden mapping stores.

## Synthetic examples

The initial registered mappings are synthetic examples used to exercise registry behavior. They do not claim compatibility with any real CRM, ERP, vendor product, customer system, or production deployment.

## Deliberate non-scope

This slice does not define:

- transformation execution;
- expression language semantics;
- lookup-table storage;
- adapter precedence;
- AI-selected mappings;
- domain-specific canonical contracts;
- production or stable compatibility guarantees.

Those capabilities should be added only in separately reviewable slices with deterministic evidence.
