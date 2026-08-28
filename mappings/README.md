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

The registered mappings currently in this repository are synthetic examples for testing the registry. They do not claim compatibility with real vendors or production systems.

See `docs/architecture/mapping-registry.md` for the selection and security boundary.
