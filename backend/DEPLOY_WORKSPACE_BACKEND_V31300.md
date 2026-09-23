# Deploy Workspace Backend v3.13.0

Deploy only after v3.12.0 is live and verified. The deployment copies the v3.12 backend, applies the backend-only v3.13 overlay, builds images while v3.12 remains live, runs an in-image OpenAPI/media-contract preflight, applies migration 044, switches only `sc-workspace-*` containers, and verifies health, OpenAPI, Analytics R 2.2.0, runtime hardening, and migration tables. `sc-postgres` is never removed.
