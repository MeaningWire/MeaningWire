# MeaningWire Round-Trip Experiments

This directory contains adversarial experiments for the provisional substrate hypothesis.

## Governing rule

MeaningWire must earn its primitives.

A candidate substrate is not considered sufficient because it can describe an example conceptually. It must preserve explicit semantic invariants through representation and reconstruction.

## Case 001

**Domain:** Music  
**Format:** MusicXML  
**Status:** EXPERIMENT SETUP / NOT YET PASSED

Pipeline:

Real source artifact
-> source semantic inventory
-> MeaningWire D/R/O/F representation
-> reconstruction
-> invariant comparison
-> loss report

The first test deliberately includes simultaneous musical events so that a one-dimensional ordering model can be falsified.

## Result vocabulary

- PASS: required semantic invariants preserved.
- PARTIAL: representation works but one or more nontrivial semantics are lost.
- FAIL: a required invariant cannot be represented or reconstructed.
- AMBIGUOUS: multiple materially different interpretations remain.
- BLOCKED: source or tooling is insufficient to execute the test.

No result should be upgraded from conceptual to empirical without an actual artifact and reproducible comparison.
