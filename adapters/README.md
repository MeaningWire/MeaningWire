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

Initial reference adapters should be read-oriented, narrowly scoped, deterministic, and public. Their purpose is to prove the adapter boundary before authenticated vendor integrations are attempted.

The first planned reference pair is repository-local JSON object and JSON Lines input. They should use synthetic fixtures and make no vendor compatibility claim.

Reference adapters should document:

- source format/system and version assumptions;
- authentication boundary without embedding credentials;
- input and output contracts;
- mapping identifiers and versions when mappings are used;
- known unsupported fields;
- known lossy transforms;
- provenance behavior;
- deterministic fixtures and tests.
