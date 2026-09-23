# Deploy Workspace Backend v3.18.0

Baseline: verified Workspace backend v3.17.0 at `/opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.17.0`.

The deployment script:

1. copies the verified v3.17 backend to a new v3.18 directory;
2. applies and validates the backend-only v3.18 overlay;
3. builds v3.18 images while v3.17 remains live;
4. runs a containerized OpenAPI/causal-workspace preflight;
5. applies additive migration 049 to `sc_workspace`;
6. switches only `sc-workspace-*` containers and never removes `sc-postgres`;
7. validates health, OpenAPI, causal boundaries, Catalyst Analytics R 2.2, runtime hardening, and all eight migration tables;
8. automatically returns the Workspace runtime to v3.17 if a post-switch acceptance gate fails.

Command:

```bash
bash /tmp/deploy_workspace_backend_v3_18_0_vps.sh /tmp/sustainable-catalyst-workspace-backend-v3.18.0-overlay.zip
```
