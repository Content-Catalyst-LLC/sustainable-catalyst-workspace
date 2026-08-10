# Sustainable Catalyst Workspace v0.33.0 — Source Capture & Research Clipping

Release date: 2026-08-09

## Purpose

v0.33.0 turns the Research Notebook into a real capture surface. Users can save source records, excerpts, quotations, document references, Knowledge Library material, Research Librarian results, and external research context into a project notebook while retaining explicit provenance and bibliographic context.

## What changed

- Adds a privacy-conscious Source Capture inbox at the Workspace level for same-origin capture handoffs that arrive before a destination project/notebook is chosen.
- Adds manual Source / Excerpt capture inside Research Notebook with author, publisher/container, publication date, identifier/DOI, locator/pages, license, source surface, and source URL fields.
- Adds `sc-workspace-source-capture-v1.js`, a public same-origin producer helper for Knowledge Library, Research Librarian, and future Sustainable Catalyst surfaces. Capture payloads are staged in sessionStorage or postMessage; research content is never placed in the handoff URL.
- Adds portable JSON capture-request import for sources outside the Sustainable Catalyst origin.
- Notebook blocks advance to v2.0 and retain capture provenance plus bibliographic context.
- Promotions remain explicit and preserve the original notebook block. Promoted Source/Evidence objects inherit source title, URL, capture time, and a readable citation/context line when available.
- No remote URL fetch, page scraping, citation guessing, automatic metadata extraction, AI processing, publishing, or automatic upload is introduced.

## Migration

- Workspace storage: 28 → 29
- Project schema: `sc-workspace-project/13.0` → `sc-workspace-project/14.0`
- Project export: `sc-workspace-project-export/13.0` → `sc-workspace-project-export/14.0`
- Notebook workspace: `sc-workspace-notebook-workspace/1.0` → `2.0`
- Notebook: `sc-workspace-notebook/1.0` → `2.0`
- Notebook block: `sc-workspace-notebook-block/1.0` → `2.0`
- Notebook export: `sc-workspace-notebook-export/1.0` → `2.0`

Existing notebook blocks are normalized into v2.0 with empty bibliographic context and explicit `manual` capture provenance. Existing projects, object IDs, lifecycle milestones, account backups, sync enrollment, restore points, Safe Actions, reconciliation receipts, collaboration records, and institutional handoffs are preserved.

## Governance boundary

Capture is an explicit user action. The adapter does not run unless a source surface invokes it. Workspace does not automatically fetch the source URL or infer bibliographic facts. Incoming captures enter an inspectable queue and are saved only after the user chooses a destination.

## Integration note

v0.33.0 establishes the Workspace-side Source Capture contract and public producer helper. Knowledge Library, Research Librarian, and other Sustainable Catalyst products must adopt that helper (or emit the documented capture-request schema) before their own **Add to Notebook** actions become end-to-end producers. This release does not modify those separate product repositories.
