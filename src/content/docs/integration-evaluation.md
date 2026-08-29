---
title: Integration & evaluation
description: Evaluate MeaningWire against another system without granting it special access or write authority.
---

MeaningWire's first integration posture is intentionally conservative: **read, normalize, map, validate, and compare before writing anything back**.

## Use public contracts only

An integration should consume the same public schemas, mappings, adapter boundaries, CLI behavior, and release artifacts available to any other user. A private downstream system must not receive hidden contracts or privileged MeaningWire behavior.

## Begin with an isolated fixture

Represent the external system with synthetic or appropriately isolated input first. Record source identity and version, preserve provenance, select an explicit mapping, and validate the target envelope.

The existing repository proof demonstrates this sequence with synthetic CRM-shaped input:

```bash
python tools/meaningwire.py proof run --json
```

## Treat ambiguity as a result

If multiple mappings could apply, a mapping is lossy, a transform is unsupported, or required source meaning is absent, fail explicitly rather than guessing. Interoperability evidence is more valuable when it records what MeaningWire cannot safely infer.

## Keep downstream changes out of evaluation

A successful compatibility test does not authorize modification of another repository, API, database, workflow, or production system. Write-capable integration belongs behind a separate design, security, and authority decision.

## Capture evidence

For a real compatibility study, retain the tested source contract/version, MeaningWire commit or release, mapping identity/version, fixtures or reproducible synthetic substitutes, validation results, known losses, and unsupported cases. That evidence can then inform public adapter or mapping work without making the private system a hidden dependency.
