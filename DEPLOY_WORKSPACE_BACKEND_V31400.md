# Deploy Workspace Backend v3.14.0

Baseline: `/opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.13.0`

Upload `sustainable-catalyst-workspace-backend-v3.14.0-overlay.zip` and `deploy_workspace_backend_v3_14_0_vps.sh` to `/tmp`, then run the deployment script with the overlay path.

The script clean-copies v3.13.0, applies and validates the backend-only v3.14 overlay, builds images while v3.13 remains live, performs a containerized OpenAPI/source-integrity preflight, applies migration 045, switches only Workspace containers, checks health/OpenAPI/Analytics R 2.2/runtime hardening/migration tables, and automatically rolls runtime back to v3.13.0 if a post-switch gate fails.

`sc-postgres` is never removed by this script.
