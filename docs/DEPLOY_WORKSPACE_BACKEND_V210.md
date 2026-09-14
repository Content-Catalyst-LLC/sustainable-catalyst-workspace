# Deploy Workspace Backend v2.1.0

This release introduces a private FastAPI service intended to sit on the same Docker network as the Sustainable Catalyst PostgreSQL service. WordPress remains the browser-facing gateway.

## 1. Prepare the service configuration

Copy `backend/.env.example` to a server-only environment file and set a long random `SC_WORKSPACE_SERVICE_TOKEN` plus the PostgreSQL connection string. Do not expose the service token to browser JavaScript or commit it to Git.

## 2. Database

Create a dedicated Workspace database/user or point the service at an approved PostgreSQL database. Initialize the schema with either:

```bash
python -m app.init_db
```

or the reviewed SQL in `backend/migrations/001_initial.sql`.

## 3. Start the backend

The supplied `backend/docker-compose.example.yml` binds the service to `127.0.0.1:8089` and joins the external `sc-internal` Docker network. Adapt only deployment-specific names/credentials.

Verify locally on the VPS:

```bash
curl -fsS http://127.0.0.1:8089/health | python3 -m json.tool
```

Then verify authenticated readiness from an allowed server context using the configured Bearer token and `X-SC-User-ID` header.

## 4. Install the WordPress v2.1.0 plugin

Install the v2.1.0 WordPress package while leaving the backend bridge disabled. Existing local-first and WordPress `user_meta` behavior remains available in this state.

## 5. Configure the server-only WordPress bridge

In server configuration (not front-end code), define:

```php
define('SC_WORKSPACE_BACKEND_URL', 'http://sc-workspace-backend:8089');
define('SC_WORKSPACE_BACKEND_TOKEN', 'long-random-shared-service-token');
define('SC_WORKSPACE_BACKEND_MODE', 'primary');
```

Before switching to `primary`, check:

- `/wp-json/sc-workspace/v2/backend-contract`
- `/wp-json/sc-workspace/v2/backend-status`

The status response must not expose the token or full internal URL.

## 6. Migration boundary

v2.1.0 deliberately does not bulk-migrate existing `user_meta` project/notebook copies. Keep the old data intact while the dedicated backend is verified. A later migration build should enumerate, validate, fingerprint, copy, reconcile, and receipt legacy server copies before retirement of the old store.

## Rollback

Set `SC_WORKSPACE_BACKEND_MODE` to `disabled` and restore the v2.0.4 WordPress package if the new backend plane must be taken out of service. Browser-local project data is not migrated by this release.
