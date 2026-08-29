# Changelog

MeaningWire follows a public, evidence-based development process. This file records user-visible project changes while they are unreleased and, later, under versioned release headings.

The repository currently has a prerelease candidate version identifier, but **no public versioned release has been published yet**.

## Unreleased

### Added

- Public project foundation, governance, contribution, conduct, security, support, roadmap, citation, issue-template, and Apache-2.0 licensing files.
- Quiet pre-release positioning and a documented public-implementation boundary.
- Canonical Reference, Authority, Provenance, and Envelope schema primitives.
- Draft 2020-12 local schema validation and a public schema registry.
- Deterministic mapping registry with explicit relationship vocabulary and ambiguity handling.
- Fail-closed identity mapping execution and bounded simple-member mapping application.
- Read-only Adapter SDK.
- Local JSON object and transactional JSON Lines reference adapters.
- Pinned synthetic adapter-to-mapping-to-target-envelope interoperability proof.
- Experimental Identity / Party canonical contract.
- Pre-release CLI for health checks, schema validation, registry inspection, and the pinned interoperability proof.
- Public quickstart for reproducing the current proof from a fresh checkout.
- Canonical repository `VERSION` source, currently identifying the `0.1.0-alpha.0` candidate line.
- Deterministic non-publishing release-candidate builder using exact Git object contents.
- Normalized candidate archive, embedded content manifest, `SHA256SUMS`, and machine-readable release evidence.
- CI proof of byte-for-byte repeated candidate builds in the tested Linux / CPython environment.
- Fresh-environment verification of the extracted candidate in an isolated Python environment.
- Manual-only release-candidate workflow that retains verified evidence without publishing a release.
- Accepted Astro + Starlight documentation architecture and low-cognitive-load information architecture, without deployment.
- Deterministically generated schema and mapping reference pages with CI drift detection.
- Explicit pre-release compatibility and migration policy covering schemas, mappings, execution behavior, CLI, Adapter SDK, artifact/evidence formats, and documentation.
- Evidence-first release-notes template for future versioned publication.

### Changed

- Phase 3 Technical MVP is recorded as complete at its experimental baseline; primary work has moved into Phase 4 documentation, release experience, evidence, and hardening.
- Release terminology now distinguishes a **candidate version/build** from a **published public release**.
- Pre-1.0 compatibility policy permits breaking changes during alpha while requiring explicit classification, migration guidance, evidence updates, and versioned release notes before publication.

### Security

- Private security and conduct reporting paths are documented without requiring public disclosure of sensitive information.
- Release-candidate automation uses read-only repository permissions and performs no release publication.

No stable or public preview release has been published yet. Items remain under `Unreleased` until an explicitly authorized versioned release is actually published.
