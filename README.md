# Sustainable Catalyst Workspace

Free, local-first personal workspace for structured research, evidence, analysis, decisions, visual reasoning, briefing, knowledge, review, recovery, optional account persistence, and conflict-safe sync.

## Current release: **v0.27.0 — Reconciliation Provenance & Decision Receipts

v0.26.0 extends deterministic Change Review into a controlled selective-apply workflow. Users choose individual changes, preview the resulting project state, resolve dependency blockers, and create a new reconciled project copy while both source states remain untouched.

### Reconciliation model

- deterministic differences from the existing Project Diff engine
- explicit change selection; nothing selected automatically
- dependency validation before creation
- human acknowledgement required
- new reconciled project copy with remapped local identities
- portable reconciliation-plan JSON
- browser-local reconciliation history
- no automatic merge, overwrite, or source mutation

## Access boundary

Guest/local Workspace remains first-class. Accounts add optional private recovery and explicit sync; they are not a login wall. Workspace does not provide institutional tenants or organization permissions.

## Data boundary

- Workspace storage schema: **25**
- Project schema: **sc-workspace-project/11.0** (unchanged)
- Change Review schema: **sc-workspace-change-review/1.0**
- Safe Actions schema: **sc-workspace-safe-actions/1.0**
- Reconciliation schema: **sc-workspace-reconciliation/1.0**
- Canonical public route: `/platform/`
- Canonical Knowledge Library route: `/knowledge-libraries/`

## WordPress

Shortcodes: `[sc_workspace]`, `[sc_workspace_entry]`, `[sc_workspace_platform]`.

Public contracts include `/wp-json/sc-workspace/v1/health`, `/project-contract`, `/version-history-contract`, `/change-review-contract`, `/safe-actions-contract`, and `/reconciliation-contract`.

## Release integrity

The release installer validates checksums, Python contracts, PHP syntax/runtime migration tests, JavaScript syntax/runtime tests, canonical Git origin, full release-history reconstruction, and tagged release installation.
