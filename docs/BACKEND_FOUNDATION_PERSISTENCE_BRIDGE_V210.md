# Workspace v2.1.0 — Backend Foundation & Persistence Bridge

## Purpose

Workspace v2.1.0 introduces the first dedicated Workspace backend without abandoning the local-first ownership and explicit-sync boundaries established across the 1.x and 2.0 product lines.

The v2.0.4 browser application remains authoritative on-device. The backend is a server persistence and revision plane for user-initiated account backup/sync; it is not allowed to silently upload, mutate, merge, or execute project content.

## Backend runtime

The new `backend/` service is a FastAPI application intended for the Sustainable Catalyst VPS private service network. PostgreSQL stores project/notebook heads and append-only accepted revisions. The service provides:

- `/health` — process/service health without database dependency.
- `/ready` — database and service-auth readiness.
- `/v1/capabilities` — authenticated runtime capabilities and configured limits.
- `/v1/projects` and `/v1/projects/{project_id}` — compatible project persistence.
- `/v1/projects/{project_id}/revisions` — server revision metadata.
- `/v1/projects/{project_id}/revisions/{revision}` — one retained server revision.
- `/v1/notebooks` and `/v1/notebooks/{notebook_id}` — compatible notebook persistence.

Every accepted write retains a SHA-256 package fingerprint and an explicit monotonically increasing server revision. Existing sync pushes retain the revision-precondition and idempotent-operation boundaries already used by Workspace.

## WordPress bridge

The WordPress plugin adds `SC_Workspace_Backend`, a server-only bridge. Browser JavaScript continues to call the existing WordPress routes; it never receives the backend service token and does not need a new client API.

Configuration is intentionally explicit:

```php
define('SC_WORKSPACE_BACKEND_URL', 'http://sc-workspace-backend:8089');
define('SC_WORKSPACE_BACKEND_TOKEN', 'long-random-shared-service-token');
define('SC_WORKSPACE_BACKEND_MODE', 'primary');
```

When the mode is `disabled` (the default), v2.0.4 WordPress `user_meta` persistence remains active. When the mode is `primary`, project/notebook cloud routes proxy to the dedicated backend and fail closed if that backend is unavailable. They do not silently fall back to `user_meta`, preventing split-brain server state.

The public diagnostic contracts are:

- `/wp-json/sc-workspace/v2/backend-contract`
- `/wp-json/sc-workspace/v2/backend-status`

No secret, backend token, or full backend URL is returned by those contracts.

## Compatibility

- Storage remains `35`.
- Project schema remains `sc-workspace-project/20.0`.
- Project export remains `sc-workspace-project-export/20.0`.
- Existing v1 cloud project/notebook WordPress REST routes remain the browser-facing API.
- Presentation/runtime assets are promoted from the v2.0.4 baseline without behavioral changes.
- There is no automatic migration of existing WordPress account backups.
- Rollback baseline is v2.0.4.

## Deliberately deferred

Object/blob storage, background jobs, compute orchestration, server-side search/indexing, collaboration, institutional tenancy, and backend-native project objects are not introduced in v2.1.0. Those should be layered on after the persistence plane is deployed and verified.
