# Sustainable Catalyst Workspace v1.7.0 — Cross-Device Continuity & Account Sync Productionization

Workspace v1.7.0 productionizes the existing account/cloud continuity foundation without changing the local-first ownership model.

## Added
- Deterministic cross-device continuity planning: local-only, enroll, push, guarded pull, open remote copy, recreate cloud head, no-op, or conflict.
- Privacy-minimized sync receipts containing continuity metadata/fingerprints rather than project content.
- Explicit production continuity status inside the existing Cross-Device Sync surface.
- Conflict-preserving and revision-precondition boundaries promoted into the current production release contract.
- Interrupted-operation reconciliation and idempotent retry remain first-class release requirements.

## Preserved boundaries
- Guest/local Workspace remains first-class.
- Sync requires an authenticated WordPress account plus explicit per-project enrollment.
- No background sync, automatic enrollment, silent last-write-wins, device fingerprinting, automatic AI, or behavioral/query telemetry.
- Storage 35, Project 20.0, and Export 20.0 remain frozen.

Rollback baseline: v1.6.0.
