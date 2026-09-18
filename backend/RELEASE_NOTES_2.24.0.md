# Workspace v2.24.0 — Backend Authority & Domain Service Consolidation

Workspace v2.24.0 changes where canonical product meaning lives. The browser remains responsible for interaction, rendering, transient UI state, and local drafts; the Python/PostgreSQL backend becomes the explicit authority for canonical project and notebook validation, revision preconditions, fingerprints, persistence, provenance, mutation policy, and mutation receipts.

## Added

- `sc-workspace-domain-authority/1.0` authority profile.
- Server-side project and notebook structural validation.
- Duplicate project-object and notebook-cell identifier rejection before canonical persistence.
- Durable `workspace_domain_mutation_receipts` records for project/notebook backup, sync, and delete operations.
- Mutation receipts capture before/after revision, request SHA-256, canonical SHA-256, validation decision, policy context, and provenance context.
- `GET /v1/domain-authority`.
- `POST /v1/domain-authority/validate`.
- `GET /v1/domain-mutation-receipts` and receipt lookup.
- Health/capability identity explicitly declares backend-authoritative state and non-authoritative browser state.
- WordPress now serves the v2.24 versioned main Workspace JS/CSS files rather than continuing to pin the v2.20 filename.
- Thin-client JavaScript contract marker (`SCWorkspaceBackendAuthority`) describes the backend authority endpoints without moving domain rules into JavaScript.

## Boundary

v2.24.0 does **not** rewrite the browser UI in Python. It narrows the browser's authority. Scientific runtimes, provenance, canonical persistence, revision policy, and domain validation stay server-side; JavaScript remains appropriate for presentation and interaction.

## Security / execution

No arbitrary code execution is introduced. Existing bounded scientific runtime policies remain unchanged.
