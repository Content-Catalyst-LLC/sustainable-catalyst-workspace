# Deploy Workspace Backend v2.24.0

Upload `sustainable-catalyst-workspace-backend-v2.24.0.zip` to `/tmp` on the Workspace VPS, extract it, then run:

```bash
chmod +x deploy_workspace_backend_v2_24_0_vps.sh
./deploy_workspace_backend_v2_24_0_vps.sh /tmp/sustainable-catalyst-workspace-backend-v2.24.0.zip
```

The deployment applies migration `024_backend_authority_domain_service.sql`, rebuilds the inherited bounded runtime fabric, verifies backend health identity, validates the domain-authority profile, performs server-side project validation, persists an authoritative sync revision, verifies its durable mutation receipt, and removes the smoke-test project.

A successful run ends with:

```text
PASS: Workspace backend v2.24.0 API + authoritative domain state + mutation receipts + inherited scientific runtime fabric are running.
```
