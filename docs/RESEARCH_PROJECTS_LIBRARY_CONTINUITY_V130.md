# Workspace v1.3.0 — Research Projects & Library Continuity

v1.3.0 connects research projects to the Sustainable Catalyst Knowledge Library while preserving two canonical systems. Workspace remains the project context; the Library remains the canonical discovery, recommendation, watchlist, queue, and source-bundle system.

## Supported continuity records
- Saved searches
- Watchlists
- Research queue items
- Source bundles
- Private personal recommendations

## Identity and privacy
Authenticated continuity reuses the same WordPress identity; no second Library account is required. Guest Workspace remains fully usable. Private personal recommendations remain user-scoped and private by default. Workspace does not enumerate another user's Library records.

## Promotion boundary
Library records are staged locally through an explicit JSON package or same-origin handoff event. Adding a staged item to a project creates a provenance-preserving Workspace Source copy only after explicit user action. The canonical Library record is never mutated or replaced.

## Frozen contracts
Storage schema 35, project schema sc-workspace-project/20.0, and export schema sc-workspace-project-export/20.0 are unchanged.
