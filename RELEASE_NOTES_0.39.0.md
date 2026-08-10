# Sustainable Catalyst Workspace v0.39.0 — Notebook Review & Provenance

## Purpose
Apply Workspace's explicit review, reconciliation, audit, and provenance principles directly to Research Notebooks without weakening the local-first and conflict-safe behavior introduced in v0.38.0.

## Added
- Notebook Change Review comparing a named notebook restore point with the current notebook.
- Categorized notebook changes across notebook metadata, sections, and blocks.
- Explicit selective reconciliation from a completed Change Review.
- Reconciliation into a new notebook copy; neither reviewed source state is overwritten.
- Stale-review protection: if the current notebook changes after review, a new review is required before reconciliation.
- Derived notebook audit history built from authoritative notebook records, links, promotions, syntheses, assistance drafts, restore points, sync state, reviews, and reconciliations.
- Source-lineage inspection for notebook blocks and referenced Workspace material.
- Notebook export provenance containing relevant review and reconciliation records.

## Governance
- Change Review is advisory and does not apply edits automatically.
- No hidden change, confidence, quality, or governance score is calculated.
- Reconciliation requires explicit user-selected changes and creates a new notebook copy.
- Audit history and lineage are derived views, not a second provenance database.
- Lineage relationships are not inferred automatically.
- v0.38 revision-precondition synchronization, preserve-both conflict handling, and no-background-sync boundaries remain intact.

## Schema advancement
- Storage: 34 → 35
- Project: 19.0 → 20.0
- Project Export: 19.0 → 20.0
- Notebook Workspace: 7.0 → 8.0
- Notebook Export: 7.0 → 8.0
- Notebook Change Review: 1.0
- Notebook Reconciliation: 1.0
- Notebook Audit Event: 1.0
- Notebook Lineage: 1.0
- Notebook Governance: 1.0
