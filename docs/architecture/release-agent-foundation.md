# Release Agent Foundation

MeaningWire's first release-agent capability is deliberately non-publishing. Its job is to prove that a candidate can be built reproducibly from an exact public Git commit and retained with enough evidence to audit what was built.

It does **not** create a GitHub Release, create or push a tag, publish a package, update a website, announce a release, purchase a service, or change a downstream project.

## Canonical version source

`VERSION` is the repository's single pre-release software-version source.

The current version is `0.1.0-alpha.0`. The `alpha` prerelease identifier is intentional: it identifies build output without claiming a stable or publicly launched release.

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

This is a demonstrated Linux/CPython build property, not yet a claim of reproducibility across every operating system or every future Python implementation.

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

## External release evidence

The build output directory also contains:

- `SHA256SUMS` — SHA-256 for the candidate archive;
- `release-evidence.json` — source commit, version, archive digest, embedded-manifest digest, file count, and explicit non-publication state.

These files are evidence for a candidate build, not a signature or third-party attestation.

## GitHub Actions workflow

`.github/workflows/release-candidate.yml` is manual-only (`workflow_dispatch`). It:

1. checks out the exact selected ref;
2. installs the pinned public validation dependency;
3. runs contract validation, the CLI proof, and deterministic unit tests;
4. builds the candidate twice from the exact Actions commit;
5. requires the two archives, checksum files, and evidence files to be byte-identical;
6. retains one verified candidate set as a GitHub Actions artifact.

The workflow has read-only repository permissions. Artifact upload is workflow-output retention, not release publication.

## Publication boundary

A future publishing workflow must be a separate capability. Before it is enabled, MeaningWire should explicitly define:

- release approval authority;
- tag/version relationship;
- release-note generation and review;
- signing / provenance strategy;
- SBOM expectations;
- package-registry behavior, if any;
- rollback and revocation behavior;
- the exact transition from candidate evidence to a public GitHub Release.

Until that later boundary is approved and implemented, the release agent stops at a verified retained candidate artifact.
