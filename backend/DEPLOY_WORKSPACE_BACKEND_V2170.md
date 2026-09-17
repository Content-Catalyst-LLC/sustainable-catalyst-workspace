# Deploy Workspace backend v2.17.0

Upload `sustainable-catalyst-workspace-backend-v2.17.0.zip` to `/tmp`, extract it, then run:

```bash
./deploy_workspace_backend_v2_17_0_vps.sh /tmp/sustainable-catalyst-workspace-backend-v2.17.0.zip
```

The deployer preserves the existing `.env`, applies migrations through 017, rebuilds the existing Python/R/Julia/ML/Arrow-Parquet stack, validates the prior runtime gates, then performs a real database-backed tolerance-aware cross-runtime verification and checks the public verification profile API.
