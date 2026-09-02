# GitHub reference adapter

> **Maturity:** Experimental

This directory contains MeaningWire's first read-only GitHub reference adapter. It demonstrates how data from a vendor-specific API can be retrieved, normalized, and wrapped with explicit provenance without prematurely redefining MeaningWire's still-evolving canonical schemas around one provider.

## What it does

The initial adapter reads repository metadata from the GitHub REST API and emits an adapter-local experimental JSON record.

It currently captures:

- GitHub repository identifiers and URLs;
- owner and repository names;
- visibility and archival state;
- default branch;
- primary language;
- license identifier when available;
- topics;
- source timestamps; and
- retrieval provenance, including the GitHub API version.

The output deliberately declares `canonical_contract: null`. MeaningWire canonical repository semantics are not stable yet.

## Run it

Python 3.11+ is sufficient; the adapter uses only the standard library.

```bash
python adapters/github/github_repository_adapter.py MeaningWire/MeaningWire
```

For public repositories, authentication is optional. To use an authenticated GitHub API request, set a token through the environment rather than storing credentials in the repository:

```bash
export GITHUB_TOKEN='...'
python adapters/github/github_repository_adapter.py MeaningWire/MeaningWire
```

Do not commit tokens, installation credentials, or other secrets.

## Authentication boundary

- Public repository reads can use the unauthenticated GitHub REST API subject to GitHub's rate limits.
- Authenticated reads use the value of `GITHUB_TOKEN` by default.
- The token is used only to construct the request Authorization header and is never included in adapter output.
- Future GitHub App support should use least-privilege installation tokens and document the exact permissions required.

## Input

A GitHub repository slug in `owner/name` form.

## Output

The current adapter-local envelope is identified as:

```text
github.repository.snapshot.v0
```

This is not a stable MeaningWire canonical contract. It is an experimental source adapter format intended to let mapping and provenance behavior be exercised while the canonical schema work proceeds through the project's RFC process.

## Known limitations

- Repository metadata only; issues, pull requests, releases, Actions, and other resources are not yet mapped.
- Read-only.
- No pagination is required for this first endpoint.
- No canonical MeaningWire repository schema is claimed.
- No webhook or GitHub App installation flow is implemented yet.
- GitHub Enterprise Server endpoints are not yet supported.

## Why GitHub first

GitHub is a useful reference system because it exposes well-documented developer APIs and real-world concepts—repositories, identities, issues, pull requests, events, provenance, and automation—that exercise MeaningWire's interoperability goals. The adapter is intended to remain provider-specific at the edge while reusable MeaningWire semantics evolve independently.

## Next increments

1. Add deterministic fixture-based tests.
2. Add a canonical source/provenance primitive through the normal MeaningWire RFC process.
3. Add read-only issue and pull-request resources.
4. Define explicit mappings from GitHub concepts to released MeaningWire contracts.
5. Add a least-privilege GitHub App installation mode.
6. Publish a small CLI/package entry point once the adapter SDK shape is stable.
