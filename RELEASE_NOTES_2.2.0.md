# Sustainable Catalyst Workspace v2.2.0 — Persistence Migration, Object Storage & Recovery Hardening

Workspace v2.2.0 turns the v2.1.0 backend foundation into a durable server persistence layer without changing Workspace's local-first ownership model.

## Added

- plan/apply migration path from legacy WordPress `user_meta` account copies into PostgreSQL
- all-or-nothing conflict gate before migration writes
- idempotent migration receipts keyed by source fingerprint
- preservation of legacy project/notebook revision numbers during import
- retention of the original WordPress account store after migration
- SHA-256 content-addressed artifact/blob storage
- artifact heads and append-only artifact revision metadata
- artifact revision preconditions
- persistent Docker object-storage volume
- artifact integrity verification endpoint
- bounded recovery snapshots containing project, notebook, and artifact head manifests
- WordPress REST proxy routes for migration planning/apply, receipts, integrity, and recovery snapshots

## Preserved

- Storage schema 35 for browser-local Workspace data
- `sc-workspace-project/20.0`
- `sc-workspace-project-export/20.0`
- `sc-workspace-notebook/3.0`
- guest/local Workspace
- explicit backup and explicit sync only
- no background sync
- no automatic conflict resolution
- no browser-direct backend credentials
- no compute orchestration in this release

## Deployment lineage

Previous release: v2.1.0. Rollback baseline: v2.1.0. The PostgreSQL additions are additive. The legacy WordPress account store is retained and is not deleted automatically.
