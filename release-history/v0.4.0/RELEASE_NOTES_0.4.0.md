# Sustainable Catalyst Workspace v0.4.0
## Research Workspace
Released 2026-08-08

v0.4.0 introduces the first domain workspace built on the v0.3.0 object model.

### Added
- Project-scoped Research Workspace (`sc-workspace-research/1.0`).
- Research questions with active-question selection, priority, and lifecycle state.
- Rapid source capture into canonical Source objects.
- Reading queue with unread / reading / read state.
- Evidence extraction into canonical Evidence objects.
- Source-to-evidence relationship records using stable object IDs.
- Research claims with exploratory / supported / contested / rejected state.
- Evidence-to-claim links using stable Evidence object IDs.
- Research progress metrics.
- Research Librarian and Knowledge Library project-context handoffs.
- Public `/wp-json/sc-workspace/v1/research-contract` endpoint.

### Migration
- Browser storage schema 3 → 4.
- Project schema 2.0 → 3.0.
- Existing v0.3.0 objects remain `sc-workspace-object/1.0` and are preserved.
- v0.2.0 project exports and v0.1.0-compatible imports remain accepted.

### Boundaries
Workspace remains free public software with device-local persistence. v0.4.0 adds no account requirement, cloud project storage, collaboration service, automatic publication, or server-side research storage.
