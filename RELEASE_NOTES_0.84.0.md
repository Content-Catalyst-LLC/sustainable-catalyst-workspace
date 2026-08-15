# Sustainable Catalyst Workspace v0.84.0

## Production Sign-Off Closure & 1.0 Release Readiness

v0.84.0 is the final pre-1.0 release-control build after Live Production Certification & Release Sign-Off. It intentionally adds no new Workspace product subsystem and performs no storage, project, or export schema migration.

### What changes

- Adds **Review → 1.0 Readiness**.
- Requires the signed v0.83.0 production-signoff certificate as prerequisite evidence.
- Adds a human-controlled readiness record and exportable `sc-workspace-ga-readiness-dossier/1.0` dossier.
- Adds `/wp-json/sc-workspace/v1/ga-readiness-contract`.
- Advances the current cumulative assets to `workspace-v0.84.0.js` and `workspace-v0.84.0.css`.
- Advances deployment, production-certification, registry, and rollback lineage to v0.83.0 → v0.84.0.
- Keeps Storage 35, Project `sc-workspace-project/20.0`, and Project Export `sc-workspace-project-export/20.0` frozen.

### Readiness boundary

A `ready-for-1.0-decision` dossier means the pre-1.0 evidence gate is complete. It does **not** publish v1.0.0, change lifecycle state automatically, or waive unresolved defects. Any incomplete prerequisite keeps the dossier on `hold`.

### Explicit non-actions

Workspace does not inspect project content, auto-certify production, auto-promote to 1.0, purge caches, perform rollback, migrate projects, mutate canonical data, or send behavioral telemetry as part of this release.
