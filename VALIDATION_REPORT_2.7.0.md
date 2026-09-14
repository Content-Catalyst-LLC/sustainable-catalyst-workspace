# Validation Report — Workspace v2.7.0

Release: **Reproduction Execution Plans & Controlled Runtime Handoffs**  
Date: 2026-09-14

## Release-specific gate

- `scripts/validate_controlled_runtime_handoffs_v270.py`: PASS
- `PYTHONPATH=backend pytest -q backend/tests tests/test_controlled_runtime_handoffs_v270.py`: **34 passed**
- Python compileall for `backend/app`: PASS
- PHP syntax: **31/31 files PASS**
- VPS deployment script `bash -n`: PASS

## Full historical suite

- **1,142 passed / 122 failed**
- Failures are legacy tests that hard-code earlier releases as the current Workspace version, asset filename, README heading, or release lineage. The v2.7 release-specific gate is clean.

## v2.7 contracts verified

- Reproduction execution plans are durable PostgreSQL records.
- Each plan freezes the reproduction plan, reproduction run, input/environment/runtime-adapter fingerprints, target product, operation, job envelope, and readiness evidence.
- Runtime-adapter capability and server-configured route availability are required readiness gates.
- Plan creation does not queue or execute work.
- Dispatch requires a distinct `sc-workspace-controlled-runtime-handoff/1.0` request with `humanAuthorized=true`.
- Target product and operation cannot be supplied by the handoff request; they are frozen by the execution plan.
- Client-supplied runtime URLs and credentials are not accepted.
- Runtime handoff receipts retain the execution-plan fingerprint, job request fingerprint, route transport, job id, and human-authorization evidence.
- Arbitrary code execution remains disabled.
- Migration 007 grants `sc_workspace` access to the new v2.7 tables and preserves v2.4–v2.6 registry grants.

## Compatibility

Storage schema remains 35; project schema remains `sc-workspace-project/20.0`; export schema remains `sc-workspace-project-export/20.0`. Rollback target: v2.6.0.
