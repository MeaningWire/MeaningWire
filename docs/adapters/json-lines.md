# JSON Lines Reference Adapter

The JSON Lines reference adapter is the second concrete implementation of the pre-release read-only Adapter SDK boundary.

It is a local format adapter, not a vendor integration. It demonstrates bounded multi-record ingestion while preserving explicit record identity, source provenance, and all-or-nothing prevalidation.

## Input

The adapter reads a UTF-8 JSON Lines file where every physical line must contain exactly one JSON object.

The caller supplies:

- the source reference;
- the MeaningWire contract reference represented by every record;
- the namespace used for emitted record references;
- the object field containing the record ID;
- optional byte and record-count ceilings.

Blank lines are rejected rather than skipped. Array, scalar, and null line values are rejected.

## Record identity

Every object must contain the configured record-ID field as a non-empty string. Duplicate IDs within the file are rejected.

MeaningWire does not use line number or filename as implicit business identity.

## Transactional prevalidation

For this bounded reference implementation, the complete file is parsed and validated before the first envelope is yielded.

That means an invalid later line, duplicate record ID, record-count overflow, or other parse failure cannot produce a silently partial read result.

The tradeoff is bounded in-memory buffering. The default guardrails are:

- maximum file size: 2 MiB;
- maximum records: 10,000.

These are conservative pre-release limits, not permanent protocol limits.

## Output

Each validated source object becomes one canonical MeaningWire envelope through the public Adapter SDK. Every envelope:

- preserves the source object as `data`;
- carries an explicit record reference;
- binds provenance to the adapter's declared source;
- uses `source_authority` with `approval = not_asserted`;
- remains `EXPERIMENTAL`.

## Safety boundaries

The adapter performs no network access and no writes. It does not:

- execute mappings or transforms;
- infer schemas or mappings;
- infer record identity from position;
- skip malformed records;
- manage credentials;
- assert human approval;
- contact vendor systems;
- claim production compatibility.

## Synthetic fixture

`tests/fixtures/adapters/json-lines-records.jsonl` contains two synthetic records using `.invalid` email addresses. It represents no real person, customer, vendor, or production system.

## Current invocation

For repository smoke testing:

```text
python adapters/reference/json_lines.py tests/fixtures/adapters/json-lines-records.jsonl
```

Script-mode identities are synthetic. Library callers must supply their own explicit source, contract, record namespace, and record-ID field.

This adapter remains pre-release and EXPERIMENTAL.
