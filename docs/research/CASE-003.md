# CASE-003 — Adversarial Composition / Serialized Round Trip

**Status:** EVALUATED / EXPERIMENTAL  
**Date:** 2026-10-08  
**Purpose:** Falsify the current semantic substrate if it cannot preserve meaning across a deliberately compositional MusicXML case.

## Current substrate under test

The current candidate substrate is:

1. **DISTINCTION** — something is distinguishable from something else.
2. **RELATION** — a typed relationship connects distinctions.
3. **ORDER** — distinctions can be ordered on typed axes rather than one universal sequence.
4. **REFERENCE** — stable identity allows relationships to survive serialization.

CASE-002 established that ORDER cannot safely be treated as one universal sequence. This test therefore uses multiple order axes, including temporal position and voice-local sequence.

## Adversarial fixture

The fixture intentionally combines:

- three independent parts / voices;
- simultaneous events;
- a 4/4 → 3/4 meter change;
- tuplets with a 3:2 time modification;
- ties crossing a measure boundary;
- rests;
- MusicXML `backup` and `forward` cursor operations;
- independent voice-local timelines.

The fixture contains **21 events: 15 notes and 6 rests**, plus **2 tie relations** and **1 tuplet represented through 2 membership relations**. The source contains **3 `backup`** and **2 `forward`** operations.

## Experiment

The actual isolated round trip executed was:

```
MusicXML A
   ↓ parse
MeaningWire MW₁
   ↓ serialize
MusicXML B
   ↓ parse
MeaningWire MW₂
   ↓ serialize
MusicXML C
   ↓ parse
MeaningWire MW₃
```

Comparison was made at the semantic MeaningWire level rather than by byte-for-byte XML equality.

The semantic fingerprint compared:

- event identity/type;
- part;
- measure;
- voice;
- temporal onset;
- duration;
- pitch;
- meter;
- tie continuity;
- tuplet membership and ratio.

## Results

| Property | Result |
|---|---|
| Event count | PASS — 21 → 21 |
| Note/rest distinction | PASS — 15 notes / 6 rests preserved |
| Simultaneity | PASS — simultaneous onset clusters preserved |
| Independent voices | PASS |
| Meter change | PASS — 4/4 → 3/4 preserved |
| Tie continuity | PASS — 2 tie relations preserved |
| Tuplet structure | PASS — 3:2 group preserved |
| Forward/backup-derived timing | PASS — semantic onset positions preserved |
| MW₁ ≡ MW₂ | PASS |
| MW₂ ≡ MW₃ | PASS |
| MW₁ ≡ MW₃ | PASS |

## Interpretation

**CASE-003 did not falsify the current four-primitive substrate.**

More importantly, the test produced evidence for a stronger claim:

> The current substrate can preserve a non-trivial semantic structure through repeated representation changes when temporal position, voice-local order, identity, and typed relationships are explicitly represented.

This is not evidence that MeaningWire is universal. It is evidence that the current substrate survives this particular adversarial composition.

## Interdisciplinary invariants exposed by CASE-003

### State
Event state includes pitch/rest, duration, part, measure, voice, and temporal position.

### Relationship
Tie continuity and tuplet membership cannot be represented reliably as isolated fields; they require explicit relationships.

### Transformation
MusicXML cursor operations (`backup` / `forward`) can be transformed into semantic temporal positions without requiring those source operations to remain literally identical.

### Invariant
The important invariant is not the XML syntax. It is the semantic event/relationship structure.

### Information loss
Source-level formatting and cursor choices may change without semantic loss. The experiment therefore separates **representational loss** from **meaningful loss**.

### Composition
A→MW→B→MW→C→MW remained semantically stable across repeated composition.

### Context
Voice and part context remain necessary to interpret ordering and simultaneity correctly.

## What CASE-003 did NOT prove

It does **not** establish that:

- the four primitives are mathematically complete;
- MeaningWire is universal;
- arbitrary MusicXML can round-trip;
- arbitrary schemas can round-trip;
- all provenance can be preserved;
- lossy transformations are safely characterized;
- causal, probabilistic, physical, spatial, or biological semantics are covered.

Those remain open falsification targets.

## Next falsification target

The next experiment should deliberately introduce **non-preserving transformations** and require MeaningWire to say exactly what was lost.

That moves the research from:

> "Can meaning survive?"

to:

> **"Can MeaningWire distinguish what must survive, what may be transformed, what can be reconstructed, and what has been irreversibly lost?"**

That is the next architectural pressure test.
