# Workspace v2.3.0 Validation Report

## Release

**Sustainable Catalyst Workspace v2.3.0 — Background Jobs & Compute Orchestration Foundation**

Rollback / predecessor baseline: **v2.2.0**.

## Targeted release gate

- `python scripts/validate_background_jobs_orchestration_v230.py` — PASS
- `PYTHONPATH=backend pytest -q backend/tests tests/test_background_jobs_orchestration_v230.py` — **21 passed**
- Python compileall for `backend/app` — PASS
- PHP syntax check for the full WordPress package — **31/31 files passed**
- deployment shell syntax (`bash -n`) — PASS

The targeted tests cover v2.3.0 identity/lineage, job request validation, the separate worker service, local background execution, route blocking instead of endpoint guessing, named cross-product route registration, the compute handoff contract, and WordPress proxy routes.

## Full historical suite

`PYTHONPATH=backend pytest -q`

- **1107 passed**
- **118 failed**

The remaining failures are legacy current-release assertions. They expect historical plugin headers/assets/release-stage strings or older README headings such as `Version: 2.0.4`, `workspace-v2.0.4.js`, `visual-regression-theme-isolation`, and earlier release-title text. These failures are not v2.3.0 job/worker/orchestration contract failures.

## Architecture checks

- Browser-supplied arbitrary route URLs are not part of the job request schema.
- Product endpoints and optional credentials are server-configured only.
- An unconfigured downstream product is marked `blocked`; no endpoint is inferred.
- The worker is a separate Docker service and does not execute long work in the FastAPI request process.
- Existing PostgreSQL persistence, object storage, migration receipts, recovery snapshots, Storage 35, Project 20.0, and Export 20.0 remain additive/compatible.
