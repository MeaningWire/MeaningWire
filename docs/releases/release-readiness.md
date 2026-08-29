# Release Readiness Gate

Status: **PRE-RELEASE / NON-PUBLISHING**

MeaningWire uses a machine-readable readiness gate before any future public-release action. The gate answers whether an exact candidate has enough evidence to proceed to a human publication decision. It does not publish, approve, sign, attest, tag, announce, or deploy anything.

The executable gate is:

```text
python tools/release_readiness.py
```

## Two valid outcomes

The gate has two normal report states:

- `BLOCKED` — one or more engineering, launch-experience, or publication-path prerequisites remain;
- `READY_FOR_HUMAN_DECISION` — all machine-evaluated prerequisites pass, but explicit human release authorization is still required.

`BLOCKED` is not a tool failure. It is a successful evaluation that explains why the release agent must continue engineering rather than ask for publication approval.

Malformed, inconsistent, missing, or unsafe candidate evidence is a tool error and exits separately.

## Three readiness layers

The report deliberately separates three questions.

### 1. Release threshold

The mechanical release-threshold section checks the verified candidate evidence set, including:

- explicit prerelease SemVer identity;
- exact source commit;
- candidate archive digest;
- candidate SBOM digest;
- `SHA256SUMS` binding for archive and SBOM;
- SBOM validation `PASS` state and validation-evidence digest binding;
- embedded candidate manifest identity and non-publication state;
- required public implementation, quickstart, compatibility, release, schema, mapping, adapter, and proof material inside the archive;
- explicit candidate non-publication/non-attestation state;
- an assertion that the workflow's isolated extracted-candidate proof completed before the gate ran.

The fresh-environment assertion is meaningful in the governed workflows because the gate step is ordered after the isolated proof. A caller outside that workflow must not set the flag unless equivalent evidence has actually been produced.

### 2. Launch experience

The launch-experience section separates **source presence** from **successful build evidence**.

The candidate must contain the locked Starlight source foundation:

- a `package.json` declaring `@astrojs/starlight`;
- a committed `package-lock.json` in the same site root;
- an Astro configuration file in that site root.

That source check alone does **not** clear launch readiness. The caller must also set:

```text
--documentation-build-verified
```

and may do so only after the governed workflow has:

1. selected the pinned Node runtime from `.node-version`;
2. installed the committed npm graph with `npm ci`;
3. built the static Starlight output;
4. built it again from the same exact source and locked dependency graph; and
5. verified the two complete static output trees are byte-identical.

The current governed documentation toolchain is Node `22.19.0`, npm `10.9.3`, Astro `7.2.9`, and `@astrojs/starlight` `0.41.10`.

The flag is a workflow-order assertion, not a self-certifying property of source files. A caller outside the governed workflow must not set it without equivalent successful build evidence.

A successful build still does not mean the site has been deployed. Public deployment remains a separate action.

### 3. Publication capability

The publication-capability section looks for a future:

```text
.github/workflows/release-publication.yml
```

A publication path is not treated as governed merely because that file exists. The expected minimum contract is:

- manual `workflow_dispatch` entry;
- invocation of `tools/release_readiness.py` with `--require-ready`;
- immutable full-SHA use of `actions/attest` for the future public attestation path;
- `id-token: write` and `attestations: write` only in that explicitly publishing workflow.

Until these controls exist and are reviewed, the report remains blocked for publication.

## Human authority never disappears

Even when the report becomes:

```text
READY_FOR_HUMAN_DECISION
```

it records:

```text
human_boundary.required = true
human_boundary.authority = "explicit public release authorization"
human_boundary.status = "PENDING"
```

The release agent may ask for that authorization only after the machine-evaluated blockers are gone. The readiness tool contains no operation that can satisfy the human boundary itself.

## Normal candidate usage

The governed candidate workflow runs the readiness gate after:

1. exact-commit candidate construction;
2. locked dependency verification;
3. official SPDX schema verification;
4. MeaningWire SBOM policy validation;
5. repeated-build reproducibility checks;
6. checksum verification;
7. isolated extracted-candidate execution; and
8. the locked, repeated, byte-compared Starlight static build.

It writes:

```text
release-readiness.json
```

and retains it with the candidate evidence set.

The normal candidate workflow does **not** use `--require-ready`, because retaining a deterministic `BLOCKED` report is useful evidence while engineering prerequisites remain.

## Future publication usage

A future publication workflow must call the same gate with:

```text
--require-ready
```

In that mode, `BLOCKED` exits nonzero and prevents publication from continuing.

This gives candidate generation and publication one shared definition of readiness rather than maintaining two drifting policy implementations.

## Current expected state

Once the locked documentation build succeeds for the exact candidate, the launch-experience layer should pass while the project remains blocked on the separately governed publication and public-attestation paths:

```text
release_threshold.status = PASS
launch_experience.status = PASS
overall_status = BLOCKED
```

The expected remaining blockers are:

```text
governed_publication_path_not_ready
public_attestation_path_not_ready
```

That is intentional. A working documentation build is evidence of a launch-capable source experience; it is not authorization to deploy, attest, or publish a release.
