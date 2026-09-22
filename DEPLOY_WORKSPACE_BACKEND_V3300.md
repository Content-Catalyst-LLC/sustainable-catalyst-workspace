# Deploy Workspace backend v3.3.0

Copy `sustainable-catalyst-workspace-backend-v3.3.0.zip` and `deploy_workspace_backend_v3_3_0_vps.sh` to the VPS, then run:

```bash
chmod +x /tmp/deploy_workspace_backend_v3_3_0_vps.sh
bash /tmp/deploy_workspace_backend_v3_3_0_vps.sh /tmp/sustainable-catalyst-workspace-backend-v3.3.0.zip
```

The script validates the Platform Core v3 contract, applies migrations through 034, rebuilds bounded runtime services, checks the 59-endpoint typed-client contract, and verifies the v3.3 binding registry.
