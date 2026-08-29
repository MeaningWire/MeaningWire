# Synthetic End-to-End Interoperability Proof

MeaningWire's first complete interoperability proof connects existing public components without private code, vendor APIs, credentials, or hidden fixtures.

## Proven path

The deterministic proof is:

```text
synthetic JSON object
    ↓
JSON Object reference adapter
    ↓
validated source envelope (synthetic CRM customer contract)
    ↓
explicit registered mapping: example-crm-email@0.1.0
    ↓
simple-member path application + identity transform
    ↓
validated target envelope (synthetic party contract)
```

The input fixture is `tests/fixtures/adapters/json-object-record.json` and the exact expected target envelope is pinned at `tests/fixtures/proofs/json-object-crm-email-target.json`.

## Contract binding

The pipeline requires the source envelope's contract reference to exactly match `mapping.source.contract`. It never searches for a likely mapping and never substitutes a merely similar contract.

The target envelope's contract is taken directly from `mapping.target.contract`. Target record identity is supplied explicitly by the caller rather than inferred from the source filename, line number, or arbitrary field.

## Provenance behavior

The target preserves the original source provenance and appends a transformation entry:

```text
operation = meaningwire.mapping.apply
mapping   = the explicit versioned mapping reference
```

No clock value is injected into the proof, keeping the expected output deterministic across runs.

## Authority behavior

Transformation does not silently transfer approval or authority.

Even if a valid source envelope carries human approval, the transformed target is emitted with:

```text
kind     = none
approval = not_asserted
```

and an explicit basis explaining that mapping application does not transfer source approval or authority to the target representation.

This is intentionally conservative. Future authority-propagation policies, if any, require separate semantics and review.

## What this proves

The repository now contains a public, deterministic example showing that:

- a local external-format record can enter through the Adapter SDK boundary;
- a canonical source envelope can be validated;
- an explicit public registry mapping can be resolved;
- the mapping's source path can be applied;
- the allowed identity transform can execute;
- the target path can be populated in a fresh object;
- transformation provenance can be preserved and extended;
- a canonical target envelope can be validated;
- the exact expected target can be asserted from a public fixture.

## What this does not prove

This proof does not establish:

- production readiness;
- vendor compatibility;
- full JSONPath support;
- multi-field or mapping-set conversion;
- non-identity transform support;
- performance or streaming guarantees;
- authenticated integration;
- stable public API compatibility.

It is synthetic, isolated, pre-release evidence for the architecture and public-implementation boundary.

## Run locally

```text
python tools/interoperability_pipeline.py
```

The full deterministic unit suite also pins the target envelope exactly.

This capability remains EXPERIMENTAL.
