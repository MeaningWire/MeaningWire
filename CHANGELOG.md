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
- Locked Starlight documentation source/build foundation using Node 22.19.0, npm 10.9.3, Astro 7.2.9, Starlight 0.41.10, a committed npm lockfile, static output, local Pagefind search, and exact-head CI proof of byte-identical repeated builds.
- Initial Starlight entry pages for getting started, builders, model/research readers, integration/evaluation readers, and project-owned 404 recovery behavior without inventing a deployment URL.
- Deterministically generated schema and mapping reference pages with CI drift detection.
- Starlight-native generated schema and mapping reference pages derived from the same canonical registries, exposed through the documentation sidebar and verified in deterministic static output with the local Pagefind bundle.
- Worked `How MeaningWire works` documentation grounded in the existing synthetic JSON-object adapter → source envelope → explicit mapping → target envelope proof, including transformation provenance and the explicit non-transfer of source approval/authority.
- Fail-closed Pagefind UI CSS diagnostics that emit hashes and an exact diff if the asset diverges across repeated full documentation builds, without weakening complete-output reproducibility checks.
- Public accessibility evidence page that targets WCAG 2.2 AA without claiming formal conformance and separates static automated evidence from keyboard, browser, assistive-technology, contrast, zoom/reflow, and manual testing still required.
- Dependency-free rendered HTML/CSS accessibility and integrity validation covering document language, titles/descriptions, unique titles, main/heading structure, a named working skip target, image alt presence, autoplay rejection, and remote subresource rejection while preserving byte-identical documentation builds.
- Evidence-backed standards crosswalk that distinguishes MeaningWire's current normative JSON Schema dependency from informative standards references and comparative models without claiming equivalence, certification, affiliation, endorsement, or unproven compatibility.
- Explicit pre-release compatibility and migration policy covering schemas, mappings, execution behavior, CLI, Adapter SDK, artifact/evidence formats, and documentation.
- Evidence-first release-notes template for future versioned publication.
- Immutable full-commit-SHA pinning for external GitHub Actions with CI enforcement against floating references.
- Fully resolved, exact-version, SHA-256-hashed validation dependency lock for the governed CPython 3.12 / Linux x86-64 candidate environment.
- Deterministic transitional SPDX 2.3 candidate SBOM covering the candidate archive plus the exact governed validation dependency set.
- Immutable upstream SPDX 2.3 JSON Schema identity verification using the exact SPDX source commit and Git blob object.
- SBOM validation against both the official SPDX 2.3 schema and MeaningWire-specific package-scope, digest, license, purl, and relationship policy.
- Deterministic `spdx-validation-evidence.json` and release-evidence promotion from SBOM validation `PENDING` to `PASS` only after successful validation.
- Candidate SBOM verification documentation with explicit inventory boundaries and non-claims.
- Machine-readable `release-readiness.json` evaluation that separates mechanical release threshold, launch experience, publication capability, and the explicit human release boundary.
- Fail-closed `--require-ready` mode intended for a future governed publication workflow.
- Deterministic readiness-report comparison across repeated candidate builds and retention of the report with manual candidate evidence.

### Changed

- Phase 3 Technical MVP is recorded as complete at its experimental baseline; primary work has moved into Phase 4 documentation, release experience, evidence, and hardening.
- Release terminology now distinguishes a **candidate version/build** from a **published public release**.
- Pre-1.0 compatibility policy permits breaking changes during alpha while requiring explicit classification, migration guidance, evidence updates, and versioned release notes before publication.
- Governed validation dependencies are installed fail-closed with exact hashes and binary-only artifacts for the tested candidate target.
- Candidate `SHA256SUMS` now covers both the candidate archive and its transitional SPDX document.
- Release notes now require explicit SBOM format, scope, digest, validation evidence, and supply-chain non-claims when an SBOM is published.
- Release-readiness reconciliation is now executable rather than an informal future checklist: `BLOCKED` is a valid evaluated state, while `READY_FOR_HUMAN_DECISION` still requires explicit release authorization.
- Verified deterministic documentation-build evidence can now satisfy the launch-experience layer independently of publication capability; publication remains blocked until the governed publication and public-attestation paths exist.
- The retained candidate evidence set now includes the deterministic readiness report in addition to archive, SBOM, checksums, release evidence, and SBOM-validation evidence.
- GitHub workflow actions were refreshed to reviewed current v7 releases that natively declare Node 24 while preserving full-commit-SHA pinning and the existing workflow behavior used by MeaningWire.

### Security

- Private security and conduct reporting paths are documented without requiring public disclosure of sensitive information.
- Release-candidate automation uses read-only repository permissions and performs no release publication.
- External workflow actions are immutable by commit identity rather than floating version tags.
- Current checkout, Python setup, and artifact-upload actions now natively target Node 24 instead of relying on GitHub's forced compatibility execution of deprecated Node 20 action bundles.
- Public cryptographic artifact/SBOM attestations remain disabled during quiet pre-release candidate work; no signing key, OIDC attestation permission, Sigstore transparency-log entry, or public release is created by the current candidate process.
- A future publication workflow is expected to fail closed through the same readiness evaluator rather than maintaining a separate, weaker release criterion.

No stable or public preview release has been published yet. Items remain under `Unreleased` until an explicitly authorized versioned release is actually published.
