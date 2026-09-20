# Deploy Workspace Backend v2.34.0

Deploy the backend ZIP before WordPress or Git patch updates.

```bash
cd /tmp
rm -rf sc-workspace-v2.34.0-deploy
mkdir -p sc-workspace-v2.34.0-deploy
unzip -q sustainable-catalyst-workspace-backend-v2.34.0.zip -d sc-workspace-v2.34.0-deploy
cd sc-workspace-v2.34.0-deploy/sustainable-catalyst-workspace-backend-v2.34.0
chmod +x deploy_workspace_backend_v2_34_0_vps.sh
./deploy_workspace_backend_v2_34_0_vps.sh /tmp/sustainable-catalyst-workspace-backend-v2.34.0.zip
```

The deployer applies migration 031, verifies the authorization receipt privilege, rebuilds the inherited bounded runtime fabric, and performs a server-resolved identity/default-deny authorization smoke test.
