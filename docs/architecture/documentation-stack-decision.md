# Documentation Stack Decision

Status: **ACCEPTED FOR IMPLEMENTATION, PRE-DEPLOYMENT**

MeaningWire will use **Astro + Starlight** as the preferred documentation-site stack for the first public release experience, subject to a reproducible locked build being proven before the scaffold is merged as an operational dependency.

This decision selects the architecture. It does not deploy a site, purchase hosting or a domain, create a public launch surface, or authorize dependency installation without a committed lockfile and CI evidence.

## Decision criteria

The documentation experience needs to support:

- static output that can be hosted on ordinary static infrastructure;
- Markdown-first authoring with an escape hatch for richer components;
- built-in local search without requiring a hosted search service;
- strong accessibility defaults and a WCAG 2.2 AA project target;
- keyboard-friendly navigation and low-cognitive-load information architecture;
- light and dark themes with controllable contrast;
- responsive mobile behavior;
- concise navigation for beginners plus deep references for builders and researchers;
- future generated schema and mapping references;
- source ownership in the MeaningWire repository;
- deterministic CI builds with pinned dependencies;
- a small maintenance surface during pre-release work;
- no requirement for a server-side application runtime in production.

## Selected stack

### Astro + Starlight

Starlight is an official Astro documentation framework and is the selected starting point.

The evaluated current generation provides the features MeaningWire needs without requiring an application backend:

- static-site generation through Astro;
- Markdown and MDX content;
- documentation-oriented navigation and table of contents;
- Pagefind as the default static-site search provider;
- responsive navigation;
- built-in dark/light theme support;
- a keyboard-focusable skip link and accessibility-oriented UI labels;
- customizable CSS variables and a theme editor that can target WCAG AA/AAA contrast levels;
- per-page draft and search-index controls;
- extension points for future generated references and custom components.

Current Astro installation guidance requires Node.js 22.12.0 or higher. The current Starlight 0.41 generation supports Astro 7 and no longer supports Astro 6. The implementation must therefore pin a compatible Astro 7 / Starlight 0.41-or-newer pair together rather than mixing major generations.

Primary research references:

- https://starlight.astro.build/
- https://starlight.astro.build/getting-started/
- https://starlight.astro.build/guides/site-search/
- https://starlight.astro.build/reference/configuration/
- https://starlight.astro.build/reference/overrides/
- https://starlight.astro.build/guides/css-and-tailwind/
- https://docs.astro.build/en/install-and-setup/
- https://docs.astro.build/en/guides/upgrade-to/v7/

## Alternatives considered

### VitePress

VitePress remains a credible fallback. It provides Markdown-first static documentation and built-in local fuzzy full-text search using MiniSearch.

Reasons not to select it first:

- MeaningWire would gain less documentation-specific accessibility and content-structure guidance out of the box;
- its Vue-centered extension model is useful but unnecessary for the current project;
- Starlight's built-in docs primitives, Pagefind integration, and accessibility-oriented component surface align more directly with MeaningWire's release-experience goals.

Reference: https://vitepress.dev/reference/default-theme-search

### Material for MkDocs

Material for MkDocs is mature, responsive, searchable, accessible, Markdown-first, and capable of fully static/offline output. It would otherwise be a strong candidate, particularly because MeaningWire already uses Python tooling.

It is not selected for the first implementation because its own 2026 project guidance describes significant ecosystem uncertainty around the MkDocs 1.x to MkDocs 2.0 transition and incompatibility between Material for MkDocs and the MkDocs 2.0 pre-release direction. MeaningWire should avoid introducing that transition risk while its own public contracts are still young.

References:

- https://squidfunk.github.io/mkdocs-material/
- https://squidfunk.github.io/mkdocs-material/philosophy/
- https://squidfunk.github.io/mkdocs-material/blog/2026/02/18/mkdocs-2.0/

### Docusaurus

Docusaurus is a mature documentation platform, but its broader React application surface is more machinery than MeaningWire currently needs. MeaningWire's first docs experience should favor static documentation primitives and a smaller customization burden rather than a general React site framework.

Docusaurus may be reconsidered only if future requirements materially exceed Starlight's documentation-focused extension model.

## Implementation constraints

The Starlight scaffold must not be merged merely from a generated starter template. Before the site becomes an operational repository dependency:

1. Node runtime expectations must be explicit and pinned for CI.
2. Direct dependencies must be version-pinned.
3. A real package-manager lockfile must be committed.
4. CI must use the lockfile rather than floating dependency resolution.
5. The production site must build as static output without a server adapter unless a separately justified requirement emerges.
6. The build must not require private packages, secrets, private APIs, analytics, remote fonts, or proprietary services.
7. Search should remain local/static by default.
8. Customization should prefer Starlight configuration and small custom CSS over component replacement.
9. Accessibility must be tested after MeaningWire-specific styling; framework defaults are not proof of WCAG 2.2 AA conformance.
10. Deployment is a separate step from source implementation and remains disabled until explicitly appropriate.

## MeaningWire visual and cognitive-accessibility direction

The initial site should be calm and restrained rather than visually dense.

Defaults should favor:

- a limited navigation depth;
- one obvious next action on entry pages;
- short introductory sections before deep reference material;
- generous whitespace and readable line length;
- visible focus states;
- no autoplay, motion-heavy decoration, modal marketing, or engagement popups;
- no dependence on color alone for state or meaning;
- system fonts initially, avoiding remote font requests and an extra supply-chain/privacy dependency;
- both light and dark themes with measured contrast;
- progressive disclosure for detailed architecture and standards material.

## Deployment boundary

Selecting Starlight does not select a host.

The first implementation should produce a deterministic static `dist/` directory in CI. Hosting choices—GitHub Pages, a custom domain, or another static host—remain separate decisions. No domain purchase, DNS change, analytics integration, or public launch is implied by this architecture decision.

## Reconsideration triggers

Re-evaluate this decision if:

- Starlight loses active maintenance or accessibility quality;
- its dependency or Node requirements become disproportionate to the site's value;
- deterministic static builds become unreliable;
- MeaningWire requires a capability that cannot be added without extensive framework overrides;
- a lower-complexity option demonstrably meets the same accessibility, search, reference-generation, and maintenance requirements better.
