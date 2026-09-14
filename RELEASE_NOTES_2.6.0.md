# Workspace v2.6.0 — Runtime Adapter Registry & Reproduction Verification

## Added
- Revisioned `RuntimeAdapter` records with Python, R, Julia, and custom runtime families.
- Runtime version, dependency-manager, container identity, platform constraints, and bounded capability descriptors.
- Metadata-only environment compatibility/readiness checks.
- `runtimeAdapterRef` and immutable adapter fingerprint binding on execution runs.
- Durable reproduction plans that freeze original run inputs, environment, runtime adapter, and expected output digests.
- Immutable reproduction verification receipts with `exact`, `compatible`, `divergent`, and `incomplete` classifications.
- Deterministic comparison over input/environment/adapter fingerprints and output SHA-256/byte evidence.

## Safety and scope
- No arbitrary shell commands or command templates are accepted by runtime adapters.
- No automatic code execution or automatic reproduction is introduced.
- Compatibility checks inspect recorded metadata only and are not a claim that a runtime is installed or healthy.
- Reproduction verification compares recorded evidence; it does not independently validate scientific correctness.

## Compatibility
- Storage schema: 35 (unchanged)
- Project schema: `sc-workspace-project/20.0` (unchanged)
- Export schema: `sc-workspace-project-export/20.0` (unchanged)
- Previous/rollback release: v2.5.0
