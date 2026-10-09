# CASE-004O — Equality Rules Across Serialization Boundaries

- **Maturity:** EXPERIMENTAL
- **Promotion:** Isolated experiment only; no merge is authorized.
- **Parent experiment:** CASE-004N, PR #66
- **Question:** Do typed, domain-aware equality decisions survive JSON and positional relational serialization/deserialization without semantic drift?

## Hypothesis

If equality rules are part of an artifact's semantic state, then serialization must preserve both the rule data and the conflict decisions produced from it. Missing rules must remain missing (and retain the conservative default), while malformed or ambiguous rules must not be silently normalized into a valid-looking policy.

## Test design

The tests use the same two verified claims with numeric values `1` and `1.0`, evaluated through both historical and active conflict views.

1. **Explicit numeric equivalence:** A scoped `numeric_equivalence` rule makes the values equal. JSON and relational round trips must preserve the rule and both conflict counts must remain zero.
2. **No rule:** The `value_equality_rules` field must remain absent after both round trips. The conservative default preserves the numeric representation difference, so both conflict counts remain one.
3. **Ambiguous rules:** Two rules that both match the same claim domain must survive serialization as authored and continue to raise an ambiguity error when interpreted.
4. **Structural fidelity:** Reconstructed artifacts must be canonically identical to the source artifact for each path.

## Relational encoding compatibility

The existing positional layout remains `case-004c-v1` when the optional rule field is absent. Artifacts that include `value_equality_rules` use `case-004c-v2`, whose root tuple adds that field. The decoder accepts both layouts and does not synthesize an empty rule list for v1 artifacts. This preserves the semantic distinction between an absent field and an explicitly present list.

## Falsification criteria

CASE-004O fails if any round trip:
- drops, changes, or invents a rule;
- changes a historical or active conflict count;
- turns an ambiguous rule set into an accepted policy; or
- changes the artifact structure beyond the declared versioned relational representation.

## Limits

These are deterministic synthetic fixtures, not proof of correctness for every serializer, schema, or domain. The experiment tests the current JSON and repository-local positional encoding only. It does not establish wire-format negotiation, cross-version interoperability, database persistence, or behavior of external implementations.

## Run

```bash
python -m unittest tests/test_cross_interpreter_consistency.py -v
python -m unittest discover -s tests -v
```
