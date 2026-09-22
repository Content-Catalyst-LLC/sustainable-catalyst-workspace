# Workspace v3.2.0 — Unified Research Project Context

Workspace v3.2.0 introduces a server-authoritative project context that joins the canonical Workspace project record with scientific objects, execution runs, visualization specifications, reproducible study packages, cross-product research handoffs, and the linked Platform Core v3 unified research session.

## Boundaries
- Workspace/PostgreSQL remains authoritative for Workspace project data and scientific objects.
- Platform Core remains authoritative for the shared cross-product research-session registry.
- Context assembly is reference-first and does not replicate specialist object content into Core.
- Context snapshots are immutable manifests for reproducibility and audit, not alternate mutable project stores.
- No automatic scientific inference, evidence ranking, or decision authority is introduced.

## New API
- `GET /v1/research-context`
- `GET /v1/research-context/projects/{project_id}`
- `POST /v1/research-context/projects/{project_id}/snapshots`
- `GET /v1/research-context/projects/{project_id}/snapshots`

## Persistence
Migration `033_unified_research_project_context.sql` adds immutable context snapshots with deterministic fingerprints and project/Core linkage.
