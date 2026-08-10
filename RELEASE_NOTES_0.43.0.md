# Sustainable Catalyst Workspace v0.43.0

## Research Collections & Dynamic Views

v0.43.0 builds on Knowledge Search & Advanced Retrieval by adding reusable research organization without creating another canonical content store.

### Added

- Browser-local smart research collections that store explicit retrieval criteria rather than record copies.
- Dynamic collection membership recalculated from the canonical Integrated Knowledge corpus at render time.
- Saved research views with explicit grouping and density preferences.
- Built-in project-aware Sources, Evidence, Decisions, Analysis, Notebooks, and Documented views.
- A derived Research dashboard showing source, evidence, decision, documented-record, project, and total-record counts for the current project/scope lens.
- Dynamic grouped preview by project, kind, subtype, origin, or no grouping.
- `/wp-json/sc-workspace/v1/research-collections-contract`.
- `sc-workspace-research-collection/1.0` and `sc-workspace-research-view/1.0` contracts.

### Architecture boundary

This is a schema-stable release:

- Storage: 35 → 35
- Project: 20.0 → 20.0
- Project Export: 20.0 → 20.0
- Notebook Workspace: 8.0 → 8.0
- Notebook Export: 8.0 → 8.0

Smart collections and saved views are browser-local definitions only. They do not copy canonical research content or store membership snapshots. Membership and dashboards are recomputed from the existing v0.42 retrieval/index layer.

v0.43.0 introduces no server collection index, semantic inference, automatic AI, automatic membership mutation, or canonical record mutation.

### Preserved

The complete v0.32–v0.42 Notebook, Integrated Knowledge, Unified Research Navigation, and Advanced Retrieval lineage remains active, including conflict-safe sync, Notebook Review & Provenance, explainable retrieval ranking, saved searches, related-material navigation, and canonical-origin handoffs.
