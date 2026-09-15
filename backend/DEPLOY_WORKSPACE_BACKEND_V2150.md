# Deploy Workspace Backend v2.15.0

Artifact: `sustainable-catalyst-workspace-backend-v2.15.0.zip`

## From macOS

```bash
cd ~/Downloads

scp -i ~/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes \
  sustainable-catalyst-workspace-backend-v2.15.0.zip \
  catalystadmin@94.72.113.77:/tmp/

ssh -i ~/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes \
  catalystadmin@94.72.113.77
```

## On the VPS

```bash
cd /tmp
rm -rf sc-workspace-v2.15.0-deploy
mkdir -p sc-workspace-v2.15.0-deploy

unzip -q \
  sustainable-catalyst-workspace-backend-v2.15.0.zip \
  -d sc-workspace-v2.15.0-deploy

cd sc-workspace-v2.15.0-deploy/sustainable-catalyst-workspace-backend-v2.15.0
chmod +x deploy_workspace_backend_v2_15_0_vps.sh

./deploy_workspace_backend_v2_15_0_vps.sh \
  /tmp/sustainable-catalyst-workspace-backend-v2.15.0.zip
```

The deployer preserves the prior Workspace `.env`, provisions an ML service token when needed, applies migrations through 015, rebuilds the API/worker/R/Julia/ML services, verifies the repaired Julia runtime, runs a durable linear-regression ML job, verifies model/evaluation receipts, and asserts the ML sandbox.

Expected final line:

```text
PASS: Workspace backend v2.15.0 API + worker + R + Julia + predictive analytics/ML runtimes are running.
```
