# Deploy Workspace backend v2.13.0

Deploy with `scripts/deploy_workspace_backend_v2_13_0_vps.sh` or the copy included at the root of the backend ZIP.

The installer snapshots the existing Workspace `.env`, creates an R runtime bearer token only if one does not already exist, configures the R service on the private runtime network, applies additive migrations through 013, rebuilds the backend/worker/R containers, and executes a real bounded R linear-model smoke job.
