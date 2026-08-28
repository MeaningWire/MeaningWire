# MeaningWire Roadmap

This roadmap describes direction, not promises. Dates and scope may change as evidence, standards research, and implementation results improve the plan.

The repository is public during development, but the roadmap is not a request for outside developers to implement unfinished items. The immediate goal is to complete and validate a coherent first usable release before any broader launch or adoption push.

## Phase 1 — Name and identity

**Status: complete**

- MeaningWire selected as the project name.
- Public GitHub organization created.
- Initial public repository created.
- Preliminary namespace and conflict screen completed.

## Phase 2 — Public foundation

**Status: complete**

- README and project positioning
- governance model
- contribution policy
- code of conduct
- security policy
- support policy
- roadmap
- citation metadata
- changelog
- issue and pull-request templates
- RFC and Labs structure
- Apache-2.0 project license
- protected default branch
- private project contact and disclosure path
- public organization profile
- quiet pre-release posture

## Phase 3 — Technical MVP

Target capabilities:

- canonical core and domain conventions;
- JSON Schema representation;
- schema registry;
- mapping registry;
- mapping relationships: exact, equivalent, broader, narrower, derived, transformed, lossy, unsupported;
- provenance and authority metadata;
- validation tooling;
- CLI;
- adapter SDK;
- two representative read-oriented reference adapters;
- deterministic tests;
- synthetic / isolated downstream compatibility proof.

Phase 3 is governed by the [public implementation boundary](docs/architecture/public-implementation-boundary.md): supported MeaningWire behavior must be understandable, buildable, testable, and releasable without access to a proprietary or private MeaningWire codebase. Prior research, experiments, prototypes, and implementation lessons may inform the work, but the released public implementation must stand on its own.

Initial canonical domains:

- Identity / Parties
- Products / Services
- Commerce
- Finance (interoperability semantics, not a replacement ledger)
- Operations
- Communications
- Content
- Governance
- Integration

## Phase 4 — Documentation and release experience

- evaluate Astro + Starlight against project needs;
- accessible documentation site targeting WCAG 2.2 AA;
- concise quickstart and installation path;
- beginner, builder, researcher, and integration/enterprise entry paths;
- architecture explanations and worked mapping examples;
- standards crosswalk documentation;
- searchable schema and mapping reference;
- reproducible release automation and release evidence;
- release artifacts with documented version and provenance.

## Phase 5 — Real-world proof

- synthetic and isolated compatibility fixtures;
- public example adapters;
- published compatibility and loss evidence;
- integration guides that consume only public MeaningWire contracts;
- no private downstream repository modifications as part of the public project's proof requirement.

Actual integrations into unrelated existing repositories are separate workstreams governed by those repositories' own authority and approval processes.

## Release threshold

Before MeaningWire is presented as something people should try or adopt, the project should have evidence for a minimum release threshold:

- a versioned usable build;
- deterministic validation;
- working CLI behavior for the documented quickstart;
- at least one complete mapping / adapter path that demonstrates the model end to end;
- reproducible release automation;
- release provenance and artifacts;
- installation and quickstart documentation that works without private context;
- explicit statements of supported, experimental, and unfinished behavior;
- a fresh-environment proof that supported public software can be built, tested, validated, and released without private repositories, private packages, hidden schemas, private test data, or undocumented services.

Meeting this threshold enables a release announcement. It does not imply production readiness or stable compatibility unless those claims are separately supported.

## Phase 6 — Public preview

After the release threshold is met:

- publish a versioned preview release;
- announce what is actually available rather than pitching unfinished roadmap ideas;
- document compatibility and migration expectations;
- open broader review and contribution channels if useful;
- enable GitHub Discussions if it serves a real purpose;
- use the transparent RFC process for consequential public-contract changes;
- request expert review where genuine independent review is needed;
- establish a security and supply-chain baseline appropriate to a public preview.

## Phase 7 — Growth

Potential directions, subject to evidence:

- additional adapters and standards mappings;
- package publication;
- expanded SDK language support;
- technology and standards radar;
- contributor and maintainer progression if sustained external participation develops;
- public interoperability test corpus;
- conformance tooling;
- case studies based on verified real-world use;
- stronger OpenSSF / OSPS-aligned project security maturity.

## MeaningWire Labs

Frontier concepts may be researched without becoming core commitments. Labs work uses explicit maturity states:

`DISCOVERED → RESEARCH → EVALUATED / EXPERIMENTAL → PREVIEW → STABLE`

Concepts may also become `REJECTED`, `SUPERSEDED`, or `DEPRECATED`.

## Decision filter

A roadmap item should earn priority by improving at least one of:

- semantic correctness;
- interoperability reach;
- provenance / authority safety;
- developer usability;
- deterministic validation;
- release readiness;
- standards alignment;
- accessibility;
- security and operational trust.

Novelty alone is not sufficient.
