# Frontend Logic Reduction & Legacy JS Retirement — v2.35.0

## Primary browser boundary

The active `workspace-v2.35.0.js` runtime is a thin coordinator. It owns presentation bootstrap, interaction routing, transient UI state coordination, and explicit draft/outbox handoff only.

## Backend authority

Scientific meaning, canonical persistence, authorization, revision/conflict decisions, handoff validation, provenance authority, and scientific execution remain server-owned.

## Legacy compatibility

The prior local-project runtime is isolated in `sc-workspace-local-project-compat-v2350.js` and loaded only for guest/local mode or when existing browser-local Workspace data is detected. It is explicitly non-authoritative for server state.

## Asset retirement

Historical `workspace-v*` JavaScript and CSS release files are removed from the active WordPress package. Only the v2.35 shell/style remain, plus the isolated local-project compatibility bundle.

## Package integrity

Release asset checks derive current JS/CSS names from `SC_WORKSPACE_VERSION` rather than hard-coding a prior release.
