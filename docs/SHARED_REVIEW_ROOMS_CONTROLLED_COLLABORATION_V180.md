# Shared Review Rooms & Controlled Collaboration — v1.8.0

## Purpose

Shared Review Rooms provide a controlled review layer around canonical Workspace projects. They build on existing Collaboration Architecture actors/policies, Shared Review handoffs, comments, proposals, and project ownership rather than introducing a second collaboration stack.

## Room lifecycle

A room is created against one project and one declared owner actor. The owner selects the object scope to review. The room starts in `draft` and can move through `open`, `in-review`, `changes-requested`, `approved`, and `closed`.

Every explicit state transition is recorded as a room audit event. Closing a room is owner-controlled.

## Invitations and permissions

Room invitations reference existing local Collaboration Architecture actors. Roles are `owner`, `editor`, `reviewer`, and `observer`. Capabilities are evaluated locally by the review-room runtime.

These permissions are governance records. They do not create WordPress users, send invitations, grant organization access, or establish a server ACL.

## Immutable snapshots

The room's selected object IDs are frozen into an explicit review snapshot only when a user chooses **Freeze review snapshot**. The snapshot contains a frozen copy of those selected objects plus project/release metadata and an integrity fingerprint. Later changes to the canonical project do not rewrite the snapshot.

## Comments and review state

Room comments are audit events associated with an actor and optional object ID. Comments and review state changes do not mutate canonical project objects. Existing Collaboration Architecture comments/proposals remain available for structured canonical-target review.

## Portability

A room can be exported as `sc-workspace-review-room-export/1.0`. Import validation is stage-first and fingerprint-aware. Exporting a room is a deliberate disclosure action; Workspace does not automatically send room contents externally.

## Privacy and governance boundaries

- browser-local room ledger
- no live co-editing
- no shared cloud tenant
- no automatic invitation delivery
- no team cloud storage
- no background sync
- no automatic canonical mutation
- no automatic AI
- no query or behavioral telemetry
- canonical project ownership remains with the project owner

## Schema compatibility

- Storage: 35
- Project: `sc-workspace-project/20.0`
- Export: `sc-workspace-project-export/20.0`
- Migration required: no
