# Sustainable Catalyst Workspace v2.1.0 — Backend Foundation & Persistence Bridge

Workspace v2.1.0 adds the first dedicated FastAPI + PostgreSQL backend and a server-only WordPress persistence bridge while preserving the v2.0.4 local-first product contract.

## Added

- Dedicated `backend/` FastAPI service for VPS deployment.
- PostgreSQL project and notebook persistence.
- Append-only server revision history for accepted project/notebook writes.
- Existing revision-preconditioned sync and idempotent operation semantics.
- SHA-256 package and Workspace-compatible project fingerprints.
- Service-token authentication between WordPress and the private backend.
- WordPress backend configuration/status contract.
- Fail-closed `primary` backend mode; no silent fallback writes.
- Configurable backend storage limits substantially beyond the legacy WordPress `user_meta` defaults.

## Preserved

- Storage 35.
- `sc-workspace-project/20.0` and `sc-workspace-project-export/20.0`.
- Existing browser-facing `/wp-json/sc-workspace/v1/cloud-projects` and `/cloud-notebooks` routes.
- Guest/local Workspace access.
- Explicit enrollment and explicit sync only.
- No background upload, automatic merge, automatic AI, behavioral telemetry, or query telemetry.

## Migration and rollback

There is no automatic migration of existing account copies stored in WordPress `user_meta`. The dedicated backend is opt-in and defaults to disabled until configured. Exact rollback baseline: v2.0.4.
