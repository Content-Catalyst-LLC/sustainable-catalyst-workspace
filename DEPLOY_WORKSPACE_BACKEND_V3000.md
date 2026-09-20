# Deploy Workspace Backend v3.0.0

Deploy backend first using `backend/deploy_workspace_backend_v3_0_0_vps.sh`, then install the WordPress package and apply the Git patch. No new migration is introduced; existing migrations through 031 remain replay-safe. Rollback baseline is v2.36.0.
