# Deploy Workspace Backend v3.35.0 to Contabo

Production baseline: **v3.34.0**. This release has no database migration.

Upload the full backend archive and deployer from the Mac release directory:

```bash
scp -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes \
  sustainable-catalyst-workspace-backend-v3.35.0.zip \
  DEPLOY_WORKSPACE_BACKEND_V33500_CONTABO.sh \
  catalystadmin@94.72.113.77:/tmp/

ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes \
  catalystadmin@94.72.113.77
```

Then on Contabo:

```bash
cd /tmp
chmod +x DEPLOY_WORKSPACE_BACKEND_V33500_CONTABO.sh
./DEPLOY_WORKSPACE_BACKEND_V33500_CONTABO.sh \
  /tmp/sustainable-catalyst-workspace-backend-v3.35.0.zip
```

The deployer performs pre-switch neural certification, switches the backend/worker/neural-runtime containers, verifies public health and the 69-operation registry, submits an end-to-end GNN evaluation job, verifies the governed GNN artifact, checks container hardening, and restores v3.34.0 automatically if a post-switch step fails.
