---
title: Accessibility

description: See the accessibility target, current automated evidence, and testing that MeaningWire has not yet claimed.
---

MeaningWire targets [WCAG 2.2 AA](https://www.w3.org/TR/WCAG22/) for its documentation experience.

**MeaningWire does not currently claim WCAG 2.2 AA conformance.** Automated checks can catch useful regressions, but WCAG conformance requires broader evidence, including human evaluation.

## What the current site already provides

MeaningWire keeps Starlight's framework-native accessibility behavior rather than replacing its core page components. Starlight documents a skip link as the first element inside the page body and a semantic header/sidebar/main page frame.

MeaningWire also adds a small project-owned CSS layer that:

- uses system fonts rather than remote font dependencies;
- keeps long-form paragraph and list text to a restrained line length;
- gives `:focus-visible` elements an explicit outline;
- reduces animation and transition duration when `prefers-reduced-motion: reduce` is active.

The documentation search remains local to the generated Pagefind bundle; MeaningWire does not add analytics or a remote search service.

## What CI checks automatically

The rendered static site fails validation if a page loses high-value structural invariants that can be established without a browser. The current checks require:

- a non-empty document language;
- one non-empty page title and one non-empty meta description;
- unique rendered page titles;
- exactly one `main` landmark and one `h1` inside it;
- a named pre-main skip link whose fragment target exists inside `main`;
- no skipped heading level inside the main content;
- an `alt` attribute on every rendered `img` element;
- no autoplay audio or video;
- no HTTP(S) subresource dependency for scripts, styles, fonts, images, frames, or media;
- valid rendered internal documentation links.

These checks run inside the same repeated static documentation build that must remain byte-identical.

## What still needs broader testing

Static HTML validation does **not** establish all accessibility behavior. Before any formal conformance claim, MeaningWire still needs appropriate evidence for areas including:

- complete keyboard navigation and logical focus order;
- focus visibility and focus-not-obscured behavior across interactive states;
- sidebar and mobile navigation behavior;
- Pagefind search behavior with keyboard and assistive technology;
- text zoom, reflow, and responsive behavior;
- text, component, state, and focus-indicator contrast;
- screen-reader naming, roles, state announcements, and reading order;
- target sizes and other interaction details that require rendered-browser inspection;
- representative manual testing and documented conformance evaluation.

The project will extend evidence in bounded steps rather than converting an automated green check into an unsupported compliance claim.
