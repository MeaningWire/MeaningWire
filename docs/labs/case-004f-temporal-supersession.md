# CASE-004F — Temporal Validity and Explicit Supersession

- **Maturity:** EXPERIMENTAL
- **Purpose:** Determine whether a conflict should persist when the artifact explicitly says a later verified claim supersedes an earlier verified claim.
- **Depends on:** CASE-004C relational tuple encoding and CASE-004E multi-claim conflict analysis.

## Rule under test

A claim is treated as superseded only if all of the following hold:
1. The artifact contains an explicit `supersedes` relation from the newer claim to the older claim.
2. Both claims exist, are verified, and have the same subject, predicate, and scope.
3. Both observations have timezone-aware timestamps.
4. The superseding claim's observation time is strictly later.

Otherwise the relation is rejected for this experiment and the active conflict is not silently erased. Original claims and their provenance remain in the artifact.

## Falsification cases

- Contradictory verified claims with no supersession link remain in conflict.
- A later verified claim explicitly superseding an earlier same-scope claim removes the older claim from the *active verified set* but preserves its historical record.
- An earlier claim cannot supersede a later one.
- A supersession relation cannot cross subject/predicate/scope.
- The analysis must survive ordinary JSON and CASE-004C relational round trips.

## Limits

This is a deliberately narrow policy experiment, not a universal rule for truth. The word `supersedes` is an explicit semantic commitment, not something inferred from timestamps alone. This version does not resolve clock trust, source independence, legal authority, physical repair, measurement tolerance, partial repairs, or whether an observation is still valid today. It never declares the whole bridge unsafe and does not automatically choose truth outside the explicit supersession rule.

## Run

```bash
python -m unittest tests/test_temporal_claim_reasoning.py -v
```

A pass demonstrates only the stated rule and synthetic cases; it does not prove semantic minimality.
