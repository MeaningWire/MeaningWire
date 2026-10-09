# CASE-004J — Event Identity and Duplicate Detection

- **Maturity:** EXPERIMENTAL
- **Purpose:** Probe a failure mode in CASE-004I: typed transitions can appear valid even when event identity is ambiguous.
- **Depends on:** CASE-004I explicit resolution and escalation contract.
- **Promotion:** Isolated; no merge authorized.

## Hypothesis

A resolution or escalation history is not trustworthy under this contract if event IDs are absent or reused. Event identity must be unique across the complete artifact, not merely among events attached to one claim, or the same event can be counted twice or misattributed.

## Tests

1. Reuse an escalation event ID on a second event linked to an unrelated claim; global integrity and the affected escalation contract must fail.
2. Duplicate a resolution confirmation; the artifact and resolution contract must fail.
3. Remove an event ID; the artifact and escalation contract must fail.
4. Confirm distinct IDs leave the previously valid escalation path valid.

## Expected implication

Serialization preserves identifiers, but preservation alone does not make identifiers valid. Identity integrity is a separate invariant. This experiment checks uniqueness within one artifact only; it does not solve distributed identity, replay attacks, signatures, actor authorization, or cross-version identity.

## Limits

Synthetic data only. No physical-world or safety conclusion. The event identity policy is a declared experimental contract, not yet a core MeaningWire rule.

## Run

```bash
python -m unittest tests/test_event_integrity.py -v
```
