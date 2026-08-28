# MeaningWire

**Define meaning once. Map systems at the edges.**

MeaningWire is a vendor-neutral, open-source semantic interoperability framework for connecting systems, data, APIs, events, AI agents, automation, and knowledge workflows through shared public contracts rather than brittle point-to-point integrations.

> **Project status:** early public foundation. The architecture, governance, schemas, mappings, and APIs are being developed in the open. No production-readiness or compatibility guarantees are claimed yet.

## Why MeaningWire

Modern organizations rarely have one system of record, one data model, or one automation surface. Applications, ERPs, CRMs, finance tools, content systems, event streams, analytics platforms, and AI agents all describe overlapping concepts differently.

MeaningWire is intended to provide a neutral layer between them:

```text
System A ─┐
System B ─┼─> adapters / mappings ─> MeaningWire canonical contracts ─> adapters / mappings ─┬─> System X
System C ─┘                                                                           └─> System Y
```

The goal is not to replace source systems. It is to make meaning explicit, versioned, testable, and portable between them.

## Planned capabilities

- Canonical schemas and semantic models
- Mapping and normalization registry
- Adapter / connector SDK
- Validation and provenance
- Canonical event model
- CLI, API, and SDK interfaces
- AI and agent interoperability contracts
- Standards mappings and crosswalks
- Transparent governance, RFCs, security practices, and maturity labels

## Design principles

1. **Vendor neutral.** Public contracts must not privilege one downstream product or vendor.
2. **Meaning before transport.** Interoperability starts with semantics, not merely moving bytes.
3. **Canonical is not authoritative.** A canonical representation normalizes meaning; it does not automatically determine truth or approval authority.
4. **Mappings are explicit.** Exact, equivalent, broader, narrower, derived, transformed, lossy, and unsupported relationships should be distinguishable.
5. **Provenance is first class.** Data lineage, transformation history, source identity, and authority boundaries must remain visible.
6. **AI inference is not human approval.** Automated interpretation must never silently become organizational authority.
7. **Public contracts first.** Downstream projects consume released public interfaces with no private shortcuts.
8. **Accessibility matters.** Documentation and interfaces target WCAG 2.2 AA and low-cognitive-load interaction patterns.
9. **Maturity is visible.** Experimental ideas are labeled honestly rather than presented as stable features.

## Standards strategy

MeaningWire will draw from established standards where they improve interoperability without importing any one external model wholesale.

Primary reference families include:

- OAGIS
- Schema.org
- OASIS UBL
- GS1 EPCIS / CBV
- FIBO
- CloudEvents concepts
- JSON Schema
- OpenAPI
- AsyncAPI

Additional comparison references may include Microsoft CDM, TM Forum SID, NIEM, SAP and Salesforce canonical-model patterns, and other relevant public specifications.

## Planned project structure

```text
schemas/        canonical schemas and semantic contracts
mappings/       mappings, crosswalks, and transformation metadata
adapters/       reference adapters and adapter documentation
packages/       core libraries, CLI, SDKs, and supporting packages
docs/           architecture, guides, RFCs, Labs, and research
.github/        issue forms, pull-request templates, and project automation
```

The repository will begin as a monorepo so contracts, tooling, documentation, and tests can evolve together while the project is young.

## Governance and contribution

MeaningWire is being built publicly and deliberately. Project governance, contribution rules, support boundaries, security reporting, RFC procedures, and roadmap material are being introduced through reviewed pull requests.

See:

- [Governance](GOVERNANCE.md)
- [Contributing](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security](SECURITY.md)
- [Support](SUPPORT.md)
- [Roadmap](ROADMAP.md)

## Maturity model

Frontier concepts may move through:

`DISCOVERED → RESEARCH → EVALUATED / EXPERIMENTAL → PREVIEW → STABLE`

Other terminal states include `REJECTED`, `SUPERSEDED`, and `DEPRECATED`.

Stable public contracts will use explicit versioning and compatibility policy before a stable release is declared.

## License

A project license has **not yet been finalized**. Until a license file is added, the repository should not be treated as granting open-source reuse rights. The licensing decision will be made explicitly before the first public preview release.

## Current focus

The immediate work is the public foundation and technical MVP:

- establish governance and contributor infrastructure;
- define the canonical core and schema conventions;
- define the mapping registry;
- build validation and provenance primitives;
- design the CLI and adapter SDK;
- implement two representative reference adapters;
- produce synthetic / isolated interoperability proofs;
- document everything well enough for an outside contributor to understand and challenge it.

MeaningWire does not claim existing adoption, customers, expert endorsement, or production readiness. Evidence and maturity will be published as they are earned.
