# CASE-004M — Structured Value Equivalence Across Interpreters

- **Maturity:** EXPERIMENTAL
- **Promotion:** Isolated experiment only; no merge is authorized.
- **Parent experiment:** CASE-004L, PR #64
- **Question:** Can two interpreters disagree about whether claims conflict when their JSON object values contain the same keys and values in a different insertion order?

## Falsification target

Raw claim analysis compares JSON-compatible values using canonical JSON with sorted object keys. Temporal analysis previously used Python's `repr(value)` as its grouping key. For dictionaries, representation can depend on insertion order, so semantically identical JSON objects could be treated as different active values. That would create a false active conflict while the historical view reported no disagreement.

## Contract

- Use one canonical JSON value-equality rule for both raw and temporal conflict analysis.
- Sort object keys and use deterministic compact serialization when constructing comparison keys.
- Different key order alone must not create historical disagreement or an active unresolved conflict.
- Preserve real value differences, explicit supersession rules, source claims, and serialization round-trip guarantees.

## Regression case

The test assigns the two claims equivalent objects with reversed key order:

- `{"surface": "crack", "depth_mm": 2}`
- `{"depth_mm": 2, "surface": "crack"}`

Expected result: historical disagreement = 0; active unresolved conflict = 0; temporal analysis has one active value for the group.

## Run

```bash
python -m unittest tests/test_cross_interpreter_consistency.py -v
```

## Limits

This experiment defines equality for JSON-compatible structured values; it does not establish equivalence for domain-specific units, aliases, measurement tolerances, or semantically related but differently encoded values. Those require explicit domain mappings rather than guesswork.
