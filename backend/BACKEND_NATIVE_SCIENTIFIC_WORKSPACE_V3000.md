# Backend-Native Scientific Workspace — v3.0.0

## Architecture milestone

Workspace v3.0.0 makes the backend-native boundary a first-class product contract rather than an accumulation of individual backend services.

- PostgreSQL is the canonical persistent store.
- Python domain services own scientific meaning, validation, revision authority, provenance, orchestration, and authorization.
- The browser is a presentation/interaction client with memory-only canonical projections plus transient UI state and explicit draft/outbox state.
- Signed-in work cannot silently fall back to browser-local canonical authority.
- Guest/browser-local compatibility remains available through a lazy compatibility bundle and is scoped to browser-local projects only.
- Scientific execution is constrained to registered, bounded internal runtime operations; arbitrary code execution remains disabled.
- Cross-product handoffs, study packages, visualization specifications, receipts, and provenance remain backend-authoritative.

## New API

- `GET /v1/backend-native-workspace` — architecture profile.
- `GET /v1/backend-native-workspace/bootstrap` — consolidated signed-in bootstrap carrying server-resolved identity, authority profiles, canonical thin-client projection, sync checkpoint, and a deterministic session fingerprint.

No database migration is introduced. Migration lineage remains `031_backend_policy_identity_authorization_consolidation.sql`. Rollback baseline: v2.36.0.
