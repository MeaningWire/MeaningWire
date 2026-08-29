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

**Status: complete at the pre-release experimental baseline**

The Phase 3 baseline now includes:

- canonical envelope, reference, provenance, and authority primitives;
- canonical domain conventions and the first experimental Identity / Party contract;
- JSON Schema Draft 2020-12 representation and local-only validation;
- public schema registry;
- deterministic mapping registry and explicit ambiguity handling;
- mapping relationship vocabulary: exact, equivalent, broader, narrower, derived, transformed, lossy, unsupported;
- fail-closed identity-transform execution;
- bounded simple-member mapping application without claiming full JSONPath support;
- pre-release CLI for health, schema validation, mapping inspection, and the pinned proof;
- read-only Adapter SDK;
- local JSON object and transactional JSON Lines reference adapters;
- deterministic tests;
- a pinned synthetic adapter-to-mapping-to-target-envelope compatibility proof.

Phase 3 is governed by the [public implementation boundary](docs/architecture/public-implementation-boundary.md): supported MeaningWire behavior must be understandable, buildable, testable, and releasable without access to a proprietary or private MeaningWire codebase. Prior research, experiments, prototypes, and implementation lessons may inform the work, but the released public implementation must stand on its own.

Completing this baseline does not make the contracts stable, production-ready, vendor-certified, or complete across every planned domain. It means the minimum technical architecture is implemented well enough to shift the primary work toward release experience, documentation, evidence, and hardening.

Initial canonical domains remain:

- Identity / Parties
- Products / Services
- Commerce
- Finance (interoperability semantics, not a replacement ledger)
- Operations
- Communications
- Content
- Governance
- Integration

Additional domain contracts should be added when they improve a concrete interoperability path rather than merely to populate the list.

## Phase 4 — Documentation and release experience

**Status: in progress**

Current evidence already includes:

- a concise public pre-release quickstart;
- a canonical `VERSION` source using an explicit prerelease version;
- a deterministic release-candidate builder sourced from exact Git object contents;
- normalized candidate archives with embedded content manifests;
- SHA-256 checksums and machine-readable release evidence;
- CI proof that repeated candidate builds from the same commit are byte-identical in the tested Linux / CPython environment;
- a manual-only, non-publishing release-candidate workflow with read-only repository permissions;
- fresh-environment verification of the extracted candidate in an isolated Python environment before candidate evidence is considered verified;
- an accepted Astro + Starlight documentation-stack decision with explicit reproducibility, accessibility, static-output, and deployment constraints;
- a low-cognitive-load documentation information architecture for beginner, builder, model/research, and evaluation/integration entry paths;
- deterministic human-readable schema and mapping references generated from canonical registries, with CI drift detection so generated documentation cannot silently diverge from the JSON source of truth.

Remaining Phase 4 work includes:

- create the Starlight source scaffold only after a pinned compatible Node/Astro/Starlight toolchain and committed package-manager lockfile can be validated;
- accessible documentation site targeting WCAG 2.2 AA;
- implement the beginner, builder, researcher/model, and integration/evaluation entry paths;
- architecture explanations and worked mapping examples beyond the current proof;
- standards crosswalk documentation;
- integrate the generated schema and mapping references into local static-site search once the Starlight build is locked and reproducible;
- release-note and compatibility/migration expectations;
- supply-chain evidence appropriate to a public preview, including SBOM/signing/provenance decisions;
- an explicitly governed publication path from a verified candidate to a public GitHub Release.

Public documentation deployment and public release publication remain outside the current automated release-agent boundary.

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
- a fresh-environment proof that supported public software can be built, tested, validated, and prepared for release without private repositories, private packages, hidden schemas, private test data, or undocumented services.

The technical mechanisms for these items are being assembled and tested during Phase 4. Meeting the threshold still requires a deliberate release-readiness reconciliation; it does not automatically publish anything.

Meeting this threshold enables a release decision and, if separately authorized, a release announcement. It does not imply production readiness or stable compatibility unless those claims are separately supported.

## Phase 6 — Public preview

After the release threshold is met and publication is separately authorized:

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
