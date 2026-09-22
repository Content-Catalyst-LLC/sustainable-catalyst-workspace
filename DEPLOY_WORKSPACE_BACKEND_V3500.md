# Deploy Workspace Backend v3.5.0

Upload `sustainable-catalyst-workspace-backend-v3.5.0.zip` and `deploy_workspace_backend_v3_5_0_vps.sh` to the VPS, then run the deploy script against the ZIP. The script carries forward the previous `.env`, applies migrations through `036_catalyst_analytics_r_runtime_adapter.sql`, rebuilds the hardened R image with Catalyst Analytics R 2.1.0 installed, verifies the provider contract, and confirms the read-only/non-root production runtime boundary.
