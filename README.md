# Sustainable Catalyst Workspace

Free, local-first personal workspace for structured research, evidence, analysis, decisions, visual reasoning, briefing, knowledge, review, recovery, optional account persistence, conflict-safe sync, and inspectable governance history.

## Current release: **v0.28.0 — Project Audit Trail & Governance Ledger**

v0.28.0 unifies consequential Workspace events into one source-labeled chronological view. The view is derived from the authoritative histories already maintained by Workspace and does not create a shadow audit database.

### Audit model

- project and event-source filters
- newest-first chronology
- Version History, account recovery, sync, Safe Actions, reconciliation receipts, Collaboration, Institutional Handoff, Share, interoperability, and project activity
- portable audit JSON without project/object content
- read-only derived events
- no hidden governance score, compliance inference, or people ranking

## Access boundary

Guest/local Workspace remains first-class. Accounts add optional private recovery and explicit sync; they are not a login wall. Workspace does not provide institutional tenants or organization permissions.

## Data boundary

- Workspace storage schema: **26** (unchanged from v0.27.0)
- Project schema: **sc-workspace-project/11.0** (unchanged)
- Audit Trail schema: **sc-workspace-audit-trail/1.0**
- Audit Event schema: **sc-workspace-audit-event/1.0**
- Canonical public route: `/platform/`
- Canonical Knowledge Library route: `/knowledge-libraries/`

## WordPress

Shortcodes: `[sc_workspace]`, `[sc_workspace_entry]`, `[sc_workspace_platform]`.

Public contracts include `/wp-json/sc-workspace/v1/health`, `/version-history-contract`, `/change-review-contract`, `/safe-actions-contract`, `/reconciliation-contract`, `/reconciliation-receipts-contract`, and `/audit-trail-contract`.

## Release integrity

The release installer validates checksums, Python contracts, PHP syntax/runtime migration tests, JavaScript syntax/runtime tests, canonical Git origin, full release-history reconstruction, and tagged release installation.
