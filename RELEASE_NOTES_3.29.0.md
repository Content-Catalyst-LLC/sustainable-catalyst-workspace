# Workspace v3.29.0 — Accelerator & Device Orchestration

## Added
- governed neural device inventory and fingerprinted device plans;
- explicit `cpu`, `auto`, `accelerator`, and allowed `cuda:N` requests;
- strict/fallback policy with recorded fallback reasons;
- request-local device context across existing neural operations;
- bounded accelerator smoke operation;
- device-plan lineage in Workspace polyglot receipts;
- opt-in Docker Compose GPU exposure file.

## Preserved
- CPU is the default production policy;
- v3.28 reproducible model packages and packaged inference;
- declarative-only neural execution and hardened container limits;
- typed endpoint count remains 291;
- no database migration.

Rollback baseline: Workspace v3.28.0.
