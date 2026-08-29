# Supply-Chain Evidence Strategy

Status: **ACCEPTED FOR PREVIEW HARDENING; PUBLIC ATTESTATION NOT YET ENABLED**

MeaningWire should make release integrity independently inspectable without introducing long-lived signing secrets, floating workflow dependencies, or premature public attestation records during quiet pre-release development.

This document records the current supply-chain direction. It does not publish a release, generate a public attestation, create a signing key, or claim a SLSA level.

## Immediate control: immutable GitHub Actions pins

All external GitHub Actions used by MeaningWire workflows must be pinned to a full 40-character commit SHA.

Human-readable version comments remain beside the SHA so reviewers can see which upstream release was intentionally selected.

Current pins:

| Action | Reviewed release | Immutable commit |
| --- | --- | --- |
| `actions/checkout` | `v4.4.0` | `11d5960a326750d5838078e36cf38b85af677262` |
| `actions/setup-python` | `v5.6.0` | `a26af69be951a213d495a4c3e4e4022e16d87065` |
| `actions/upload-artifact` | `v4.6.2` | `ea165f8d65b6e75b540449e92b4886f43607fa02` |

`tools/validate_workflow_pins.py` scans `.github/workflows/*.yml` and `.yaml` and fails CI if an external `uses:` reference is not pinned to a full commit SHA.

A future action update should:

1. identify the intended upstream version from the action's official repository;
2. resolve that version tag to its exact commit SHA;
3. review release notes and breaking/runtime requirements;
4. replace the SHA and adjacent version comment together;
5. require the normal MeaningWire exact-head CI and PR review before merge.

A floating major tag such as `actions/checkout@v4` is not acceptable after this control is merged.

## SBOM direction

MeaningWire intends to publish a machine-readable Software Bill of Materials with a future public release.

### Preferred standards direction

**SPDX 3** is the preferred strategic SBOM family for MeaningWire once an implementation toolchain is proven end to end.

Reasons:

- SPDX is an ISO/IEC standard and the SPDX project lists version 3.0 as its current specification generation;
- the in-toto Attestation Framework now includes a vetted SPDX 3 predicate (`https://spdx.dev/Document/v3`);
- SPDX is directly aligned with software-component, licensing, dependency, and provenance use cases relevant to a public open-source release.

CycloneDX remains a supported interoperability format worth testing. CycloneDX 1.7 is the current published specification as of this decision, while CycloneDX 2.0 has been announced for later in 2026. MeaningWire should avoid adopting a format solely because it is newer; the deciding factor is end-to-end generator, validator, attestation, and consumer interoperability.

### Why SBOM generation is not enabled in this slice

The current public repository has one explicitly pinned top-level Python validation dependency, but the release process does not yet maintain a fully resolved dependency lock with hashes for every transitive installed package.

An SBOM should describe what was actually built or shipped with sufficient precision to be useful. MeaningWire should therefore not create a decorative or incomplete SBOM merely to check a roadmap box.

Before SBOM generation becomes release evidence, the implementation should prove:

1. the dependency input being described is explicit and reproducible;
2. the SBOM generator is itself pinned and auditable;
3. the exact SBOM specification version is explicit;
4. the generated document validates against that specification;
5. repeated generation from the same candidate inputs has understood determinism properties;
6. the SBOM is bound to the exact release artifact digest through the release/attestation process;
7. consumers can verify the result using documented public tooling.

A transitional SPDX 2.3 SBOM is acceptable only if current generator or attestation interoperability requires it and the release notes say so explicitly. It must not be mislabeled as SPDX 3.

## Provenance direction

SLSA 1.2 is the current SLSA specification generation at this research checkpoint.

MeaningWire's existing release evidence already records exact source commit and artifact digests, but that file is project-generated evidence rather than a cryptographically signed third-party attestation.

For a future public release, the preferred next layer is a standard SLSA build-provenance attestation bound to the published artifact digest.

MeaningWire does **not** currently claim SLSA Build Level 1, 2, 3, or any other level. A level should be claimed only after the complete requirements for that level have been evaluated and evidenced.

## Attestation and signing direction

GitHub's current consolidated `actions/attest` action supports:

- automatically generated build provenance;
- SBOM attestations from SPDX or CycloneDX JSON;
- custom attestation predicates.

The older `actions/attest-sbom` action is deprecated in favor of `actions/attest` and should not be introduced into MeaningWire.

GitHub artifact attestations use Sigstore. For public repositories, GitHub uses the Sigstore Public Good Instance and the resulting signing event is associated with a publicly readable transparency log.

That public transparency property is desirable for an actual public release, but it also means creating an attestation is more consequential than producing an ephemeral internal candidate artifact.

Therefore:

- the quiet pre-release candidate workflow does **not** request `id-token: write` or `attestations: write`;
- it does **not** invoke `actions/attest`;
- it does **not** create a public Sigstore transparency-log entry;
- enabling public artifact/SBOM attestations belongs to the separately governed publication path.

## Key management

MeaningWire should prefer identity-based/keyless signing through GitHub Actions OIDC + Sigstore for public release artifacts rather than creating a long-lived private signing key stored as a repository secret.

Keyless signing binds an ephemeral signing key to an authenticated identity and records verification material in the transparency system. This reduces the operational burden and compromise risk associated with maintaining a persistent release-signing private key.

A self-managed signing key should be introduced only if a concrete interoperability or governance requirement cannot be met with keyless signing.

## Candidate evidence versus published attestation

The project deliberately separates two stages.

### Quiet pre-release candidate evidence

Current candidate evidence may include:

- exact source commit;
- deterministic archive;
- embedded release manifest;
- SHA-256 artifact digest;
- machine-readable release evidence;
- repeated-build byte comparison;
- isolated extracted-candidate execution;
- CI run identity;
- immutable workflow action pins.

These checks do not create a public release or external cryptographic attestation.

### Future public-release evidence

Subject to release authorization and completed implementation, a public release should add:

- validated SBOM in an explicitly named specification/version;
- build-provenance attestation bound to the release artifact digest;
- SBOM attestation bound to the same artifact;
- keyless Sigstore/GitHub identity evidence;
- documented verification commands;
- release notes containing exact artifact and evidence references.

## Verification-first rule

An attestation is useful only if consumers can verify it and understand what policy it proves.

MeaningWire should not present an attestation as proof that software is secure. It proves facts about provenance/integrity and signing identity; consumers still need to evaluate the source, workflow, dependencies, tests, and policy.

The public release documentation must include a verification procedure rather than merely displaying a supply-chain badge.

## Current external references

Research checkpoint references:

- SPDX specifications: https://spdx.dev/use/specifications/
- CycloneDX specification overview: https://cyclonedx.org/specification/overview/
- SLSA specification/provenance: https://slsa.dev/spec/
- in-toto vetted predicates: https://github.com/in-toto/attestation/tree/main/spec/predicates
- GitHub artifact attestations: https://docs.github.com/en/actions/concepts/security/artifact-attestations
- GitHub artifact-attestation workflow guidance: https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations
- `actions/attest`: https://github.com/actions/attest
- Sigstore signing overview: https://docs.sigstore.dev/cosign/signing/overview/

These references describe upstream capabilities. Their presence does not imply endorsement, certification, or a MeaningWire security-level claim.
