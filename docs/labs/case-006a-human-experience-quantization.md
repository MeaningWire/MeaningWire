# CASE-006A — Quantizing Human-Experience States

**Maturity:** EXPERIMENTAL  
**Status:** Isolated research harness; no stable contract or psychological validity claim  
**Implementation:** `tools/case_006a_human_experience.py`  
**Tests:** `tests/test_case_006a_human_experience.py`

## Question

Can MeaningWire represent states such as hope, shame, and trust as structured, quantized records while preserving the distinctions that must not be compressed away: who the state concerns, what it concerns, context, provenance, time, and the fact that multiple states may coexist?

## Hypothesis

A typed record with a versioned dimension codebook can reduce numeric precision to eight ordinal levels while preserving non-numeric semantic bindings exactly. The maximum scalar reconstruction error for uniform nearest-level quantization on [0, 1] is 1/14 (approximately 0.07143). Whether these dimensions validly represent human experience is a separate empirical question and is not tested here.

## Synthetic state dimensions

The dimensions below are experimental placeholders, not a validated emotion scale.

- **Hope:** goal importance, perceived possibility, personal agency, expectation confidence.
- **Shame:** negative self-evaluation, perceived exposure, belonging threat, norm-violation belief.
- **Trust:** perceived reliability, perceived benevolence, willingness to be vulnerable, evidence confidence.

Each value is an ordinal modeling input normalized to [0, 1]. It is not a probability unless an independently defined measurement model says so. The model does not infer an emotion from text, behavior, physiology, or any other signal. All example values are synthetic.

## Encoding contract

Each state preserves:
- state ID and subject reference;
- state type;
- target and context references;
- source kind: `self_report`, `observation`, or `inference`;
- observation time;
- confidence in the representation;
- dimension levels under the explicit codebook version.

Numeric dimensions are encoded positionally in a fixed, versioned order. The decoder rejects unknown versions, missing or extra dimensions, invalid levels, duplicate state IDs, and malformed records. It does not guess missing data.

Concurrent states remain separate records. Hope and shame may coexist; the encoder must not force them into a single winning label.

## Experiment and tests

The deterministic test suite checks:
1. scalar quantization error over 1,001 values;
2. round-trip preservation of state type, subject, target, context, source kind, and time;
3. bounded numeric distortion for hope, shame, and trust fixtures;
4. preservation of self-report versus inference;
5. coexistence of multiple states without collapse;
6. fail-closed behavior for unknown codebooks, missing dimensions, and duplicate IDs.

Run:

```bash
python -m unittest tests/test_case_006a_human_experience.py -v
```

## What this experiment does not establish

- It does not define universal or clinically validated measures of hope, shame, or trust.
- It does not establish that different people use the dimensions or scales equivalently.
- It does not infer emotions or establish the truth of a person's self-report.
- It does not test whether the quantized representation is smaller on the wire. JSON integer tokens are not a bit-packed encoding, and codebook distribution, envelope overhead, and synchronization costs have not been measured.
- It does not show that eight levels are perceptually or socially sufficient.

## Falsification and next steps

The implementation-level hypothesis fails if quantization exceeds its stated error bound, changes semantic bindings or provenance, silently collapses concurrent states, or accepts malformed/unknown codebooks.

If this narrow test passes, the next experiment should compare several quantization resolutions against explicit task-level distinctions, including cases where nearby numeric values must remain distinguishable. Only after that should we measure total communication cost, including codebook setup and version updates. Human-subject validation would require a separate, appropriately designed study and should not be implied by synthetic tests.

## Interpretation

This is a test of a representation technique, not a claim that emotion can be reduced to numbers. The intended result is a compact, revisable description of selected dimensions with explicit provenance and bounded numeric distortion—while leaving the lived experience itself larger than the encoding.
