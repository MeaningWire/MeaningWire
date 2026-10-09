# CASE-004I — Explicit Resolution and Typed Escalation Contract

- **Maturity:** EXPERIMENTAL
- **Purpose:** Test the user-selected semantics: explicit resolution state plus supporting event; significance remains a judgment; escalation is a typed, timestamped, attributable event sequence with explicit transitions.
- **Depends on:** CASE-004C relational encoding and CASE-004H field-sensitivity interpreter.
- **Promotion:** Isolated experiment only. No merge or core-contract promotion is authorized.

## Contract under test

### Resolution
A claim labeled `resolved` is contract-valid only when exactly one `resolution_confirmed` event references that claim, has a non-empty event ID, references an existing entity as actor, and has a timezone-aware timestamp. A confirmation event paired with a non-resolved state is inconsistent. Even a valid record does not establish physical repair, engineering adequacy, or safety.

### Significance
The claim's significance is preserved as a recorded judgment. This experiment does not convert that judgment into an action or override the policy layer.

### Escalation
Escalation is an ordered sequence of typed events, each with an event ID, a known actor reference, a claim reference, and a timezone-aware timestamp. Timestamps may not regress in artifact order. The allowed state transitions are:

- no state → `escalation_requested`
- requested → acknowledged or withdrawn
- acknowledged → resolved or withdrawn
- resolved / withdrawn → no further transition in this version

An invalid transition is reported rather than silently repaired. The validator retains event order and only derives state from valid transitions.

## Falsification tests

- A resolution label without a supporting event is invalid.
- A resolution event without a valid actor or timestamp is invalid.
- A confirmation event paired with an unresolved claim is inconsistent.
- A complete escalation path is accepted; a direct request-to-resolved path is rejected.
- Escalation chronology must be timezone-aware and non-regressing.
- Significance remains a judgment and does not trigger an automatic action.
- Contract outputs survive ordinary JSON and CASE-004C relational round trips.

## Limits

The allowed escalation vocabulary and transition graph are experiment choices, not universal truths. Real deployments would need domain-specific authorization, event identity rules, trusted time, actor authority, and concurrency/duplicate-event handling. A valid record is not proof of physical-world outcomes. Tests use synthetic data only.

## Run

```bash
python -m unittest tests/test_resolution_escalation_contract.py -v
```
