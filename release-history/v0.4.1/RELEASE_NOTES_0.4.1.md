# Sustainable Catalyst Workspace v0.4.1
## Identity, Accounts & Persistence Boundary

Released 2026-08-08.

### Added
- Anonymous-first identity boundary with no login wall.
- Optional recognition of an existing WordPress-authenticated account.
- Sign-in/sign-out return flow to `/platform/workspace/`.
- Registration link only when WordPress site registration is already enabled.
- Stable pseudonymous device identity stored locally.
- `sc-workspace-identity/1.0` identity contract.
- `sc-workspace-project/3.1` project persistence metadata.
- Storage schema 5 and explicit v0.4.0 migration.
- `/wp-json/sc-workspace/v1/identity-contract`.

### Persistence boundary
Projects remain saved on the current device whether the visitor is a guest or signed in. v0.4.1 does not upload project content, enable cloud synchronization, or silently claim local projects into an account. Existing JSON export/import remains the manual cross-device portability path.

### Business-model boundary
Workspace remains a high-quality free personal environment. This release prepares identity for future personal sync while preserving a clean distinction between personal Workspace capabilities and institutional Catalyst Intelligence capabilities.
