# v0.53.0 — Collaboration Architecture Foundation

Workspace collaboration now has an explicit architecture layer before any future live multi-user system is introduced.

## Capabilities
- Browser-local collaboration actors with stable local IDs and descriptive roles: owner, editor, contributor, reviewer, observer.
- Per-project ownership policies with explicit role grants.
- Inspectable role capability vocabulary for review/export responsibilities.
- Project- or object-linked comments using canonical project/object IDs rather than copied source content.
- Review proposals with explicit lifecycle: draft, submitted, accepted, rejected, withdrawn.
- Proposal acceptance records a review decision only; it never applies the proposed value to the canonical project.
- Shareable-project contracts carrying project identity, owner, grants, scope object IDs, and governance declarations without project content.
- Portable Collaboration Architecture export/import for local coordination records.
- Existing portable asynchronous review packages remain available for compatibility.

## Governance boundary
This is collaboration architecture, not a shared tenant. Role grants do not create server accounts, organization membership, shared cloud storage, or enforceable server permissions. Comments and proposals are local coordination records around canonical IDs. Missing project/object targets remain unresolved rather than being silently rebound. No live co-editing or automatic proposal application is introduced.

## Schema boundary
Storage remains 35. Project remains `sc-workspace-project/20.0`. Collaboration Architecture lives in a dedicated browser-local ledger and therefore does not require project migration.
