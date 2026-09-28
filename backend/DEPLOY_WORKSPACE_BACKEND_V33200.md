# Deploy Workspace Backend v3.32.0

Prerequisite: Workspace v3.31.0 must be deployed and present at `/opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.31.0` with its `.env`; it is the automatic rollback baseline.

```bash
cd /tmp
chmod +x DEPLOY_WORKSPACE_BACKEND_V33200_CONTABO.sh
./DEPLOY_WORKSPACE_BACKEND_V33200_CONTABO.sh /tmp/sustainable-catalyst-workspace-backend-v3.32.0.zip
```

The deployer performs pre-switch production certification, representative cross-capability neural smoke tests, post-switch Workspace certification execution, persisted-artifact retrieval, certification verify/report jobs, receipt-lineage checks, OpenAPI/registry validation, and container-hardening validation. No database migration is required.
