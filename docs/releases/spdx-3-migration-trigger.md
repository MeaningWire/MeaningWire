# SPDX 3 migration trigger

## Decision

**KEEP SPDX 2.3 FOR THE 0.1 PREVIEW LINE. REEVALUATE SPDX 3 WHEN THE MIGRATION CONDITIONS BELOW ARE MET.**

This is a tooling/evidence decision, not a judgment that SPDX 3 is immature as a specification. SPDX 3 is the current SPDX generation, and SPDX 3.0.1 provides a substantially richer RDF-based model, profiles, JSON-LD serialization, structural and semantic validation, and a defined canonical serialization. MeaningWire should adopt those capabilities when the governed release path can prove them at least as strongly as it currently proves SPDX 2.3.

MeaningWire must not migrate merely because a higher specification version exists.

## Current MeaningWire evidence baseline

The current transitional SPDX 2.3 release SBOM path is already governed by deterministic evidence:

- an exact candidate archive is built from an exact Git commit;
- the SBOM is generated deterministically for that candidate;
- the official SPDX 2.3 JSON Schema is fetched from an immutable upstream SPDX commit and its exact Git object identity is verified;
- the generated SBOM is validated structurally against that exact official schema;
- MeaningWire-specific scope, relationship, dependency-lock, and digest policy is validated separately;
- SBOM validation evidence is digest-bound into release evidence;
- the SBOM and archive are rebuilt twice and compared byte-for-byte;
- `SHA256SUMS` binds both artifacts;
- the extracted candidate is exercised in a fresh locked environment;
- release readiness consumes the exact validated SBOM evidence.

A replacement SPDX 3 path must preserve or improve these properties. A migration that weakens deterministic verification, source identity, validation coverage, or reproducibility is not an upgrade for MeaningWire.

## What SPDX 3.0.1 adds

### Model and profiles

SPDX 3 uses an RDF-based extensible data model and separates capabilities into profiles. Core is mandatory; additional profiles include Software, Security, Licensing, Dataset, AI, Build, Lite, and Extension.

For MeaningWire's current release SBOM use case, the relevant starting point is primarily Core + Software, with only additional profiles that correspond to information MeaningWire actually emits and validates.

MeaningWire should not claim conformance to profiles merely because classes from those profiles appear in an output document. Profile-specific restrictions must be validated.

### SBOM model

SPDX 3.0.1 defines `/Software/Sbom` as a concrete BOM collection describing a package and its related SPDX elements. This is a cleaner explicit SBOM concept than treating the whole serialization merely as a version-2-style document inventory.

That is useful, but it also means a migration is a **model migration**, not just changing `spdxVersion` or translating field names.

### JSON-LD and validation

SPDX 3.0.1 defines a JSON-LD representation and publishes:

- a version-specific global JSON-LD context;
- an SPDX JSON Schema for structural validation;
- an SPDX OWL ontology/SHACL model for semantic validation.

The SPDX 3.0.1 serialization specification states that JSON-LD conformance involves both structural validation against the JSON Schema and semantic validation against the ontology/SHACL restrictions.

MeaningWire therefore should not replace its current 2.3 schema validation with only a single SPDX 3 JSON Schema check and call the migration equivalent. A governed v3 path should prove both structural and semantic validation for the selected profiles.

### Canonical serialization

SPDX 3.0.1 specifies a canonical JSON serialization intended to be normalized, deterministic, and reproducible, including ordering and whitespace rules.

This is directly aligned with MeaningWire's evidence model. However, specification-level canonicalization is only useful to the release pipeline once the chosen generator/serializer can reliably produce or normalize that representation and MeaningWire can prove byte-identical output in CI.

## Current tooling evidence

### Python SPDX tools

The SPDX `tools-python` project remains a strong and relevant ecosystem signal for MeaningWire because MeaningWire's governed release tooling is currently Python-based.

Its published documentation describes full validation support for SPDX 2.2/2.3, while its SPDX 3 support is described as experimental and not yet complete/stable. The v3 subpackage can create elements/payloads, convert some v2 documents to v3, and serialize JSON-LD, but the project documentation still distinguishes this from the mature v2 validation path.

This alone is sufficient reason not to replace MeaningWire's currently proven 2.3 validator with `tools-python` v3 generation today.

MeaningWire is not required to use `tools-python` for SPDX 3, but any alternative would need equivalent licensing, maintenance, deterministic behavior, locked dependency support, generation, and complete validation evidence.

### SPDX 3 validation tooling

Current SPDX 3 model documentation describes two complementary validation mechanisms:

1. JSON Schema structural validation; and
2. SHACL semantic validation.

It references tooling including `spdx3-validate`, `ajv`, `check-jsonschema`, and `pyshacl`. This demonstrates that a local automated validation path exists in principle.

For MeaningWire, availability is not enough. Before migration, the chosen path must be pinned, reproducible, dependency-audited, appropriately licensed, stable enough for CI, and tested against positive and negative MeaningWire fixtures.

### GitHub ecosystem signal

GitHub's current Dependency Graph SBOM export API still documents an SPDX 2.3 response. GitHub's current SBOM-generation guidance also highlights actions that produce SPDX 2.2-compatible output, and dependency-submission examples remain oriented around SPDX 2.x or translated snapshot data.

MeaningWire does not require GitHub's dependency graph to dictate its release format. However, this is useful ecosystem evidence that moving to SPDX 3 would currently reduce alignment with common GitHub-native SBOM examples rather than improve it.

GitHub artifact/SBOM attestation can remain conceptually separate from the SBOM format: the important release requirement is that the exact validated SBOM bytes and exact released subject digest are bound correctly. Format migration therefore does not need to be rushed to unlock future attestation design.

## Migration conditions

MeaningWire should reevaluate migration only when **all applicable conditions** below can be demonstrated on an isolated branch without weakening the current 2.3 path.

### 1. Stable specification target

- A specific SPDX 3.x version is selected and pinned.
- Its official model, JSON Schema, JSON-LD context, ontology/SHACL shapes, and canonical-serialization requirements can be bound to immutable upstream identities or cryptographic digests.
- MeaningWire does not consume mutable `latest`, `main`, or `develop` specification artifacts in governed validation.

### 2. Complete local validation

- Structural validation is enforced against the exact selected official JSON Schema.
- Semantic/profile validation is enforced against the exact selected official ontology/SHACL rules or another equivalently authoritative validator.
- The selected Core/Software profile conformance boundary is explicit.
- Negative fixtures prove that structural and semantic/profile failures are rejected.

### 3. Deterministic serialization

- The chosen generator/serializer emits a canonical representation directly or MeaningWire has a separately justified canonicalization step faithful to the SPDX specification.
- Two independent same-source builds are byte-identical for the SBOM.
- Array/object ordering and identifier generation are deterministic.
- No timestamps, UUIDs, environment paths, dependency traversal order, or network response ordering can silently perturb governed output.

### 4. Generator maturity

- The chosen SPDX 3 generation library/tool no longer describes the required MeaningWire feature set as experimental/incomplete, **or** MeaningWire has independently proven and bounded the exact subset it uses strongly enough to justify adoption despite that label.
- Required features have maintained releases and usable changelogs/security posture.
- The dependency graph can be locked with exact versions/hashes under the governed validation target.
- License terms are compatible with MeaningWire's public build and redistribution requirements.

### 5. MeaningWire semantic parity

A generated v3 SBOM must preserve at least the evidence MeaningWire currently records for:

- the released candidate artifact;
- governed validation dependencies;
- package identities and versions;
- package URLs or other stable external identifiers where applicable;
- relationships between the candidate/project and dependencies;
- declared SBOM scope;
- source/version provenance;
- exact artifact/SBOM digest bindings in external release evidence.

A v2-to-v3 converter is not sufficient proof of semantic parity by itself.

### 6. Release-pipeline parity

The v3 prototype must pass the same release controls as v2.3:

- deterministic candidate build;
- deterministic SBOM build;
- official upstream validation identity;
- MeaningWire-specific SBOM policy validation;
- SHA-256 evidence;
- extracted-candidate verification;
- release-readiness evaluation;
- non-publication state;
- future attestation subject/digest compatibility.

The migration should be reversible until a public release has adopted the new format.

### 7. Consumer/ecosystem check

Before first publication in SPDX 3, verify current behavior of the intended consumer/tool set, including at minimum:

- GitHub release/attestation verification path used by MeaningWire;
- at least one independent SPDX 3 validator other than the generator itself;
- ordinary JSON/JSON-LD inspection tooling used in troubleshooting;
- any repository/security tooling MeaningWire publicly documents as able to consume the SBOM.

GitHub Dependency Graph support for SPDX 3 is desirable but not mandatory unless MeaningWire chooses to promise that integration. If GitHub still exports/accepts primarily SPDX 2.x, the release notes must state that boundary truthfully.

## Prototype gate for a future reevaluation

A future SPDX 3 reevaluation should begin as an isolated **dual-output experiment**:

```text
same exact candidate source
├── governed SPDX 2.3 evidence (unchanged control)
└── experimental SPDX 3.x evidence (candidate replacement)
```

Do not replace the 2.3 output at the start of the experiment.

The experiment should compare:

- represented packages/components;
- relationships;
- identifiers;
- scope;
- validator coverage;
- deterministic bytes;
- dependency/tooling burden;
- external-consumer behavior;
- failure diagnostics.

Only after the SPDX 3 lane satisfies the migration conditions should a separate PR propose changing the governed release format.

## Current conclusion

For MeaningWire `0.1.0-alpha.0` and the initial preview line:

**SPDX 2.3 remains the governed transitional SBOM format.**

SPDX 3.0.1 is technically compelling and should remain the planned future direction, especially because its profile model, semantic validation, and canonical serialization align well with MeaningWire's evidence-first architecture. The present constraint is not the standard itself; it is proving an end-to-end generator + canonicalization + structural/semantic validator + ecosystem path with evidence at least as strong as the existing 2.3 implementation.

This decision should be revisited when the tooling and integration evidence materially changes, not on a calendar deadline.

## Authoritative references

- SPDX specifications/current version: https://spdx.dev/use/specifications/
- SPDX 3.0.1 model and serializations: https://spdx.github.io/spdx-spec/v3.0.1/serializations/
- SPDX 3.0.1 SBOM class: https://spdx.github.io/spdx-spec/v3.0.1/model/Software/Classes/Sbom/
- SPDX 3 model validation guidance: https://github.com/spdx/spdx-3-model/blob/develop/serialization/jsonld/validation.md
- SPDX tools-python: https://github.com/spdx/tools-python
- GitHub SBOM REST API: https://docs.github.com/en/rest/dependency-graph/sboms
- GitHub SBOM export/generation guidance: https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/establish-provenance-and-integrity/export-dependencies-as-sbom

These sources are informative evidence for this migration decision. The executable governed path must pin exact upstream objects/digests when it later consumes specification artifacts; documentation URLs alone are not sufficient release validation identity.
