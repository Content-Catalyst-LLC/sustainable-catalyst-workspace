# Workspace v3.9.1 — Catalyst Analytics R v2.2 Provider Promotion

Workspace v3.9.1 promotes the governed Catalyst Analytics R provider from v2.1.0 to v2.2.0 while preserving the v3.9 Timeline, Event Reconstruction & Investigative Sequence Workspace.

## Added / changed
- vendored `catalystanalyticsr` R package promoted to 2.2.0
- production R image build assertion promoted to 2.2.0
- Workspace analytical provider metadata promoted to provider 2.2.0 / adapter 3.9.1
- explicit diagnostics contract: `sc.analytics-r.statistical-diagnostics-validation.v1`
- health/readiness flags for statistical diagnostics and validation
- WordPress provider adapter promoted to 2.2.0
- typed-client release identity promoted to Workspace 3.9.1

## Preserved
- Platform Core provider contract: `sc.core.analytical-runtime-provider.v1`
- Workspace-owned authentication, execution, persistence, and receipts
- bounded method whitelist; no arbitrary R/code execution
- read-only/non-root production R runtime
- v3.9 investigation graph, timeline, event reconstruction, and temporal diagnostics
- migration lineage through `040_timeline_event_reconstruction_investigative_sequence_workspace.sql`

## Database
No migration is required. Existing analytical-provider receipts already persist provider version per receipt, so new v2.2.0 executions remain distinguishable from historical v2.1.0 executions.

## Epistemic boundary
Statistical diagnostics and validation outputs are evidence for human review. Workspace and Catalyst Analytics R do not automatically certify scientific validity, causal truth, substantive significance, or a preferred model.

Rollback runtime baseline: v3.9.0. Database migration 040 remains authoritative and unchanged.
