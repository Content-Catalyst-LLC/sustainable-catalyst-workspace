# Deploy Workspace backend v3.19.0

Baseline directory: `/opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.18.0`  
Target directory: `/opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.19.0`

The deployment script copies the verified v3.18 backend, applies the backend-only v3.19 overlay, builds/preflights while v3.18 remains live, applies migration 050 to `sc_workspace`, switches only `sc-workspace-*` containers, preserves `sc-postgres`, checks health/OpenAPI/Analytics R/container hardening/migration tables, and automatically restores the v3.18 Workspace runtime if a post-switch gate fails.
