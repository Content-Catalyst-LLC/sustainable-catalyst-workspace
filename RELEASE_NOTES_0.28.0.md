# Sustainable Catalyst Workspace v0.28.0

## Project Audit Trail & Governance Ledger

v0.28.0 adds a derived, chronological governance view across existing Workspace ledgers without creating a duplicate event database.

### Changes
- Adds a top-level **Audit** environment.
- Derives source-labeled events from project activity, Version History, account recovery, cross-device sync, Safe Actions, reconciliation/decision receipts, Collaboration, Institutional Handoff, Share, and Import & Interoperability.
- Adds project and event-source filters plus portable audit JSON export.
- Audit export excludes project/object content and records that the view is derived.
- Events are not editable from Audit Trail; authoritative records remain in their source ledgers.
- Adds no governance score, compliance inference, or people ranking.
- Fixes the rendered Workspace storage-version attribute to match schema 26.

### Data boundary
No storage or project migration occurs. Storage remains schema 26; projects remain `sc-workspace-project/11.0`.
