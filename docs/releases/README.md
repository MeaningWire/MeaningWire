# Release Policy

MeaningWire is in pre-release development. This directory documents how versioned candidate builds, compatibility expectations, migration information, supply-chain evidence, and eventual public releases are intended to work.

Current documents:

- [`compatibility-and-migrations.md`](compatibility-and-migrations.md) — pre-1.0 compatibility surfaces, change classification, migration expectations, and stability progression
- [`candidate-sbom.md`](candidate-sbom.md) — transitional SPDX 2.3 candidate SBOM scope, deterministic generation, official-schema validation, MeaningWire policy validation, and explicit non-claims
- [`release-notes-template.md`](release-notes-template.md) — evidence-first template for a future versioned public release
- [`../architecture/release-agent-foundation.md`](../architecture/release-agent-foundation.md) — deterministic non-publishing candidate builder and evidence boundary
- [`../architecture/supply-chain-evidence.md`](../architecture/supply-chain-evidence.md) — action pinning, dependency locking, SBOM/provenance direction, signing strategy, and publication boundary

## Current state

The repository version is currently an explicit prerelease version. A version identifier in `VERSION` makes candidate artifacts auditable; it does **not** mean that version has been publicly released.

The current candidate process can produce and verify:

- a deterministic candidate archive;
- SHA-256 checksums;
- machine-readable release evidence;
- a target-specific hashed Python validation dependency environment;
- a deterministic transitional SPDX 2.3 SBOM covering the candidate archive and that governed validation environment;
- deterministic SBOM validation evidence against a pinned immutable official SPDX 2.3 schema plus MeaningWire's narrower scope policy.

Until a public release is separately authorized and published:

- `VERSION` identifies the current candidate line;
- Git commits and CI runs are the evidence for implemented behavior;
- `CHANGELOG.md` records unreleased user-visible changes;
- candidate artifacts and SBOMs are verification outputs, not public release assets;
- no compatibility, security, certification, or production-readiness promise should be inferred beyond what the repository explicitly documents and tests.

## Publication boundary

A public GitHub Release, tag, package-registry publication, documentation deployment, announcement, cryptographic public attestation, or compatibility claim remains a separate action from building and verifying a release candidate.
