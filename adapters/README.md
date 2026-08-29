# Adapters

MeaningWire adapters terminate source-specific concerns at public MeaningWire contracts without redefining those contracts around a particular downstream system.

## SDK foundation

The first public reference interface lives at `tools/adapter_sdk.py`. It is intentionally read-only and pre-release.

A conforming foundation adapter:

- identifies itself with a versioned descriptor;
- declares a source boundary and recognized MeaningWire maturity state;
- declares `read_records` and may optionally declare `discover_contracts`;
- exposes `describe()` without triggering a data read;
- emits canonical MeaningWire envelopes through `read()`;
- binds emitted provenance to the adapter's declared source;
- never asserts human approval;
- does not require a private MeaningWire runtime or hidden schema.

Write-back, event emission, subscription, credential management, and administrative source-system capabilities are outside this foundation.

See `docs/architecture/adapter-sdk-foundation.md` for the behavioral, trust, credential, and semantic boundaries.

## Reference adapters

The initial reference adapters are read-oriented, narrowly scoped, deterministic, public, and non-vendor-specific. Their purpose is to prove the adapter boundary before authenticated vendor integrations are attempted.

Current reference implementations:

- `adapters/reference/json_object.py` — reads exactly one local UTF-8 JSON object and emits one validated canonical envelope. See `docs/adapters/json-object.md`.
- `adapters/reference/json_lines.py` — prevalidates a bounded local UTF-8 JSON Lines file and emits one validated canonical envelope per explicitly identified record. See `docs/adapters/json-lines.md`.

These format adapters use synthetic fixtures and make no vendor compatibility claim.

Reference adapters should document:

- source format/system and version assumptions;
- authentication boundary without embedding credentials;
- input and output contracts;
- mapping identifiers and versions when mappings are used;
- known unsupported fields;
- known lossy transforms;
- provenance behavior;
- deterministic fixtures and tests.
