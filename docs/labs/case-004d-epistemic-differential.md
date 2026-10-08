# CASE-004D — Epistemic Differential Round-Trip

- **Maturity:** EXPERIMENTAL
- **Status:** Awaiting automated validation
- **Depends on:** CASE-004B interpreter and CASE-004C relational tuple encoder
- **Purpose:** Test whether a meaningful distinction—reported but unverified versus verified—changes observable reasoning and survives both serialization paths.

## Controlled pair

The reported variant preserves the original synthetic fixture. The verified variant changes the claim's epistemic status and appends a verification event while retaining the original report event. This is a controlled test mutation, not a real-world inspection record.

## Expected differences

The declared interpreter should distinguish the pair in exactly these groups:

- **T2 evidence:** `reported_not_verified` versus `verified`
- **T4 uncertainty:** verified flag and whether the claim must be treated as uncertain
- **T5 time:** whether a current condition is established
- **T9 decision:** `manual_review` versus `assess_risk`

The test also asserts that neither variant establishes that the entire bridge is unsafe or asserts human approval.

## Round-trip requirement

For both variants, test:
1. Standard JSON serialization/deserialization.
2. Positional relational encoding, serialization of that encoding, and decoding back to the named artifact.
3. Structural equality and equality of all nine declared behavior groups.

## Run

```bash
python -m unittest tests/test_semantic_differential.py -v
```

## What would falsify the current claim?

The test fails if the interpreter does not distinguish the epistemic states, if it changes unrelated behavior groups, or if either round-trip path changes the artifact or its declared reasoning outputs.

A pass is narrow: it validates one interpreter, one fixture family, and one pair of states. It does not prove general semantic equivalence, safe real-world decision-making, or minimality. The interpreter's fixed claim-ID behavior remains a known limitation; multi-claim and contradictory-evidence reasoning need a later experiment.
