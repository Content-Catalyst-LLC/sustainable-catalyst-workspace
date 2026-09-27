# Deploy Workspace backend v3.20.0

Baseline directory: `/opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.19.0`  
Target directory: `/opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.20.0`

v3.20.0 adds the `sc-workspace-neural-runtime` PyTorch service and upgrades the Workspace backend/worker runtime catalog. No database migration is required.

The deployment script:

1. expands the full v3.20.0 backend package into the versioned target directory;
2. preserves the verified v3.19.0 `.env`;
3. guarantees a neural runtime bearer token exists in the target `.env`;
4. builds the new neural service plus backend and worker;
5. switches only `sc-workspace-neural-runtime`, `sc-workspace-backend`, and `sc-workspace-worker`;
6. verifies backend health, the authenticated neural status route, direct neural runtime health, a real bounded neural job, receipt persistence, typed OpenAPI completeness, and container hardening;
7. restores the v3.19.0 backend/worker and removes the v3.20 neural service if a post-switch validation gate fails.
