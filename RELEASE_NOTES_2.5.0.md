# Workspace v2.5.0 — Reproducible Execution Environments & Dependency Manifests

## Added
- Revisioned execution-environment registry.
- Runtime and language version descriptors.
- Dependency manifests with exact content-addressed lock-artifact references.
- Container/image identity and bounded system/hardware descriptors.
- Random-seed capture and execution configuration.
- Environment-variable name capture only; secret values are not accepted by the contract.
- Execution runs freeze an environment id, revision, and SHA-256 environment fingerprint.
- Compatibility with v2.4 inline environment metadata.

## Backend migration
Migration `005_reproducible_execution_environments.sql` adds the environment registry and run environment linkage. It also repairs DML grants for v2.4 registry tables created by an administrative migration role.

## Non-goals
- No arbitrary code execution inside Workspace.
- No automatic reconstruction of an environment from a manifest.
- No secret environment-variable values.
- No replacement for Lab/Workbench specialist compute runtimes.
