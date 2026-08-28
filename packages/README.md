# Packages

This directory is reserved for MeaningWire implementation packages that expose public, versioned project interfaces.

The initial plan is to keep related implementation work in this monorepo while contracts and tooling are still evolving together.

Expected package families include:

- core semantic / validation library;
- CLI;
- adapter SDK;
- schema and mapping utilities;
- provenance helpers.

## Current CLI prototype

The first read-only CLI foundation intentionally lives at `tools/meaningwire.py` rather than being published or presented as a stable package. It exercises real public repository behavior while command boundaries and package layout are still experimental.

Moving that CLI into an installable package should be a later release-hardening decision with an explicit package name, versioning policy, reproducible build, dependency lock/provenance evidence, and installation tests.

Package boundaries, implementation languages, and publication targets are not yet stable and should be established through architecture decisions and executable prototypes rather than assumed here.
