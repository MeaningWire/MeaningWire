# MeaningWire Substrate Hypothesis v0.1

**Status:** RESEARCH / PROVISIONAL — not a stable contract

## Purpose

Record the results of the first cross-domain ontology and schema-translation stress tests. This document captures a research hypothesis; it does not claim that the proposed substrate is a universal ontology of reality or a replacement for established standards.

## Research question

Can a small common representational substrate describe and translate heterogeneous things and schemas across physical, biological, social, informational, computational, musical, evidential, and organizational domains without silently losing essential semantics?

## Current hypothesis

The smallest candidate substrate identified so far is:

1. **DISTINCTION** — establishes a distinguishable referent.
2. **RELATION** — connects referents through typed relationships.
3. **ORDER** — locates distinctions and relations in sequence, time, space, dependency, hierarchy, simultaneity, version, or other ordered dimensions.
4. **REFERENCE FRAME** — identifies the frame, perspective, model, scope, jurisdiction, definition, observer, or other conditions under which a distinction or relation is interpreted.

We intentionally use **REFERENCE FRAME** rather than treating "context" as a primitive. Context may be constructed from structured reference information and relevant relations.

## Derived structures under investigation

The following currently appear representable as specialized structures/relations rather than foundational primitives:

- entity / identity
- boundary
- containment
- state
- change
- process
- causation
- membership
- ownership
- probability
- uncertainty
- meaning
- truth status
- contradiction
- memory
- knowledge
- agency
- emergence
- holarchy / whole-part organization
- provenance

This is a hypothesis and remains open to falsification.

## Stress test results

### Stress Test 1 — nested organized existence

Initial comparison included cell, human, family/social group, ecosystem, and artificial computational agent.

Result: a recurring structure of boundary, components, relationships, state, processes, environment, and feedback was observed.

Key finding: **"container" is too narrow to serve as a universal primitive.**

### Stress Test 2 — physical → informational → social → cosmic

Test cases included atom, rock, river, hurricane, concept, family, city, computer/network, planet, galaxy, and universe-scale representations.

Result: the candidate structure remained usable across domains, but boundaries had to be allowed to be physical, functional, social, informational, analytical, or model-relative.

Key finding: **containment is better represented as a typed relation than as a foundational primitive.**

### Stress Test 3 — heterogeneous things

Test cases:

- physical object
- living organism
- thought
- song
- legal institution
- mathematical concept
- memory
- knowledge artifact
- artificial agent
- civilization

Result: the same candidate primitives could represent all ten at a structural level.

Caveat: representability does not mean the substrate explains consciousness, life, or emergence; it only means the same representational machinery can describe their modeled structure.

### Stress Test 4 — semantic relationships

Tested:

- identity
- equivalence
- similarity
- difference
- containment
- causation
- ownership
- membership
- sequence
- probability
- uncertainty
- meaning
- truth
- contradiction
- emergence

Result: all were representable, but probability, uncertainty, meaning, and truth repeatedly required an explicit reference/perspective/model frame.

Key finding: **REFERENCE FRAME is likely necessary at the substrate boundary, even if CONTEXT is not a primitive.**

### Stress Test 5 — formalization

Target statement:

> "The speed limit on Route X was 55 mph under jurisdiction Y from date A through date B, according to source Z, with confidence C."

Result: the assertion could be represented as a proposition plus typed relations for scope, validity interval, provenance, and confidence.

Key finding: **a claim must itself be distinguishable so that other assertions can refer to it.** This permits claims to carry provenance, assessments, temporal scope, and conflicts.

### Stress Test 6 — schema families

Compared the candidate substrate with RDF, JSON-LD, relational databases, OWL, W3C PROV, and MusicXML.

Result: each could be conceptually mapped into the substrate, but lossless interoperability requires preserving more than raw data:

- domain vocabulary/types
- constraints
- inference or validation rules
- provenance
- identity mappings
- multidimensional ordering where applicable

Key finding: **MeaningWire should not try to replace domain schemas. It may instead provide a neutral substrate and translation boundary beneath them.**

### Stress Test 7 — project-oriented round trip

Initial adversarial examples:

- Summit Evidence: meeting → source document → extraction → claim → provenance
- Devsembly: repository → issue/PR → commit → review → policy/evidence
- Music: score → measures → notes → temporal/simultaneous structure
- MeaningWire: symbol → interpretation → reference frame → source/claim
- Geographic hierarchy: location → administrative/geographic relationships → broader systems

Result: conceptual round trips succeeded for the structures tested. Exact byte/format round trips remain untested until actual source artifacts are used.

## Current architecture hypothesis

MeaningWire should be considered as three major layers, with supporting metadata:

### 1. Substrate

**DISTINCTION + RELATION + ORDER + REFERENCE FRAME**

### 2. Domain schema

- vocabulary
- types
- semantics
- constraints
- domain rules

### 3. Operations

- query
- compare
- compose
- transform
- infer
- validate
- project
- translate

Supporting capabilities:

- provenance
- identity resolution/mapping
- loss semantics
- versioning
- evidence
- uncertainty

## Important negative findings

- We have **not** proven that the four substrate candidates are mathematically minimal.
- We have **not** proven that they form an ontology of reality.
- We have **not** demonstrated complete lossless translation for arbitrary existing schemas.
- We have **not** demonstrated that every higher-order concept can be derived from the four candidates without adding specialized operators or formal semantics.
- We should not replace mature standards such as RDF, JSON-LD, OWL, PROV, SQL, or MusicXML merely because they can be mapped conceptually.

## Next falsification tests

1. Use actual artifacts from Summit Evidence, Devsembly, and Music Intelligence.
2. Define explicit D/R/O/F semantics rather than relying on prose.
3. Perform source → MeaningWire → source-schema round trips.
4. Measure semantic loss, not merely syntactic similarity.
5. Test constraints, inference rules, provenance, identity resolution, temporal validity, simultaneity, uncertainty, and contradictions.
6. Record every case where an additional primitive or operation becomes necessary.
7. Compare the resulting model against established formal frameworks rather than treating them as competitors.

## Research principle

**Derived findings must remain separated from source claims.**

The research corpus should preserve:

- source
- interpretation
- synthesis
- hypothesis

as distinct epistemic layers.

## Working conclusion

The strongest current hypothesis is not "container" and not "holon" as a universal primitive.

The current candidate is:

> **DISTINCTION + RELATION + ORDER + REFERENCE FRAME**

with higher-level structures emerging from their composition.

This remains **RESEARCH / PROVISIONAL** until formal semantics and round-trip tests against real artifacts support it.
