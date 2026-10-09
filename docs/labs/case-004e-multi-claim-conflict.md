# CASE-004E — Multi-Claim and Contradictory Evidence

- **Maturity:** EXPERIMENTAL
- **Purpose:** Test whether the representation and reasoning path can retain multiple claims about the same scoped subject/predicate, flag conflicting verified values, and preserve that behavior through JSON and positional relational round trips.
- **Depends on:** CASE-004B serialization/interpreter, CASE-004C relational tuple encoder, CASE-004D epistemic-state distinction.

## Controlled fixture

A synthetic member-level condition has two claims:
- `claim-C1`: condition = `present`, verified.
- `claim-C2`: condition = `absent`, verified.

Both claims are scoped to `member-M`, refer to `crack-C`, and retain separate source references and events. This is a deliberately contradictory test fixture, not a real inspection or engineering conclusion.

## Required behavior

1. Preserve both claims independently, including their status, source, scope, and value.
2. Flag a conflict only when at least two verified claims for the same subject, predicate, and scope have different values.
3. Do not silently pick a winner, erase either claim, or infer that the entire bridge is unsafe.
4. Treat a disagreement involving an unverified claim as not yet a *verified* conflict.
5. Reject duplicate claim identifiers.
6. Preserve the artifact and both the CASE-004E analysis and the legacy CASE-004B observable output through ordinary JSON and CASE-004C relational tuple round trips.

## Known limitations

The analyzer is deliberately narrow: it compares exact values and exact subject/predicate/scope keys; it does not resolve time-validity, source independence, supersession, units, measurement tolerance, claim entailment, or the reliability of an inspector. A verified conflict means the record contains incompatible verified claims under this rule—not that either claim is true or that a physical asset is unsafe.

The CASE-004B interpreter still reads a fixed claim identifier (`claim-C1`). This experiment exposes that limitation rather than silently rewriting its established output contract. A later experiment should test whether a generalized interpreter can replace fixed-ID assumptions without changing prior single-claim behavior.

## Run

```bash
python -m unittest tests/test_multi_claim_reasoning.py -v
```

A passing test demonstrates only this fixture and these explicitly defined rules. It does not establish a universal semantic substrate, full semantic equivalence, or minimality.
