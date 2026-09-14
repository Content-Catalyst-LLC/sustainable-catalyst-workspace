# Workspace v2.10.0 — Attestation Verification, Compliance Gates & Runtime Trust

Workspace v2.10.0 adds a post-attestation trust layer above the v2.9 runtime evidence registry. Runtime attestations remain immutable evidence; v2.10 introduces revisioned runtime-trust policies, durable attestation-verification receipts, downstream compliance gates, and explicit human compliance waivers.

## Added
- Revisioned Runtime Trust Policy Registry.
- Verification of attestation source, attestor identity label, evidence digest, sandbox mode, budget/sandbox compliance, execution success, and allowed downstream scope.
- Immutable verification receipts classified as `verified`, `verified-with-waiver`, `rejected`, or `incomplete`.
- Human-authorized compliance waivers scoped to specific failed attestation checks and downstream uses.
- Waivers cannot change the original attestation, relax execution policy, authorize execution, or waive failed/incomplete terminal execution evidence.
- WordPress proxy routes for trust policies, waivers, and verification receipts.
- Migration 010 with PostgreSQL tables, indexes, and `sc_workspace` grants.

## Compatibility
Storage 35, Project 20.0, Export 20.0, and Notebook 3.0 remain unchanged. v2.9 runtime-attestation authentication remains server-to-server only.
