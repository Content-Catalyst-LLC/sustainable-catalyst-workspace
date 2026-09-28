# Workspace v3.32.0 — Neural Runtime Production Certification

- Adds four bounded production-certification operations; neural registry is now 52 operations.
- Adds machine-verifiable certification plan, artifact, and report schemas.
- Certifies registry integrity, hardened identity/cache policy, security boundaries, CPU device resolution, deterministic inference, reproducible package round trip, dependency pins, evidence boundaries, and remote-broker safety.
- Persists certification artifacts separately in Workspace and records certification lineage in polyglot receipts.
- Remote GPU transport is explicitly conditional when no operator-managed worker is attached; the release does not claim unperformed GPU execution.
- Adds production deployment certification across representative neural capabilities from v3.20–v3.31.
- No database migration. Rollback baseline: v3.31.0.
