# CASE-004B — Semantic Round-Trip Differential Test

- **Maturity:** EXPERIMENTAL
- **Status:** Initial executable harness
- **Purpose:** Test whether a synthetic semantic artifact preserves specified reasoning outputs across JSON serialization/deserialization, then run targeted ablations to expose information loss.
- **Non-goals:** This is not a structural-engineering tool, a stable MeaningWire contract, a proof of universal semantic equivalence, or a byte-minimality proof.

## Hypothesis

For a fixed artifact, deterministic interpreter, and declared test battery, the outputs required by the test contract should remain unchanged after serialization and deserialization:

`R(Decode(Encode(X))) = R(X)`

Here, equality means structural equality of the specified observable outputs—not equality of internal implementation steps and not equivalence for every possible question.

## Test artifact

`tests/fixtures/proofs/case-004b-bridge.json` is synthetic. It represents a reported-but-unverified crack in a load-bearing member, with a source, confidence, scope, timestamp, resolution state, significance label, event, and versioned policy. It does not establish that any real bridge is unsafe.

## Run

From the repository root, using only the Python standard library:

```bash
python tools/semantic_roundtrip.py
python tools/semantic_roundtrip.py --json
python -m unittest tests/test_semantic_roundtrip.py -v
```

The harness emits nine reference behavior groups:
1. semantic identification and relationships;
2. evidence status and source;
3. conditional causal implication;
4. uncertainty;
5. time;
6. scope;
7. counterfactual response contract;
8. provenance/event trace;
9. policy-bound decision behavior.

It also removes selected information classes one at a time and reports which observable behavior groups change.

## Interpretation rules

- A round-trip PASS establishes only that this fixture's defined outputs survive this serializer/decoder/interpreter combination.
- A targeted ablation divergence establishes that the current test battery depends on the removed information for at least one output.
- No divergence does not establish universal redundancy. A field may matter for an untested query or another artifact class.
- A missing policy version is treated as a change in decision context, not silently replaced with a default.
- The harness is deliberately deterministic and network-free.
- The fixture's confidence value is test data, not a calibrated probability.
- The policy and outputs are synthetic. They must not be used for actual engineering or safety decisions.

## Initial falsification boundary

The harness can falsify a candidate reduction when a targeted deletion changes one or more declared outputs. It cannot prove global minimality: that would require a declared query/behavior domain, a justified equivalence relation, and stronger arguments about all encodings under consideration.

The next research step after this harness passes is to compare the current full representation against an explicitly relational reduced representation, not merely to delete isolated keys from the full representation. That comparison must retain a common interpreter and report both behavioral divergence and encoded byte size.
