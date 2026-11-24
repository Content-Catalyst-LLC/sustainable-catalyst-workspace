# SC-PUB-TIPTAP-01 — Scientific Publication Studio editor integration

**Status:** Implemented on feature branch; production cutover and authenticated owner acceptance are separate actions.

## What is integrated

Tiptap 3.34.0 (open-source core) and its ProseMirror engine now power the controlled visual text blocks of the existing Workspace Scientific Publication Studio. This is **not** a second publication service or a replacement for Workspace's project/revision storage.

The editor is bundled **locally** with esbuild 0.28.2 and served from the existing authenticated `/v1/private-research/reporting-studio/publication/editor.bundle.js` route. The bundle may not be loaded anonymously; the Document Studio page retains a hashed inline script CSP and allows only same-origin JavaScript. No public CDNs, editor vendor accounts, external publishing APIs, or client-side authority over ownership are introduced.

The existing *Scientific Publication Studio* remains the entry point for scientific reports, policy briefs, working papers, interactive analyses and research overviews. The current Project Catalog, Citation Studio, immutable Workspace revisions, Research bridge, source hash checks, and HTML/PDF/DOCX export routes are reused. The institutional black/white/red document styles and verification disclaimer remain intact.

## Editing and data contract

- **Authoritative saved format:** Existing `markdown` text in `sc-scientific-publication/1.0`. Visual editing changes only the selected text block. All other Markdown source is preserved exactly.
- **Tiptap input:** Heading, ordinary paragraph, simple bulleted list, and basic quotation blocks. Formatting: bold, italic, heading, bulleted list, undo and redo.
- **Source-only blocks:** Equations/LaTeX, figures and asset refs, data tables, code fences, raw HTML, task lists, and complex/unrecognized Markdown. Visible but not silently rewritten by the beta Markdown extension; use Markdown source to edit.
- **Citation compatibility:** Existing valid `[@key]`, multi-citation and locator markers in an edited block are restored from serializer escaping. Escaped literal tokens or new unapproved markers are not promoted into active citations. Bibliographic keys remain resolved and frozen by the existing Citation Studio.
- **Versioning:** Saving and exporting still go through Workspace owner authorization and optimistic revision concurrency; exports are disabled when the manuscript is dirty.
- **Research:** Source objects, rights, notebooks, models and scientific release decisions remain in their existing governed systems. A visual edit does **not** execute, verify or approve calculations.

## Build and test

The Reporting Studio Dockerfile includes a locked, local Tiptap build:

```bash
cd backend/reporting_tiptap
npm ci --ignore-scripts --no-audit --no-fund
npm run build
npm test
node tests/browser-smoke.mjs  # after playwright install chromium
```

The build rejects a missing output bundle; production Python does not fetch a CDN. The lockfile is part of this PR; do not update dependencies outside review.

CI workflow `.github/workflows/sc-pub-tiptap-01.yml` runs local bundle compilation, isolated Chromium editing and source-preservation checks, Markdown compatibility tests, Workspace adapter syntax checks, and the existing branded DOCX/PDF/HTML unit tests.

## Deployment compatibility

1. Merge only after the current PR's Tiptap CI, cross-cutting Workspace/Research checks, and targeted brand/export tests pass. Do not repeat unrelated historical publishing acceptance suites by default.
2. Build a **new candidate Reporting Studio image from the exact reviewed commit**. Preserve the deployed image's digest and rollback path. This is a source-only editor update: **no SQL migration** and no new storage service.
3. Deploy to the **existing** isolated SC-PUB-M1 stage (no new PostgreSQL, users, volumes or WordPress installation). Verify a real authenticated Workspace editor session using nonproduction content.
4. Open the preserved Wexford scientific report and policy brief **as separate document IDs**, switch to visual mode and back, verify no content changes when not edited, edit a paragraph containing a Harvard citation, save a new immutable revision, then export all three formats with the same figures, equations, and references.
5. Check the selected revision and source SHA-256 against the original; ensure no figure, mathematical expression, citation, notebook result or geospatial object silently disappears. Only explicit owner edits may change its Markdown hash.
6. Obtain already-required independently verified off-host restore/recovery acceptance and production operator approval, then update only the Reporting Studio service through the established release procedure. Verify authenticated route, JS bundle CSP, exporting, and a reversible rollback. Do **not** turn on Research publication writes or change Bluehost to deploy this editor.
7. The Research public site and production editorial release remain governed by separate real-owner rights/publication decisions.

## Non-goals / follow-on

This change does not claim full Word desktop fidelity or DOCX roundtrip preservation, collaborative presence, paginated WYSIWYG, custom interactive equation nodes, automatic notebook result insertion, or live MapLibre/Cesium rendering inside exports. Those extensions should use the **same editor package** and authenticated Workspace object pickers, pinning verified source and run hashes and carrying explicit release/rights state. Avoid copying notebook data into editor JSON or creating parallel editor accounts.

**Release gate:** CI passing is evidence of code integration, not proof of production installation or scientific publication approval.
