# Sustainable Catalyst Workspace v0.25.0

## Change Gates & Safe Actions

This release turns Change Review into an explicit safety preflight for higher-risk Workspace actions.

### Protected actions

- Restore a named restore point as a new local copy.
- Resolve a cross-device synchronization conflict by keeping local as the new sync head.
- Resolve a synchronization conflict by using cloud locally while preserving the divergent local copy.
- Export a portable project or static review copy.
- Export an institutional promotion package for Catalyst Intelligence.

### Gate behavior

Each protected action opens a visible preflight. When a comparison state exists, Workspace generates a deterministic Change Review and shows added, removed, modified, and relationship changes. Sync conflicts compare local and cloud project states directly. Share and institutional exports use the newest named restore point as the comparison baseline when available.

The action runs only after an explicit acknowledgement. If no prior restore-point baseline exists, Workspace says so rather than manufacturing a score or silently treating the project as unchanged.

### Safe Actions ledger

A browser-local `sc-workspace-safe-actions/1.0` ledger records proceeded, cancelled, and blocked gates with the project, action, comparison basis, and change summary. It contains no hidden risk or productivity score.

### Data boundary

Workspace storage advances from schema 23 to **24**. Project schema remains `sc-workspace-project/11.0`. Existing projects, restore points, account backups, sync enrollment/history, collaboration state, and institutional handoffs migrate non-destructively.

### Governance

No gate can merge, apply, restore, sync, share, or promote automatically. Human acknowledgement remains the control point, and the existing server revision precondition continues to protect sync conflicts after the preflight.
