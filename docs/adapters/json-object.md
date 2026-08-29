# JSON Object Reference Adapter

The JSON object reference adapter is the first concrete implementation of the pre-release read-only Adapter SDK boundary.

It is a format adapter, not a vendor integration. It demonstrates how one local source record enters MeaningWire without network access, hidden schemas, credentials, or write-back behavior.

## Input

The adapter reads exactly one UTF-8 JSON document whose root is an object.

The caller must supply explicit references for:

- the source boundary;
- the MeaningWire contract represented by the object;
- the record identity.

The adapter does not infer business meaning or identity from the filename, directory name, or JSON keys.

## Output

A successful read emits exactly one MeaningWire canonical envelope using `adapter_sdk.build_read_envelope(...)` and revalidates that envelope before returning it.

The envelope:

- preserves the JSON object as `data`;
- binds provenance to the caller-supplied source reference;
- uses `source_authority` with `approval = not_asserted`;
- carries `EXPERIMENTAL` maturity through the adapter descriptor.

## Safety boundaries

The adapter:

- performs no network access;
- opens the source file read-only;
- writes no output files;
- rejects missing files;
- rejects non-UTF-8 input;
- rejects malformed JSON;
- rejects array/scalar/null roots;
- enforces a configurable positive byte ceiling before parsing;
- does not execute mappings or transforms;
- does not infer a schema or mapping;
- does not manage credentials;
- does not claim compatibility with any vendor or product.

The default size ceiling is 1 MiB. This is a conservative pre-release guardrail, not a permanent format limit.

## Synthetic fixture

`tests/fixtures/adapters/json-object-record.json` is intentionally synthetic and uses the reserved `.invalid` email namespace. It is test data only and does not represent a real person, customer, vendor, or production system.

## Current invocation

For repository smoke testing:

```text
python adapters/reference/json_object.py tests/fixtures/adapters/json-object-record.json
```

The script-mode references are synthetic smoke-test identities. Library callers must provide their own explicit source, contract, and record references.

This adapter remains pre-release and EXPERIMENTAL.
