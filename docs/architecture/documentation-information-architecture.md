# Documentation Information Architecture

MeaningWire's documentation should answer **what do I do next?** before exposing the full depth of the architecture.

The site will use progressive disclosure: a small number of entry paths lead to increasingly detailed material, while canonical schemas, mappings, and governance remain directly inspectable in the repository.

## Primary entry paths

### Start here

Audience: someone encountering MeaningWire for the first time.

Goal: understand the problem, see one working proof, and know what the project does **without** reading architecture papers first.

Initial pages:

- What is MeaningWire?
- Five-minute pre-release quickstart
- What the current release does and does not claim
- The adapter → mapping → canonical-envelope example
- Where to go next

Primary next action: run the pinned proof or inspect its exact output.

### Build with MeaningWire

Audience: developers and integrators.

Goal: understand the executable contracts and implement against them without private context.

Initial sections:

- Canonical envelope
- References and identifiers
- Provenance and authority
- Schema registry
- Mapping registry
- Mapping execution and current path subset
- Adapter SDK
- JSON object adapter
- JSON Lines adapter
- CLI reference
- Testing and validation
- Release artifacts and verification

Primary next action: validate a local fixture or inspect a mapping.

### Understand the model

Audience: architects, standards practitioners, technical reviewers, and researchers.

Goal: explain why the model has its boundaries and how external standards inform it.

Initial sections:

- Public implementation boundary
- Canonical-domain conventions
- Identity / Party model
- Mapping relationship semantics
- Provenance and authority model
- Standards strategy
- Crosswalk methodology
- Known losses, ambiguities, and unsupported semantics
- RFCs and MeaningWire Labs

Primary next action: inspect the relevant canonical contract and evidence before proposing a semantic change.

### Evaluate / integrate

Audience: teams deciding whether MeaningWire is relevant to an integration problem.

Goal: provide an evidence-oriented path without marketing claims.

Initial sections:

- Current maturity and compatibility statement
- Supported vs experimental behavior
- Fresh-environment proof
- Reproducible candidate build
- Security and disclosure
- Governance and change process
- Integration checklist
- Compatibility/loss evidence
- Release and migration policy when established

Primary next action: reproduce the proof in a clean environment and compare the public contract to the target integration boundary.

## Global navigation

Keep top-level navigation intentionally small:

```text
Start Here
Build
Model
Evaluate
Reference
Project
```

`Reference` contains generated or source-derived schema, mapping, CLI, and adapter references.

`Project` contains roadmap, governance, security, support, contributing, RFC process, Labs maturity, changelog, and citation information.

Do not create separate top-level navigation for every canonical domain. Domains belong under `Model` and `Reference` until content volume proves otherwise.

## Page pattern

Most conceptual pages should follow the same predictable order when applicable:

1. **Purpose** — one short paragraph.
2. **Current status** — maturity and compatibility boundary.
3. **How it works** — the smallest useful explanation.
4. **Example** — preferably executable or linked to a deterministic fixture.
5. **What it does not do** — explicit non-claims and unsupported behavior.
6. **Reference** — schema, mapping, source, or standards links.
7. **Next** — one or two relevant next pages, not a wall of choices.

Reference pages may use a denser structure, but should still expose maturity and version near the top.

## Cognitive-accessibility rules

- Prefer descriptive headings over clever headings.
- Keep paragraphs short enough to scan without turning every sentence into a separate block.
- Use one primary call to action per entry page.
- Put advanced caveats near the feature they constrain rather than in a distant legalistic appendix.
- Preserve consistent vocabulary from the public schemas and code.
- Do not use icons, color, or maturity badges without accompanying text.
- Avoid unexplained acronyms in beginner paths.
- Do not require readers to understand GitHub contribution mechanics before they can understand the software.
- Use tables only where comparison is clearer than prose.
- Long standards discussions belong in `Model` or research pages, not in the quickstart.
- Search results should prioritize user-facing guides before deep generated references where Pagefind ranking configuration allows it.

## Source-of-truth rule

The documentation site is a presentation layer, not a second canonical repository.

- schemas remain canonical under `schemas/`;
- mapping definitions remain canonical under `mappings/`;
- executable behavior remains canonical in public code/tests;
- governance files remain canonical at their repository locations;
- the docs site may render, summarize, or link these resources but must not maintain contradictory copies.

Generated reference pages should be built from canonical repository data whenever practical.

## Pre-release visibility

The site source may be developed and tested before deployment. Until the release threshold and publication decision are satisfied:

- no production-readiness banner or adoption prompt;
- no newsletter, analytics, tracking pixel, social campaign, or contributor-recruitment funnel;
- no implication that experimental contracts are stable;
- no public deployment is required merely because the site builds successfully.

The desired first-release experience is evidence-first: **here is what exists, here is how to run it, here is what it proves, and here are its limits.**
