# Workspace v3.46.4.0 — Canonical State & Persistence Boundary Decoupling

Introduces canonical host-neutral state and persistence modules:
- `app/state/workspace-state-store-v34640.js`
- `app/state/workspace-persistence-runtime-v34640.js`

The persistence runtime now owns canonical loading, verified local saves, read-after-write verification, write-journal integration, last-known-good recovery and corrupted-state quarantine. The state store owns the canonical in-memory root object while preserving root identity for the remaining compatibility UI.

The compatibility runtime retains schema normalization/migration policy temporarily, but its `readState()` and `writeState()` functions are now delegates and do not perform canonical storage transactions.

No browser-storage schema migration, no database migration and no scientific-runtime behavior change.
