# Sustainable Catalyst Workspace v1.0.1

## GA Field Stabilization & Production Evidence Closure

This is a narrow post-GA stabilization release. It closes the first production-field evidence loop without expanding the Workspace feature surface or changing canonical data contracts.

### Added
- Review → GA Stabilization field-evidence surface.
- `/wp-json/sc-workspace/v1/ga-stabilization-contract`.
- Browser-local, explicitly exportable `sc-workspace-ga-stabilization-report/1.0` report.
- Production browser, cache coherence, reinstall, accessibility, cross-browser/device, recovery, and blocking-defect checks.

### Repaired / hardened
- Current release metadata consistently identifies the production/stable 1.x line.
- Deployment and production-certification current asset detection advances cleanly to semantic v1.0.1 cumulative assets.
- v1.0.0 is retained as the exact rollback baseline.

### Unchanged
- Storage 35.
- Project `sc-workspace-project/20.0`.
- Export `sc-workspace-project-export/20.0`.
- Local-first project ownership.
- No behavioral telemetry, automatic release certification, automatic rollback, cache purge, or automatic project migration.
