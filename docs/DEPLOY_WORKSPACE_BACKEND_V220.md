# Deploy Workspace Backend v2.2.0

v2.2.0 upgrades the running v2.1.0 Workspace backend. The existing PostgreSQL database role/database and service token are reused. The example compose file binds Workspace to `127.0.0.1:8094` and adds the persistent Docker volume `sc-workspace-data`.

## Recommended order

1. Apply and push the v2.2.0 repository patch.
2. Upload the v2.2.0 backend package to the VPS.
3. Replace the backend source directory while preserving `.env`.
4. Rebuild/restart `sc-workspace-backend`.
5. Verify `/health`, `/ready`, `/v1/capabilities`, and `/v1/storage/integrity`.
6. Install the v2.2.0 WordPress package.
7. Keep `SC_WORKSPACE_BACKEND_MODE` unchanged while planning migration.
8. Run `/wp-json/sc-workspace/v2/backend-migration/plan` while signed in.
9. Apply only when `safeToApply` is true.
10. Confirm a migration receipt and create a recovery snapshot.

## Safety

Migration does not delete WordPress `user_meta`. Divergent backend records block apply with HTTP 409. Existing browser-local Workspace data is unaffected.
