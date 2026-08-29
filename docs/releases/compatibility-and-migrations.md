# Compatibility and Migration Policy

Status: **PRE-RELEASE POLICY**

MeaningWire is still in initial development. The current repository version, `0.1.0-alpha.0`, identifies a candidate line and does not claim stable compatibility, production readiness, or a published release.

MeaningWire uses Semantic Versioning syntax as its version vocabulary. Before `1.0.0`, compatibility expectations are intentionally narrower than a stable-release promise. Breaking changes may still occur as the model is validated. That flexibility does not permit silent or unexplained breakage.

## Core rule

**Pre-1.0 means change is possible; it does not mean surprise is acceptable.**

For any public preview release, a user-visible incompatible change should be:

1. classified as breaking;
2. described in the changelog and release notes;
3. tied to the affected compatibility surface;
4. accompanied by a practical migration note when migration is possible;
5. covered by updated deterministic tests and examples;
6. reflected in generated reference documentation when canonical data changes;
7. associated with a new version before publication.

## Compatibility surfaces

MeaningWire does not treat compatibility as one undifferentiated promise. Each surface can mature independently.

### Canonical schemas

Examples: envelope, reference, provenance, authority, Identity / Party.

Potentially breaking changes include:

- removing or renaming a property;
- changing a property's meaning;
- changing a type incompatibly;
- making an optional property required;
- narrowing an allowed enum or validation range;
- changing identifier semantics;
- changing authority or provenance semantics in a way that alters interpretation;
- changing a schema ID without an explicit replacement path.

Usually compatible or additive changes include adding an optional property or broadening accepted values, but even additive changes must be evaluated for downstream assumptions such as exhaustive enum handling or `additionalProperties` behavior.

Schema compatibility must be reasoned about from actual validation behavior, not merely from JSON shape.

### Mapping definitions and relationship semantics

Potentially breaking changes include:

- changing source or target contract identity;
- changing source or target path;
- changing relationship classification;
- changing transform kind or semantics;
- changing loss behavior;
- changing mapping identity or version resolution behavior;
- turning deterministic unique selection into ambiguous or implicit selection.

A mapping that changes semantic meaning should normally receive a new mapping version rather than silently changing an existing published definition.

### Mapping execution behavior

Potentially breaking changes include:

- changing which path syntax is accepted;
- changing error or fail-closed behavior;
- changing transform execution semantics;
- changing provenance emitted by a transformation;
- introducing implicit mapping selection where exact selection was previously required;
- changing treatment of unsupported, lossy, or ambiguous mappings.

Expanding the supported path subset may be additive, but existing paths must continue to produce the documented result for a compatible release line.

### CLI

Potentially breaking changes include:

- removing or renaming a command, subcommand, flag, or positional argument;
- changing exit-code meaning;
- changing machine-readable JSON field meaning or removing fields;
- changing default behavior in a way that can alter results;
- changing output from local-only to network-active behavior without an explicit command boundary;
- changing an operation from read-only to write-capable without a new explicit contract.

Human-readable text output is less stable than JSON output, but release notes should still call out material changes that affect documented examples or automation.

### Adapter SDK

Potentially breaking changes include:

- changing required adapter methods or result shapes;
- changing exception/error contracts;
- changing record-order or transaction semantics;
- changing read-only/write-capability boundaries;
- changing how source identity, provenance, or authority metadata must be supplied.

The SDK remains experimental until a published release explicitly assigns it a stronger maturity level.

### Release candidate artifact and evidence format

Potentially breaking changes include:

- changing archive layout;
- removing required evidence files;
- changing checksum or manifest semantics;
- changing `release-evidence.json` fields incompatibly;
- changing the interpretation of `source_commit`, artifact digest, or publication state.

These formats exist so builds can be audited. Changes that weaken traceability or make provenance ambiguous are not considered routine compatibility changes; they require explicit review.

### Documentation and generated references

Editorial wording may change without a version bump. Documentation becomes compatibility-relevant when it defines a public contract, command, migration requirement, or support boundary.

Generated schema and mapping references are derived presentation artifacts. Canonical JSON remains authoritative when a discrepancy is found; CI should prevent such drift from reaching `main`.

## Change classes

Every material user-visible change should fit one of these classes.

### Additive

Adds capability without intentionally invalidating documented existing behavior.

Examples:

- new optional schema field;
- new independent schema;
- new mapping identity;
- new CLI command;
- new reference adapter;
- additional generated reference information.

Additive does not automatically mean risk-free. Tests should establish that previously supported behavior is unchanged.

### Corrective

Fixes behavior that contradicted the documented contract or deterministic test evidence.

A corrective change can still be disruptive. If users could reasonably have depended on the old behavior, release notes should explain both the defect and the corrected behavior.

### Breaking

Requires a consumer, integration, fixture, invocation, or interpretation to change in order to preserve equivalent behavior.

During alpha, breaking changes are permitted, but they must not be hidden inside a generic "cleanup" or "refactor" description.

### Security-sensitive

Changes authentication, authorization, secret handling, provenance integrity, execution trust, dependency trust, or vulnerability exposure.

Security-sensitive changes may also be additive, corrective, or breaking. Security classification does not replace compatibility classification.

### Internal-only

Changes implementation detail without changing a documented public contract or observable supported behavior.

Internal-only should be used narrowly. A refactor that changes JSON output order, archive bytes, exit behavior, or evidence fields is not purely internal if those outputs are part of tested public behavior.

## Migration-note requirements

A breaking change should include a migration note containing, when applicable:

- **Affected surface** — schema, mapping, executor, CLI, SDK, artifact/evidence, or another named surface;
- **Before** — the previous documented behavior;
- **After** — the new behavior;
- **Why** — the reason for the incompatibility;
- **Action** — the minimum consumer change required;
- **Detection** — how a consumer can identify affected data/configuration/code;
- **Fallback** — any temporary compatibility path, if one exists;
- **Evidence** — tests, fixtures, schema IDs, mapping versions, or commands that demonstrate the change.

If no automated migration exists, say so explicitly. Do not imply a compatibility shim exists when it does not.

## Version progression before 1.0

The project may use prerelease identifiers such as `alpha`, `beta`, or `rc` to communicate increasing release readiness.

The intended meaning is:

- **alpha** — architecture and contracts are usable for evaluation but material changes remain expected;
- **beta** — intended preview behavior is largely present, with compatibility hardening underway;
- **rc** — release candidate for a defined preview/stable target; changes should primarily address release-blocking defects;
- **1.0.0** — only after the project deliberately defines which public compatibility surfaces are stable and has evidence supporting those commitments.

These labels describe MeaningWire's intended process, not universal definitions imposed on other projects.

## Contract maturity versus software version

Repository/software version and individual contract maturity are related but distinct.

A MeaningWire candidate can contain contracts labeled `EXPERIMENTAL` even when the repository has a versioned release. A later repository release does not automatically promote every contained contract to `PREVIEW` or `STABLE`.

Contract maturity changes must be explicit in the contract metadata and documentation.

## Deprecation

Before stable compatibility is promised, deprecation periods may be short, but the project should still prefer an explicit progression when practical:

1. mark the old surface deprecated;
2. document the replacement;
3. provide migration guidance;
4. keep deterministic evidence for both during the overlap when feasible;
5. remove the old surface only in a version whose release notes identify the removal as breaking.

Security defects or severe correctness problems may justify immediate removal. In that case the release notes should state why an ordinary deprecation window was unsafe or misleading.

## What `0.1.0-alpha.0` currently guarantees

Only what is directly supported by the public repository and deterministic evidence on the exact commit being evaluated.

At the current baseline this includes, among other tested behavior:

- local validation of registered public schemas;
- deterministic registry inspection;
- fail-closed exact mapping selection for the implemented path;
- the bounded simple-member mapping behavior used by the pinned synthetic proof;
- read-only JSON object and JSON Lines reference adapters;
- the documented CLI health/inspection/validation/proof commands;
- deterministic candidate archive creation in the tested Linux / CPython environment;
- checksum, manifest, and release-evidence generation;
- fresh-environment execution of the extracted candidate in the tested CI environment;
- generated schema/mapping reference drift detection.

This list is evidence-oriented, not a warranty or production-support commitment.

## What it does not guarantee

The current pre-release line does not guarantee:

- production readiness;
- vendor certification or compatibility;
- stable schema, CLI, SDK, or mapping APIs;
- full JSONPath or arbitrary expression support;
- authenticated remote integration;
- write-back behavior;
- cross-platform reproducible archives on every OS/interpreter/toolchain;
- long-term support duration;
- backward compatibility across all future alpha versions;
- automatic migration between breaking pre-release changes.

## Release-notes requirement

Before a public preview release is published, its release notes should use the repository release-note template and identify:

- exact version and source commit;
- maturity and intended audience;
- verified artifacts/evidence;
- supported behavior;
- breaking changes;
- migration instructions;
- known limitations;
- security-relevant changes;
- compatibility claims that have actual evidence;
- explicit non-claims.

A release should not be published merely because an archive can be built. Publication remains a separate human-authority boundary.
