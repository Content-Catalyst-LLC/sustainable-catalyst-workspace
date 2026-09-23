# Deploy Workspace Backend v3.16.0

Use the v3.16 backend overlay only after v3.15.0 is the verified production baseline.

```bash
scp -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes \
  sustainable-catalyst-workspace-backend-v3.16.0-overlay.zip \
  deploy_workspace_backend_v3_16_0_vps.sh \
  catalystadmin@94.72.113.77:/tmp/

ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes catalystadmin@94.72.113.77

chmod +x /tmp/deploy_workspace_backend_v3_16_0_vps.sh
bash /tmp/deploy_workspace_backend_v3_16_0_vps.sh \
  /tmp/sustainable-catalyst-workspace-backend-v3.16.0-overlay.zip
```

The deployment builds and preflights v3.16 before switching the Workspace containers, applies additive migration 047 to `sc_workspace`, preserves `sc-postgres`, validates Analytics R 2.2.0, and rolls the Workspace runtime back to v3.15.0 if a post-switch acceptance gate fails.
