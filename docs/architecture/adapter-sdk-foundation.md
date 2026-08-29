# Adapter SDK Foundation

MeaningWire's first Adapter SDK boundary is deliberately read-only. It defines how an adapter identifies itself and how adapter reads enter MeaningWire as validated canonical envelopes without redefining MeaningWire around any vendor or downstream system.

## Reference implementation

The current public reference interface lives in `tools/adapter_sdk.py`. It is a pre-release Python prototype, not a published package or a claim that Python is the permanent SDK language.

## Descriptor contract

A read-only adapter descriptor contains:

- `adapter_id` — a versioned MeaningWire-style reference identifying the adapter;
- `version` — equal to `adapter_id.version`;
- `source` — a reference identifying the external/source boundary represented by the adapter;
- `capabilities` — a unique, sorted list of capabilities;
- `maturity` — a recognized MeaningWire maturity state.

The initial capability allowlist is intentionally small:

- `read_records` — required;
- `discover_contracts` — optional.

Write-back, event emission, subscription, remote mutation, administrative actions, and credential-management capabilities are not permitted by this foundation.

## Behavioral protocol

A read-only adapter exposes:

- `describe()` — returns its descriptor;
- `read()` — yields MeaningWire canonical envelopes.

Structural validation checks the descriptor without consuming records. This avoids turning adapter discovery into an accidental data read.

## Envelope boundary

`build_read_envelope(...)` creates an envelope using the existing public MeaningWire envelope contract. It:

- deep-copies caller-owned data;
- binds provenance to the adapter's declared source;
- marks authority as `source_authority`;
- always uses `approval = not_asserted`;
- validates the finished envelope with the existing dependency-free semantic validator.

`validate_emitted_envelope(...)` additionally requires emitted provenance to match the adapter's declared source and prevents a read-only adapter from asserting human approval.

## Trust and credential boundary

The SDK does not define credential storage, secret distribution, token refresh, login flows, or privileged source-system actions. Reference adapters introduced during the Technical MVP should prefer local/synthetic fixtures and read-only inputs until authentication and secret-handling contracts receive their own review.

Adapters must never embed live credentials in descriptors, fixtures, logs, examples, or public repository content.

## Semantic boundary

Adapters terminate source-specific concerns at public MeaningWire contracts. They do not:

- redefine canonical schemas around one vendor;
- invent private contract variants;
- silently select mappings;
- imply human approval;
- infer missing business meaning with AI;
- claim compatibility that has not been tested;
- require a private MeaningWire runtime.

## Reference-adapter sequence

After this SDK foundation is validated, the first two reference adapters should exercise the boundary using public, deterministic, non-vendor-specific formats before any authenticated vendor integration is considered. Suitable initial targets are repository-local JSON object and JSON Lines inputs.

Those adapters should remain read-only, fixture-driven, and explicit about supported record shapes.

This capability remains pre-release and EXPERIMENTAL.
