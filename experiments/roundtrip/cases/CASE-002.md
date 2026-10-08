# CASE-002 — MusicXML Multi-Order Stress Test

**Status:** EXECUTED / PARTIAL PASS

## Purpose

Attack the current ORDER model with several independent structures in one score:

- multiple voices;
- explicit timeline rewind using MusicXML `backup`;
- rests;
- a 3:2 tuplet;
- a tie crossing a measure boundary;
- separate voice timelines sharing one measure.

## Fixture

`experiments/roundtrip/fixtures/CASE-002-multiorder.musicxml`

The fixture contains:

- Voice 1: C4-D4-E4 as a 3:2 triplet, with C4 tied into measure 2.
- Voice 2: rest followed by G3.
- Measure 2: tied C4 continuation in voice 1 and rest in voice 2.

## Ground-truth invariants

The candidate representation must preserve:

1. note/rest identity;
2. voice identity;
3. measure membership;
4. per-voice start positions;
5. duration;
6. tuplet ratio;
7. tie start/stop linkage;
8. explicit timeline rewind / independent ordering;
9. the distinction between rest and silence-by-absence.

## D/R/O/F pressure points

### DISTINCTION
A rest is a distinguishable event, not merely missing information.

### RELATION
The tie connects two distinct note events while asserting musical continuity.

### ORDER
There is no single cursor for the whole measure. Each voice has an event order, while `backup` expresses a movement through the shared MusicXML encoding timeline.

### REFERENCE FRAME
Timing depends on divisions, meter, measure, and voice.

## Preliminary execution result

The fixture can be normalized into distinct events with:

- voice;
- measure;
- start;
- duration;
- pitch/rest;
- tuplet ratio;
- tie markers.

The normalized event model preserves the tested invariants.

## Result

**PARTIAL PASS**

The candidate survives the tested multi-order features at the event-model level.

However, the test exposes an important distinction:

> MusicXML's `backup` is an encoding mechanism, while the underlying musical order is a set of voice-specific event timelines.

Therefore MeaningWire should not necessarily model `backup` itself as a primitive. It should preserve the semantic ordering it expresses and treat the source encoding operation as provenance/schema information.

## Falsification target

The next failure test should introduce:

- simultaneous events in multiple voices;
- tuplets with different ratios in different voices;
- nested/overlapping ties;
- rests interleaved with notes;
- voices that do not begin at the same time;
- meter changes.

If those require a new foundational structure, record it rather than extending ORDER ad hoc.
