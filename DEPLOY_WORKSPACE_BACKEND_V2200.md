# Deploy Workspace Backend v2.20.0

Upload `sustainable-catalyst-workspace-backend-v2.20.0.zip` to `/tmp`, extract it, and run `deploy_workspace_backend_v2_20_0_vps.sh` with the ZIP path. The deployer preserves the existing `.env`, applies all idempotent migrations through 020, rebuilds the backend/worker/runtime stack, and validates the uncertainty runtime, a durable seeded Monte Carlo job result, receipt discovery, and runtime sandbox.
