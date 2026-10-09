# CASE-004J — Event Identity and Duplicate-Record Integrity

- **Maturity:** EXPERIMENTAL
- **Purpose:** Adversarially test whether explicit resolution and escalation records remain unambiguous when event IDs are missing or duplicated.
- **Depends on:** CASE-004I resolution/escalation contract.
- **Promotion:** Isolated experiment only; no merge is authorized.

## Rules under test

- Every event has a non-empty ID.
- Event IDs are globally unique within one artifact.
- A resolution event ID collision invalidates resolution evidence.
- An escalation event ID collision invalidates the affected escalation sequence.
- A duplicate ID on unrelated events still invalidates artifact event integrity, but must not be falsely reported as a collision involving a different resolution event.
- Events for another claim do not enter the selected claim's escalation state sequence.

## Falsification cases

Tests cover duplicate IDs across event types, missing IDs, duplicate resolution confirmations, collisions unrelated to a resolution event, and events scoped to another claim.

## Limits

This experiment uses a single artifact as the uniqueness boundary. It does not define global event identity across artifacts, distributed idempotency keys, signatures, clock trust, concurrency, or event correction/retraction. The current contract checker remains a bounded experimental interpreter.

## Run

```bash
python -m unittest tests/test_event_identity_integrity.py -v
```
