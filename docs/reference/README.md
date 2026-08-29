# Reference

MeaningWire reference documentation is derived from canonical public repository data wherever practical.

Generated references:

- [`generated/schemas.md`](generated/schemas.md) — schema registry plus registered schema metadata
- [`generated/mappings.md`](generated/mappings.md) — mapping registry plus registered mapping source/target and transform metadata

These generated pages are **not** independent sources of truth. Their canonical inputs remain:

- `schemas/registry.json` and the registered JSON Schema documents;
- `mappings/registry.json` and the registered mapping definitions.

Regenerate locally with:

```text
python tools/generate_reference_docs.py
```

Verify without modifying files with:

```text
python tools/generate_reference_docs.py --check
```

CI runs the check form and fails when a committed generated page is missing or stale. This lets the future documentation site index readable Markdown without requiring maintainers to manually synchronize duplicate semantic definitions.
