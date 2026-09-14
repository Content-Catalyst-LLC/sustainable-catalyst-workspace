# Sustainable Catalyst Workspace Backend v2.1.0

This service adds the first dedicated server-side runtime for Workspace while preserving the v2.0.4 local-first product contract.

## Responsibilities

- PostgreSQL persistence for explicit Workspace project and notebook backup/sync heads.
- Append-only server revision history for every accepted project/notebook write.
- Revision-precondition conflict protection and idempotent operation replay.
- SHA-256 package and canonical object fingerprints.
- WordPress-proxied account isolation: browsers do not receive the service token and do not address the backend directly.
- Health, readiness, and capability endpoints.

## Non-goals for v2.1.0

No background sync, automatic upload, live collaboration, object storage, background job queue, compute execution, automatic AI, or project-schema migration. Browser-local projects remain canonical unless the user explicitly invokes backup/sync.

## VPS deployment shape

Run the service on the existing private `sc-internal` Docker network. Bind its host port to loopback only (example: `127.0.0.1:8089`) or omit host publication entirely when WordPress can reach it through the private network. Do not expose the service token to browser JavaScript.

Required environment variables:

- `SC_WORKSPACE_DATABASE_URL`
- `SC_WORKSPACE_SERVICE_TOKEN`

Then initialize/start the service and verify:

```bash
curl -fsS http://127.0.0.1:8089/health | python3 -m json.tool
curl -fsS http://127.0.0.1:8089/ready | python3 -m json.tool
```

The WordPress bridge is opt-in. Define these in server-side WordPress configuration, not in page HTML:

```php
define('SC_WORKSPACE_BACKEND_URL', 'http://sc-workspace-backend:8089');
define('SC_WORKSPACE_BACKEND_TOKEN', 'replace-with-the-same-long-random-token');
define('SC_WORKSPACE_BACKEND_MODE', 'primary');
```

`primary` is fail-closed: if the configured backend cannot complete a request, Workspace does not silently write the same operation into WordPress `user_meta`.
