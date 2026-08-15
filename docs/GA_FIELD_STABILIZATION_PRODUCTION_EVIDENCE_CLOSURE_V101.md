# Workspace v1.0.1 — GA Field Stabilization & Production Evidence Closure

v1.0.1 is the first post-General-Availability stabilization release. It adds no new product subsystem and performs no canonical Workspace schema migration.

## Field evidence boundary

The Review → GA Stabilization surface records eight explicit checks: released v1.0.0 GA predecessor evidence, production browser smoke, cache/asset coherence, install/reinstall behavior, accessibility regression smoke, cross-browser/device smoke, recovery/rollback readiness, and no-known-blocking-defects attestation.

The evidence record is browser-local unless the user explicitly exports a report. It does not collect raw user-agent strings, server filesystem paths, project content, or behavioral telemetry. It cannot automatically certify a release, purge caches, roll back, migrate projects, or mutate project data.

## Frozen contracts

- Storage schema: 35
- Project schema: `sc-workspace-project/20.0`
- Project export schema: `sc-workspace-project-export/20.0`
- Rollback baseline: v1.0.0
- Lifecycle: production
- Channel: stable
