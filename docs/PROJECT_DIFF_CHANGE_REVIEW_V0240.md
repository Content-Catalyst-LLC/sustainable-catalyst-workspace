# Project Diff & Change Review — v0.24.0

Change Review is a derived, local-first comparison layer over current project state and v0.23 restore points. It does not persist a duplicate project state or create a merge engine.

## Review contract

1. Select a project.
2. Select a restore point as the base.
3. Compare against current project state or another restore point.
4. Review categorized added/removed/modified records.
5. Export the review JSON when useful.
6. Decide separately whether to restore, sync, share, or promote.

No hidden score or automatic reconciliation is performed.
