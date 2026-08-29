# Supply-Chain Evidence Strategy

Status: **ACCEPTED FOR PREVIEW HARDENING; PUBLIC ATTESTATION NOT YET ENABLED**

MeaningWire should make release integrity independently inspectable without introducing long-lived signing secrets, floating workflow dependencies, or premature public attestation records during quiet pre-release development.

This document records the current supply-chain direction. It does not publish a release, generate a public cryptographic attestation, create a signing key, or claim a SLSA level.

## Immediate control: immutable GitHub Actions pins

All external GitHub Actions used by MeaningWire workflows must be pinned to a full 40-character commit SHA.

Human-readable version comments remain beside the SHA so reviewers can see which upstream release was intentionally selected.

Current pins:

| Action | Reviewed release | Immutable commit | Runtime |
| --- | --- | --- | --- |
| `actions/checkout` | `v7.0.1` | `3d3c42e5aac5ba805825da76410c181273ba90b1` | Node 24 |
| `actions/setup-python` | `v7.0.0` | `5fda3b95a4ea91299a34e894583c3862153e4b97` | Node 24 |
| `actions/upload-artifact` | `v7.0.1` | `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` | Node 24 |

These pins were selected from the official upstream release tags and verified against each action's committed `action.yml`. The update replaces older pins whose action metadata targeted Node 20 and which GitHub-hosted runners were already forcibly executing under Node 24 with deprecation warnings. MeaningWire prefers reviewed actions that natively declare the current runner runtime instead of relying on a platform compatibility override.

The v7 changes were reviewed before adoption. For MeaningWire's current usage:

- checkout v7's stricter handling of trusted-context fork-PR checkout is compatible with the normal `pull_request`/`push` workflow and strengthens an unused risky boundary;
- setup-python v7 removes the `pip-install` input, which MeaningWire does not use, and retains the `python-version` input used by the workflows;
- upload-artifact v7 adds optional direct single-file upload behavior, while MeaningWire continues using the normal archived directory upload path.

`tools/validate_workflow_pins.py` scans `.github/workflows/*.yml` and `.yaml` and fails CI if an external `uses:` reference is not pinned to a full commit SHA.

A future action update should:

1. identify the intended upstream version from the action's official repository;
2. resolve that version tag to its exact commit SHA;
3. review release notes and breaking/runtime requirements;
4. inspect the pinned action metadata when runtime generation is relevant;
5. replace the SHA and adjacent version comment together;
6. require the normal MeaningWire exact-head CI and PR review before merge.

A floating major tag such as `actions/checkout@v7` is not acceptable.

## Validation dependency lock

MeaningWire maintains two different dependency artifacts for different purposes:

- `requirements-validation.txt` is the small direct dependency input used for ordinary cross-platform evaluation;
- `requirements-validation.lock` is the fully resolved, exact-version, SHA-256-hashed validation environment used by governed candidate evidence for **CPython 3.12 on Linux x86-64**.

The current lock resolves the `jsonschema==4.26.0` input into six packages:

- `attrs==26.1.0`;
- `jsonschema==4.26.0`;
- `jsonschema-specifications==2025.9.1`;
- `referencing==0.37.0`;
- `rpds-py==2026.6.3`;
- `typing-extensions==4.16.0`.

Each locked package has an accepted wheel SHA-256. The target is deliberately narrow because `rpds-py` uses platform-specific binary wheels. The lock is evidence for the tested GitHub-hosted Linux x86-64 candidate environment; it is not a claim that the same wheel digest applies to macOS, Windows, Linux ARM64, or another interpreter generation.

Governed CI installs the lock with:

```text
pip install --require-hashes --only-binary=:all: -r requirements-validation.lock
```

This causes installation to fail if:

- a transitive dependency is missing from the lock;
- a locked version cannot satisfy the dependency graph;
- the selected wheel digest is not one of the allowed hashes;
- a source build would otherwise be required.

`tools/validate_dependency_lock.py` additionally requires exact pins and SHA-256 hashes, verifies that the direct requirement is represented at the same version, and can verify installed package versions against the lock. The extracted-candidate proof performs this verification inside a newly created virtual environment.

When the direct validation requirement is intentionally upgraded, the dependency lock must be re-resolved from public package metadata, reviewed, and proven by exact-head CI before merge. A dependency version should not be changed merely to make a hash mismatch disappear.

## SBOM direction

MeaningWire intends to publish a machine-readable Software Bill of Materials with a future public release and now generates SBOM evidence during candidate verification.

### Strategic format direction

**SPDX 3** remains the preferred strategic SBOM family once an implementation toolchain is proven end to end.

MeaningWire does not label current evidence as SPDX 3 merely because the newer specification exists. Generator, validator, attestation, and consumer interoperability must be proven together.

CycloneDX remains a relevant interoperability format to evaluate. Format selection should be driven by reliable end-to-end evidence rather than novelty.

### Current transitional candidate implementation

The current candidate process emits **SPDX 2.3 JSON** as an explicitly transitional format.

Its declared scope is intentionally narrow:

- the exact MeaningWire candidate archive; and
- the complete target-specific validation environment represented by `requirements-validation.lock`.

It does not claim to inventory the host operating system, runner internals, Git, interpreter implementation files, transient system libraries, or untested platforms.

The root MeaningWire SPDX package is bound to the exact candidate archive SHA-256. Each locked dependency records its exact package version, accepted target wheel SHA-256, and PyPI package URL.

The SBOM is generated deterministically by `tools/generate_spdx_sbom.py`. Its creation timestamp is derived from the exact source Git commit rather than wall-clock build time, and the SPDX document namespace binds the candidate version and source commit.

### Official schema identity and validation

MeaningWire does not vendor the upstream SPDX 2.3 JSON Schema into the Apache-2.0 repository.

Candidate validation fetches the official schema from this immutable SPDX source identity:

```text
repository: spdx/spdx-spec
commit: 44ab76293754df4af5af700fd4abd5453b866c86
path: schemas/spdx-schema.json
Git blob SHA-1: 0ca1c7b56bebb10fb637285698e401342b4910d6
upstream license: CC-BY-3.0
```

`tools/fetch_spdx_schema.py` recomputes the downloaded file's Git blob object identifier and fails closed if the bytes do not match the pinned blob. The schema is then used locally for SPDX 2.3 JSON Schema validation and is not retained as a MeaningWire candidate artifact.

Passing the official schema is necessary but not sufficient. `tools/validate_spdx_sbom.py` additionally verifies MeaningWire's declared package scope, candidate digest, root license, exact locked package set, package hashes, purls, and dependency relationships.

### Validation evidence lifecycle

Fresh candidate generation records SBOM validation as `PENDING` in `release-evidence.json`.

After both official SPDX schema validation and MeaningWire policy validation pass, CI creates `spdx-validation-evidence.json` and promotes the release-evidence state to `PASS`. The promoted evidence records the validation-evidence SHA-256 and exact upstream SPDX schema identity used.

The candidate builder runs twice. CI requires byte-identical:

- candidate archive;
- SPDX document;
- `SHA256SUMS`;
- SBOM validation evidence; and
- promoted release evidence.

`SHA256SUMS` covers the candidate archive and the SPDX document. The validation-evidence digest is bound inside the promoted release evidence because that file is produced only after schema validation succeeds.

See [`../releases/candidate-sbom.md`](../releases/candidate-sbom.md) for the public verification contract and explicit non-claims.

### Why this remains transitional

The current implementation satisfies a useful candidate-evidence need without claiming that SPDX 2.3 is the project's permanent format.

Before migrating candidate or release evidence to SPDX 3, MeaningWire should prove:

1. a suitable generator is pinned and auditable;
2. the exact SPDX 3 specification version is explicit;
3. generated output validates against the selected specification;
4. repeated generation has understood determinism properties;
5. the SBOM can be bound to the exact release artifact digest through the selected attestation path;
6. consumers can verify the result using documented public tooling.

The transition should be treated as an evidence-format compatibility change and documented accordingly.

## Provenance direction

SLSA 1.2 is the current SLSA specification generation at this research checkpoint.

MeaningWire's existing release evidence records exact source commit and artifact digests, but that file is project-generated evidence rather than a cryptographically signed third-party attestation.

For a future public release, the preferred next layer is a standard SLSA build-provenance attestation bound to the published artifact digest.

MeaningWire does **not** currently claim SLSA Build Level 1, 2, 3, or any other level. A level should be claimed only after the complete requirements for that level have been evaluated and evidenced.

## Attestation and signing direction

GitHub's current consolidated `actions/attest` action supports build provenance, SBOM attestations, and custom attestation predicates. MeaningWire should use the current supported consolidated path rather than introduce deprecated attestation actions.

GitHub artifact attestations use Sigstore. For public repositories, signing events use public infrastructure with publicly readable transparency evidence.

That public transparency property is desirable for an actual public release, but it also makes attestation more consequential than producing a non-published candidate artifact.

Therefore:

- the quiet pre-release candidate workflow does **not** request `id-token: write` or `attestations: write`;
- it does **not** invoke a public artifact-attestation action;
- it does **not** create a public Sigstore transparency-log entry;
- enabling public artifact/SBOM attestations belongs to the separately governed publication path.

## Key management

MeaningWire should prefer identity-based/keyless signing through GitHub Actions OIDC + Sigstore for public release artifacts rather than creating a long-lived private signing key stored as a repository secret.

Keyless signing binds an ephemeral signing key to an authenticated identity and records verification material in the transparency system. This reduces the operational burden and compromise risk associated with maintaining a persistent release-signing private key.

A self-managed signing key should be introduced only if a concrete interoperability or governance requirement cannot be met with keyless signing.

## Candidate evidence versus published attestation

The project deliberately separates two stages.

### Quiet pre-release candidate evidence

Current candidate evidence includes or may include:

- exact source commit;
- deterministic archive;
- embedded release manifest;
- SHA-256 artifact digest;
- machine-readable release evidence;
- repeated-build byte comparison;
- isolated extracted-candidate execution;
- exact hashed validation dependency environment for the tested target;
- deterministic transitional SPDX 2.3 candidate SBOM;
- validation against an immutable official SPDX 2.3 schema identity;
- deterministic SBOM validation evidence;
- CI run identity;
- immutable workflow action pins.

These checks do not create a public release or external cryptographic attestation.

### Future public-release evidence

Subject to release authorization and completed implementation, a public release should add:

- the governed validated SBOM associated with the published artifact;
- build-provenance attestation bound to the release artifact digest;
- SBOM attestation bound to the same artifact;
- keyless Sigstore/GitHub identity evidence;
- documented public verification commands;
- release notes containing exact artifact and evidence references.

## Verification-first rule

An SBOM or attestation is useful only if consumers can verify it and understand what policy it proves.

MeaningWire should not present an SBOM, signature, or attestation as proof that software is secure. These mechanisms establish bounded inventory, provenance, integrity, or signing identity; consumers still need to evaluate source, workflows, dependencies, tests, vulnerabilities, and policy.

The public release documentation must include a verification procedure rather than merely displaying a supply-chain badge.

## Current external references

Research checkpoint references:

- SPDX specifications: https://spdx.dev/use/specifications/
- SPDX specification repository: https://github.com/spdx/spdx-spec
- CycloneDX specification overview: https://cyclonedx.org/specification/overview/
- SLSA specification/provenance: https://slsa.dev/spec/
- in-toto vetted predicates: https://github.com/in-toto/attestation/tree/main/spec/predicates
- GitHub artifact attestations: https://docs.github.com/en/actions/concepts/security/artifact-attestations
- GitHub artifact-attestation workflow guidance: https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations
- `actions/attest`: https://github.com/actions/attest
- Sigstore signing overview: https://docs.sigstore.dev/cosign/signing/overview/

These references describe upstream capabilities. Their presence does not imply endorsement, certification, or a MeaningWire security-level claim.
