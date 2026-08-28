# MeaningWire Governance

MeaningWire is an early-stage public open-source project. Governance is intentionally lightweight at the beginning and is expected to evolve as independent contributors and maintainers emerge.

## Principles

- Technical decisions are evidence-driven and documented.
- Public contracts are not shaped around private downstream projects.
- Canonical representation is distinct from source authority and human approval authority.
- Experimental work is clearly labeled.
- Contributors receive attribution for their work.
- Maintainer roles are earned through sustained, constructive participation rather than implied by branding.
- No person, company, standards body, or downstream system receives hidden decision rights.

## Current maintainership

The project currently has a single administrative maintainer. This is a factual description of the present state, not a claim of a larger team.

As participation grows, additional maintainers may be added based on demonstrated contribution quality, reliability, project understanding, respectful collaboration, and willingness to uphold project governance.

## Decision classes

### Routine maintenance

Examples: typo fixes, documentation clarifications, test improvements, non-semantic refactoring, and reversible repository hygiene.

These may be accepted through ordinary pull-request review.

### Public contract changes

Examples: canonical schemas, mapping semantics, identifiers, versioning rules, event envelopes, adapter interfaces, provenance rules, authority semantics, and compatibility policy.

These require:

1. a written rationale;
2. compatibility and migration analysis;
3. tests or executable examples where practical;
4. public review through a pull request or RFC;
5. explicit maturity labeling.

### Governance and security changes

Changes that alter maintainer authority, release authority, disclosure policy, contribution rights, or security boundaries require an explicit governance proposal and public review.

## RFC process

Substantial design changes should begin as an RFC under `docs/rfcs/`.

An RFC should state:

- problem and user need;
- proposed behavior;
- alternatives considered;
- compatibility impact;
- security/privacy implications;
- provenance and authority implications;
- migration plan where relevant;
- maturity target;
- unresolved questions.

Accepted RFCs document project intent; implementation and release evidence still determine whether a capability is actually available.

## Maturity states

MeaningWire uses the following maturity vocabulary:

- `DISCOVERED`
- `RESEARCH`
- `EVALUATED`
- `EXPERIMENTAL`
- `PREVIEW`
- `STABLE`
- `REJECTED`
- `SUPERSEDED`
- `DEPRECATED`

A maturity label is a statement about project confidence and support, not marketing language.

## Releases

Stable release policy is not yet finalized. Before the first stable release, the project will define versioning, compatibility, deprecation, provenance, and release-signing expectations.

## Conflicts of interest

Contributors should disclose material conflicts when proposing decisions that directly benefit a vendor, employer, commercial product, or downstream implementation they control.

A disclosed interest does not disqualify participation; undisclosed preferential treatment is incompatible with vendor neutrality.

## Changes to this document

Governance changes should be proposed through pull requests with a clear explanation of why the change is needed and what authority or process it alters.
