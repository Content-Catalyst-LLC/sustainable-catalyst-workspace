# Sustainable Catalyst Workspace

Free, local-first personal workspace for structured research, evidence, analysis, decisions, visual reasoning, briefing, knowledge, review, recovery, optional account persistence, and conflict-safe sync.

## Current release: **v0.25.0 — Change Gates & Safe Actions**

v0.25.0 makes Change Review an explicit preflight before higher-risk Workspace actions. Restore, sync conflict resolution, portable sharing, and institutional promotion now require a visible gate and human acknowledgement before proceeding.

### Safe-action model

- explicit change review before protected actions
- local/cloud diff review for sync conflict resolution
- restore-point/current-state review for restore, share, and promotion
- human acknowledgement required before proceed
- browser-local safe-action decision ledger
- no hidden risk score
- no automatic merge, apply, restore, sync, share, or promotion

## Access boundary

Guest/local Workspace remains first-class. Accounts add optional private recovery and explicit sync; they are not a login wall. Workspace does not provide institutional tenants or organization permissions.

## Data boundary

- Workspace storage schema: **24**
- Project schema: **sc-workspace-project/11.0** (unchanged)
- Change Review schema: **sc-workspace-change-review/1.0**
- Safe Actions schema: **sc-workspace-safe-actions/1.0**
- Canonical public route: `/platform/`
- Canonical Knowledge Library route: `/knowledge-libraries/`

## WordPress

Shortcodes: `[sc_workspace]`, `[sc_workspace_entry]`, `[sc_workspace_platform]`.

Public contracts include `/wp-json/sc-workspace/v1/health`, `/project-contract`, `/version-history-contract`, `/change-review-contract`, and `/safe-actions-contract`.

## Release integrity

The release installer validates checksums, Python contracts, PHP syntax/runtime migration tests, JavaScript syntax/runtime tests, canonical Git origin, full release-history reconstruction, and tagged release installation.
