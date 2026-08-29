# Mapping Application Boundary

MeaningWire's first mapping-application layer connects explicit mapping paths to the fail-closed mapping executor without claiming a complete JSONPath implementation.

## Path syntax

The supported pre-release path language is a deliberately strict subset:

```text
$
$.member
$.member.member
```

Member names are currently ASCII identifiers matching `[A-Za-z_][A-Za-z0-9_]*`.

This syntax is compatible with the basic JSONPath member-name shorthand used by the current synthetic mappings, but MeaningWire does **not** claim full JSONPath support. JSONPath is standardized by RFC 9535 and supports substantially richer selectors and member-name syntax than this implementation.

The application layer explicitly rejects bracket selectors, array indexes, wildcards, filters, recursive descent, quoted member names, special-character member names, and malformed paths.

## Application behavior

`apply_mapping(mapping, source_data)`:

1. validates the explicit mapping;
2. reads exactly one source value from `mapping.source.path`;
3. delegates transform behavior to the existing fail-closed mapping executor;
4. writes the resulting value to a fresh object at `mapping.target.path`;
5. returns the target object plus explicit mapping/execution metadata.

The source object is never mutated.

## Failure behavior

Application fails explicitly when:

- a path uses unsupported syntax;
- a source member is absent;
- traversal crosses a non-object value;
- a target path collides with a non-object intermediate member;
- a target path is already occupied;
- a root target would replace a non-empty object;
- a mapping is invalid;
- the requested transform kind is not executable.

No fallback path interpretation, implicit mapping selection, or best-effort partial conversion occurs.

## Scope

This slice applies one explicit mapping to one source object. It does not yet:

- apply a mapping set;
- merge multiple target fields;
- resolve mappings implicitly;
- convert a complete adapter envelope into a target envelope;
- execute arrays or JSONPath queries;
- perform lossy/expression/lookup/code transforms;
- expose mapping application through the CLI.

Those remain separately testable capabilities.

## Standards direction

If MeaningWire later claims JSONPath conformance, that implementation must be evaluated explicitly against RFC 9535 rather than assuming this small subset is equivalent to the standard.

This capability remains pre-release and EXPERIMENTAL.
