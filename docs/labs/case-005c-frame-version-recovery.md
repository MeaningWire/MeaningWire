# CASE-005C — Frame Version Drift and Recovery

- **Maturity:** EXPERIMENTAL
- **Promotion:** Isolated experiment only; no merge is authorized.
- **Parent experiment:** CASE-005B, PR #69
- **Question:** When sender and receiver hold different versions of a shared semantic frame, can the receiver detect the mismatch, reject ambiguous decoding, and recover after receiving a validated frame update?

## Hypothesis

Compact frame references are only safe when both ends agree on the frame schema. A versioned reference plus a schema digest should prevent silent reinterpretation. A receiver should accept an update only when its current version and digest match the update's declared predecessor, then advance exactly one version.

## Protocol under test

- Each local frame record carries a stable frame ID, monotonically increasing integer version, full schema, and SHA-256 digest of canonical schema JSON.
- Each encoded scene carries frame ID, version, digest, and the CASE-005B compact payload.
- A frame update includes the expected prior version/digest, next version, replacement schema, and next digest.
- Updates are validated before a new frame record is returned. The current frame is not mutated.
- Unknown, stale, out-of-order, tampered, or schema-incompatible references fail closed.

This is a small experimental protocol, not a claim of production-grade authentication. A digest detects schema mismatch/tampering only when the expected digest is trusted; it does not authenticate the sender or prevent replay by itself.

## Tests

1. Versioned round trip preserves exact semantic state.
2. A version-2 payload is rejected by a version-1 receiver until the update is applied.
3. Replaying an old update is rejected.
4. A modified update digest is rejected.
5. Two different schemas claiming the same frame ID/version are not silently treated as equivalent.
6. Byte accounting includes the initial frame record, the frame update, and every instance envelope/payload, against repeated explicit scene JSON for a ten-scene batch.

## Measurement and caveats

The byte comparison is an accounting experiment, not a preordained compression win. It counts canonical JSON serialization of the initial frame record, one update, and all versioned instance messages; baseline cost is the canonical JSON size of all explicit scenes. It does not yet include transport headers, retries, loss/reordering recovery messages, decoder distribution, authentication, or multi-party synchronization. The digest repeated in each instance may cost more than it saves for small messages. The result applies only to this synthetic workload.

## Falsification criteria

The safety hypothesis fails if an incompatible schema is silently accepted, an out-of-order update is applied, an update mutates current state before validation, or a recovered scene differs from the sender's scene. The efficiency hypothesis is not considered supported unless total bytes, including updates and all per-message metadata, beat the explicit baseline for the workload under test.

## Run

```bash
python -m unittest tests/test_frame_version_recovery.py -v
python -m unittest discover -s tests -v
```
