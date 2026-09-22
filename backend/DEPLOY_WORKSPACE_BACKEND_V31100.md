# Deploy Workspace Backend v3.11.0

Prerequisite: verified v3.10.0 backend at `/opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.10.0`.

The deployment script:
1. clones the v3.10.0 backend directory into a v3.11.0 release directory;
2. applies and validates the backend-only overlay;
3. builds Docker images while v3.10 remains live;
4. runs the v3.11 OpenAPI/documentary preflight inside the new backend image;
5. applies additive migration 042 to `sc_workspace`;
6. switches Workspace containers to v3.11;
7. validates health, 150+ typed endpoints, documentary capability flags, Analytics R 2.2.0, runtime hardening, and migration tables;
8. rolls back runtime containers to v3.10 if post-switch gates fail.

The script never removes `sc-postgres`.
