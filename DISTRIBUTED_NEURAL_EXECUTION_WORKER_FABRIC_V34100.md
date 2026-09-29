# Workspace v3.41.0 — Distributed Neural Execution & Worker Fabric

Adds a governed orchestration fabric for distributed neural jobs without accepting client-supplied worker endpoints or executable payloads.

## Operations

- distributed-worker-contract
- distributed-worker-pool-plan
- distributed-capability-match
- distributed-shard-plan
- distributed-dispatch-plan
- distributed-lease-heartbeat
- distributed-retry-failover-plan
- distributed-execution-receipt

Workers are operator-provisioned identities. The runtime records capabilities, devices, concurrency, deterministic shard/dispatch plans, lease/heartbeat state, bounded retry/failover decisions, and cross-worker execution receipts. Dispatch plans carry only a payload SHA-256 fingerprint, never executable payloads, credentials, SSH material, or worker URLs.

No database migration is introduced. v3.40.0 is the rollback baseline.
