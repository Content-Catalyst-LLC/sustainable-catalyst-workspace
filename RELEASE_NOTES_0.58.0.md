# Sustainable Catalyst Workspace v0.58.0 — Scale, Performance & Large-Project Hardening

v0.58.0 hardens the local-first Workspace for substantially larger projects and research collections while remaining schema-stable.

## Added
- Review → Performance scale profile.
- Derived Integrated Knowledge index cache with explicit cache clearing.
- 120-record bounded Integrated Knowledge render windows with manual Load more up to 600 visible cards.
- Storage-size and browser-quota visibility where supported.
- Advisory scale budgets for project, object, notebook, notebook-block, index, and storage pressure.
- Deterministic large-project stress fixtures for regression testing.
- `sc-workspace-scale-performance/1.0`, `sc-workspace-scale-profile/1.0`, and `sc-workspace-performance-budget/1.0` contracts.
- `/wp-json/sc-workspace/v1/scale-performance-contract`.

## Boundaries
- Storage remains 35.
- Project remains 20.0; Project Export remains 20.0.
- Notebook Workspace remains 8.0.
- No automatic deletion, archival, compaction, migration, or canonical mutation.
- The 4px editorial header treatment is retained.
