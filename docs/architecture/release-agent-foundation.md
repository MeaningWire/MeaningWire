# Release Agent Foundation

MeaningWire's release-agent capability is deliberately staged. Its current job is to prove that a candidate can be built reproducibly from an exact public Git commit, validate its supply-chain evidence, exercise the extracted candidate in a clean environment, and produce a machine-readable release-readiness decision.

It does **not** create a GitHub Release, create or push a tag, publish a package, update a website, announce a release, create a public cryptographic attestation, purchase a service, or change a downstream project.

## Canonical version source

`VERSION` is the repository's single pre-release software-version source.

The current version is `0.1.0-alpha.0`. The `alpha` prerelease identifier is intentional: it identifies candidate output without claiming a stable or publicly launched release.

The CLI reads the same file so build and runtime version strings cannot drift independently without failing tests.

## Exact-commit input boundary

`tools/release_builder.py` builds from Git object contents at the checked-out `HEAD` commit.

It does not copy mutable working-tree bytes into the candidate. For each tracked regular file it reads the blob recorded in the Git tree, records the Git object ID, SHA-256 digest, byte size, and normalized archive mode, and packages those exact bytes.

The builder rejects:

- an expected source commit that does not exactly match `HEAD`;
- paths that are absolute, contain traversal components, or use backslashes;
- symlinks and unsupported special Git file modes;
- a missing or invalid SemVer `VERSION`;
- Git failures or unparseable repository state.

## Deterministic archive

The candidate is a gzip-compressed tar archive named:

```text
MeaningWire-<version>.tar.gz
```

To make repeated builds comparable, archive metadata is normalized:

- files are ordered by repository path;
- modification time is `0`;
- UID and GID are `0`;
- user and group names are empty;
- regular file modes are normalized from the committed Git mode;
- the gzip header uses a fixed timestamp;
- the generated content manifest is deterministic JSON.

The same commit, version, repository tree, Python/tar implementation behavior, and builder code should therefore produce byte-identical candidate archives. CI proves this by building twice and comparing the resulting bytes.

This is a demonstrated Linux/CPython build property, not a claim of reproducibility across every operating system or future Python implementation.

## Embedded content manifest

Each archive contains `RELEASE-MANIFEST.json` under the versioned top-level directory. It records:

- project and version;
- maturity;
- exact source commit;
- every packaged tracked path;
- each file's SHA-256 digest and Git object ID;
- byte size and normalized mode;
- `publication_performed = false`;
- `runtime_network_access = false`.

The manifest intentionally describes the archive's source content. It does not contain the archive's own hash, avoiding a circular digest.

## Locked validation environment

The governed candidate target uses `requirements-validation.lock`, which contains the complete current CPython 3.12 / Linux x86-64 validation dependency graph as exact package versions plus accepted wheel SHA-256 hashes.

Governed CI installs it with `--require-hashes --only-binary=:all:` and then verifies both dependency consistency and installed versions. The same lock is packaged inside the candidate archive and used again in a fresh virtual environment after extraction.

`requirements-validation.txt` remains a direct dependency input for exploratory cross-platform evaluation; it is not the exact governed candidate environment.

## Candidate SBOM

The builder also emits:

```text
MeaningWire-<version>.spdx.json
```

The current SBOM is explicitly transitional SPDX 2.3. Its scope is the exact candidate archive plus the governed locked validation environment.

Candidate validation fetches the official SPDX 2.3 JSON Schema from one immutable upstream SPDX commit, verifies the exact Git blob object identity, validates the SBOM against that schema, and then applies MeaningWire-specific package-scope and digest policy.

Fresh build output records SBOM validation as `PENDING`. Only successful validation may create `spdx-validation-evidence.json` and promote the release evidence to `PASS`.

See [`../releases/candidate-sbom.md`](../releases/candidate-sbom.md) for the exact scope and non-claims.

## External candidate evidence

A verified candidate evidence directory contains:

- `MeaningWire-<version>.tar.gz` — deterministic candidate archive;
- `MeaningWire-<version>.spdx.json` — deterministic transitional SPDX candidate SBOM;
- `SHA256SUMS` — SHA-256 bindings for the archive and SBOM;
- `release-evidence.json` — exact source/version/digests, manifest digest, SBOM identity, validation state, and explicit non-publication/non-attestation state;
- `spdx-validation-evidence.json` — official-schema identity and MeaningWire policy validation evidence;
- `release-readiness.json` — machine-readable release-threshold, launch-experience, and publication-capability status.

These files are candidate evidence. They are not public signatures or third-party attestations.

## Fresh-environment candidate proof

Normal CI and the manual candidate workflow verify the built archive itself rather than relying only on the source checkout that produced it.

The proof:

1. verifies the archive and SBOM against `SHA256SUMS`;
2. extracts the versioned candidate into a fresh directory;
3. creates a new Python virtual environment;
4. installs the exact hashed validation environment from the extracted candidate's `requirements-validation.lock`;
5. runs `pip check` and verifies installed versions against the lock;
6. disables user-site Python packages with `PYTHONNOUSERSITE=1`;
7. runs `meaningwire doctor` from the extracted candidate;
8. runs the pinned interoperability proof from the extracted candidate;
9. validates the synthetic Identity / Party fixture from the extracted candidate.

This demonstrates that the documented public path works from a clean extracted candidate without a `.git` directory, private repository, private package, hidden schema, private fixture, credential, or undocumented MeaningWire service.

Dependency installation and pinned SPDX-schema retrieval use ordinary public internet sources during candidate verification. The MeaningWire runtime proof itself remains local and performs no network access. This is evidence for the tested GitHub-hosted Linux / CPython 3.12 environment, not universal platform compatibility.

## Machine-readable readiness gate

`tools/release_readiness.py` evaluates the verified candidate evidence after the isolated proof.

It separates:

- **release threshold** — candidate/evidence integrity and required public release material;
- **launch experience** — whether the planned locked Starlight documentation build foundation exists;
- **publication capability** — whether a future manual fail-closed publication workflow and public attestation path are implemented.

The gate can report `BLOCKED` or `READY_FOR_HUMAN_DECISION`.

`BLOCKED` is a normal successful evaluation when engineering prerequisites remain. `READY_FOR_HUMAN_DECISION` still does not authorize release: the report always preserves a pending explicit human public-release boundary.

A future publication workflow must invoke the same tool with `--require-ready` so any blocker prevents publication from continuing.

See [`../releases/release-readiness.md`](../releases/release-readiness.md).

## GitHub Actions candidate workflow

`.github/workflows/release-candidate.yml` is manual-only (`workflow_dispatch`). It:

1. checks out the exact selected ref;
2. verifies immutable workflow pins and the hashed dependency lock;
3. installs and verifies the governed validation environment;
4. runs contract validation, public CLI proof, and deterministic unit tests;
5. builds the candidate twice from the exact Actions commit;
6. fetches and verifies the exact official SPDX 2.3 schema object;
7. validates both candidate SBOMs and promotes both release-evidence files to `PASS`;
8. requires the two candidate evidence sets to be byte-identical;
9. verifies candidate checksums and exercises the extracted candidate in an isolated locked environment;
10. generates byte-identical release-readiness reports;
11. stages and retains the verified candidate evidence set as a GitHub Actions artifact.

The workflow has read-only repository permissions. Artifact upload is workflow-output retention, not release publication.

## Publication boundary

A future publishing workflow is a separate capability. Before it may pass the readiness gate, MeaningWire expects an explicitly reviewed publication contract including:

- manual release entry and approval authority;
- fail-closed `--require-ready` enforcement;
- tag/version relationship;
- release-note generation and review;
- public build/SBOM attestation and verification;
- keyless signing/provenance strategy;
- package-registry behavior, if any;
- rollback and revocation behavior;
- the exact transition from retained candidate evidence to a public GitHub Release.

The readiness gate is intentionally designed so the publication workflow cannot declare itself ready merely by existing. Until the remaining launch and publication controls are implemented and explicit human release authorization is granted, the release agent stops at verified retained candidate evidence plus a machine-readable blocker report.
