# MeaningWire

**Define meaning once. Map systems at the edges.**

MeaningWire is a vendor-neutral, open-source semantic interoperability framework for connecting systems, data, APIs, events, AI agents, automation, and knowledge workflows through shared public contracts rather than brittle point-to-point integrations.

> **Project status: pre-release development.** This repository is public for transparency, inspectability, and durable project history. MeaningWire has not announced a usable release, does not claim production readiness, and does not recommend depending on unfinished contracts yet.

Public visibility is not a request for outside developers to build the project. The current priority is to produce, validate, document, and release a coherent first usable version before any broader community or adoption push.

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

The repository begins as a monorepo so contracts, tooling, documentation, and tests can evolve together while the project is young.

## Pre-release posture

MeaningWire is being developed in a public repository, but it is not being publicly launched yet.

Until the first usable versioned release is ready:

- no production-readiness or compatibility guarantee is made;
- no broad adoption or contributor-recruitment campaign is underway;
- unfinished schemas, mappings, APIs, and CLI behavior may change materially;
- public history exists so decisions and implementation can be inspected rather than reconstructed later;
- external contribution is welcome if someone independently chooses to participate, but it is not a prerequisite for completing the first release.

When a release is ready, the project will describe what actually exists, how it was tested, what compatibility it provides, and what remains experimental.

## Governance and project policies

The project keeps governance and contribution rules in place during pre-release development so decisions, security boundaries, and unexpected external contributions can be handled consistently.

See:

- [Governance](GOVERNANCE.md)
- [Contributing](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security](SECURITY.md)
- [Support](SUPPORT.md)
- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [Citation metadata](CITATION.cff)

For security vulnerabilities, follow [SECURITY.md](SECURITY.md) rather than posting sensitive details publicly.

## Maturity model

Frontier concepts may move through:

`DISCOVERED → RESEARCH → EVALUATED / EXPERIMENTAL → PREVIEW → STABLE`

Other terminal states include `REJECTED`, `SUPERSEDED`, and `DEPRECATED`.

Stable public contracts will use explicit versioning and compatibility policy before a stable release is declared.

## License

MeaningWire is licensed under the [Apache License 2.0](LICENSE). Contributions submitted for inclusion in the project are provided under the same license unless explicitly agreed otherwise.

## Current focus

The immediate goal is a credible first usable release rather than a public idea pitch. Current work is focused on:

- defining the canonical core and schema conventions;
- defining the mapping registry and mapping-loss semantics;
- implementing validation and provenance primitives;
- building a working CLI and adapter SDK;
- implementing representative reference adapters;
- producing deterministic tests and synthetic / isolated interoperability proofs;
- establishing reproducible release automation and release evidence;
- producing a concise quickstart and enough documentation to evaluate the released software without relying on private context.

MeaningWire does not claim existing adoption, customers, expert endorsement, or production readiness. Evidence and maturity will be published as they are earned.
