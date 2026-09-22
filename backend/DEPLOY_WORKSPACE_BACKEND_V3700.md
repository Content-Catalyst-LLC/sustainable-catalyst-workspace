# Deploy Workspace Backend v3.7.0

## Release

**Workspace v3.7.0 — Claims, Evidence & Investigative Research Workspace**

This is an additive deployment over the verified v3.6.0 backend. It preserves the v3.6 visual-research layer and the v3.5 Catalyst Analytics R 2.1.0 provider.

## Database lineage

- Workspace database: `sc_workspace`
- Prior migration: `037_platform_core_visual_analysis_research_object_workspace.sql`
- New migration: `038_claims_evidence_investigative_research_workspace.sql`
- Rollback baseline: `3.6.0`

Migration 038 is additive and idempotent. If a later deployment gate fails, the runtime rollback can restore v3.6 containers while the additive v3.7 tables remain unused by v3.6.

## Upload from macOS

```bash
cd ~/Downloads/sc-workspace-v3.7.0-release

scp -i ~/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes \
  sustainable-catalyst-workspace-backend-v3.7.0-overlay.zip \
  deploy_workspace_backend_v3_7_0_vps.sh \
  catalystadmin@94.72.113.77:/tmp/
```

Connect:

```bash
ssh -i ~/.ssh/id_ed25519 \
  -o IdentitiesOnly=yes \
  catalystadmin@94.72.113.77
```

Deploy:

```bash
chmod +x /tmp/deploy_workspace_backend_v3_7_0_vps.sh

bash /tmp/deploy_workspace_backend_v3_7_0_vps.sh \
  /tmp/sustainable-catalyst-workspace-backend-v3.7.0-overlay.zip
```

## Expected production acceptance

```text
WORKSPACE_V370_HEALTH=PASS
WORKSPACE_V370_OPENAPI=PASS typed_endpoints=87
CATALYST_ANALYTICS_R_PROVIDER=PASS
ReadonlyRootfs=true User=10001
WORKSPACE_V370_MIGRATION_038=PASS
PASS: Workspace v3.7.0 backend deployed; v3.6 visual research and Analytics R v3.5 preserved; investigative research layer active
```

The endpoint count may be greater than 87 if later compatible endpoints exist; the deployment gate requires at least 87.
