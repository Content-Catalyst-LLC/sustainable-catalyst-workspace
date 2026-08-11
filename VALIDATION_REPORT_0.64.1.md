# Sustainable Catalyst Workspace v0.64.1 — Validation Report

**Release:** Accessibility Runtime & Desktop Layout Recovery  
**Date:** 2026-08-10  
**Result:** PASS — ready for deployment and production smoke validation

## Release intent

v0.64.1 is a surgical hotfix over v0.64.0. It removes the invalid self-referential WordPress dependency on `sc-workspace-accessibility-v1` and hardens the two desktop grids implicated by the production capture: the editorial hero and the Focused Research Workspace overview. No canonical data schema changes.

## Automated validation

- PASS — v0.64.1 release validator
- PASS — 823 Python contract tests
- PASS — 124 JavaScript syntax checks
- PASS — 45 JavaScript runtime files
- PASS — 10 PHP syntax checks
- PASS — 6 PHP runtime files
- PASS — WordPress enqueue dependency graph has no self-edge or cycle among statically declared Workspace script handles
- PASS — 350 JSON records parsed
- PASS — release-diff whitespace check against the v0.64.0 repository baseline

## Browser layout regression fixture

A headless Chromium fixture exercised the hardened editorial/research grids at the release target matrix:

| Viewport | Hero text track | Focused Research text track | Page overflow |
|---:|---:|---:|---|
| 1600 px | 646.6 px | 581.7 px | none |
| 1440 px | 646.6 px | 581.7 px | none |
| 1280 px | 653.7 px | 588.0 px | none |
| 1024 px | 517.8 px | 467.0 px | none |
| 768 px | 689.2 px | 687.2 px | none |
| 390 px | 348.0 px | 368.0 px | none |

The fixture verifies that the affected text tracks do not collapse to character-width columns and that the page does not acquire horizontal overflow at the target widths.

## Runtime repair

- `sc-workspace-accessibility-v1` now depends only on `sc-workspace-browser-compatibility-v1`.
- New PHP runtime regression test parses Workspace enqueue declarations and rejects self-dependencies/cycles.
- Current cumulative assets are `workspace-v0.64.1.css` and `workspace-v0.64.1.js`.
- Public Beta II version-current checks now recognize v0.64.1.

## Layout repair

- Editorial hero: `minmax(0,1.18fr) minmax(0,.82fr)`.
- Focused Research overview: `minmax(0,1.05fr) minmax(0,.95fr)`.
- Affected grid children and nested preview/research grids receive explicit `min-width:0` / `max-width:100%` containment.
- Existing single-column breakpoints at 980 px and 900 px remain explicit.
- No artificial character-breaking is introduced on desktop.

## Schema and governance boundary

- Storage schema: **35**
- Project schema: **sc-workspace-project/20.0**
- Schema migration: **none**
- v0.64 accessibility runtime/checklist: **preserved**
- v0.63 browser compatibility layer: **preserved**
- v0.62 persistence-integrity layer: **preserved**
- Telemetry: **none introduced**
- Canonical mutation: **none introduced**
- Automated WCAG certification claim: **none**

## Production validation still required

The invalid dependency edge has been removed, but without the production PHP error log this release does not claim that the dependency cycle was conclusively the only cause of the captured WordPress fatal. After deployment, smoke-test the real `/platform/` page and confirm:

1. the page renders through the WordPress/site footer with no critical error;
2. the hero copy and illustrative Workspace remain proportionate at desktop width;
3. Focused Research copy is readable and not character-stacked;
4. Start / Projects / Research / Review / Exchange routes still open correctly;
5. keyboard navigation and the Accessibility review surface still operate as in v0.64.0.

## Packaging

Packaging checksum and ZIP-integrity results are recorded in the release bundle `SHA256SUMS` and were rechecked after archive creation.
