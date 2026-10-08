# CASE-001 — MusicXML Simultaneity

**Status:** PARTIAL PASS / HARNESS EXECUTED  
**Hypothesis under test:** DISTINCTION + RELATION + ORDER + REFERENCE FRAME can represent and reconstruct a small MusicXML score without losing required event semantics.

## Adversarial feature

The test includes **same-time events inside one part** (a chord) plus an independent second part. This attacks the assumption that musical ORDER is one-dimensional.

A representation that collapses the chord into a strict sequence would fail.

## External real-world reference

A real public MusicXML 4.0 fixture was inspected at:

https://github.com/VjiaoBlack/claude-debussy/blob/main/examples/twinkle.musicxml

Its structure includes two independent parts (Melody and Bass) and overlapping events across part timelines. The source file was not copied into this repository because its license was not established from the available files.

## Executed local fixture

MeaningWire uses an original minimal MusicXML 4.0 fixture in this repository:

- Melody: C4/E4/G4 simultaneously, then D4.
- Bass: a whole-note C3 beginning at the same time.
- Both parts use the same measure/time context.

## Ground-truth invariants

The executed comparison checks:

1. Part identity and names.
2. Number of note events.
3. Note pitch.
4. Measure membership.
5. Start position.
6. Duration.
7. Simultaneous-note grouping.

The checker compares normalized semantic invariants rather than raw XML bytes.

## Candidate MeaningWire model

### DISTINCTIONS

- score
- parts
- measure
- note events
- pitch values
- durations

### RELATIONS

- part contains measure
- measure contains note
- note has-pitch pitch
- note participates-in simultaneity relation where applicable

### ORDER

Each part gets an independent timeline. Multiple events may share the same position.

This avoids incorrectly encoding a chord as C4 < E4 < G4.

### REFERENCE FRAME

At minimum:

- source format/version
- score
- part
- measure
- timing/division convention

## Automated execution

The local invariant checker returned:

**PASS**

The normalized source and reconstructed representations matched for:

- 2 parts
- 5 note events
- the C4/E4/G4 simultaneity group
- note positions
- durations
- pitch identities

## Result

**PARTIAL PASS**

Why not full PASS?

Because this execution proves the **candidate representation and invariant harness** on an original controlled fixture. It does not yet prove a complete, production-grade MusicXML → MeaningWire → MusicXML implementation.

## Remaining test

Implement an explicit serialized MeaningWire representation as an intermediary, then perform:

MusicXML → MeaningWire → MusicXML → semantic comparison

with broader MusicXML features such as:

- ties
- rests
- multiple voices
- tuplets
- dynamics
- articulations
- key/time changes
- lyrics
- metadata
- nested/complex ordering

The test must record every semantic loss or required extension to D/R/O/F.
