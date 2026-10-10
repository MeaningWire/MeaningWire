# CASE-006B — Quantization Resolution Sweep

**Maturity:** EXPERIMENTAL  
**Status:** Engineering characterization; synthetic inputs only  
**Companion:** CASE-006A human-experience quantization

## Question

How does the number of scalar quantization levels affect numeric distortion and collapse of task-defined distinctions? Does a positional quantized JSON example reduce serialized bytes compared with an explicit named-dimension JSON record?

## Method

The harness sweeps 2, 4, 8, 16, and 256 levels across 1,001 evenly spaced values in [0, 1]. It reports theoretical maximum absolute error, observed maximum and mean error on that grid, and collisions among four synthetic critical pairs: (0.49, 0.51), (0.24, 0.26), (0.74, 0.76), and (0.10, 0.90).

Critical pairs are task-defined engineering fixtures only. They are not claims about emotional thresholds or human judgments. The test demonstrates that numeric distortion and task-specific distinction preservation are different metrics.

A separate single-record comparison measures UTF-8 bytes for compact JSON serialization of an explicit named-dimension state and a positional quantized representation. It is not bit packing. The one-record result excludes codebook distribution, framing, update/recovery costs, and workload variation.

## Run

```bash
python tools/case_006b_resolution_sweep.py
python -m unittest tests/test_case_006b_resolution_sweep.py -v
```

## Falsification criteria

- The measured error exceeds the stated nearest-level theoretical bound.
- Increasing the resolution fails to weakly reduce the maximum-error bound.
- A task-defined pair expected to separate at high resolution still maps to the same code.
- The serialized-size comparison is reported without its scope limitations.

## Interpretation limits

This is not human-subject research, does not validate the CASE-006A dimensions, and cannot establish that a particular number of levels is adequate for any emotion. Synthetic pair collisions are controlled probes, not empirical perceptual thresholds.

A smaller JSON record is not sufficient evidence of lower total communication cost. The next stage must charge for schema/codebook synchronization, context references, uncertainty, exceptions, and recovery after loss or version mismatch.
