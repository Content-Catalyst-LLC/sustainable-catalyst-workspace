# v0.64.1 — Accessibility Runtime & Desktop Layout Recovery

## Incident addressed

The v0.64.0 production capture showed two defects: a WordPress critical-error boundary after substantial Workspace output and severe desktop column collapse that rendered headings/body copy character-by-character.

## Script dependency repair

The v0.64.0 accessibility helper was registered with its own handle inside its dependency array. v0.64.1 removes that self-reference. A release test parses the static Workspace enqueue declarations and rejects a dependency graph containing a self-edge or cycle.

This repair removes an identified invalid dependency relationship. It does **not** assert that the production PHP fatal was conclusively caused by that relationship without the host server error log. Production smoke validation must still confirm full render through the site footer.

## Grid hardening

CSS Grid items have an automatic intrinsic minimum size unless constrained. Rich preview/tool content can therefore pressure a neighboring fractional track even when the intended design is proportional. v0.64.1 changes the affected desktop tracks to `minmax(0, …fr)` and places `min-width: 0` on the relevant children.

The target behavior is:

- 1600 / 1440 / 1280 / 1024px: readable two-column editorial and research layouts.
- 768 / 390px: intentional single-column layouts through the existing breakpoints.
- no character-wide text columns;
- no forced horizontal page overflow from the hardened grids.

## Release boundary

No canonical schema, project content, persistence record, accessibility checklist, telemetry boundary, or cloud behavior changes in this hotfix.
