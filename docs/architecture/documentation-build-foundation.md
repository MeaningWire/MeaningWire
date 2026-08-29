# Documentation Build Foundation

Status: **PRE-DEPLOYMENT / REQUIRES EXACT-HEAD CI**

MeaningWire's documentation source is built as a static Starlight site from the public repository. This foundation exists to make the first release experience reproducible before any hosting or deployment decision is made.

## Governed toolchain

The current direct documentation toolchain is pinned to:

- Node `22.19.0` via `.node-version`;
- npm `10.9.3` via `package.json#packageManager`;
- Astro `7.2.9`;
- `@astrojs/starlight` `0.41.10`;
- the complete npm dependency graph recorded in `package-lock.json`.

Node `22.19.0` is intentionally above Astro's framework minimum because the resolved dependency graph includes `undici@8.10.0`, which declares Node `>=22.19.0`. The governed runtime follows the actual locked graph rather than suppressing an engine mismatch.

## Build contract

Governed CI must:

1. check out the exact source commit;
2. select the Node version from `.node-version`;
3. install dependencies with `npm ci` from the committed lockfile;
4. run `npm run docs:build`;
5. confirm a static `dist/index.html` exists;
6. retain the first static output tree temporarily;
7. rebuild from the same exact source and locked dependency graph;
8. compare the complete output trees byte-for-byte; and
9. reject symbolic links in the generated static output.

Only after those steps succeed may the workflow pass `--documentation-build-verified` to the release-readiness evaluator.

A committed `package.json`, lockfile, and Astro configuration are therefore necessary but not sufficient evidence of launch readiness.

## Information architecture

The initial source provides four deliberately small entry paths:

- getting started;
- builder;
- researcher & model;
- integration & evaluation.

The home page states the quiet pre-release boundary and does not present the project as stable, production-ready, or already launched.

## Accessibility and dependency boundaries

The initial customization is intentionally restrained:

- system fonts only;
- visible focus treatment;
- readable content width;
- reduced-motion handling;
- no analytics;
- no remote fonts;
- no private APIs or packages;
- no server adapter;
- no proprietary build service.

These controls support the project's WCAG 2.2 AA target but do not themselves constitute an accessibility-conformance claim. Accessibility testing remains required as the site grows.

## Deployment boundary

This foundation creates source and static build evidence only. It does not configure GitHub Pages or another host, create a domain or DNS record, publish a release, upload a public site, or create public attestations.
