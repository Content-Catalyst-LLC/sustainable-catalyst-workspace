# Sustainable Catalyst Workspace v3.4.0

## Scientific Execution & Provenance Workspace

Workspace v3.4.0 turns backend execution records into a project-level scientific provenance surface. It resolves each execution run to the exact dataset/model/parameter/environment/runtime-adapter references used, projects output artifact digests and scientific runtime receipts, exposes the run's Platform Core research-session binding, and emits an explicit provenance graph without moving authority away from the specialist stores.

### Added
- `GET /v1/execution-provenance`
- `GET /v1/execution-provenance/projects/{project_id}`
- `GET /v1/execution-provenance/projects/{project_id}/runs/{run_id}`
- `POST /v1/execution-provenance/projects/{project_id}/snapshots`
- `GET /v1/execution-provenance/projects/{project_id}/snapshots`
- migration `035_scientific_execution_provenance_workspace.sql`
- immutable execution-provenance snapshot registry
- 64-operation OpenAPI-derived typed client surface
- WordPress server proxy and browser adapter for execution provenance
- execution provenance embedded into Unified Research Project Context

### Deployment hardening
The Workspace runtime bridge now uses the stable Docker network name `sc-workspace-runtime`. The v3.4 deploy script removes only empty legacy versioned Workspace runtime networks before Compose starts, preventing Docker default-address-pool exhaustion seen during v3.3 deployment.

### Authority boundary
Workspace remains authoritative for execution records and scientific receipts. Platform Core remains authoritative for cross-product research-session registration. v3.4 does not copy execution-object bodies into Core, execute arbitrary code, interpret scientific results automatically, rank evidence, or make decisions.
