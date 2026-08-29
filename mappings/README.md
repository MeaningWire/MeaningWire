# Mappings

MeaningWire mappings are versioned semantic relationships and crosswalks between source contracts and target contracts.

Relationship vocabulary:

- `exact`
- `equivalent`
- `broader`
- `narrower`
- `derived`
- `transformed`
- `lossy`
- `unsupported`

Mappings preserve provenance, identify source and target contract versions, document transformation intent, and make known loss or ambiguity visible.

## Registry

`registry.json` is the public index of mapping definitions under `definitions/`.

The registry is deliberately conservative:

- registered identities and paths must be unique;
- registry identity/version must match the mapping document;
- mapping paths must remain inside `mappings/definitions/`;
- candidate lookup is deterministic;
- broad lookup may return multiple candidates;
- the registry never silently chooses a "best" mapping when the result is ambiguous.

Use `tools/mapping_registry.py` for deterministic registry integrity checks and lookup behavior.

## Execution foundation

`tools/mapping_executor.py` provides the deliberately narrow transform primitive. It accepts an explicit mapping plus an already-selected source value and currently executes only `transform.kind = identity`.

All other transform kinds, missing transforms, and invalid mappings fail closed.

## Mapping application

`tools/mapping_application.py` connects explicit mapping source/target paths to the executor. It currently supports only `$` and simple dot-separated ASCII object-member paths such as `$.email` and `$.contact.email`.

This is intentionally a strict subset, not a claim of complete JSONPath support. Rich selectors, arrays, wildcards, filters, recursive descent, quoted/special member syntax, implicit mapping selection, and partial best-effort conversion are rejected.

Application reads one source value, executes one explicit mapping, and writes the result into a fresh target object without mutating the source.

The registered mappings currently in this repository are synthetic examples for testing registry, execution, and application behavior. They do not claim compatibility with real vendors or production systems.

See `docs/architecture/mapping-registry.md`, `docs/architecture/mapping-execution-foundation.md`, and `docs/architecture/mapping-application.md` for the selection, execution, and path boundaries.
