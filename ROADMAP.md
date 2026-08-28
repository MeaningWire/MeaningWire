# MeaningWire Roadmap

This roadmap describes direction, not promises. Dates and scope may change as evidence, contributors, standards research, and implementation results improve the plan.

## Phase 1 — Name and identity

**Status: complete**

- MeaningWire selected as the project name.
- Public GitHub organization created.
- Initial public repository created.
- Preliminary namespace and conflict screen completed.

## Phase 2 — Public foundation

**Status: in progress**

- README and project positioning
- governance model
- contribution guide
- code of conduct
- security policy
- support policy
- roadmap
- citation metadata
- issue and pull-request templates
- RFC and Labs structure
- explicit license decision
- organization profile and public contact strategy

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

## Phase 4 — Documentation experience

- evaluate Astro + Starlight against project needs;
- accessible documentation site targeting WCAG 2.2 AA;
- beginner, builder, researcher, and integration/enterprise entry paths;
- architecture explanations and worked mapping examples;
- standards crosswalk documentation;
- searchable schema and mapping reference.

## Phase 5 — Real-world proof

- synthetic and isolated compatibility fixtures;
- public example adapters;
- published compatibility and loss evidence;
- integration guides that consume only public MeaningWire contracts;
- no private downstream repository modifications as part of the public project's proof requirement.

Actual integrations into unrelated existing repositories are separate workstreams governed by those repositories' own authority and approval processes.

## Phase 6 — Public preview

- versioned preview release;
- documented compatibility and migration expectations;
- GitHub Discussions if useful;
- transparent RFC process;
- expert-review requests where genuine independent review is needed;
- security and supply-chain baseline appropriate to a public preview.

## Phase 7 — Growth

Potential directions, subject to evidence:

- additional adapters and standards mappings;
- package publication;
- expanded SDK language support;
- technology and standards radar;
- contributor and maintainer progression;
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
- contributor usability;
- deterministic validation;
- standards alignment;
- accessibility;
- security and operational trust.

Novelty alone is not sufficient.
