# Public Implementation Boundary

MeaningWire is intended to be a self-contained public implementation of its interoperability contracts and tooling.

The project may be informed by prior research, experiments, prototypes, implementation experience, standards analysis, or requirements discovered outside this repository. That does not imply the existence of a finished proprietary MeaningWire product, and public documentation must not make claims about prior products or implementations that cannot be substantiated.

## Core rule

A MeaningWire release must not require access to a proprietary or private MeaningWire codebase in order to understand, build, test, validate, or release the supported public software.

Private knowledge may inform design. Private code is not a hidden dependency of the public product.

## Requirements

For a capability to be included in a public MeaningWire release:

- the source required to build the supported capability must be present in the public repository or come from documented public dependencies;
- schemas, mappings, interfaces, fixtures, and validation rules required for supported behavior must be public and versioned;
- deterministic tests and release checks must run without access to private repositories, undocumented services, or private test data;
- release automation and provenance must be reproducible from public source and documented tooling;
- no proprietary library, private package, hidden schema, private API, or private build step may be required for ordinary supported use;
- documentation must explain supported behavior without relying on private organizational context;
- any code incorporated from another source must have clear provenance and licensing compatible with inclusion in MeaningWire;
- private downstream systems may be used for requirement discovery or isolated compatibility analysis only when separately authorized, and they do not receive hidden contract privileges.

## Reimplementation

Ideas, requirements, architectural lessons, and observed interoperability problems may be reimplemented in MeaningWire when doing so is lawful and consistent with project governance.

Reimplementation should produce a public contract and implementation that stands on its own. It should not preserve accidental private coupling merely because an earlier experiment or prototype used it.

Where independent clean-room procedures are actually required for legal or licensing reasons, those procedures must be explicitly designed and documented. MeaningWire does not use the phrase “clean-room implementation” as a casual synonym for ordinary open-source reimplementation.

## Release evidence

Before a capability is represented as supported, release evidence should demonstrate that a fresh environment can obtain the public source, resolve documented public dependencies, run validation/tests, and produce the documented artifacts without private access.

A failure of that test is a release blocker, not a documentation inconvenience.

## Public communication

MeaningWire may accurately describe itself as a public implementation developed from first principles and informed by research, standards, experiments, and prior learning where supported by evidence.

It must not imply undisclosed customers, adoption, a hidden commercial product, a larger team, or a previously completed proprietary implementation unless those facts are both true and appropriate to disclose.
