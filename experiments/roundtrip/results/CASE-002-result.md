# CASE-002 Result

**Status:** PARTIAL PASS

## Tested

MusicXML fixture with:

- multiple voices;
- backup-based timeline rewind;
- rests;
- 3:2 tuplets;
- cross-measure tie;
- independent voice timelines.

## Observed

The event normalization preserves the tested semantic invariants:

- note/rest distinction;
- voice;
- measure;
- start;
- duration;
- tuplet ratio;
- tie markers;
- independent event ordering.

## Finding

The experiment strengthens the case that ORDER should be modeled as **multiple typed/independent order relations or axes**, rather than one universal sequence.

It also separates **source encoding operations** from **underlying semantics**: MusicXML `backup` is an encoding instruction, not necessarily a MeaningWire primitive.

## Limitation

This is still an event-level test, not complete MusicXML round-trip interoperability.

Next: cross-voice simultaneity plus differing tuplets and meter changes.
