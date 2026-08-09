# v0.12.0 — Personal Knowledge Environment

## Purpose

Make device-local Workspace knowledge discoverable across projects without creating a second copy of canonical project content.

## Architecture

The Personal Knowledge Environment is a workspace-level contract (`sc-workspace-personal-knowledge/1.0`). The search index is derived at runtime from canonical Workspace Objects. Stored knowledge state contains only collections, stable `{projectId, objectId}` references, and local view preferences.

## Capabilities

- Cross-project browser-local search across project titles, object titles, summaries, content, tags, and provenance.
- Filters for object type, project, tag, and active/archived scope.
- Provenance inspection and internal reference counts.
- Transparent related-work discovery using shared tags, matching source URLs, and matching provenance titles.
- Reusable collections with up to 200 object references each and up to 30 collections.
- Open any knowledge result back in its canonical project/object editor.
- Portable JSON export for a collection and its referenced objects.

## Governance boundary

- No server-side knowledge index.
- No embeddings or hidden semantic relevance score.
- No cloud synchronization.
- No copied object-body store inside the knowledge layer.
- Deleting a collection never deletes Workspace Objects.
- Deleting a project or object removes dead collection references.

## Migration

Storage schema advances from 12 to 13. Project schema remains `sc-workspace-project/10.0`; v0.11.0 projects are not rewritten. Existing Workspace state receives an empty Personal Knowledge environment on first load.
