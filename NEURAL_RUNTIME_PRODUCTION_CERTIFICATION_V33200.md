# Workspace v3.32.0 — Neural Runtime Production Certification

Workspace v3.32.0 closes the v3.20–v3.31 neural runtime sequence with a machine-verifiable production certification layer.

## Certification operations

- `workspace.neural.certification-plan`
- `workspace.neural.certification-execute`
- `workspace.neural.certification-verify`
- `workspace.neural.certification-report`

The neural registry contains 52 bounded operations.

## Governed schemas

- `sc-workspace-neural-production-certification-plan/1.0`
- `sc-workspace-neural-production-certification-artifact/1.0`
- `sc-workspace-neural-production-certification-report/1.0`
- profile: `workspace-neural-production/1.0`

Workspace persists the executed certification artifact as `application/vnd.sc.workspace.neural-production-certification+json` and binds its ID, SHA-256, certification ID, status, required-check counts, and remote-GPU transport status into the polyglot execution receipt.

## Required checks

The runtime certification artifact requires all of the following to pass:

1. runtime registry integrity;
2. hardened identity and cache contract;
3. bounded security boundary;
4. explicit CPU device planning;
5. deterministic neural inference;
6. reproducible neural model-package round trip;
7. dependency/runtime contract;
8. evidence/prediction boundary;
9. remote-broker safety.

Remote GPU transport is a conditional check. A CPU-only or broker-disabled deployment can be production-certified without falsely claiming a physical GPU worker was exercised. The artifact reports `not-exercised-no-worker-attached` until an operator-managed remote worker is deliberately configured.

## Production deployment certification

The v3.32 Contabo deployer uses v3.31.0 as its rollback baseline. Before switching it runs the production certification plus representative training, checkpoint, evaluation, explainability, embedding, packaging/inference, hyperparameter search, and broker-protocol smoke tests inside the hardened neural container. After switching, it runs a real Workspace certification job, retrieves the separately persisted certification artifact, verifies the artifact using the runtime, generates a certification report, validates execution-receipt lineage, checks the 52-operation registry, and rechecks container hardening.

No database migration is required.
