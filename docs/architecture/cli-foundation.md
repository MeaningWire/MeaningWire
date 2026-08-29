# CLI Foundation Boundary

MeaningWire's first CLI surface is intentionally read-only and local-first. It exists to expose public repository contracts and validation behavior before transformation execution is introduced.

## Invocation

During pre-release development the CLI is invoked directly from the repository:

```text
python tools/meaningwire.py <command>
```

This slice does not publish a package, install a global executable, or claim stable command compatibility.

## Initial commands

The first bounded command set is:

- `doctor` — run the public schema, fixture, and mapping-registry health checks;
- `schemas list` — list registered MeaningWire schemas deterministically;
- `schema validate <schema-id> <file>` — validate a local JSON instance against a registered Draft 2020-12 schema;
- `mappings list` — list registered mappings deterministically;
- `mappings inspect <id>` — inspect one mapping, with optional explicit namespace/version selection.

Each command that returns structured data supports `--json` for machine-readable output.

## Read-only boundary

The CLI does not:

- execute mapping transforms;
- convert or rewrite user data;
- mutate registries, schemas, mappings, or fixtures;
- contact remote schema servers or APIs;
- select among ambiguous mappings;
- invoke AI or model inference;
- integrate with downstream private projects;
- publish packages or releases.

The CLI consumes the same public registry and validation modules used by CI. It does not maintain a second hidden registry or alternate semantic source of truth.

## Validation behavior

`schema validate` uses the same local-only Draft 2020-12 registry resolution established by `tools/validate_jsonschema.py`. MeaningWire URN references are resolved from the public repository registry only.

A valid instance exits with code `0`. A validation failure or deterministic user-facing lookup/input error exits with code `2`. Machine-readable mode returns structured JSON so automation does not need to parse prose.

`doctor` validates both MeaningWire-specific bootstrap invariants and the standards-compliant Draft 2020-12 layer, then verifies mapping-registry integrity. It performs no network access.

## Dependency boundary

Registry listing and mapping inspection remain based on repository-local code. Standards validation commands require the documented public validation dependency in `requirements-validation.txt`.

No private package, private service, private schema, or custom MeaningWire domain is required.

## Deliberate non-scope

This is a CLI foundation, not the full MeaningWire command surface. Later reviewable slices may add `init`, mapping discovery filters, transformation execution, conversion, adapter inspection, provenance inspection, package installation, and release artifacts only after their underlying behavior exists and is independently testable.

The CLI must not expose a command whose implementation would imply a capability that MeaningWire does not yet possess.
