# Deploy Workspace backend v2.12.0

Upload `sustainable-catalyst-workspace-backend-v2.12.0.zip` to `/tmp`, extract it, and run `deploy_workspace_backend_v2_12_0_vps.sh`. The deployment reuses the existing Workspace `.env`, applies migrations through 012, rebuilds the API/worker, checks the runtime catalog, and executes a bounded SQL aggregate job through the durable queue.

R, Julia, and WASM runtime URLs are optional in v2.12. They remain disabled until their server-side runtime services are configured.
