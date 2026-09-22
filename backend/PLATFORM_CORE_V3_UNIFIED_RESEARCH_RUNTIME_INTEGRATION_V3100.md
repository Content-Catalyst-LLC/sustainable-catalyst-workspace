# Workspace v3.1.0 — Platform Core v3 Unified Research Runtime Integration

Workspace v3.1.0 binds backend-native Workspace projects to Platform Core v3.0 unified research sessions without transferring authority over Workspace projects, scientific objects, or scientific execution.

## Added
- Durable Workspace-project → Core-session mappings.
- Durable integration receipts for session creation and Core bindings.
- Platform Core readiness/compatibility check against `sc.research.unified-research-scientific-investigation-runtime.v1`.
- Reference-first Core bindings for Workspace scientific objects, execution runs, visualization specifications, study packages, and cross-product research handoffs.
- Account-scoped proxy access to Core session summary, lineage, and bundle views.
- WordPress server-proxy and typed-client support; the Core write key never enters browser state.

## Authority boundary
Workspace remains authoritative for project state, scientific objects, calculations, runtime execution, visualization specifications, study-package contents, and Workspace authorization. Platform Core stores cross-product session context and declared lineage references only. Core does not execute Workspace scientific work, infer findings, or authorize Workspace users.

Migration: `032_platform_core_v3_unified_research_runtime_integration.sql`.
Rollback baseline: v3.0.0.
