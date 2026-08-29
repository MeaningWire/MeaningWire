---
title: Documentation build foundation
description: How MeaningWire proves its pre-deployment documentation source builds reproducibly.
---

MeaningWire's documentation is built from a committed, locked Astro + Starlight toolchain before any hosting or deployment decision is made.

The governed build uses Node `22.19.0`, npm `10.9.3`, Astro `7.2.9`, and Starlight `0.41.10` with the complete npm graph recorded in `package-lock.json`.

CI installs that graph with `npm ci`, builds the static site twice from the same exact source commit, and compares the complete output trees. Only a successful repeated build can satisfy the release-readiness documentation-build assertion.

This source foundation does not deploy a website or publish a release.
