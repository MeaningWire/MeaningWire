# CASE-004L — Explicit Dual Conflict Views

- **Maturity:** EXPERIMENTAL
- **Promotion:** Isolated experiment only; no merge is authorized.
- **Parent experiment:** CASE-004K, PR #63
- **Decision encoded:** Preserve historical disagreement and separately report active unresolved conflict.

## Contract

MeaningWire publishes two measures. Neither overwrites the other:

- `historical_disagreement_count`: number of subject/predicate/scope groups with incompatible verified claim values in the raw claim record. A later valid supersession does not erase this history.
- `active_unresolved_conflict_count`: number of subject/predicate/scope groups that still have multiple distinct active verified values after only explicit, valid, later supersession edges are applied.

Both measures count conflicting groups, not all possible pairs of claims. The corresponding records are exposed separately as `historical_disagreements` and `active_unresolved_conflicts`. The legacy `raw_claim_analysis.conflict_count` remains the raw/historical measure for compatibility inside this experimental branch; it is not silently repurposed as the active measure.

## Cases

1. **Contradictory claims, no supersession:** historical = 1; active unresolved = 1.
2. **Later verified same-scope claim explicitly supersedes earlier claim:** historical = 1; active unresolved = 0.
3. **Invalid or non-later supersession edge:** the edge is rejected; the contradiction remains active.
4. **Three or more conflicting values in one scope:** counts one conflicting group, not the number of pairwise combinations.
5. **Serialization:** both the artifact and the composed interpreter output must remain deterministic across JSON and relational round trips.

## Run

```bash
python -m unittest tests/test_cross_interpreter_consistency.py -v
```

## Limits

Synthetic evidence only. This contract defines reporting semantics; it does not prove that a source is authoritative, that a physical condition changed, or that a claim should trigger an operational action. Significance remains a judgment, and resolution/escalation remain governed by their explicit typed contract.
