# Sustainable Catalyst Workspace v2.3.0 — Background Jobs & Compute Orchestration Foundation

v2.3.0 adds a durable PostgreSQL-backed background-job plane and separate Python worker on top of the v2.2.0 persistence/object-storage backend. Workspace now owns job state, retry/cancel semantics, event history, worker health, and server-configured cross-product routing while preserving local-first project ownership and existing Workspace schemas.

See `RELEASE_NOTES_2.3.0.md`, `docs/BACKGROUND_JOBS_COMPUTE_ORCHESTRATION_V230.md`, `docs/DEPLOY_WORKSPACE_BACKEND_V230.md`, `VALIDATION_REPORT_2.3.0.md`, and `backend/README.md`.
