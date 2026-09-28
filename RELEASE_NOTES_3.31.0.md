# Workspace v3.31.0 — Remote GPU Execution Broker

Baseline: Workspace v3.30.0. Database migration: none.

This release adds operator-governed dispatch of existing bounded neural operations to registered remote GPU workers while preserving the local CPU-safe execution path.

Highlights:

- 48 bounded neural operations (44 inherited + 4 broker operations).
- Operator-managed worker registry; no client-supplied remote URLs.
- HMAC-SHA256 signed dispatch envelopes and worker receipts.
- Short-lived dispatch TTL and nonce replay protection.
- Explicit worker/device binding and recursive-broker-operation rejection.
- Remote result, dispatch, worker, device-plan, and receipt fingerprints.
- Separate governed remote execution artifact persisted by Workspace.
- Polyglot receipt enrichment for remote GPU provenance.
- Remote worker Compose template for an NVIDIA host.
- Broker disabled by default in the normal Contabo Compose deployment.
- No database migration.

Deployment of v3.31.0 requires v3.30.0 to be present as the rollback baseline.
