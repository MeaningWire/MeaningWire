# CASE-005E — Compact Cached-Frame Envelope

- **Maturity:** EXPERIMENTAL
- **Promotion:** Isolated experiment only; no merge is authorized.
- **Parent experiment:** CASE-005D, PR #71
- **Question:** Can the frame-reuse encoding reach break-even for stable schemas by removing redundant per-instance metadata without weakening fail-closed frame-version checks?

## Hypothesis

CASE-005D found that the existing envelope loses bytes for stable schemas. The current encoder carries a frame reference and digest in the outer versioned envelope, while the nested payload repeats the frame reference. This experiment tests a separate, opt-in codec that sends the frame reference and version once and relies on a receiver's validated frame cache for the schema digest.

## Protocol variants

- **Existing:** outer `frame_ref`, `frame_version`, and `frame_digest`, plus the inner payload's repeated `frame_ref`.
- **Compact:** outer `frame_ref` and `frame_version`; payload carries only `scene_id`, positional entity values, and relations. The digest is validated when the frame is loaded or updated, not repeated on every instance.

The compact decoder rejects unknown frame references, version mismatches, malformed payload shapes, non-integer versions, and a cached frame whose digest does not match its schema. This is a synthetic codec experiment, not a replacement of the CASE-005C protocol.

## Results

Break-even means total frame-protocol bytes are no greater than explicit canonical JSON. First tested batch size at break-even:

| Schema-change policy | First tested break-even batch | Compact savings at 100 messages |
|---|---:|---:|
| Stable | 5 | +4,578 bytes (19.93%) |
| Every 10 messages | 5 | +16,419 bytes (37.07%) |
| Every 4 messages | 25 | +20,001 bytes (40.09%) |
| Every 2 messages | 25 | +21,195 bytes (40.95%) |

For the stable 100-message case, the existing envelope saved **-7,022 bytes** (a 30.57% loss), while the compact envelope saved **4,578 bytes** (19.93%). At one message, both variants lose because the initial frame definition has not been amortized; the compact variant is still 174 bytes larger than explicit JSON. This illustrates why setup cost must be counted.

These are synthetic byte counts, not throughput or real-network measurements. The schema-change schedule stops after five extra attributes are added, even when the selected interval would otherwise trigger another update. Results do not establish that frequent changes are generally beneficial.

## Cost accounting

For both variants, total cost includes the initial versioned frame, every schema update, and every instance envelope plus payload. Explicit canonical JSON is the baseline. The same deterministic vehicle fixture and schema-update schedule from CASE-005D are reused so the envelope change is isolated.

## Safety and trade-offs

The compact envelope assumes sender and receiver share a validated frame cache and that updates are applied in order. It does not authenticate senders, prevent replay on its own, or provide automatic recovery if an update is lost. A production protocol would need explicit cache-miss behavior, acknowledgements/recovery policy, and threat-model review. Omitting the per-instance digest saves bytes but moves consistency responsibility to the frame lifecycle.

## Run

```bash
python -m unittest tests/test_frame_envelope_variants.py -v
python -m unittest discover -s tests -v
```

## Falsification criteria

If the compact envelope does not preserve exact decoded scene semantics, fails closed on frame mismatches, or does not improve fully accounted byte cost on stable repeated batches, the optimization hypothesis is unsupported. Results remain specific to this synthetic fixture until representative workloads are tested.
