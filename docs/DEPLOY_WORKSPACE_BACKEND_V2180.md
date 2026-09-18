# Deploy Workspace backend v2.18.0

Upload `sustainable-catalyst-workspace-backend-v2.18.0.zip` to `/tmp` on the Contabo VPS, extract it, and run `deploy_workspace_backend_v2_18_0_vps.sh` with the ZIP path. The deployer preserves the prior `.env`, applies migration 018, provisions the internal forecast runtime credential, rebuilds all Workspace runtimes, and performs a real durable forecast smoke test.
