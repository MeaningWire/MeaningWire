# Release-only attestation path

MeaningWire plans to use cryptographic artifact attestations as **release evidence**, not as a substitute for review, testing, authorization, or security assurance.

This document defines the intended future attestation contract. It is design evidence only. The current repository does **not** execute a public artifact or SBOM attestation, does not request GitHub OIDC for release signing, and does not create a Sigstore transparency-log signing event.

## Current state

- Candidate artifacts and the transitional SPDX 2.3 SBOM are built deterministically from an exact public Git commit.
- Candidate and SBOM SHA-256 digests are already recorded in release evidence and `SHA256SUMS`.
- The non-publishing publication preflight binds a proposed release to exact source/version/tag/title/candidate evidence while preserving human release authorization as `PENDING`.
- Publication capability remains `BLOCKED` until a separately governed publication path and release-only attestation path are implemented and validated.

## Intended attestation subjects

The future release path should attest the exact bytes that are actually published.

### Build-provenance subject

Primary subject:

```text
MeaningWire-<version>.tar.gz
```

The attestation subject digest must equal the SHA-256 already recorded for that archive in the verified release evidence. The publishing workflow must fail closed if the artifact digest changes between candidate verification and attestation.

### SBOM attestation

The SPDX SBOM describes the candidate archive plus the governed validation dependency environment. A future SBOM attestation should therefore use the released candidate archive as the subject and the exact validated:

```text
MeaningWire-<version>.spdx.json
```

as the SBOM input. The SBOM file digest must match the digest already bound by release evidence and `SHA256SUMS`.

Attesting the SBOM does not expand its declared scope and does not prove that the artifact is vulnerability-free or secure.

## GitHub identity and permission boundary

GitHub's current artifact-attestation model uses the workflow's OIDC identity and requires, for binary/file artifacts:

```yaml
permissions:
  contents: read
  id-token: write
  attestations: write
```

MeaningWire should grant these permissions only inside the future explicitly governed release workflow/job that performs attestation. Ordinary pull-request validation, branch validation, candidate generation, and publication preflight should remain unable to mint attestations.

If MeaningWire later publishes a container image, additional registry/package permissions would be a separate design decision; they are not part of the current file-artifact preview path.

## Identity that verifiers should bind

Verification should establish more than a matching digest. Consumers should be able to bind the attestation to the expected MeaningWire repository and GitHub Actions identity, including the repository/workflow provenance recorded by the attestation.

The future verification guide should require the expected repository owner/repository and, where supported by the verification tooling, constrain signer/workflow identity rather than accepting any cryptographically valid attestation for the same bytes.

A valid signature from an unexpected workflow identity is not sufficient MeaningWire release provenance.

## Verification flow

The future published release should provide instructions equivalent in intent to:

1. download the released artifact and checksum evidence;
2. verify `SHA256SUMS` locally;
3. verify the GitHub artifact attestation for the candidate archive against `MeaningWire/MeaningWire` using GitHub's supported attestation verification tooling;
4. verify the SBOM attestation for that same candidate subject;
5. confirm the attested subject digest equals the digest shown in the release evidence and release notes;
6. inspect the attestation's repository/workflow/source identity rather than treating signature validity alone as sufficient;
7. preserve the distinction between provenance evidence and human release authorization.

Exact CLI syntax should be revalidated against current official GitHub documentation immediately before the first public release rather than being frozen prematurely in this pre-release design document.

## Transparency and privacy boundary

MeaningWire must treat public keyless attestation as an externally observable event.

GitHub artifact attestations use identity-bearing provenance. Sigstore-style keyless signing uses short-lived certificates bound to an OIDC identity and records signing events in transparency infrastructure. A release workflow must therefore assume that public attestation can make repository/workflow identity and signing-event evidence publicly discoverable.

This is intentional for a future public release, but it is also why MeaningWire does not exercise the path during quiet pre-release engineering.

Deletion or revocation mechanisms must not be described as erasing historical transparency evidence unless the relevant platform explicitly guarantees that behavior.

## Fail-closed publication contract

Before a future publisher may invoke attestation, it must establish all of the following from the exact source commit:

- canonical `VERSION` matches the proposed tag and release title;
- deterministic candidate generation passed;
- candidate archive and SBOM digests match verified candidate evidence;
- official SPDX validation passed;
- extracted-candidate proof passed;
- documentation/release-note preflight passed;
- the machine-readable release-readiness evaluator passes with `--require-ready`;
- explicit human public-release authorization has been recorded;
- attestation permissions are scoped only to the release job that requires them;
- the attestation action is immutably pinned to a full commit SHA;
- attestation subjects are the exact artifacts selected for publication.

No attestation step should precede the human release boundary merely to make readiness appear greener.

## Non-claims

A future MeaningWire attestation can provide evidence about artifact identity and build provenance. It does not by itself establish:

- vulnerability-free software;
- semantic correctness;
- external-standard conformance;
- vendor certification;
- production readiness;
- human approval of transformed data;
- universal reproducibility across platforms;
- endorsement by GitHub, Sigstore, or any referenced standards body.

Approval is not transferred.

## Evidence sources and refresh rule

This design is based on the current official GitHub artifact-attestation guidance and Sigstore keyless-signing model. Because actions, permissions, CLI behavior, and verification options can evolve, the executable release workflow must refresh official documentation and pin exact action revisions immediately before implementation or consequential updates.
