# Sustainable Catalyst Workspace

Free, local-first personal workspace for structured research, evidence, analysis, decisions, visual reasoning, briefing, knowledge, review, and deliberate account recovery/synchronization.

## Current release: **v0.22.0 — Cross-Device Sync & Conflict-Safe Recovery**

Workspace remains fully usable as a guest with browser-local projects. Signed-in users may opt individual projects into explicit cross-device synchronization. Sign-in or enrollment alone sends no project content; synchronization occurs only when the user chooses **Sync now**.

### Sync model

- explicit per-project enrollment
- manual Sync now; no background sync
- SHA-256 local/cloud project fingerprints
- server revision precondition for every sync push
- stale pushes rejected with HTTP 409
- safe remote pull only when local has not diverged
- conflicts are never silently overwritten
- cloud can be opened as a copy
- accepting cloud preserves the divergent local project as a conflict copy
- keeping local as sync head requires explicit confirmation

Manual account backups and restore-as-copy recovery from v0.21.0 remain available independently of sync.

## Access boundary

Guest/local Workspace remains first-class. Accounts add optional private recovery and explicit sync; they are not a login wall. Workspace does not provide team tenants or institutional permissions. Catalyst Intelligence remains the governed institutional environment.

## Data boundary

- Workspace storage schema: **22**
- Project schema: **sc-workspace-project/11.0** (unchanged)
- Cross-device sync schema: **sc-workspace-cross-device-sync/1.0**
- Sync push schema: **sc-workspace-sync-push/1.0**
- Canonical public route: `/platform/`
- Canonical Knowledge Library route: `/knowledge-libraries/`

## WordPress

Shortcodes: `[sc_workspace]`, `[sc_workspace_entry]`, `[sc_workspace_platform]`.

Public contracts include `/wp-json/sc-workspace/v1/health`, `/project-contract`, `/account-persistence-contract`, and `/sync-contract`. Account backup/sync endpoints require an authenticated WordPress account and REST nonce.

## Release integrity

The release installer validates checksums, Python contracts, PHP syntax/runtime migration tests, JavaScript syntax/runtime adapter tests, canonical Git origin, full release-history reconstruction, and tagged release installation.
