# CASE-004C — Relational Tuple Encoding Comparison

- **Maturity:** EXPERIMENTAL
- **Status:** Executable differential test; validation pending
- **Purpose:** Compare a named-field JSON artifact with an explicit positional relational tuple encoding, using the same decoder contract and CASE-004B reasoning interpreter.
- **Non-goals:** This is not proof of a universally minimal representation, not a benchmark of every serialization format, and not an engineering safety tool.

## Research question

Can a reduced relational representation reconstruct the full semantic artifact and preserve all nine CASE-004B observable behavior groups while using fewer serialized bytes?

This is stronger than deleting fields: the experiment encodes records into positional tuples, then decodes them back to the named artifact consumed by the existing interpreter.

## Run

From the repository root:

```bash
python tools/relational_encoding.py
python tools/relational_encoding.py --json
python -m unittest tests/test_relational_encoding.py -v
```

## What is compared

- **Named JSON:** the existing synthetic CASE-004B bridge-inspection fixture.
- **Relational tuple JSON:** fixed tables for entities, relations, claims, events, and policy; each row is represented as a positional array under the declared `case-004c-v1` layout.
- **Semantic behavior:** both original and reconstructed artifacts are passed to the same `reason()` interpreter and compared across its nine observable output groups.
- **Structural fidelity:** the decoded relational artifact is compared with the original fixture using deterministic canonical JSON.

The encoder rejects unexpected or missing record fields rather than silently discarding them. The decoder rejects unknown layout identifiers, missing/extra envelope fields, and tuple-arity mismatches. Tests also check that explicit null values and duplicate relation rows survive structural reconstruction. These tests exercise a small set of adversarial inputs, not all malformed inputs.

## Cost accounting caveat

The report includes the serialized artifact bytes, but **excludes** the shared tuple schema, decoder implementation, and version-negotiation overhead. Positional tuples rely on an agreed column order, so the apparent byte savings are not total-system savings. A fairer follow-up would count the schema/decoder costs, test schema evolution, and compare repeated artifacts where a shared schema can be amortized.

## Interpretation

- **PASS** means the current fixture reconstructs and its declared behavior outputs remain equal under this specific encoding and decoder.
- A smaller byte count means only that this tuple encoding is smaller for this fixture, under the stated exclusions.
- It does not establish that MeaningWire's primitives are minimal, that a generic relational substrate is best, or that equivalence holds for untested artifacts and queries. The CASE-004B interpreter currently inspects one fixed claim ID; exact reconstruction of additional or contradictory claims does not prove the interpreter reasons correctly over them.
- The artifact is synthetic; confidence and policy values are test data only.

## Next falsification target

If CASE-004C passes, the next experiment should introduce schema evolution and adversarial cases: reordered fields, unknown predicates, missing/null values, duplicate relations, contradictory claims, and multiple events. The representation should preserve distinctions or fail explicitly—not silently normalize them away.
