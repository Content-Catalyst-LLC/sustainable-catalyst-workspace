# Sustainable Catalyst Workspace v2.3.0 — Background Jobs & Compute Orchestration Foundation

Workspace v2.3.0 adds the first durable asynchronous execution plane on top of the v2.2.0 PostgreSQL/object-storage backend. It does not move scientific engines into Workspace. Instead, Workspace now owns durable job state, worker execution, event history, retry/cancel semantics, and bounded cross-product routing contracts.

## Added

- PostgreSQL-backed `workspace_jobs`, `workspace_job_events`, and `workspace_worker_heartbeats` records.
- A separate `sc-workspace-worker` process so long-running work does not execute in the web request process.
- Explicit job states: queued, running, blocked, succeeded, failed, and cancelled.
- Immutable job event history and worker heartbeat/status reporting.
- Idempotency keys, retry bounds, cancellation requests, priorities, and per-account job limits.
- Local background operations for echo/diagnostics, storage-integrity verification, and recovery-snapshot creation.
- A server-configured orchestration route registry for Catalyst Core, Research Lab, Workbench, Decision Studio, Knowledge Library, and Site Intelligence.
- `sc-workspace-compute-handoff/1.0` as the first generic Workspace-to-product execution envelope.
- WordPress REST proxy routes for job submission, status, event history, cancel/retry, worker status, and orchestration route status.

## Safety and architecture boundaries

- Browsers cannot supply arbitrary execution URLs.
- Cross-product URLs and optional service credentials are configured only on the server.
- Unconfigured routes become `blocked`; Workspace does not guess product endpoints.
- A successful handoff receipt is not human approval and does not imply scientific validity.
- Browser-local projects remain canonical on-device.
- Existing Storage 35, Project 20.0, Export 20.0, cloud backup, sync, migration, artifact, and recovery contracts are preserved.

## Rollback

The compatible rollback baseline is Workspace v2.2.0. The v2.3.0 job tables are additive and may remain in PostgreSQL during rollback.
