# Sustainable Catalyst Workspace v2.5.0

## Reproducible Execution Environments & Dependency Manifests

Workspace remains local-first in the browser while its optional Python backend now records revisioned execution environments for reproducible runs.

### v2.5.0
- runtime/language versions
- dependency manifests and frozen lock-artifact references
- container/image identity
- OS/architecture and bounded hardware metadata
- deterministic random seeds
- environment variable names only; no secret values
- exact environment revision/fingerprint frozen into execution runs

Storage schema remains 35. Project schema remains `sc-workspace-project/20.0`. Export schema remains `sc-workspace-project-export/20.0`.
