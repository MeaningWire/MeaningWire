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
- a locked documentation source/build foundation using Node 22.19.0, npm 10.9.3, Astro 7.2.9, Starlight 0.41.10, a committed npm lockfile, static output, and local Pagefind search;
- exact-head CI proof that the locked documentation build succeeds twice with byte-identical complete static output and no output symlinks;
- initial Starlight entry paths for getting started, builders, model/research readers, and integration/evaluation readers, plus a project-owned pre-deployment 404 page;
- a low-cognitive-load documentation information architecture for beginner, builder, model/research, and evaluation/integration entry paths;
- deterministic human-readable schema and mapping references generated from canonical registries, with CI drift detection so generated documentation cannot silently diverge from the JSON source of truth;
- generated schema and mapping references integrated into Starlight navigation and local Pagefind search while the canonical JSON registries remain authoritative;
- exact-head CI proof that both generated reference routes render canonical registry identifiers and remain byte-identical across repeated complete static builds;
- a worked synthetic architecture walkthrough covering read-only adapter input, source envelope construction, explicit deterministic mapping, target envelope construction, transformation provenance, and the non-transfer of source approval/authority;
- fail-closed documentation-build diagnostics that preserve the complete byte-identical-output requirement while emitting Pagefind UI CSS hashes and an exact diff if that asset ever diverges across repeated builds;
- dependency-free rendered documentation integrity/accessibility checks for document language, metadata, duplicate titles, main/heading structure, working named skip targets, image alt presence, autoplay media, remote HTML/CSS subresources, and invalid internal links;
- a public accessibility evidence page that targets WCAG 2.2 AA while explicitly separating static automated evidence from keyboard, browser, assistive-technology, contrast, zoom/reflow, and formal conformance testing that has not been claimed;
- an evidence-backed standards crosswalk that distinguishes the current normative JSON Schema Draft 2020-12 dependency from informative standards references and comparative models, and explicitly rejects unsupported equivalence, certification, affiliation, endorsement, compatibility, or authority-transfer claims;
- an explicit pre-release compatibility policy that classifies additive, corrective, breaking, security-sensitive, and internal-only changes across named compatibility surfaces;
- migration-note requirements for breaking changes and an evidence-first release-note template for future versioned publication;
- a reconciled unreleased changelog that distinguishes candidate builds from published releases;
- immutable full-commit pins for external GitHub Actions plus CI enforcement that rejects floating workflow action references;
- a target-specific CPython 3.12 / Linux x86-64 validation lock containing the complete currently resolved six-package environment with accepted SHA-256 wheel hashes;
- governed CI and extracted-candidate verification that install the validation environment with `--require-hashes --only-binary=:all:` and verify installed versions against the lock;
- an accepted supply-chain evidence direction: SPDX 3 as the preferred strategic SBOM family once tooling is proven, SLSA 1.2 provenance as the current provenance model, keyless GitHub/Sigstore identity for future release signing, and the supported consolidated GitHub attestation path for a future publication workflow;
- a deterministic transitional SPDX 2.3 candidate SBOM scoped to the candidate archive and governed locked validation environment;
- exact upstream SPDX 2.3 schema identity pinning, Git-blob verification, official-schema validation, and a second MeaningWire-specific scope/digest policy validation layer;
- deterministic SBOM validation evidence plus a `PENDING` → `PASS` release-evidence lifecycle that prevents an unvalidated SBOM from being presented as verified;
- a deterministic machine-readable release-readiness gate that separately evaluates mechanical release-threshold evidence, launch experience, and publication capability;
- a verified documentation-build input that allows the launch-experience layer to pass only when the current source scaffold and repeated deterministic build have both been proven;
- a fail-closed future-publication contract in which `--require-ready` must reject publication while any machine-evaluated blocker remains;
- an explicit human authority boundary that remains pending even after a future `READY_FOR_HUMAN_DECISION` result;
- an explicit boundary that public Sigstore/GitHub attestations remain disabled during quiet pre-release candidate work and belong to the separately governed publication path.

Remaining Phase 4 work includes:

- accessibility review and hardening toward the WCAG 2.2 AA target without claiming formal conformance before sufficient testing;
- deepen the beginner, builder, researcher/model, and integration/evaluation paths as the public surface grows;
- maintain and deepen the evidence-backed standards crosswalk as implemented mappings or reference coverage grow;
- evaluate and prove an eventual SPDX 3 migration path without weakening current deterministic SBOM verification;
- implement the separately governed manual publication workflow with fail-closed readiness enforcement;
- implement release-only build/SBOM attestations and documented public verification inside that publication boundary;
- reconcile the machine-readable readiness report until the exact candidate reaches `READY_FOR_HUMAN_DECISION` before asking for public release authorization.

Public documentation deployment, public artifact attestation, and public release publication remain outside the current automated candidate boundary. The canonical Astro `site` URL remains intentionally unset until a real deployment URL is separately authorized and exists.

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
- explicit compatibility and migration expectations for the release's public surfaces;
- immutable external CI/action inputs and documented supply-chain verification expectations;
- a fully resolved, hashed dependency environment for the governed candidate target;
- an accurately scoped, deterministically generated SBOM that passes an immutable official specification validation path plus project-specific scope validation;
- a provenance and public-attestation strategy appropriate to the artifact actually being published;
- a fresh-environment proof that supported public software can be built, tested, validated, and prepared for release without private repositories, private packages, hidden schemas, private test data, or undocumented services;
- a machine-readable readiness report that binds those candidate checks to the exact source commit and exposes remaining launch/publication blockers rather than silently treating them as satisfied.

`tools/release_readiness.py` now performs that reconciliation. Passing the mechanical release-threshold section does not automatically make the project launch-ready: the report separately evaluates documentation/launch experience and governed publication/attestation capability.

Only a future `READY_FOR_HUMAN_DECISION` report permits the release agent to ask for public release authorization. It does not grant that authorization itself.

Meeting this threshold enables a release decision and, if separately authorized, a release announcement. It does not imply production readiness or stable compatibility unless those claims are separately supported.

## Phase 6 — Public preview

After the readiness gate reports `READY_FOR_HUMAN_DECISION` and publication is separately authorized:

- publish a versioned preview release through the governed publication workflow;
- announce what is actually available rather than pitching unfinished roadmap ideas;
- publish compatibility and migration expectations with the release;
- attach or reference the governed SBOM and verifiable provenance/attestation evidence;
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
