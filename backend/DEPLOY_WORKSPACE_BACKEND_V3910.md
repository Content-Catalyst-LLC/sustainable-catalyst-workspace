# Deploy Workspace Backend v3.9.1

Upload `sustainable-catalyst-workspace-backend-v3.9.1.zip` and `deploy_workspace_backend_v3_9_1_vps.sh` to the VPS. The deployment carries forward the existing Workspace `.env`, requires the v3.9 timeline tables and the Analytics R receipt table, introduces no database migration, rebuilds the backend/worker and hardened R runtime, and verifies Catalyst Analytics R 2.2.0 plus the diagnostics contract.

Final gates:
- Workspace health version 3.9.1
- Catalyst Analytics R provider 2.2.0
- diagnostics contract `sc.analytics-r.statistical-diagnostics-validation.v1`
- typed endpoints 111 with no missing OpenAPI operations
- migration lineage remains 040
- R runtime `ReadonlyRootfs=true User=10001`
