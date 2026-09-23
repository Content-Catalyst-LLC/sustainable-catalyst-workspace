# Deploy Workspace v3.17.0 Backend

Baseline directory: `/opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.16.0`

Target directory: `/opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.17.0`

The deployment script copies the verified v3.16 backend, applies the backend-only v3.17 overlay, validates Python/OpenAPI/contracts in the newly built backend image while v3.16 remains live, applies migration 048 to `sc_workspace`, switches only `sc-workspace-*` containers, validates health/OpenAPI/Analytics R/runtime hardening/table lineage, and automatically returns the runtime to v3.16 if a post-switch gate fails.

`sc-postgres` is never removed by the deployment script.
