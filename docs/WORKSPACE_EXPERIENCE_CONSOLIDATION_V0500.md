# Workspace Experience Consolidation — v0.50.0

v0.50.0 is a product-experience release rather than a research-schema release.

## Primary information architecture

Workspace continues to expose five primary areas:

1. Start
2. Projects
3. Research
4. Review
5. Exchange

Specialized routes remain contextual within Research, Review, and Exchange.

## Experience controls

The presentation layer stores only browser-local preferences under `sc_workspace_experience_v0500`.

- `Comfortable` is the default density.
- `Compact` reduces visual padding and minimum card height without changing record content.
- `Ctrl/Meta + K` opens the route command palette.
- `Alt + 1…5` navigates among the five primary areas.
- `/` focuses the current view's search field when one is available.
- `Escape` closes Workspace experience dialogs.

## Terminology

The Help surface defines Project, Research, Notebook, Knowledge, Review, and Exchange using the same language as the application.

## Responsive behavior

On small screens, primary and contextual navigation remain single-row horizontally scrollable controls rather than becoming a long vertical navigation stack. Primary controls maintain a 44px minimum target.

## Governance

This layer does not create, copy, rewrite, score, infer, upload, publish, or synchronize research. Navigation commands invoke existing explicit UI routes only. Density changes presentation only. No schema migration is required.

## Visual boundary

The Sustainable Catalyst editorial header rule remains **4px** on desktop and mobile. Internal Notebook rules that had remained heavier from earlier builds are normalized to the same 4px grammar where appropriate.
