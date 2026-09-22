# Deploy Workspace Backend v3.4.0

Copy `sustainable-catalyst-workspace-backend-v3.4.0.zip` and `deploy_workspace_backend_v3_4_0_vps.sh` to `/tmp` on the Contabo VPS, then run the deploy script with the ZIP path.

The script preserves the existing Workspace `.env`, verifies Platform Core v3 compatibility, applies migrations through `035_scientific_execution_provenance_workspace.sql`, removes only empty legacy Workspace runtime networks, rebuilds the bounded runtime fabric, verifies the 64-operation typed contract, and validates the v3.4 execution-provenance profile and database privileges.
