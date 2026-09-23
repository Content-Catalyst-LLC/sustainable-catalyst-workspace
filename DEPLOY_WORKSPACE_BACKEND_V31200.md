# Deploy Workspace Backend v3.12.0

Deploy only after v3.11.0 is live and verified. The deployment copies the v3.11 backend, applies the backend-only v3.12 overlay, builds while v3.11 stays live, runs containerized contract preflight, applies migration 043, switches containers, then verifies health/OpenAPI/R provider/table presence.
