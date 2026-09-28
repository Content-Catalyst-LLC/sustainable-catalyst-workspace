# Workspace v3.26.0 — Embedding & Representation Runtime

- Adds governed embedding generation from declarative linear/MLP neural models.
- Adds MLP hidden/penultimate/output representation extraction and optional L2 normalization.
- Adds representation summary, bounded pairwise similarity, and nearest-neighbor analysis.
- Adds canonical embedding and representation-analysis artifact schemas.
- Persists embedding/representation artifacts separately in Workspace and records lineage in polyglot receipts.
- Preserves checkpoint/model fingerprint binding, CPU-only execution, and hardened container policy.
- No database migration. Rollback baseline: v3.25.0.
