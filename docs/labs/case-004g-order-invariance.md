# CASE-004G — Collection Order and Semantic Invariance

- **Maturity:** EXPERIMENTAL
- **Purpose:** Test which collection-order changes should leave declared reasoning unchanged, while preserving the event history as supplied.
- **Depends on:** CASE-004B interpreter, CASE-004C relational encoding, CASE-004E multi-claim analyzer, CASE-004F temporal analyzer.

## Invariant under test

For this experiment, entities, claims, and relations are treated as collections whose input order should not alter reasoning. Events are treated as an ordered history: their order is preserved by serialization and is not silently canonicalized away. The experiment does not assert that event order itself changes the reasoning of every current interpreter; it asserts that the artifact must preserve the supplied event sequence.

## Tests

1. Reverse claim, entity, and relation arrays and compare the CASE-004B, CASE-004E, and CASE-004F outputs.
2. Reverse event history and confirm the serialized artifact differs, while claim-level analyses remain stable.
3. Round-trip a permuted artifact through the CASE-004C tuple layout and verify structural equality and analysis equality.

## Why this matters

Byte-for-byte reconstruction and semantic invariance are different contracts. An encoder can preserve the exact array order while a reasoning layer should treat some arrays as unordered collections. If those semantics are intended, output ordering must be deterministic rather than accidentally inherited from insertion order. Event history is kept separate because chronology/provenance is not merely a set.

## Limits

This tests one deterministic permutation, not exhaustive property-based or fuzz testing. It assumes the collection semantics stated above; a future schema must explicitly declare whether each array is ordered, unordered, or partially ordered. No real-world safety conclusion is drawn.

## Run

```bash
python -m unittest tests/test_semantic_permutation.py -v
```
