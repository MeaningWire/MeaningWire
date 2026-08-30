# MeaningWire public identity

This file is the canonical public-facing identity reference for MeaningWire during pre-release development. It exists to keep repository metadata, documentation, release material, package metadata, and future web surfaces consistent without overstating project maturity.

## Canonical identity

**Name:** MeaningWire

**Tagline:** Define meaning once. Map systems at the edges.

**Short description:** Vendor-neutral semantic interoperability framework for systems, data, APIs, events, AI, and automation.

**Expanded description:** MeaningWire is a vendor-neutral, open-source semantic interoperability framework for connecting systems, data, APIs, events, AI agents, automation, and knowledge workflows through shared public contracts rather than brittle point-to-point integrations.

**License:** Apache-2.0

**Canonical repository:** https://github.com/MeaningWire/MeaningWire

## Maturity language

Current public maturity is **quiet pre-release** / **pre-release development**.

Until a usable versioned release is actually published, public surfaces must not claim:

- production readiness;
- stable compatibility;
- customer adoption;
- community scale;
- expert endorsement;
- a completed public release.

Experimental behavior should be labeled as experimental. Claims about interoperability, compatibility, performance, security, or release readiness should point to reproducible evidence when available.

## Voice

MeaningWire copy should be precise, calm, practical, and evidence-led.

Prefer:

- concrete descriptions of what exists now;
- explicit maturity labels;
- reproducible commands and examples;
- visible limitations and authority boundaries;
- specific technical nouns and verbs.

Avoid unsupported terms such as “production-ready,” “enterprise-grade,” “revolutionary,” “seamless,” “world-leading,” or “autonomous” when the behavior is not explicitly bounded.

## Architecture relationship

MeaningWire maintains its own project identity. Public project surfaces should not imply dependence on a private implementation, hidden proprietary codebase, or unrelated commercial product.

If a future organization supports or stewards MeaningWire, any endorsement language should be subtle, factual, and subordinate to the MeaningWire project identity.

## Component naming

Use plain component names under the MeaningWire project name where a distinct brand is unnecessary, for example:

- MeaningWire Core
- MeaningWire CLI
- MeaningWire SDK
- MeaningWire Registry
- MeaningWire Adapters

Protocols, schemas, mappings, packages, and compatibility artifacts should use descriptive, versioned technical identifiers rather than new sub-brands by default.

## Metadata consistency checklist

When a public surface is added or changed, verify that the following remain aligned:

1. project name and capitalization;
2. tagline;
3. short description;
4. license identifier;
5. canonical repository URL;
6. maturity status;
7. version/release status;
8. ownership or stewardship claims;
9. package, CLI, and namespace naming;
10. accessibility and evidence language.

The README, documentation site, `CITATION.cff`, repository metadata, package metadata, release notes, and future website metadata should converge on this reference unless a surface requires a deliberately shorter form.
