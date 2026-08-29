# MeaningWire Release Notes Template

Use this template for a future versioned public release. Delete instructional text that does not apply, but do not omit a section merely because its answer is "none" or "not yet supported."

A release note is an evidence record, not a marketing substitute.

---

# MeaningWire <version>

**Release status:** `<alpha | beta | rc | preview | stable>`  
**Source commit:** `<40-character Git SHA>`  
**Release date:** `<YYYY-MM-DD>`  
**Contract maturity represented:** `<for example: EXPERIMENTAL>`

## What this release is

One short paragraph describing the concrete release and intended audience.

State whether this is for evaluation, integration testing, preview use, or stable use. Do not imply production readiness unless separately evidenced.

## Verified release evidence

- Candidate/release workflow run: `<run ID / link>`
- Source commit: `<SHA>`
- Artifact: `<filename>`
- Artifact SHA-256: `<digest>`
- Content manifest SHA-256: `<digest>`
- Fresh-environment verification: `<PASS / evidence>`
- Tested runtime/toolchain: `<for example: Linux, CPython 3.12>`
- SBOM artifact: `<filename or explicitly not provided>`
- SBOM format/version: `<for example: SPDX 2.3 transitional>`
- SBOM SHA-256: `<digest or explicitly not provided>`
- SBOM validation evidence: `<filename / digest / validation basis>`
- Build provenance/signing/attestation evidence: `<evidence or explicitly not provided>`

If an evidence item is not available, say so. Do not invent a digest, workflow run, signature, SBOM validation result, provenance statement, or attestation.

When an SBOM is provided, state its exact scope. Do not imply that an artifact-scoped or dependency-scoped SBOM inventories the operating system, build host, or other components outside its declared boundary.

## Supported in this release

List only behavior supported by the released public artifact and deterministic evidence.

Examples may include:

- registered schema validation;
- mapping registry inspection;
- exact mapping execution behavior;
- CLI commands;
- adapter behavior;
- release artifact verification.

## Added

User-visible additive changes since the previous release.

- None, if applicable.

## Changed

User-visible behavioral changes that are not necessarily breaking.

- None, if applicable.

## Fixed

Corrective changes to previously documented or tested behavior.

- None, if applicable.

## Breaking changes

For every breaking change, include:

- **Affected surface:**
- **Before:**
- **After:**
- **Why:**
- **Required action:**
- **How to detect affected consumers:**
- **Fallback/compatibility path:**
- **Evidence:**

Write `None` when there are no known breaking changes. Never hide a breaking change inside another section.

## Migration guide

Provide the smallest practical sequence a consumer needs to move from the preceding published release to this one.

If no migration is required, state that explicitly.

If migration cannot be automated, say so.

## Security-relevant changes

Describe security-sensitive changes without disclosing unsafe exploit detail.

If none are known, state `None identified for this release.`

Security vulnerability disclosure itself follows `SECURITY.md`.

## Compatibility statement

State which surfaces were tested for compatibility and which were not.

Example structure:

- Canonical schemas: `<status>`
- Mapping definitions: `<status>`
- Mapping execution: `<status>`
- CLI: `<status>`
- Adapter SDK: `<status>`
- Release artifact/evidence format: `<status>`
- SBOM/evidence format: `<status>`
- Operating-system/interpreter coverage: `<status>`

Avoid statements such as "fully backward compatible" unless the repository contains evidence broad enough to support that claim.

## Known limitations

List important unsupported or experimental behavior.

Examples may include limited path syntax, no write-back, no remote authentication, no vendor compatibility claim, or platform coverage limits.

## Explicit non-claims

State the claims a reader could otherwise reasonably infer but that this release does not support.

Typical pre-release non-claims:

- not a production-readiness certification;
- not vendor certification;
- not evidence of universal interoperability;
- not stable compatibility for experimental contracts;
- not a support-SLA commitment.

If supply-chain evidence is present, also state what it does not establish. An SBOM, checksum, provenance record, signature, or attestation is not by itself proof that software is vulnerability-free or secure.

## Public implementation boundary

Confirm that the released behavior, tests, documentation, and artifacts are reproducible from public MeaningWire sources without a private MeaningWire codebase, private schemas, hidden fixtures, or undocumented MeaningWire service dependencies.

Document any ordinary public external dependencies needed for build/install separately.

## Upgrade / rollback notes

Explain how to return to the previous release or retain the previous artifact when appropriate.

For pre-release consumers, preserving the prior versioned artifact/configuration may be the only rollback mechanism. Do not imply an automated rollback system exists unless one is actually provided.

## Checksums and artifacts

List the published artifact filenames and checksums exactly as produced by the governed release process. Include the SBOM and its validation evidence when they are part of the release evidence set.

## Changelog

Link to the corresponding `CHANGELOG.md` release section and any consequential RFCs or migration documents.
