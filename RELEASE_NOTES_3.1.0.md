# Sustainable Catalyst Workspace v3.1.0

## Platform Core v3 Unified Research Runtime Integration

Workspace v3.1.0 is the first application release to consume Platform Core v3.0's unified research, scientific-computing, and investigation runtime. The integration is reference-first: Workspace remains authoritative for projects, scientific objects, execution, study packages, visualization specifications, and handoff semantics; Core stores unified session/context bindings and declared cross-product lineage.

### Added
- Durable one-to-one Workspace project → Platform Core research-session mappings.
- Durable integration receipts for session creation and object/execution/visual/package/handoff bindings.
- Platform Core v3 readiness/contract compatibility checks.
- Account-scoped Core session summary, lineage, and bundle views.
- Server-only Platform Core write credential; credentials never enter browser configuration.
- Migration `032_platform_core_v3_unified_research_runtime_integration.sql`.
- WordPress server proxy and thin browser boundary for the integration.

### Authority boundaries
Platform Core does not execute Workspace scientific work, infer findings, authorize Workspace users, or receive canonical Workspace object content. Specialist Workspace data remains authoritative in Workspace.

### Deployment
Backend first. Apply migration 032, deploy/verify Workspace v3.1.0 against the already-deployed Platform Core v3.0 runtime, then update the WordPress plugin. Rollback baseline: Workspace v3.0.0.
