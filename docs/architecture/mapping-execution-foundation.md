# Mapping Execution Foundation

MeaningWire's first mapping executor is intentionally smaller than a document converter. It establishes one deterministic execution primitive while keeping selection, traversal, orchestration, and unsafe transform mechanisms out of scope.

## Executable behavior

The initial engine accepts:

1. one explicit, already-validated mapping definition; and
2. one source value already selected by the caller.

Only `transform.kind = identity` is executable. The result preserves the source value and returns execution metadata containing the mapping identity, mapping version, relationship, and transform kind.

Mutable source values are deep-copied before return so an identity execution cannot accidentally alias and mutate caller-owned data.

## Fail-closed behavior

The engine rejects:

- mappings without an explicit transform;
- `expression` transforms;
- `lookup` transforms;
- `code` transforms;
- `manual` transforms;
- structurally or semantically invalid mappings.

Unsupported transform kinds are not interpreted, evaluated, delegated to another runtime, or treated as identity. They fail explicitly.

## Selection boundary

`execute_registered_value(...)` may resolve a mapping only by explicit mapping identity using the existing deterministic mapping registry. The executor does not search for or infer a "best" mapping.

Ambiguous or absent identities continue to fail through the registry's existing unique-selection rules.

## Document boundary

This slice does not:

- parse JSONPath or another path language;
- read a source path from a document;
- write a target path into a document;
- merge records;
- execute mapping chains;
- perform broad conversion;
- mutate input files;
- contact remote services;
- execute arbitrary expressions or code;
- invoke AI or model inference;
- add adapters or downstream integrations.

Those behaviors require separate explicit contracts, deterministic tests, and reviewable implementation slices.

## Security rationale

Treating transform metadata as executable code would create a large trust boundary prematurely. The first executor therefore uses an allowlist of exactly one inert transform kind: `identity`.

Future transform kinds must define their syntax, determinism, resource limits, error behavior, provenance, security model, and test vectors before they become executable.

## Public implementation boundary

All execution code, mappings, tests, and examples required by this foundation live in the public repository. No private runtime, mapping service, schema, plugin, or downstream project is required.

This capability remains pre-release and EXPERIMENTAL.
