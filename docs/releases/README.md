# Release Policy

MeaningWire is in pre-release development. This directory documents how versioned candidate builds, compatibility expectations, migration information, and eventual public releases are intended to work.

Current documents:

- [`compatibility-and-migrations.md`](compatibility-and-migrations.md) — pre-1.0 compatibility surfaces, change classification, migration expectations, and stability progression
- [`release-notes-template.md`](release-notes-template.md) — evidence-first template for a future versioned public release
- [`../architecture/release-agent-foundation.md`](../architecture/release-agent-foundation.md) — deterministic non-publishing candidate builder and evidence boundary

## Current state

The repository version is currently an explicit prerelease version. A version identifier in `VERSION` makes candidate artifacts auditable; it does **not** mean that version has been publicly released.

Until a public release is separately authorized and published:

- `VERSION` identifies the current candidate line;
- Git commits and CI runs are the evidence for implemented behavior;
- `CHANGELOG.md` records unreleased user-visible changes;
- candidate artifacts are verification outputs, not public release assets;
- no compatibility promise should be inferred beyond what the repository explicitly documents and tests.

## Publication boundary

A public GitHub Release, tag, package-registry publication, documentation deployment, announcement, or compatibility claim remains a separate action from building and verifying a release candidate.
