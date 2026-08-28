# MeaningWire Architecture

MeaningWire is designed as a semantic interoperability layer, not as a replacement for every source system.

## Core pattern

```text
source systems
    ↓
adapters + mappings
    ↓
MeaningWire canonical contracts
    ↓
validation + provenance + authority metadata
    ↓
adapters + mappings
    ↓
target systems / analytics / automation / agents
```

The canonical layer reduces the need for every system to maintain bespoke point-to-point transformations with every other system.

## Architectural boundaries

### Source systems remain authoritative where appropriate

MeaningWire may normalize or transport data, but it does not automatically become the authority for the underlying business fact, approval, credential, legal status, or human decision.

### Canonical does not mean universal truth

A canonical model is a shared representation for interoperability. Different source systems may disagree, contain incomplete data, or have different scopes. MeaningWire should preserve those distinctions rather than hide them.

### Mappings are explicit objects

Mappings should be inspectable and versioned. The mapping registry will distinguish relationships such as:

- exact
- equivalent
- broader
- narrower
- derived
- transformed
- lossy
- unsupported

### Provenance travels with meaning

The project intends to preserve source identity, transformation history, mapping version, timestamps where relevant, and authority context so that normalized data remains auditable.

### AI is an interoperability participant, not an authority shortcut

Agents and models may propose classifications, mappings, transformations, or actions. Their output must retain provenance and uncertainty and must not silently acquire human approval authority.

## Initial domain model

The planned canonical domains are:

- Identity / Parties
- Products / Services
- Commerce
- Finance
- Operations
- Communications
- Content
- Governance
- Integration

Finance is an interoperability domain, not a promise to replace a general ledger or regulated accounting system.

## Interfaces

Expected public interface families include:

- JSON Schema
- JSON / JSONL
- OpenAPI
- AsyncAPI
- CloudEvents-compatible event concepts
- JSON-LD where linked-data semantics provide value
- CLI
- SDKs

Exact interface commitments will be established through RFCs and executable tests.

## Identifier strategy

Canonical identifiers must be vendor independent. UUIDv7 and ULID are candidates for evaluation; no final identifier standard has been adopted yet.

## Standards strategy

MeaningWire uses established standards as semantic references and mapping targets rather than importing any single external model as the internal database schema wholesale.

Primary reference families include OAGIS, Schema.org, OASIS UBL, GS1 EPCIS/CBV, FIBO, JSON Schema, OpenAPI, AsyncAPI, and CloudEvents concepts.

## Monorepo rationale

During early development, schemas, mapping definitions, tooling, documentation, adapters, and tests will live together so contract changes can be reviewed with their executable consequences. Repository splitting can be considered later if independent release cadence or contributor scale justifies it.
