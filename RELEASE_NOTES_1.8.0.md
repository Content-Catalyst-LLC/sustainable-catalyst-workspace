# Sustainable Catalyst Workspace v1.8.0 — Shared Review Rooms & Controlled Collaboration

Released: 2026-08-15

v1.8.0 turns the long-standing Collaboration Architecture and Shared Review handoff foundation into explicit Shared Review Rooms.

## Added

- Browser-local Shared Review Rooms attached to an existing Workspace project.
- Explicit room roles: owner, editor, reviewer, observer.
- Local role-capability checks for room management, invitations, snapshot creation, commenting, review-state transitions, export, and closure.
- Explicit invitation records. Workspace records an invitation but does not send email, create an account, or grant a server ACL.
- Immutable review snapshots over an explicit object scope. Later canonical project edits do not rewrite the frozen snapshot.
- Review states: draft, open, in-review, changes-requested, approved, closed.
- Auditable room events for creation, invitation changes, snapshot freezes, comments, state transitions, and closure.
- Portable review-room export with an integrity fingerprint.
- New REST contract: `/wp-json/sc-workspace/v1/shared-review-rooms-contract`.
- New Review Rooms panel inside the existing Collaboration surface.

## Governance boundaries

Review rooms are controlled review records, not a shared cloud tenant. Roles and invitations are local governance declarations. v1.8.0 does not add live co-editing, background sync, team cloud storage, server-enforced permissions, automatic invitation delivery, automatic AI, telemetry, or automatic canonical mutation.

Storage 35, Project 20.0, and Export 20.0 remain frozen. No migration is required.
