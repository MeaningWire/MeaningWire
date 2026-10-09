# CASE-004N — Typed, Domain-Aware Value Equality

- **Maturity:** EXPERIMENTAL
- **Promotion:** Isolated experiment only; no merge is authorized.
- **Parent experiment:** CASE-004M, PR #65
- **Decision encoded:** Use explicit schema/domain equality rules; otherwise compare conservatively.

## Contract

MeaningWire's historical and temporal conflict interpreters use the same value-equality function.

- **Default:** canonical JSON structural equality. Object key order is ignored; JSON number representation is preserved, so `1` and `1.0` remain distinct by default.
- **Explicit rules:** artifacts may supply a `value_equality_rules` list. A rule requires a `predicate`, and may optionally narrow by `subject` and `scope`.
- **Supported rules in this experiment:**
  - `canonical_json`: explicitly retain conservative canonical JSON equality.
  - `numeric_equivalence`: for JSON numbers only, treat mathematically equal numeric values as equal.
- **No unsafe coercion:** strings, booleans, and numbers remain distinct. Numeric rules do not perform unit conversion, alias matching, tolerance-based measurement comparison, or other domain inference.
- **Ambiguity fails closed:** more than one matching rule, an unsupported rule, or a malformed rule raises a validation error rather than guessing.
- **Both views agree:** the same equality key is used for historical disagreement and active unresolved conflict.

Example:

```json
{
  "value_equality_rules": [
    {
      "predicate": "condition",
      "scope": "member-M",
      "rule": "numeric_equivalence"
    }
  ]
}
```

With that explicit rule, numeric values `1` and `1.0` are equal only for claims matching the specified domain. Without the rule, they remain distinct. A string `"1"` remains distinct from numeric `1` even when the numeric rule applies.

## Falsification cases

1. No rule: `1` vs `1.0` remains a conflict in both views.
2. Explicit numeric rule: `1` vs `1.0` is not a conflict in either view.
3. Numeric rule: `1` vs `"1"` remains a conflict.
4. Overlapping rules: fail closed with an ambiguity error.
5. Existing structured-object key-order equivalence remains intact.
6. Existing explicit supersession and JSON/relational round-trip tests remain intact.

## Run

```bash
python -m unittest tests/test_cross_interpreter_consistency.py -v
```

## Limits

This is a small, explicit rule vocabulary, not a full schema-language implementation. Before adding unit conversion, tolerances, quantity dimensions, locale-aware parsing, or domain aliases, define their typed representation and validation contract as separate experiments. No physical-world truth or operational safety is inferred from value equality.
