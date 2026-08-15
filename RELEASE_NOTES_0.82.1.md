# Sustainable Catalyst Workspace v0.82.1

## Production Certification Installer & Validation Lineage Repair

v0.82.1 is a surgical Release Candidate repair for the v0.82.0 deployment failure. The v0.82.0 installer stopped when an inherited Security & Privacy Audit II validator evaluated the target tree against a frozen current-version assumption. No broken v0.82.0 commit was required for this repair.

### Repair

- Adds `scripts/release_lineage.py`, a reusable current-release parser and lineage verifier.
- Adds `scripts/verify_release_lineage.py`, a fail-closed CLI used by the installer.
- Inherited Security & Privacy Audit II, Beta Closure, Release Candidate, WordPress Deployment, and Production Certification source gates now preserve their historical contract manifests while deriving the current installed release from the live WordPress tree.
- The installer verifies lineage before touching the Git target, immediately after rsync, before staging/commit, and again after staging.
- A stale source archive or stale copied target stops the installer before commit or push.
- The current plugin header, runtime constant, registry, manifest, cumulative JS/CSS, deployment predecessor, and production-certification predecessor must agree.
- Live deployment and production-certification runtimes advance to v0.82.1 with v0.82.0 as the semantic predecessor; practical rollback remains v0.81.0, the last known-good deployed baseline.
- The registry current record now reports installed/public v0.82.1 and previous v0.82.0, while the v0.82.0 record is preserved in history.
- Adds an explicit regression that constructs a stale v0.82.0 tree and proves a v0.82.1-required lineage check rejects it.
- Adds `scripts/verify_wordpress_production_v0_82_1.sh` for the post-deployment REST identity smoke.

### Feature-freeze boundary

No product subsystem, REST route, object type, or canonical data format is added.

- Storage schema: 35
- Project schema: `sc-workspace-project/20.0`
- Project Export schema: `sc-workspace-project-export/20.0`
- Schema migration: none
- Rollback package: v0.81.0 WordPress plugin (last known-good deployed baseline)
