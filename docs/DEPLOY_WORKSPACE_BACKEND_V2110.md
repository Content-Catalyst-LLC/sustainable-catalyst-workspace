# Deploy Workspace Backend v2.11.0

Upload `sustainable-catalyst-workspace-backend-v2.11.0.zip` to `/tmp` on the Contabo VPS, then run:

```bash
cd /tmp
rm -rf sc-workspace-v2.11.0-deploy
mkdir -p sc-workspace-v2.11.0-deploy
unzip -q sustainable-catalyst-workspace-backend-v2.11.0.zip -d sc-workspace-v2.11.0-deploy
cd sc-workspace-v2.11.0-deploy/sustainable-catalyst-workspace-backend-v2.11.0
chmod +x deploy_workspace_backend_v2_11_0_vps.sh
./deploy_workspace_backend_v2_11_0_vps.sh /tmp/sustainable-catalyst-workspace-backend-v2.11.0.zip
```

The installer snapshots the newest existing Workspace `.env`, applies additive migrations through 011, rebuilds API + worker, verifies the seven-operation scientific catalog, queues a real NumPy solve job, waits for the durable worker, verifies `[3.0, 2.0]`, checks progress events, confirms the content-addressed result artifact and compute receipt, and inspects the worker sandbox envelope.
