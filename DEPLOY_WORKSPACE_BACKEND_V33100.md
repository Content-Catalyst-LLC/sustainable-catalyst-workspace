# Deploy Workspace Backend v3.31.0

The standard Contabo deployment keeps the remote GPU broker disabled and requires Workspace v3.30.0 as the rollback baseline.

```bash
./DEPLOY_WORKSPACE_BACKEND_V33100_CONTABO.sh /tmp/sustainable-catalyst-workspace-backend-v3.31.0.zip
```

The deployer builds the v3.31 images, runs a pre-switch broker/signature certification, promotes the release, verifies backend/neural health, submits a real remote-worker-inventory Workspace job, verifies its polyglot receipt, checks the 48-operation registry, and rechecks container hardening.

A real remote GPU worker is configured separately after v3.31 production certification. See `REMOTE_GPU_WORKER_DEPLOYMENT_V33100.md`.
