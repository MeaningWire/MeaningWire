# Reference

MeaningWire reference documentation is derived from canonical public repository data wherever practical.

The generator currently emits two presentation forms from the same canonical inputs:

- repository-readable references in [`generated/`](generated/);
- Starlight-native reference pages in `src/content/docs/reference/`, exposed through the documentation sidebar and included in the local Pagefind index.

Generated references include:

- [`generated/schemas.md`](generated/schemas.md) — schema registry plus registered schema metadata;
- [`generated/mappings.md`](generated/mappings.md) — mapping registry plus registered mapping source/target and transform metadata;
- `src/content/docs/reference/schemas.md` — the generated Starlight schema reference;
- `src/content/docs/reference/mappings.md` — the generated Starlight mapping reference.

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

CI fails when any committed generated page is missing or stale. The documentation build also verifies that the Starlight reference routes render canonical registry content, that the Pagefind bundle exists, and that repeated complete static builds are byte-identical. This keeps readable and searchable presentation artifacts synchronized without making them a second semantic source of truth.
