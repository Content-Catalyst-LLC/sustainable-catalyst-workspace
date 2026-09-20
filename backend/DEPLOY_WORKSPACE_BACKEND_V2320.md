# Workspace Backend v2.32.0 Deployment

Backend-first deployment is required. No new database migration is introduced; migration lineage remains through `029_local_first_synchronization_protocol.sql`.

From macOS:

```bash
cd ~/Downloads
scp -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes \
  sustainable-catalyst-workspace-backend-v2.32.0.zip \
  catalystadmin@94.72.113.77:/tmp/
ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes catalystadmin@94.72.113.77
```

On the VPS:

```bash
cd /tmp
rm -rf sc-workspace-v2.32.0-deploy
mkdir -p sc-workspace-v2.32.0-deploy
unzip -q sustainable-catalyst-workspace-backend-v2.32.0.zip -d sc-workspace-v2.32.0-deploy
cd sc-workspace-v2.32.0-deploy/sustainable-catalyst-workspace-backend-v2.32.0
chmod +x deploy_workspace_backend_v2_32_0_vps.sh
./deploy_workspace_backend_v2_32_0_vps.sh /tmp/sustainable-catalyst-workspace-backend-v2.32.0.zip
```
