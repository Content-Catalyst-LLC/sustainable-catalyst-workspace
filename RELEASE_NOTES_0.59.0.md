# Sustainable Catalyst Workspace v0.59.0

## Security, Privacy & Data-Portability Audit

v0.59.0 is a schema-stable cross-cutting audit and hardening release. It consolidates the security, privacy, recovery, disclosure, and portability boundaries accumulated across prior Workspace releases into one inspectable Review surface.

### Added

- Review → Security & Privacy surface.
- Explicit same-origin/browser-local threat model and security non-claims.
- Inventory of every current `sc_workspace*` localStorage key, including unknown future Workspace-owned keys.
- Disclosure/recovery artifact visibility.
- Metadata-only audit export.
- Explicit complete browser-local Workspace portability bundle.
- Deterministic portability-bundle integrity receipt.
- Typed-confirmation browser-local deletion plan and execution.
- Post-delete verification with deletion receipt.
- Unrelated localStorage keys remain untouched.
- Clear separation between browser-local deletion and account/cloud/server deletion.
- New `/wp-json/sc-workspace/v1/security-privacy-contract` capability endpoint.

### Security boundaries stated explicitly

Workspace does not claim application-level encryption of browser localStorage. Package fingerprints are integrity receipts, not encryption, authentication, or authorization. Durable `scw://` references are identifiers, not credentials. Account/cloud backups and already exported/shared copies are outside browser-local deletion scope.

### Schema boundary

Storage remains 35, Project remains `sc-workspace-project/20.0`, Project Export remains 20.0, and Notebook Workspace remains 8.0. No canonical research migration is required.

### Retained

v0.58 Scale, Performance & Large-Project Hardening remains intact, including derived-index caching, bounded result rendering, storage-pressure visibility, stress fixtures, and the 4px editorial header treatment.
