# Sustainable Catalyst Workspace v0.82.0 — Production Smoke, Cache & Rollback Certification

Release date: 2026-08-12

v0.82.0 stays inside the Workspace Release Candidate feature freeze. It adds no new product subsystem and makes no canonical schema migration.

## Release focus

- Add **Review → Production Certification**.
- Separate automated package readiness from live WordPress production certification.
- Detect stale/multiple cumulative Workspace assets and current cache-version mismatches.
- Require a v0.81.0 rollback artifact and explicit rollback rehearsal procedure.
- Export privacy-minimized certification evidence and a live field checklist.
- Preserve project storage as application data, never a cache-remediation target.

## Compatibility

- Storage schema: 35
- Project schema: `sc-workspace-project/20.0`
- Project Export schema: `sc-workspace-project-export/20.0`
- Rollback target: v0.81.0
- Schema migration required: no

A green packaged gate does not claim the live production site is certified. Live public-page, REST, cache, project-preservation, and rollback checks remain explicit field work.
