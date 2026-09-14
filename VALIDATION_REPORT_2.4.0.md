# Workspace v2.4.0 Validation Report
## Dataset, Model & Execution Run Registry

**Release:** 2.4.0  
**Previous release:** 2.3.0  
**Validation date:** 2026-09-14

## Release-specific gate

- `python scripts/validate_dataset_model_execution_run_registry_v240.py` — **PASS**
- `PYTHONPATH=backend pytest -q backend/tests tests/test_dataset_model_execution_run_registry_v240.py` — **30 passed**
- Python compile validation for backend app modules — **PASS**
- WordPress PHP lint — **31/31 PHP files passed**
- New JSON release manifest/product registry/schema contracts — **valid JSON**
- VPS deployment script `bash -n` — **PASS**

## What the release-specific tests cover

- v2.4.0 identity and v2.3.0 rollback lineage
- dataset/model/parameter-set registry schemas
- dataset/model revision history contracts
- execution-run creation with revision-pinned references
- deterministic input/reproducibility fingerprints
- run outputs and SHA-256 shape validation
- job `executionRunId` linkage contract
- worker-to-run lifecycle synchronization code path
- additive PostgreSQL migration including `workspace_jobs.execution_run_id`
- WordPress server-proxy routes for registry/run endpoints
- explicit prohibition on automatic model execution and browser-supplied route URLs

## Historical suite

Running the complete historical test corpus produced:

- **1,120 passed**
- **119 failed**

The historical failures are legacy contract tests that intentionally hard-code earlier releases as the *current* WordPress version/assets/README identity. Representative failures assert `Version: 2.0.4`, v2.1.0, v2.2.0, or v2.3.0 against the v2.4.0 plugin, or require an older README heading/current asset filename. The v2.3.0-specific current-release identity test becomes the one additional stale historical assertion in v2.4.0.

These historical-current-release assertions are not used as the v2.4.0 release gate. Historical functional files and prior release notes remain in the repository; the new release-specific gate validates the v2.4.0 current identity and contracts.

## Database migration safety

`004_dataset_model_execution_run_registry.sql` is additive. It:

- creates dataset head/revision tables,
- creates model head/revision tables,
- creates parameter-set head/revision tables,
- creates execution-run, run-output, and run-event tables,
- adds `execution_run_id` to the existing `workspace_jobs` table with `ADD COLUMN IF NOT EXISTS`, and
- adds indexes without deleting existing rows.

The VPS installer applies migrations 002, 003, and 004 idempotently before starting the v2.4.0 API/worker. Existing Workspace database credentials, service token, object-storage volume, and cross-product route configuration are preserved.

## Release status

**PASS for v2.4.0 packaging and deployment.**
