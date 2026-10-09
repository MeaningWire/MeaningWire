# CASE-004H — Resolution, Significance, and Escalation Sensitivity

- **Maturity:** EXPERIMENTAL
- **Purpose:** Test whether fields that survived serialization but did not affect the original CASE-004B behavior battery can be made explicitly observable without silently inventing policy.
- **Depends on:** CASE-004B round-trip harness, CASE-004C relational encoding, CASE-004E multi-claim handling, CASE-004G order contract.

## Observable distinctions

This bounded interpreter exposes four groups:
- **Claim dimensions:** subject, predicate, value, scope, observation time, epistemic status, confidence.
- **Resolution:** the exact recorded state and whether it equals the explicit label `resolved`.
- **Significance:** the exact judgment and whether a non-empty judgment is present.
- **Escalation history:** events whose type starts with `escalation_` and whose claim reference is the selected claim or is absent, retained in artifact order.

A significance judgment is exposed as recorded; it does not independently trigger an action. A resolution label is not treated as proof of physical repair or safety. Event labels are interpreted only according to the narrow prefix rule above.

## Falsification tests

1. Changing only resolution changes only the resolution output group.
2. Changing only significance changes only the significance output group.
3. Adding an escalation event changes only escalation history.
4. An event explicitly tied to another claim is not attributed to the selected claim.
5. JSON and CASE-004C relational round trips preserve both artifact structure and these observable outputs.
6. Missing or duplicate selected claim identifiers fail closed.

## Limits

The experiment demonstrates that these fields can be made semantically observable under a declared interpreter. It does not decide which significance vocabulary is authoritative, what constitutes valid resolution, which event types are canonical, or what actions those values should trigger. Those are schema/policy decisions that require explicit agreement before this interpretation becomes a core contract.

## Run

```bash
python -m unittest tests/test_artifact_semantics.py -v
```
