# Deploy Workspace Backend v3.15.0

Baseline: `/opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.14.0`

Upload the backend overlay and deployment script to `/tmp`, then run:

```bash
chmod +x /tmp/deploy_workspace_backend_v3_15_0_vps.sh
bash /tmp/deploy_workspace_backend_v3_15_0_vps.sh \
  /tmp/sustainable-catalyst-workspace-backend-v3.15.0-overlay.zip
```

Acceptance gates:

- `WORKSPACE_V31500_PREFLIGHT=PASS typed_endpoints=218`
- `WORKSPACE_V31500_HEALTH=PASS`
- `WORKSPACE_V31500_OPENAPI=PASS typed_endpoints=218`
- `CATALYST_ANALYTICS_R_V220_PROVIDER=PASS`
- `ReadonlyRootfs=true User=10001`
- `WORKSPACE_V31500_MIGRATION_046=PASS`

The script never removes `sc-postgres`. Runtime rollback returns Workspace containers to v3.14.0 if a post-switch gate fails.
