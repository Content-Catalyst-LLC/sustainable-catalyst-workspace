# Sustainable Catalyst Workspace v0.76.0
## Documentation, Recovery Guidance & Product Help

Released: 2026-08-11

v0.76.0 improves product comprehension and recovery guidance without changing canonical Workspace data.

### Added

- Start → Help & Recovery route.
- Searchable in-product help topics for first project, local-first storage, backup, restore-as-copy, save verification, import rejection, sync conflicts, device migration, shared review, and institutional handoff.
- Explicit distinction between account recovery backup and sync enrollment.
- Recovery guidance that prioritizes preserving evidence before repair.
- Privacy-minimized product-help context report.
- `GET /wp-json/sc-workspace/v1/product-help-contract`.
- Product Help, Recovery Guidance, and Product Help Report schemas.

### Governance boundaries

Product Help is advisory only. It does not automatically repair or restore state, upload project content, synchronize a project, commit an import, reconcile a review response, perform an institutional transfer, invoke AI, or mutate canonical project data.

### Schema stability

- Storage: 35
- Project: `sc-workspace-project/20.0`
- Project Export: `sc-workspace-project-export/20.0`
- Migration required: no
