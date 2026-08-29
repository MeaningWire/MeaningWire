# MeaningWire Pre-release Quickstart

MeaningWire is still in pre-release development. This quickstart is for evaluating the current public implementation from a fresh local checkout; it is not a production-readiness or stable-compatibility claim.

## Prerequisites

- Git
- Python 3.12
- network access only for the one-time installation of public validation dependencies

The MeaningWire proof itself uses repository-local code and synthetic fixtures and performs no network access.

## 1. Clone the public repository

```text
git clone https://github.com/MeaningWire/MeaningWire.git
cd MeaningWire
```

## 2. Install the validation environment

For the environment that matches MeaningWire's governed candidate proof—**CPython 3.12 on Linux x86-64**—use the exact hashed lock:

```text
python -m pip install --require-hashes --only-binary=:all: -r requirements-validation.lock
python -m pip check
python tools/validate_dependency_lock.py --verify-installed
```

The lock contains the complete currently resolved validation dependency graph and accepted wheel SHA-256 hashes for the tested candidate target. CI installs it from a clean environment and fails closed if a package version, transitive dependency, or selected artifact hash does not match.

For exploratory evaluation on another operating system or architecture, the direct input remains:

```text
python -m pip install -r requirements-validation.txt
```

That second path allows the public package index to resolve compatible transitive packages for the local platform. It is useful for evaluation, but it is **not** the exact dependency environment represented by the current Linux x86-64 candidate evidence.

The dependencies are used for JSON Schema Draft 2020-12 validation. No private package index or MeaningWire service is required.

## 3. Check repository health

```text
python tools/meaningwire.py doctor
```

A healthy checkout reports `PASS`, the registered schema and mapping counts, deterministic validation results, and that MeaningWire runtime network access is disabled for this path.

## 4. Run the pinned interoperability proof

```text
python tools/meaningwire.py proof run
```

For the complete deterministic result:

```text
python tools/meaningwire.py proof run --json
```

The proof executes this public path:

```text
synthetic JSON object
    -> JSON Object reference adapter
    -> validated source envelope
    -> explicit registered example-crm-email@0.1.0 mapping
    -> bounded simple-member path application
    -> identity transform
    -> validated target envelope
```

The resulting target is pinned by `tests/fixtures/proofs/json-object-crm-email-target.json` and includes explicit transformation provenance. Source approval or authority is not transferred to the target representation.

## 5. Inspect the public contracts

List registered schemas:

```text
python tools/meaningwire.py schemas list
```

List registered mappings:

```text
python tools/meaningwire.py mappings list
```

Inspect the mapping used by the proof:

```text
python tools/meaningwire.py mappings inspect example-crm-email --version 0.1.0 --json
```

Validate the first canonical Identity / Party fixture:

```text
python tools/meaningwire.py schema validate \
  urn:meaningwire:schema:identity:party:0.1.0 \
  tests/fixtures/domains/identity/party-person.json
```

## What this quickstart proves

It demonstrates that the current public repository can validate its registered contracts and execute one deterministic synthetic adapter-to-mapping interoperability path without private code, private schemas, credentials, vendor services, or hidden test data.

On the documented Linux x86-64 / CPython 3.12 candidate target, CI additionally proves that the validation environment can be installed from exact package versions and accepted artifact hashes from the extracted candidate itself.

It does **not** prove production readiness, vendor compatibility, arbitrary conversion support, full JSONPath support, authenticated integration, stable API compatibility, or an identical dependency artifact set on untested operating systems/architectures.

The `proof run` command intentionally has no user-supplied mapping, source, destination, credential, or network arguments. General-purpose conversion remains a separate future capability that must earn its own contract and safety boundaries.
