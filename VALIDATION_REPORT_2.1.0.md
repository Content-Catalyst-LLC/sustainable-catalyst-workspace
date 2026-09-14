# Sustainable Catalyst Workspace v2.1.0 — Validation Report

## Release boundary

- Baseline inspected: Workspace v2.0.4.
- Candidate: Workspace v2.1.0 — Backend Foundation & Persistence Bridge.
- Storage schema remains 35.
- Project schema remains `sc-workspace-project/20.0`.
- Export schema remains `sc-workspace-project-export/20.0`.
- Exact rollback baseline: v2.0.4.

## Passing release-specific validation

- `python3 scripts/validate_backend_foundation.py` — PASS.
- `PYTHONPATH=backend pytest -q backend/tests tests/test_backend_foundation_contract.py` — 13 passed, 0 warnings.
- `python3 -m compileall -q backend/app` — PASS.
- PHP syntax validation — 31/31 plugin PHP files passed `php -l`.
- Browser/PHP-compatible project sync fingerprint was compared against a Node implementation of the existing Workspace algorithm and matched exactly for the validation fixture.

## Legacy suite compatibility signal

`PYTHONPATH=backend pytest -q` completed with **1093 passed and 115 failed**.

Review of all 115 failures showed they are release-lineage/current-release assertions pinned to the v2.0.4 presentation identity: exact plugin version, `workspace-v2.0.4` asset names, the v2.0.4 release-stage string, v2.0.3 predecessor expectations, or the old compact release handle. These tests need their current-release discovery expectations advanced/refactored for v2.1.0. They do not identify a backend persistence-contract failure.

The release-specific backend/bridge suite is green, but this report intentionally does **not** claim that the unmodified historical suite is fully green.

## Safety and migration status

- Dedicated backend mode defaults to disabled.
- Existing WordPress `user_meta` account copies are not automatically migrated.
- When dedicated backend mode is enabled as `primary`, persistence fails closed rather than silently writing to both stores.
- Browser clients continue to use the existing WordPress cloud project/notebook routes.
- Service credentials remain server-side.
- No background synchronization, automatic merge, automatic AI, or project-content telemetry was introduced.
