# CASE-001 — MusicXML Simultaneity

**Status:** SETUP  
**Hypothesis under test:** DISTINCTION + RELATION + ORDER + REFERENCE FRAME can represent and reconstruct a small MusicXML score without semantic loss.

## Adversarial feature

Three notes begin at the same musical time:

- C4
- E4
- G4

All belong to the same part and measure.

A representation that collapses these into a single linear sequence would fail.

## Ground-truth invariants

The source representation must establish, at minimum:

1. Three distinct note events exist.
2. All three notes belong to the same part.
3. All three occur in the same measure.
4. All three begin at the same logical time position.
5. Each has its own pitch identity.
6. Each has its own duration.
7. Their simultaneity is preserved during reconstruction.
8. Part/measure context is preserved.
9. Any source metadata used to interpret timing remains distinguishable from the note events.

## Candidate MeaningWire model

### DISTINCTIONS

- score
- part
- measure
- note:C4
- note:E4
- note:G4
- pitch:C4
- pitch:E4
- pitch:G4
- duration:quarter

### RELATIONS

- part contains measure
- measure contains note:C4
- measure contains note:E4
- measure contains note:G4
- note:C4 has-pitch pitch:C4
- note:E4 has-pitch pitch:E4
- note:G4 has-pitch pitch:G4
- each note has-duration duration:quarter
- each note belongs-to part

### ORDER

Do **not** impose C4 < E4 < G4.

Instead preserve a shared temporal position:

- note:C4 starts-at T0
- note:E4 starts-at T0
- note:G4 starts-at T0

The experiment must permit multiple events to occupy the same position and, if necessary, maintain additional independent orders such as measure order and pitch ordering.

### REFERENCE FRAME

At minimum:

- score
- part
- measure
- timing/division convention

The exact MusicXML source metadata will determine the final reference-frame inventory.

## Required comparison

Compare source and reconstructed artifact semantically, not byte-for-byte.

Record:

- identity loss
- relation loss
- order/simultaneity loss
- reference-frame loss
- constraint loss
- provenance loss
- precision loss
- semantic loss
- ambiguity

## Current result

**BLOCKED — source artifact not yet attached or selected.**

This is intentional. This document does not claim that the hypothesis has passed a real MusicXML round trip.

## Next execution step

Use one actual, minimal MusicXML artifact, parse its semantics, create the MeaningWire representation, reconstruct it, and run the invariant comparison.
