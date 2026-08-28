# Adapters

This directory will contain reference adapters and adapter documentation.

Initial adapters should be read-oriented and narrowly scoped. Their purpose is to demonstrate how vendor- or system-specific data terminates at public MeaningWire contracts without redefining those contracts around a particular downstream system.

Reference adapters should document:

- source system and version assumptions;
- authentication boundary without embedding credentials;
- input and output contracts;
- mapping identifiers and versions;
- known unsupported fields;
- known lossy transforms;
- provenance behavior;
- deterministic fixtures and tests.
