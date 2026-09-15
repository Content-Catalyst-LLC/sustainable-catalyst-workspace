# Deploy Workspace backend v2.16.0

Upload `sustainable-catalyst-workspace-backend-v2.16.0.zip` to `/tmp`, extract it, then run `deploy_workspace_backend_v2_16_0_vps.sh /tmp/sustainable-catalyst-workspace-backend-v2.16.0.zip`. The script preserves the existing `.env`, provisions an interchange runtime token if needed, applies migration 016, rebuilds the backend/worker/runtime services, and verifies a real Parquet round-trip plus receipt persistence.
