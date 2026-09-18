# Workspace v2.25.0 — Workspace Command & Query API

Workspace v2.25.0 formalizes the backend-authority pivot introduced in v2.24.0. Mutating actions are expressed as bounded commands and persisted with command receipts; read-only projections are generated server-side through a query/read-model API. The browser remains responsible for presentation, interaction, local drafts, selection, viewport state, and rendering.

## Command surface
- project.put / project.delete
- notebook.put / notebook.delete
- artifact.put / artifact.delete
- job.submit / job.cancel / job.retry

## Query/read-model surface
- workspace.overview
- project.detail
- notebook.detail
- artifact.index
- dataset.index
- model.index
- execution.index
- provenance.receipts
- command.receipts

Commands are bounded and idempotency-aware. Queries are explicitly read-only. Arbitrary code execution remains disabled.

The authoritative store is PostgreSQL. Command execution reuses existing domain-authority validation and revision controls rather than duplicating them in the client.
