# CASE-004K — Cross-Interpreter Consistency and Historical Conflict

- **Maturity:** EXPERIMENTAL
- **Purpose:** Compose the existing CASE-004B, CASE-004E, CASE-004F, CASE-004H, and CASE-004I interpreters without collapsing their distinct views.
- **Promotion:** Isolated experiment only; no merge is authorized.

## Question

When a later verified claim explicitly supersedes an earlier verified claim, should the earlier disagreement remain visible as a raw evidence conflict while the active temporal view reports the conflict as resolved?

## Experiment

The composed view runs the base reasoning battery, raw multi-claim analysis, temporal analysis, field sensitivity, and resolution/escalation contract checks on the same artifact. It labels the relationship between raw conflicts and temporal status instead of silently rewriting one interpreter's output.

Two cases are compared:
- Contradictory verified claims with no supersession: raw and active views both report conflict.
- A later verified same-scope claim explicitly superseding an earlier one: raw evidence analysis still records the disagreement, while temporal analysis reports the older claim as superseded.

The second case is not automatically treated as a code failure: preserving a historical disagreement and reporting no active conflict can both be valid. The unresolved issue is the contract vocabulary—whether the unqualified field `conflict_count` should mean raw historical disagreement or active unresolved conflict.

## Falsification and preservation

The experiment verifies the two cases and ensures the full composed output survives ordinary JSON and CASE-004C relational round trips. It does not choose the meaning of `conflict_count` or delete historical claims.

## Limits

Synthetic data only. This does not prove that a superseding source is authoritative or that the underlying physical state changed. The policy still requires trusted source authority, domain-specific validation, and event semantics.

## Run

```bash
python -m unittest tests/test_cross_interpreter_consistency.py -v
```
