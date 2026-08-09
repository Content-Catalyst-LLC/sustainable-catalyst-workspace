# Sustainable Catalyst Workspace v0.22.0

## Cross-Device Sync & Conflict-Safe Recovery

v0.22.0 adds explicit opt-in synchronization on top of the v0.21.0 account recovery foundation. Guest/local Workspace remains fully functional. Signing in or enabling sync does not upload a project; a signed-in user must choose **Sync now** for an enrolled project.

### Changes

- Adds per-project sync enrollment and a dedicated Cross-Device Sync surface in Storage & Identity.
- Compares local SHA-256 project fingerprints, the last common fingerprint, cloud fingerprints, and server revisions.
- Requires an expected server revision for every sync push; stale writes are rejected with HTTP 409.
- Pulls a newer cloud revision in place only when the local project has not diverged from the common base.
- Never silently resolves a two-sided conflict. Users may open the cloud copy separately, keep local as the sync head, or use cloud here while preserving the local version as a conflict copy.
- Retains manual account backups and restore-as-copy recovery from v0.21.0.
- Adds a local sync history and status model; no background synchronization or periodic polling is introduced.

### Data boundary

Storage advances from schema 21 to 22 to hold local sync enrollment/history metadata. Project schema remains `sc-workspace-project/11.0`. Existing projects and canonical object IDs are preserved.

### Governance boundary

There is no automatic enrollment on sign-in, automatic upload, background sync, silent last-write-wins, team sync, or institutional sync. Catalyst Intelligence remains the governed institutional environment.
