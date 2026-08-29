---
title: How MeaningWire works
description: Follow the current synthetic adapter-to-mapping proof and see how data, provenance, and authority move through MeaningWire.
---

MeaningWire's current end-to-end proof is intentionally small. It demonstrates one inspectable path:

**read a bounded source → wrap it in an envelope → apply one explicit mapping → emit a target envelope**

The example is synthetic. It proves the current public mechanics; it does not claim production readiness, vendor compatibility, arbitrary conversion, or write-back support.

## The flow

```text
synthetic JSON object
        │
        ▼
read-only JSON object adapter
        │
        ▼
source envelope
        │
        ▼
explicit mapping: example-crm-email@0.1.0
        │
        ▼
identity transform on one simple-member path
        │
        ▼
target envelope
```

There is no implicit mapping selection in this proof. The pipeline requests the mapping by its exact identity and fails if the source envelope contract does not exactly match the mapping's declared source contract.

## 1. Read a bounded source

The public fixture contains only synthetic data:

```json
{
  "customer_id": "CUST-001",
  "email": "person@example.invalid",
  "display_name": "Synthetic Person"
}
```

The read-only JSON object adapter identifies the source, source contract, and source record explicitly. It then emits a validated MeaningWire envelope. Reading through an adapter does **not** create human approval.

For this proof, the source contract identity is:

```text
urn:example:contract:crm-customer:1
```

and the source record identity is:

```text
urn:example:record:crm-customer-CUST-001
```

## 2. Apply one explicit mapping

The registered synthetic mapping is:

```text
urn:meaningwire:mapping:example-crm-email:0.1.0
```

It declares one bounded relationship:

| Property | Value |
| --- | --- |
| Source path | `$.email` |
| Target path | `$.contact.email` |
| Relationship | `equivalent` |
| Transform | `identity` |
| Maturity | `EXPERIMENTAL` |

`equivalent` applies to these declared source and target paths. It is not a claim that the complete source and target records are equivalent.

The currently implemented path grammar is deliberately smaller than full JSONPath. This proof uses simple object-member paths only. Unsupported path syntax and unimplemented transform kinds fail closed rather than being guessed.

See the generated [mapping reference](./reference/mappings/) for the registry-derived view.

## 3. Build the target envelope

Only the mapped value is written into target data:

```json
{
  "contact": {
    "email": "person@example.invalid"
  }
}
```

The source fixture's `customer_id` and `display_name` are not silently copied because this mapping does not declare target paths for them.

The proof supplies a new target record identity:

```text
urn:example:record:party-CUST-001
```

and the mapping declares this synthetic target contract:

```text
urn:example:contract:party:0.0.1
```

This target contract is part of the synthetic interoperability proof. It should not be confused with a claim that the proof exercises every current canonical domain contract.

## 4. Preserve provenance; do not transfer approval

MeaningWire treats provenance and authority as different concerns.

The target envelope starts with a copy of the source provenance and appends a transformation record identifying the mapping operation:

```json
{
  "operation": "meaningwire.mapping.apply",
  "mapping": {
    "namespace": "urn:meaningwire:mapping",
    "id": "example-crm-email",
    "version": "0.1.0"
  }
}
```

That history answers **how this representation was produced**.

Authority is handled separately. The transformed target explicitly contains:

```json
{
  "kind": "none",
  "approval": "not_asserted",
  "basis": "MeaningWire mapping application does not transfer source approval or authority to the target representation."
}
```

**Approval is not transferred.** A source system, adapter, mapping, model, or transformation cannot silently turn source authority into human approval for the target representation.

## What fails closed

The current proof rejects or stops on conditions including:

- an invalid source envelope;
- an invalid mapping definition;
- an invalid target record reference;
- a source contract that does not exactly match the mapping source contract;
- unsupported rich JSONPath syntax;
- missing source paths;
- target-path collisions;
- unimplemented transform kinds;
- an invalid target envelope.

These boundaries are intentional. MeaningWire should surface ambiguity or unsupported behavior rather than invent semantics.

## Run the proof

From a fresh public checkout with the documented Python environment available:

```bash
python tools/meaningwire.py proof run --json
```

The same path is also exercised in deterministic tests and CI. The implementation is in `tools/interoperability_pipeline.py`; the synthetic mapping is in `mappings/definitions/example-crm-email.json`; and the source fixture is in `tests/fixtures/adapters/json-object-record.json`.

For the broader implementation boundary, continue with [Builder](./builder/) and the generated [schema reference](./reference/schemas/).
