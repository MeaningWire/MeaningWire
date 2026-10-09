# CASE-005D — Frame Reuse Break-Even Cost Model

- **Maturity:** EXPERIMENTAL
- **Promotion:** Isolated experiment only; no merge is authorized.
- **Parent experiment:** CASE-005C, PR #70
- **Question:** At what batch sizes and schema-change frequencies does shared-frame encoding save bytes after charging the initial frame, schema updates, and every per-instance envelope?

## Hypothesis

Shared frames can amortize repeated field names and structure for stable, repeated observations. The advantage should shrink or disappear for small batches and frequent schema changes, especially because this prototype repeats frame ID, version, and digest on every instance.

## Method

Run a deterministic synthetic workload at batch sizes **1, 2, 5, 10, 25, 50, and 100**. Compare four change policies:

- **Stable:** no schema changes.
- **Every 10 messages:** add a schema attribute after each interval.
- **Every 4 messages:** add a schema attribute after each interval.
- **Every 2 messages:** add a schema attribute after each interval.

Each schema update adds one schema attribute. Every scene contains one vehicle entity; each attribute retains value, epistemic status, and confidence. The baseline is canonical JSON bytes for the same explicit scene objects.

The protocol total is:

```text
initial versioned frame
+ every schema-update message
+ every versioned instance envelope and compact payload
```

For each scenario the model reports explicit baseline bytes, each cost component, total protocol bytes, bytes saved (negative means a loss), and percentage saved. The matrix deliberately does not assert that frame encoding must win.

## Run

```bash
python tools/frame_cost_model.py
python -m unittest tests/test_frame_cost_model.py -v
python -m unittest discover -s tests -v
```

The command emits a JSON matrix suitable for plotting or comparing future codec variants.

## Scope and caveats

This is a byte-count model for canonical JSON serialization, not a wire capture or throughput benchmark. It does not include transport headers, compression at the transport layer, acknowledgements, retries, lost-update recovery, decoder distribution, authentication, or costs of coordinating multiple receivers. A digest is not sender authentication. The schema-change policy is synthetic and adds attributes monotonically; real workloads may add, remove, rename, or reinterpret fields. Results should not be generalized beyond the tested fixture without representative traces.

## Falsification criteria

The efficiency hypothesis is unsupported for any scenario where total protocol bytes meet or exceed explicit JSON. A general claim that frame references reduce communication cost would require representative workloads and end-to-end accounting; this experiment alone cannot establish that claim.
