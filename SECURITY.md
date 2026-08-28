# MeaningWire Security Policy

MeaningWire is in an early development stage and is not yet declared production ready. Security practices will mature with the codebase and release process.

## Reporting a vulnerability

Please do **not** disclose a vulnerability publicly if doing so could put users, systems, credentials, data, or downstream integrations at risk.

MeaningWire does not yet publish a dedicated security email and GitHub private vulnerability reporting has not yet been established for the project.

If a private GitHub contact path to the repository owner or maintainer is available, use it and initially provide only the minimum information needed to establish contact.

If no private contact path is available, open a public issue containing only a request for private security contact. Do **not** include vulnerability details, exploit steps, credentials, personal data, sensitive production information, or attachments in that public issue. Sensitive details should be shared only after a private channel is established.

A future revision of this policy will publish a dedicated security contact and coordinated disclosure workflow.

## Useful report contents

When safe to share privately, include:

- affected component and version/commit;
- impact and realistic attack scenario;
- reproduction steps or a minimal proof of concept;
- required privileges or preconditions;
- suggested mitigation if known;
- whether the issue has been disclosed elsewhere.

## Security priorities

The project intends to treat the following as first-class concerns:

- schema and mapping integrity;
- provenance and transformation traceability;
- authority-boundary preservation;
- untrusted input handling;
- adapter credential isolation;
- dependency and supply-chain risk;
- workflow least privilege;
- artifact and release provenance;
- reproducible validation;
- secure defaults and explicit opt-in for risky capabilities.

## AI and agent safety boundary

MeaningWire must not treat model output, inferred mappings, or agent actions as equivalent to human approval. Systems integrating AI should preserve provenance, uncertainty, and the authority source that permitted any consequential action.

## Supported versions

No stable or supported release exists yet. Security fixes during the pre-release phase will target the current development line unless a release note says otherwise.

## Planned maturity work

Before stable release, the project plans to define and implement:

- private vulnerability reporting;
- dependency and secret scanning;
- branch and workflow protections;
- least-privilege GitHub Actions permissions;
- SBOM and release provenance strategy;
- signed or otherwise verifiable release artifacts where practical;
- OpenSSF Scorecard / OSPS Baseline-aligned controls appropriate to the project.

Security status will be described by evidence rather than badges alone.
