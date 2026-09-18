# Deploy Workspace Backend v2.19.0

Upload `sustainable-catalyst-workspace-backend-v2.19.0.zip` to `/tmp`, extract it, and run `deploy_workspace_backend_v2_19_0_vps.sh` with the ZIP path. The deployer preserves the existing `.env`, applies all idempotent migrations including 019, rebuilds the backend/worker/runtime stack, and validates the probabilistic runtime, durable Bayesian job result, and receipt registry.
