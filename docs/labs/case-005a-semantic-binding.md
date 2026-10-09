# CASE-005A — Semantic Binding Across Serialization

- **Maturity:** EXPERIMENTAL
- **Promotion:** Isolated experiment only; no merge is authorized.
- **Parent experiment:** CASE-004O, PR #67
- **Question:** Does a serialized representation preserve which attributes belong to which entities, not merely preserve the set of attribute values?

## Hypothesis

A scene representation must preserve bindings between entities and their attributes. If all values survive but an attribute is attached to the wrong entity, the reconstructed scene is semantically different.

## Test design

The synthetic scene contains two vehicles:
- Vehicle A is red and stopped.
- Vehicle B is blue and moving left.
- Both vehicles are parts of a shared scene frame.

The experiment checks three properties:

1. JSON and positional relational round trips preserve the exact entity–predicate–value bindings.
2. Rebinding a motion claim to the other vehicle changes the semantic binding signature even though the set of values is unchanged.
3. The scene's part–whole relations and the per-vehicle motion claims survive the relational round trip.

## Falsification criteria

CASE-005A fails if:
- any attribute becomes attached to a different entity during round-trip;
- a part–whole relation is lost or altered; or
- the test treats an artifact with the same values but different entity bindings as equivalent.

## Limits

This is a deterministic synthetic test of the repository's current JSON and positional relational encoding. It does not implement a general-purpose binding engine, validate all referential constraints, or prove cognitive/neural binding theories. It establishes a narrow structural requirement for future frame-based semantic transmission.

## Run

```bash
python -m unittest tests/test_semantic_binding.py -v
python -m unittest discover -s tests -v
```
