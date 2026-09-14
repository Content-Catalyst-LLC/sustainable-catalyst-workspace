# Sustainable Catalyst Workspace Backend v2.4.0

Workspace v2.4.0 adds durable asynchronous execution to the FastAPI + PostgreSQL backend introduced in v2.1.0 and hardened in v2.2.0.

## Added in v2.4.0

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


## v2.4.0 registry endpoints

- `GET/POST /v1/datasets` and dataset revision routes
- `GET/POST /v1/models` and model revision routes
- `GET/POST /v1/parameter-sets` and parameter-set revision routes
- `GET/POST /v1/runs`
- `POST /v1/runs/{run_id}/state`
- `GET /v1/runs/{run_id}/events`
- `GET/POST /v1/runs/{run_id}/outputs`

Execution runs freeze registry references to exact revisions/fingerprints. Jobs may include `executionRunId`; the worker mirrors durable job state into the linked run.
