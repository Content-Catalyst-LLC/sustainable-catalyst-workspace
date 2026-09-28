# Deploy Workspace backend v3.26.0

Rollback baseline: v3.25.0. No database migration is required. The deployer builds the backend/worker/neural images, runs a pre-switch embedding/representation certification, promotes v3.26.0, then verifies an end-to-end governed embedding artifact and nearest-neighbor representation artifact before final hardening/OpenAPI checks.
