# Sustainable Catalyst Workspace v0.3.0

## Workspace Objects & Artifact Model

Released: 2026-08-08

v0.3.0 introduces the first reusable artifact model inside Workspace Projects. Projects can now hold structured objects instead of relying only on project-level notes.

### Added

- Seven typed Workspace object classes: Source, Evidence, Dataset, Analysis, Decision, Document, and Export.
- Stable object IDs independent of titles.
- Object status: Draft, Working, Ready.
- Object summaries and long-form content.
- Tags and bounded project object collections.
- Provenance fields for source type, source title, source URL, and capture time.
- Object create, open, duplicate, archive, restore, delete, and JSON export actions.
- Object filtering by type and archived state.
- Per-project object counts and active-object restoration.
- Active-object handoff through stable IDs only.
- New public object contract endpoint.
- Storage schema v3 and project schema `sc-workspace-project/2.0`.

### Migration

- Existing v0.2.0 projects migrate automatically to project schema 2.0 with an empty object collection.
- Existing v0.1.0 browser sessions continue to migrate through the v0.2 project model and then into v0.3.
- v0.2.0 project exports remain importable.

### Governance boundary

Object titles, summaries, content, tags, and provenance are not placed into cross-product handoff URLs. Only stable project/object IDs are transmitted. All project and object content remains on the current device unless the user explicitly exports it.
