# Deploy Workspace Backend v2.5.0

Upload `sustainable-catalyst-workspace-backend-v2.5.0.zip` to `/tmp` on the VPS, extract it, and run `deploy_workspace_backend_v2_5_0_vps.sh`.

The installer inherits the most recent Workspace `.env`, applies migrations 002–005, repairs v2.4/v2.5 registry privileges, reuses the external `sc-workspace-data` volume, restarts the API/worker, and runs an environment-pinned execution smoke test.
