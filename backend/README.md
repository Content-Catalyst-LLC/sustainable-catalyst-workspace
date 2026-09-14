# Sustainable Catalyst Workspace Backend v2.3.0

Workspace v2.3.0 adds durable asynchronous execution to the FastAPI + PostgreSQL backend introduced in v2.1.0 and hardened in v2.2.0.

## Added in v2.3.0

- PostgreSQL-backed durable job queue
- immutable job-event history
- a separate `sc-workspace-worker` process
- worker heartbeat/status records
- bounded priority, retry, cancel, and idempotency semantics
- local background operations for storage integrity and recovery snapshots
- server-configured cross-product route registry
- `sc-workspace-compute-handoff/1.0` execution envelope
- route adapters for Catalyst Core, Research Lab, Workbench, Decision Studio, Knowledge Library, and Site Intelligence

## Safety boundaries

Browsers cannot supply arbitrary route URLs. Product routes and optional service credentials are configured only through server environment variables. Unconfigured routes become `blocked`; Workspace does not guess endpoints. A completed handoff is not scientific validation or human approval.

## Runtime

The API continues on container port `8089` and VPS loopback `127.0.0.1:8094`. A second container, `sc-workspace-worker`, runs `python -m app.worker` on the same private Docker network and PostgreSQL database. Both containers mount the existing `sc-workspace-data` volume.

## Preserved

The v2.2.0 migration, artifact storage, recovery, project/notebook persistence, and revision contracts remain unchanged. Browser-local projects remain canonical.
