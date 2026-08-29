# MeaningWire Documentation

This directory contains project documentation that should be understandable without access to any private downstream repository.

Current areas:

- [`architecture/`](architecture/) — architectural principles, boundaries, and accepted design decisions
- [`rfcs/`](rfcs/) — substantial public-contract and governance proposals
- [`labs/`](labs/) — explicitly experimental research and frontier concepts
- [`quickstart.md`](quickstart.md) — the current repository-local pre-release evaluation path

## Documentation site direction

Astro + Starlight is the accepted starting stack for the first dedicated documentation site, but no site is deployed yet and no runtime dependency has been added solely on the basis of that decision.

See:

- [`architecture/documentation-stack-decision.md`](architecture/documentation-stack-decision.md) — evaluated stack, alternatives, accessibility/reproducibility constraints, and deployment boundary
- [`architecture/documentation-information-architecture.md`](architecture/documentation-information-architecture.md) — low-cognitive-load entry paths, navigation, page patterns, and source-of-truth rules

The future site is a presentation layer over canonical repository sources, not a second source of truth. Schemas remain canonical under `schemas/`, mappings under `mappings/`, executable behavior in public code/tests, and governance in the repository's policy files.

Before the Starlight scaffold becomes an operational dependency, it must have a pinned compatible Node/Astro/Starlight toolchain, a committed package-manager lockfile, and a deterministic static-site CI build. Deployment remains a separate future decision.
