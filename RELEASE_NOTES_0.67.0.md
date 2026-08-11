# Sustainable Catalyst Workspace v0.67.0

## Cross-Device Continuity & Sync Hardening

v0.67.0 hardens explicit account-backed continuity without changing Workspace's local-first ownership model.

### Sync operation journal and retry safety
- Every project sync push receives a client-generated operation ID recorded before the network request.
- The server stores the last completed operation ID and treats an exact retry as idempotent instead of creating another revision.
- A browser restart converts unfinished `pending` operations to `interrupted`; Workspace preserves the evidence and requires a status check/retry rather than guessing the result.
- Revision preconditions remain mandatory and silent last-write-wins remains prohibited.

### Pull safety
- Before applying a remote-ahead cloud revision in place, Workspace creates a SHA-256 local `sync-safety` restore point.
- If that safety point cannot be created, the pull aborts rather than replacing the local project without a recovery anchor.
- Conflict resolution that accepts cloud state still preserves the competing local project as a separate copy.

### Device migration
- The sync panel can export a dedicated `sc-workspace-device-migration/1.0` package.
- Migration packages contain project content and a continuity baseline, but exclude device identity, account profile, REST nonce, and recent-tool history.
- Import verifies the project fingerprint and always creates a new local project copy.
- Sync enrollment is never transferred; the receiving device must explicitly enroll the new copy.
- Exact duplicate migration imports are blocked using source-project + SHA-256 fingerprint history.

### Account-backup boundary
- The server now accepts current Project 20.0 snapshots for account backup/sync.
- A manual account backup cannot overwrite an active `sync-head`; users must use explicit Sync now so the revision precondition protects cloud state.

### Boundaries
- Storage schema: **35**
- Project schema: **sc-workspace-project/20.0**
- Project Export schema: **sc-workspace-project-export/20.0**
- Schema migration: **none**
- Background sync: **none**
- Automatic enrollment: **none**
- Automatic conflict merge: **none**
