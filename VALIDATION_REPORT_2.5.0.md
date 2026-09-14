# Workspace v2.5.0 Validation Report

Release: **Reproducible Execution Environments & Dependency Manifests**  
Date: 2026-09-14

## Release-specific gate

- `scripts/validate_reproducible_execution_environments_v250.py`: PASS
- `PYTHONPATH=backend pytest -q backend/tests tests/test_reproducible_execution_environments_v250.py`: **31 passed**
- Python compile: PASS
- PHP syntax: PASS for all plugin PHP files
- `bash -n scripts/deploy_workspace_backend_v2_5_0_vps.sh`: PASS

## Full historical suite

- **1,127 passed**
- **120 failed**

The remaining failures are historical release assertions that hard-code earlier Workspace versions, prior current-asset filenames, or older README/current-release headings. They are not v2.5.0 execution-environment contract failures.

## Key release checks

- revisioned execution-environment heads/revisions are modeled;
- migration 005 adds run environment reference/fingerprint fields;
- migration 005 repairs DML permissions for the v2.4 and v2.5 registry tables;
- execution runs freeze an environment revision and SHA-256 fingerprint;
- dependency lock artifacts resolve to exact artifact revisions/digests;
- environment-variable values are not part of the request or persistence contract;
- v2.4 inline environment metadata remains compatible;
- Docker data volume is declared external to avoid cross-release Compose ownership warnings.
