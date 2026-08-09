# Guided Reconciliation & Selective Apply — v0.26.0

## Purpose

Workspace already supports named restore points, structural Change Review, conflict-safe synchronization, and Safe Action gates. v0.26.0 adds a controlled way to carry selected differences forward without treating reconciliation as an automatic merge.

## Workflow

1. Choose a project.
2. Select a base state and target state.
3. Load deterministic differences from the Project Diff engine.
4. Explicitly select the changes to carry forward. Nothing is selected automatically.
5. Preview the candidate result.
6. Resolve any structural dependency blockers.
7. Acknowledge that a new project copy will be created.
8. Create the reconciled copy.

The base state and target state remain unchanged throughout the workflow.

## Dependency safety

A selective plan may be incomplete even when every selected individual change is valid in isolation. The reconciliation engine therefore validates the candidate project for dangling relationships and references across evidence links, claims, analysis inputs, decisions, traceability, reproducibility, Canvas, and briefing structures. A candidate with blockers cannot be created.

## Identity and provenance

The intermediate reconciliation candidate retains the selected source-state structure so it can be validated. Final creation passes through the normal Workspace cloning boundary, which creates a fresh local project identity and remaps canonical object/internal relationship identifiers consistently. The resulting project is a new Workspace project, not an in-place merge.

## Governance boundary

- Explicit selection required.
- Human acknowledgement required.
- No automatic selection.
- No automatic merge.
- No automatic overwrite.
- No mutation of either source state.
- Output is always a new local project copy.
- Reconciliation history is browser-local Workspace metadata.

## Schemas

- Workspace storage: 25
- Project: `sc-workspace-project/11.0`
- Reconciliation: `sc-workspace-reconciliation/1.0`
- Reconciliation plan: `sc-workspace-reconciliation-plan/1.0`
