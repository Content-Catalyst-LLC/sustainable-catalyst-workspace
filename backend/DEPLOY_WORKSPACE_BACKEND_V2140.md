# Deploy Workspace Backend v2.14.0

Deploy with `scripts/deploy_workspace_backend_v2_14_0_vps.sh`. The installer carries forward prior Workspace credentials, creates/preserves a Julia runtime token, applies additive migrations through 014, rebuilds API/worker/R/Julia services, and executes a durable Julia RK4 smoke model.
