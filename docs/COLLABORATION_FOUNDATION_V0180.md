# v0.18.0 — Collaboration Foundation

Workspace collaboration begins with structured asynchronous review rather than a shared cloud project.

## Capabilities
- Local collaboration identity (display label + descriptive role).
- Review sessions linked to existing local projects.
- Roles: owner, contributor, reviewer, observer.
- Object-linked comment, suggestion, and question threads.
- Review statuses: draft, requested, in review, changes requested, approved, closed.
- Portable review-request packages containing a privacy-minimized project copy.
- Portable review-response packages containing review state and threads but no project content.
- SHA-256 package integrity when browser cryptography is available.
- Review request import creates a local project copy; response import requires a matching request/source-project pair.

## Governance boundary
Roles are not server-enforced permissions. Imported feedback never edits the source project automatically. There is no live co-editing, team directory, organization membership, shared cloud storage, server collaboration broker, or institutional access-control layer. Those capabilities belong to later organizational architecture rather than being simulated in the free personal Workspace.

## Data model
Workspace storage advances to schema 19. Project schema remains `sc-workspace-project/11.0`; collaboration state lives at Workspace level and references stable local project/object IDs.
