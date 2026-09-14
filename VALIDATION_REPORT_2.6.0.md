# Validation Report — Workspace v2.6.0

Release: **Runtime Adapter Registry & Reproduction Verification**  
Date: 2026-09-14

## Release-specific gate

- `scripts/validate_runtime_adapter_reproduction_v260.py`: PASS
- `PYTHONPATH=backend pytest -q backend/tests tests/test_runtime_adapter_reproduction_v260.py`: **33 passed**
- Python compileall for `backend/app`: PASS
- PHP syntax: **31/31 files PASS**
- VPS deployment script `bash -n`: PASS

## Full historical suite

- **1,134 passed / 121 failed**
- Failures are legacy tests that hard-code earlier releases as the current Workspace version, asset filename, README heading, or release lineage. The v2.6 release-specific gate is clean.

## v2.6 contracts verified

- Revisioned runtime adapters and immutable adapter fingerprints.
- Supported runtime families: Python, R, Julia, and bounded custom descriptors.
- Environment/runtime compatibility checks are metadata-only and report `executionPerformed=false`.
- Execution runs may freeze `runtimeAdapterRef` plus exact revision/fingerprint.
- Reproduction plans freeze original run provenance and expected output digests.
- Verification receipts classify `exact`, `compatible`, `divergent`, or `incomplete`.
- Rerun comparison uses input/environment/adapter fingerprints plus output SHA-256 and byte evidence.
- No arbitrary command fields, automatic re-execution, or unrestricted code execution are introduced.
- Migration 006 grants `sc_workspace` access to all new v2.6 registry tables.

## Compatibility

Storage schema remains 35; project schema remains `sc-workspace-project/20.0`; export schema remains `sc-workspace-project-export/20.0`.
