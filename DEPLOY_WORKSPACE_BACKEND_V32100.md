# Deploy Workspace backend v3.21.0 on Contabo

Baseline backend: v3.20.0. WordPress-only v3.20.0.1 did not create a new backend directory.

```bash
cd /tmp
chmod +x DEPLOY_WORKSPACE_BACKEND_V32100_CONTABO.sh
./DEPLOY_WORKSPACE_BACKEND_V32100_CONTABO.sh /tmp/sustainable-catalyst-workspace-backend-v3.21.0.zip
```

No database migration is required. The script rebuilds/switches the backend, worker and neural runtime, runs an actual transformation job, verifies the 8-operation registry, and rolls back to v3.20.0 if validation fails.
