# Sustainable Catalyst Workspace v0.23.0

## Project Version History & Restore Points

v0.23.0 adds a bounded browser-local version-history layer for named project restore points. Restore points preserve a normalized project snapshot with a SHA-256 integrity fingerprint, label, note, capture time, and source-project update time. Restoring always creates a new local project copy; the current project is never overwritten.

### Changes
- Adds top-level **History** workspace environment.
- Adds `sc-workspace-version-history/1.0` and `sc-workspace-restore-point/1.0`.
- Advances Workspace storage schema from 22 to 23; project schema remains `sc-workspace-project/11.0`.
- Supports up to 20 restore points per project, 80 per Workspace, and 1.5 MB per restore point.
- Adds SHA-256 verification, current-state fingerprint comparison, restore-as-copy, export, and explicit deletion.
- Keeps restore-point history local; there is no automatic server version history or cloud upload.
- Preserves v0.21 account backup and v0.22 conflict-safe sync.
- Fixes current-state normalization so account backup metadata and cross-device sync enrollment/history survive reload under the current storage schema.
