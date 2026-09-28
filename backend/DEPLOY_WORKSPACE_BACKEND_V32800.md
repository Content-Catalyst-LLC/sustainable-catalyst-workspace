# Deploy Workspace Backend v3.28.0

Rollback baseline: Workspace v3.27.0.

```bash
./DEPLOY_WORKSPACE_BACKEND_V32800_CONTABO.sh /tmp/sustainable-catalyst-workspace-backend-v3.28.0.zip
```

The deployer builds the backend/worker/neural images, performs a hardened pre-switch model-package certification, promotes only after that gate passes, then verifies Workspace health, direct neural health, model package artifact persistence, package receipt lineage, packaged inference, prediction provenance, OpenAPI/runtime registry coherence, and container hardening. Any post-switch failure restores v3.27.0.
