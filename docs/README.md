# MeaningWire Documentation

This directory contains project documentation that should be understandable without access to any private downstream repository.

Current areas:

- [`architecture/`](architecture/) — architectural principles, boundaries, and accepted design decisions
- [`reference/`](reference/) — human-readable references derived from canonical schema and mapping data
- [`releases/`](releases/) — pre-release compatibility, migration, release-note, supply-chain evidence, and publication-boundary guidance
- [`rfcs/`](rfcs/) — substantial public-contract and governance proposals
- [`labs/`](labs/) — explicitly experimental research and frontier concepts
- [`quickstart.md`](quickstart.md) — the current repository-local pre-release evaluation path

## Generated references

Schema and mapping reference pages under [`reference/generated/`](reference/generated/) are generated deterministically from the canonical public registries and definitions. They are presentation artifacts, not a second source of truth.

Use:

```text
python tools/generate_reference_docs.py
```

to regenerate them, or:

```text
python tools/generate_reference_docs.py --check
```

to verify that committed references match canonical repository data. CI runs the check form and fails on drift.

## Release and compatibility guidance

MeaningWire's pre-release compatibility and release-evidence expectations are explicit rather than implied by the version string alone.

See:

- [`releases/compatibility-and-migrations.md`](releases/compatibility-and-migrations.md) — compatibility surfaces, breaking/additive/corrective change classification, migration-note requirements, prerelease progression, and current non-claims
- [`releases/candidate-sbom.md`](releases/candidate-sbom.md) — transitional SPDX 2.3 candidate SBOM scope, deterministic evidence, official-schema validation, and verification boundaries
- [`releases/release-notes-template.md`](releases/release-notes-template.md) — evidence-first structure required for a future public release
- [`architecture/release-agent-foundation.md`](architecture/release-agent-foundation.md) — reproducible non-publishing candidate build and verification boundary
- [`architecture/supply-chain-evidence.md`](architecture/supply-chain-evidence.md) — current supply-chain hardening and future attestation/signing direction

The current `VERSION` identifies a candidate line. Candidate SBOMs and validation evidence are verification outputs; they do not mean a GitHub Release, package, public cryptographic attestation, documentation deployment, or launch has occurred.

## Documentation site direction

Astro + Starlight is the accepted starting stack for the first dedicated documentation site, but no site is deployed yet and no runtime dependency has been added solely on the basis of that decision.

See:

- [`architecture/documentation-stack-decision.md`](architecture/documentation-stack-decision.md) — evaluated stack, alternatives, accessibility/reproducibility constraints, and deployment boundary
- [`architecture/documentation-information-architecture.md`](architecture/documentation-information-architecture.md) — low-cognitive-load entry paths, navigation, page patterns, and source-of-truth rules

The future site is a presentation layer over canonical repository sources, not a second source of truth. Schemas remain canonical under `schemas/`, mappings under `mappings/`, executable behavior in public code/tests, and governance in the repository's policy files.

Before the Starlight scaffold becomes an operational dependency, it must have a pinned compatible Node/Astro/Starlight toolchain, a committed package-manager lockfile, and a deterministic static-site CI build. Deployment remains a separate future decision.
