# Workspace Projects & Persistent Work — v0.2.0

## Purpose

Workspace Projects provide a durable local container for work that moves across Sustainable Catalyst. The model intentionally precedes server accounts, collaboration, and cloud storage so the public Workspace can remain free and low-friction.

## Storage contract

- Storage engine: browser `localStorage`.
- Canonical storage key: `sc_workspace`.
- Storage schema version: `2`.
- Legacy source: `sc_workspace_v0_1`.
- Project schema: `sc-workspace-project/1.0`.
- Project export schema: `sc-workspace-project-export/1.0`.
- Handoff schema: `sc-workspace-handoff/1.0`.

Project content is not transmitted to Sustainable Catalyst by the Workspace plugin. Export is explicit and user-initiated.

## Project fields

Each project carries a stable ID, title, description, status, pin state, created/updated/archive timestamps, notes, recent tools, and bounded activity history. Titles can change without changing the project identity.

## Recovery

Unreadable local state is copied into `sc_workspace_recovery_v0_2` when browser storage permits. Workspace then opens a clean in-memory/local state and displays a recovery notice. The release never attempts to execute or reinterpret corrupted project text.

## Cross-product handoff

When an active project launches another Sustainable Catalyst tool, Workspace stores a short-lived handoff envelope in `sessionStorage` and adds only these query fields:

- `sc_workspace_project`
- `sc_workspace_origin=workspace`
- `sc_workspace_return=1`

No project title, description, notes, activity, or imported content is placed into the target URL.

## Deferred beyond v0.2.0

Accounts, server project persistence, cross-device sync, collaboration, permissions, comments, shared projects, and institutional tenancy remain explicitly out of scope.
