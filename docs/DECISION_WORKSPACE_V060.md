# Decision Workspace — v0.6.0

Decision Workspace completes the first end-to-end public Workspace loop: Research → Evidence → Analysis → Decision.

## Contract
- `sc-workspace-decision/1.0`
- Project schema `sc-workspace-project/5.0`
- Storage schema 7
- Local-first; no server project storage or cloud synchronization.

## Decision model
A project can hold multiple decision records. Each record can own options, weighted criteria, option/criterion assessments, risks, a selected option, rationale, confidence, and a canonical `Decision` Workspace Object.

## Integrity
Stable IDs connect decision records to Workspace Objects. Handoffs expose only project/object IDs; decision content is never placed in URLs. v0.5.0 projects migrate non-destructively.
