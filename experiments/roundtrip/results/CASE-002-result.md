# CASE-002 Result

**Status:** PARTIAL PASS / EVENT MODEL VALIDATED

## Executed

The CASE-002 fixture was parsed and normalized into **7 semantic events**:

- 5 events in measure 1 across voices 1 and 2;
- 2 events in measure 2;
- 3:2 tuplet metadata on the voice-1 triplet;
- tie start on C4 in measure 1 and tie stop on C4 in measure 2;
- explicit rest events;
- `backup` rewind separating the voice timelines.

The normalized event positions were:

- voice 1: C4@0, D4@1, E4@2, C4@12;
- voice 2: REST@0, G3@1, REST@12.

## Findings

The tested semantics remain representable when one MusicXML measure contains multiple voice timelines.

This strengthens the hypothesis that **ORDER is not one universal sequence**. It is better treated as a collection of typed/independent order axes or relations.

The experiment also separates:

- **source encoding operation:** MusicXML `backup`;
- **underlying semantics:** voice-specific event ordering and positions.

MeaningWire should preserve the latter and retain the former only when required for source reconstruction/provenance.

## Result

**PARTIAL PASS**

The candidate event model preserves the tested semantic distinctions and ordering structures.

This is not yet a complete MusicXML → MeaningWire → MusicXML round trip.

## Next falsification target

Add:

- simultaneous events across multiple voices;
- different tuplet ratios in different voices;
- meter changes;
- overlapping ties;
- rests between simultaneous events.

Then test whether the current D/R/O/F representation still suffices without ad-hoc exceptions.
