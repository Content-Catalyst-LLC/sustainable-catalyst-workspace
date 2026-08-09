# Sustainable Catalyst Workspace v0.26.0

## Guided Reconciliation & Selective Apply

This release adds an explicit reconciliation workflow on top of Change Review and Safe Actions. Users can compare two project states, choose individual changes, validate structural dependencies, and create a **new reconciled project copy**. Neither source state is modified.

### Reconciliation model

- Start from an existing Change Review or choose a project, base restore point, and target state.
- Every available change begins unselected.
- Select individual added, removed, or modified records, or use Select all / Clear as explicit user actions.
- Preview the resulting candidate project before creation.
- Dependency validation blocks incomplete selections that would create dangling references.
- Human acknowledgement is required before a reconciled copy is created.
- The reconciled result receives a new project ID and remapped canonical object/internal relationship IDs through the existing project clone boundary.
- Export a portable `sc-workspace-reconciliation-plan/1.0` plan without applying it.

### Supported change categories

Reconciliation can selectively carry forward project metadata, canonical objects, research questions/claims/evidence links, analysis assumptions/methods/findings, decisions and their supporting structures, evidence assessments, traceability, reproducibility, Canvas structures, briefing drafts, and guided workflows.

### Data boundary

Workspace storage advances from schema 24 to **25**. Project schema remains `sc-workspace-project/11.0`. The migration initializes a browser-local reconciliation ledger while preserving projects, account persistence, cross-device sync, restore points, Safe Actions, collaboration, institutional handoffs, and all existing canonical object IDs.

### Governance

There is no automatic selection, merge, overwrite, or source mutation. Reconciliation always creates a new local project copy, preserves both source states, exposes dependency blockers, and requires a human acknowledgement before creation.
