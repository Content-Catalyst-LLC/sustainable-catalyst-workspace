# Workspace v2.2.0 Validation Report

Release: **Persistence Migration, Object Storage & Recovery Hardening**  
Date: **2026-09-14**  
Previous release / rollback baseline: **v2.1.0**

## Release gates

- `scripts/validate_backend_persistence_v220.py`: **PASS**
- PHP syntax validation across the complete WordPress plugin: **PASS**
- Backend + v2.2.0 targeted contract tests: **15 passed**
- Python compilation for backend runtime modules: **PASS**

## Full historical suite

The cumulative repository suite reports **1098 passed / 117 failed** when run against the v2.2.0 current tree. The failing set consists of historical release-contract tests whose assertions still expect earlier current plugin versions, earlier current asset filenames, or earlier README/release identities. The new v2.2.0 backend tests and v2.2.0 release-contract tests are green and none of those targeted gates failed.

Historical tests remain in the repository as lineage evidence; v2.2.0 does not rewrite prior release assertions to pretend they were authored against the new release.

## Persistence invariants verified

- browser storage schema remains 35
- project schema remains `sc-workspace-project/20.0`
- export schema remains `sc-workspace-project-export/20.0`
- notebook schema remains `sc-workspace-notebook/3.0`
- migration is explicit plan/apply and non-destructive
- divergent backend records block migration apply
- source WordPress `user_meta` is retained
- migration replay is receipt/idempotency protected
- artifact content is SHA-256 addressed and atomically written
- artifact metadata/revision history is user scoped in PostgreSQL
- artifact storage has an integrity-verification endpoint
- recovery snapshots fingerprint project/notebook/artifact head manifests
- Docker object storage uses persistent volume `sc-workspace-data`
- backend host mapping is `127.0.0.1:8094 -> 8089`
- background jobs and compute orchestration remain disabled in this release
