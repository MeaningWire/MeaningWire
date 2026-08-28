# RFC 0001 — Core Semantic Primitives

- **Status:** DRAFT
- **Maturity:** EXPERIMENTAL
- **Target:** first technical MVP slice
- **Contract version:** 0.1.0

## Summary

Define the smallest machine-readable MeaningWire primitives needed before domain-specific schemas are useful: vendor-independent references, provenance, authority and approval semantics, a generic canonical envelope, explicit mapping relationships, a schema registry, and deterministic bootstrap validation.

These contracts are experimental. This RFC does not declare production readiness, stable compatibility, or a public release.

## Problem

Interoperability fails when systems move values without preserving what those values mean, where they came from, how they were transformed, or who had authority to approve consequential decisions.

MeaningWire therefore needs a small semantic substrate before it adds business-domain schemas.

## Reference

A MeaningWire reference contains `namespace` and `id`, with optional `version`. This deliberately does **not** choose UUIDv7, ULID, or another universal identifier format. Existing systems can preserve identifiers behind explicit namespaces while project-native identifier guidance is evaluated separately.

## Provenance

Provenance identifies the source reference and may record source version, observation time, and an ordered transformation history. Transformations may identify the mapping used, the actor/system that performed the transformation, and when it occurred.

## Authority

Authority is represented independently from data content.

Initial authority kinds are `source_authority`, `human_authority`, `system_authority`, `model_inference`, and `none`.

Approval state is `approved`, `rejected`, or `not_asserted`. Only `human_authority` may assert `approved` or `rejected` in this initial contract. `model_inference` must use `not_asserted` and include a confidence value from 0 to 1.

This is intentionally conservative: model output may inform a workflow, but it cannot silently become human approval.

## Canonical envelope

The envelope binds a contract reference, record reference, canonical `data`, provenance, authority, and maturity. It is transport-neutral and does not define business-domain fields.

## Mapping relationships

The mapping contract preserves the vocabulary `exact`, `equivalent`, `broader`, `narrower`, `derived`, `transformed`, `lossy`, and `unsupported`. A `lossy` mapping must document `loss_notes`.

Mappings identify source and target contract references and paths, carry provenance, have an explicit version, and carry a maturity state.

## Versioning and schema identifiers

The initial contract version is `0.1.0` with maturity `EXPERIMENTAL`. Breaking changes are expected while experimental, but versions still change so evidence can identify what it exercised.

Schemas use project-scoped URNs such as `urn:meaningwire:schema:core:reference:0.1.0`. `schemas/registry.json` binds URNs to repository-relative paths, avoiding dependence on an unpurchased domain or hosting URL.

## Validation

The first validator is intentionally dependency-free. It verifies registry/schema metadata consistency, checks the core semantic invariants, and executes valid and invalid fixtures deterministically.

It is **not** presented as a complete JSON Schema Draft 2020-12 implementation. A standards-compliant JSON Schema engine can be added later without changing the semantic rules.

## Security and privacy

Provenance and authority metadata can themselves contain sensitive identifiers. Implementations should minimize unnecessary personal data and should not treat provenance as permission to expose source-system details publicly.

Authority metadata must not be used to fabricate human approval.

## Alternatives considered

- Adopting one vendor's IDs/object model was rejected because it would make the canonical core vendor-shaped.
- Choosing UUIDv7 or ULID immediately was deferred because the first primitive only needs namespaced references.
- Collapsing provenance and authority was rejected because source lineage and decision authority answer different questions.
- Treating all mappings as generic transforms was rejected because equivalence, broadening/narrowing, transformation, loss, and unsupported concepts have different interoperability consequences.

## Open questions

- Should MeaningWire recommend UUIDv7, ULID, or another format for project-native generated IDs?
- Which maturity transitions require compatibility guarantees?
- How should contract URNs resolve in SDKs and registries?
- Which provenance fields become required for released adapters?
- Should non-human system authority ever represent a formal approval class, and if so under what explicit governance?

## Acceptance criteria

The associated implementation is ready for review when schema files parse, registry IDs/paths are unique and consistent, valid fixtures pass, invalid authority and lossy-mapping fixtures fail for the expected reasons, deterministic tests pass without third-party dependencies, no downstream repository is modified, and no production-readiness or adoption claim is introduced.
