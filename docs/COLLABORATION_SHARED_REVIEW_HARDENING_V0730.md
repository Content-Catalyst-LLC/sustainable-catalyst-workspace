# v0.73.0 — Collaboration & Shared Review Hardening

v0.73.0 strengthens Workspace's asynchronous review boundary without introducing live co-editing, server collaboration, or automatic application of reviewer changes.

## Revision-bound review packages

New review packages include a fingerprint of the frozen project scope. When a response returns, Workspace recomputes the fingerprint from the current local project and classifies the source state as current, stale, legacy-unverifiable, or missing-project.

A fingerprint is a drift/corruption signal. It is not a cryptographic identity proof, signature, or authorization mechanism.

## Stale and legacy responses

A response to a stale package may be staged, but Workspace requires an explicit owner acknowledgement before it can be reconciled into the local collaboration comment/proposal ledger. Packages created before v0.73 remain readable; because they do not carry the new source-revision fingerprint, their revision state is treated as unverifiable and they receive the same acknowledgement gate.

## Duplicate response guard

Every successful reconciliation records the exact response fingerprint in a bounded local receipt ledger. Re-importing the same response for the same handoff is blocked before another commit, preventing duplicated comments and proposals.

## Reconciliation receipts

A reconciliation receipt records the handoff, package and response fingerprints, source revision state, whether owner acknowledgement was required, the declared owner actor ID, reviewer decision, and the number of comments/proposals imported. The receipt does not mutate the canonical project.

## Identity boundary

Workspace actors and roles are descriptive local records. v0.73 does not claim that reviewer or owner identity is cryptographically verified. The owner acknowledgement is an explicit local governance action, not authentication of a real-world identity.

## Data model boundary

Storage remains 35. Project remains `sc-workspace-project/20.0`; Project Export remains `sc-workspace-project-export/20.0`. No canonical migration is required.
