# Sustainable Catalyst Workspace v0.73.0
## Collaboration & Shared Review Hardening

v0.73.0 hardens asynchronous collaboration and shared review without adding live co-editing or changing canonical project schemas.

### Added
- Revision fingerprints bound to newly prepared shared-review packages.
- Stale-source detection when a matched reviewer response returns after scoped research has changed.
- Explicit owner acknowledgement before reconciling stale, missing-project, or legacy-unverifiable responses.
- Duplicate-response commit prevention using a bounded local reconciliation-receipt ledger.
- Reconciliation receipts recording package/response fingerprints, source state, declared owner, reviewer decision, and imported comment/proposal counts.
- New Review UI status surface explaining current/stale/legacy/duplicate conditions before commit.
- New REST contract: `/wp-json/sc-workspace/v1/collaboration-review-hardening-contract`.
- Three new schemas for the hardening contract, import assessment, and reconciliation receipt.

### Preserved boundaries
- Reviewer and owner identities remain declarative local actors, not cryptographically verified identities.
- Reviewer proposals never apply directly to canonical project content.
- No automatic sending, live co-editing, server collaboration, hidden merge, or background sync is introduced.
- Older shared-review packages remain readable; their source revision is marked unverifiable and requires explicit acknowledgement before reconciliation.
- Storage 35, Project 20.0, and Project Export 20.0 remain unchanged.
