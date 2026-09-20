# Workspace v2.36.0 — Production Architecture Certification

This release freezes the v2.x backend-native architecture and certifies its machine-verifiable production boundaries before the v3.0 milestone. It adds no scientific feature surface and no database migration.

## Certified architecture

- PostgreSQL/Python remains canonical for durable state, revisions, validation, provenance and policy decisions.
- WordPress remains a same-origin server proxy; backend service credentials are never browser-visible.
- Authorization is backend-resolved, default-deny, and does not trust browser-supplied roles or scopes.
- Browser responsibilities remain presentation, interaction routing, transient UI state and explicit local draft/outbox handling.
- Local-first envelopes are non-authoritative and conflicts require server reconciliation; no automatic semantic merge.
- Unified scientific objects remain generic read projections with no generic arbitrary mutation endpoint.
- Cross-product handoffs preserve revision/fingerprint pinning and require explicit destination acceptance.
- Scientific runtimes remain bounded internal services; this release does not add arbitrary-code execution.
- Release packages use SHA-256 integrity manifests and exact v2.35→v2.36 reconstruction checks.
- Migration lineage remains `031_backend_policy_identity_authorization_consolidation.sql`; rollback baseline is v2.35.0.

## Certification scope

`architectureCertified=true` means the release and deployed backend pass deterministic architecture gates. It does **not** claim public-page/CDN/cache or live rollback field checks have been executed. Those remain explicit manual production checks.
