# CASE-005B — Frame Reference and Reconstruction

- **Maturity:** EXPERIMENTAL
- **Promotion:** Isolated experiment only; no merge is authorized.
- **Parent experiment:** CASE-005A, PR #68
- **Question:** Can a receiver reconstruct a repeated structured situation from a shared frame definition and compact instance tuples while preserving bindings, uncertainty, and part–whole relations?

## Hypothesis

For repeated scenes with a stable schema, a frame reference plus ordered attribute tuples can reduce total encoded bytes compared with repeated named JSON objects. This is only useful if the receiver reconstructs the same semantic state and fails closed when the frame is missing or incompatible.

## Test design

The frame describes a two-vehicle scene with a fixed attribute order: color, motion. Each property carries value, epistemic status, and confidence. Two entities are linked to the scene by explicit contains relations.

The test battery checks:
1. Exact round-trip reconstruction, including entity bindings and uncertainty metadata.
2. Rejection of an unknown frame reference.
3. Detection of a mismatched attribute order through semantic reconstruction comparison.
4. Amortized size comparison across ten scene instances, including the shared frame definition once.
5. Rejection of attributes not represented by the frame.

## Measurement caveats

The byte test counts canonical JSON bytes for the frame definition and all encoded instances versus the repeated explicit scene JSON. It includes the shared frame once, but excludes transport framing, version negotiation, decoder distribution, and synchronization/recovery costs. Results are limited to this synthetic schema and batch size; they do not establish general compression superiority.

## Falsification criteria

Fail if any property, binding, status, confidence, or relation changes during reconstruction; if unknown frame references are accepted; or if the encoded batch does not reduce bytes after including the frame definition.

## Run

```bash
python -m unittest tests/test_frame_reconstruction.py -v
python -m unittest discover -s tests -v
```
