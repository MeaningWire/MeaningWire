---
title: Getting started
description: Reproduce MeaningWire's current experimental proof from a public checkout.
---

The shortest useful MeaningWire evaluation is local and read-only. It does not require an account, private repository, hosted service, or downstream-system write.

## 1. Get the source

Clone the public `MeaningWire/MeaningWire` repository and enter the checkout.

## 2. Verify the repository state

Run:

```bash
python tools/meaningwire.py doctor --json
```

A healthy checkout reports the current candidate version, registered schemas and mappings, fixture validation results, and `network_access: false`.

## 3. Run the synthetic interoperability proof

```bash
python tools/meaningwire.py proof run --json
```

The proof reads a synthetic CRM-shaped JSON object, emits a source envelope, applies a registered mapping, and produces a target envelope with explicit provenance. It deliberately does **not** transfer source approval to the target representation.

## 4. Inspect before extending

Useful next commands:

```bash
python tools/meaningwire.py schemas list --json
python tools/meaningwire.py mappings list --json
```

For the fuller repository-local procedure, validation prerequisites, and current limitations, use `docs/quickstart.md` in the source repository.

## Current boundary

This is an experimental pre-release evaluation path. It is not a production deployment guide and does not imply that the current contracts are stable.
