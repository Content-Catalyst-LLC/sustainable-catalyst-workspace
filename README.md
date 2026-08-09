# Sustainable Catalyst Workspace

Free, local-first personal workspace for structured research, evidence, analysis, decisions, visual reasoning, briefing, knowledge, review, recovery, optional account persistence, and conflict-safe sync.

## Current release: **v0.24.0 — Project Diff & Change Review**

v0.24.0 adds a deterministic Change Review environment for comparing a named restore point with the current project or another restore point before recovery, synchronization, sharing, or institutional promotion.

### Change-review model

- explicit Added / Removed / Modified records
- canonical object changes
- evidence and provenance changes
- analysis assumption/method/finding changes
- decision record changes
- traceability and Canvas relationship changes
- transparent attention labels; no hidden score
- portable JSON review export
- no automatic merge, restore, sync, share, or promotion

## Access boundary

Guest/local Workspace remains first-class. Accounts add optional private recovery and explicit sync; they are not a login wall. Workspace does not provide institutional tenants or organization permissions.

## Data boundary

- Workspace storage schema: **23** (unchanged)
- Project schema: **sc-workspace-project/11.0** (unchanged)
- Change Review schema: **sc-workspace-change-review/1.0**
- Canonical public route: `/platform/`
- Canonical Knowledge Library route: `/knowledge-libraries/`

## WordPress

Shortcodes: `[sc_workspace]`, `[sc_workspace_entry]`, `[sc_workspace_platform]`.

Public contracts include `/wp-json/sc-workspace/v1/health`, `/project-contract`, `/version-history-contract`, and `/change-review-contract`.

## Release integrity

The release installer validates checksums, Python contracts, PHP syntax/runtime migration tests, JavaScript syntax/runtime tests, canonical Git origin, full release-history reconstruction, and tagged release installation.
