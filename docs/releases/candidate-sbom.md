# Candidate SBOM Evidence

Status: **PRE-RELEASE / TRANSITIONAL SPDX 2.3**

MeaningWire release-candidate builds produce a deterministic Software Bill of Materials as part of candidate verification. This is supply-chain evidence for the current pre-release candidate process; it is not a public release, attestation, certification, production-readiness claim, or claim that every component of the build host has been inventoried.

## Format decision

The current candidate SBOM is emitted as **SPDX 2.3 JSON**.

MeaningWire prefers SPDX 3 as the longer-term direction, but the project does not label current evidence as SPDX 3 until the generator, validator, attestation, and consumer path is proven end to end. The SPDX 2.3 artifact is therefore explicitly transitional.

## Exact scope

The candidate SBOM describes:

1. the exact `MeaningWire-<version>.tar.gz` candidate archive; and
2. the complete six-package Python validation environment in `requirements-validation.lock` for the governed CPython 3.12 / Linux x86-64 target.

The root MeaningWire package is bound to the candidate archive SHA-256. Each locked Python package is represented at its exact version, with its accepted target wheel SHA-256 and a Package URL (`purl`).

The SBOM deliberately does **not** claim to inventory:

- the Ubuntu/GitHub-hosted runner operating system;
- GitHub Actions runner internals;
- Git itself;
- Python interpreter implementation files;
- transient system libraries;
- unrelated tools that are not part of the locked candidate validation dependency set;
- another operating system, CPU architecture, or Python generation.

This narrow scope is intentional. An accurate bounded inventory is preferable to a broad inventory that implies evidence the project does not possess.

## Determinism

`tools/release_builder.py` emits:

```text
MeaningWire-<version>.tar.gz
MeaningWire-<version>.spdx.json
SHA256SUMS
release-evidence.json
```

The SBOM uses:

- the exact Git source commit as part of its document namespace;
- the exact Git commit timestamp as its deterministic creation timestamp;
- the candidate archive SHA-256 for the root MeaningWire package;
- package versions and accepted wheel SHA-256 values from `requirements-validation.lock`.

CI builds the candidate twice from the same exact commit and requires the archive, SPDX document, checksums, SBOM validation evidence, and promoted release evidence to be byte-identical.

## Official SPDX schema validation

MeaningWire does not vendor the upstream SPDX schema into the Apache-2.0 repository.

Candidate CI fetches the official SPDX 2.3 JSON Schema from the SPDX specification repository at the immutable upstream source identity:

```text
repository: spdx/spdx-spec
commit: 44ab76293754df4af5af700fd4abd5453b866c86
path: schemas/spdx-schema.json
Git blob SHA-1: 0ca1c7b56bebb10fb637285698e401342b4910d6
upstream license: CC-BY-3.0
```

`tools/fetch_spdx_schema.py` computes the Git blob object identifier over the downloaded bytes and fails unless it equals the pinned blob above. The downloaded schema is then used locally for JSON Schema validation and is not retained as a MeaningWire release artifact.

## MeaningWire policy validation

Passing the official SPDX schema is necessary but not sufficient.

`tools/validate_spdx_sbom.py` also fails closed unless the document:

- declares `SPDX-2.3` and `CC0-1.0` document data licensing;
- binds its namespace to the exact candidate version and source commit;
- describes exactly one MeaningWire root package plus the complete current locked validation package set;
- binds the root package to the exact candidate archive SHA-256;
- records the MeaningWire root package license as Apache-2.0;
- records each dependency at its locked name/version, accepted SHA-256, and expected PyPI purl;
- has no extra or missing package records inside the declared scope;
- records root `DEPENDS_ON` relationships for the exact locked package set.

The dependency relationships are intentionally flattened. The SBOM records the governed validation environment required by the candidate; it does not claim that every listed package is a direct Python dependency of MeaningWire.

## Validation evidence lifecycle

A freshly built `release-evidence.json` records SBOM validation as `PENDING`.

After the candidate SBOM passes both the exact official SPDX schema and MeaningWire policy validation, CI writes:

```text
spdx-validation-evidence.json
```

and promotes the SBOM validation state in `release-evidence.json` to `PASS`.

The promoted release evidence records the SHA-256 of the validation-evidence file plus the exact upstream SPDX repository, commit, path, and Git blob identity used for validation. Candidate evidence is not considered SBOM-verified while the state remains `PENDING`.

## Candidate checksum verification

`SHA256SUMS` covers both the candidate archive and SPDX document. From the verified candidate evidence directory:

```text
sha256sum -c SHA256SUMS
```

must succeed before the candidate evidence is accepted by the workflow.

The validation-evidence digest is bound separately inside the promoted `release-evidence.json` because it is produced after official-schema validation.

## What this proves

A successful candidate run provides evidence that:

- the SBOM was generated deterministically from the exact candidate and dependency lock;
- the document conformed to the pinned official SPDX 2.3 JSON Schema at validation time;
- the document also passed MeaningWire's narrower scope and digest policy;
- the candidate archive and SBOM checksums match the retained evidence;
- repeated candidate generation from the same commit produced byte-identical evidence in the tested environment.

## What this does not prove

It does not prove that:

- the software is secure or vulnerability-free;
- the SBOM covers the complete runner operating system;
- dependency licenses have undergone independent legal review;
- the current SPDX 2.3 format is the project's permanent SBOM format;
- a SLSA level has been achieved;
- the artifact has been cryptographically attested or signed;
- Sigstore or another transparency log has been written;
- a GitHub Release, package, site, or public preview has been published.

Public cryptographic build/SBOM attestations remain part of the separately governed release-publication path.
