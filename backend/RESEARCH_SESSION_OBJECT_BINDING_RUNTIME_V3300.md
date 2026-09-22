# Workspace v3.3.0 — Research Session & Object Binding Runtime

Workspace v3.3.0 makes Platform Core v3 research-session binding an operational, durable Workspace capability.

## What changed
- Added a durable Workspace-side registry for Core session/object bindings.
- Added fingerprint pinning and idempotent replay for unchanged references.
- Added explicit project binding reconciliation for selected scientific objects, executions, visualization specs, study packages, and research handoffs.
- Added a generic typed binding API and WordPress server proxy.
- Extended Unified Research Project Context with binding-state visibility.
- Added migration `034_research_session_object_binding_runtime.sql`.
- Carried migration `033_unified_research_project_context.sql` into the deployment line and corrected inherited typed-client/version deployment assertions.

## Authority boundary
Workspace retains authority over project state, scientific objects, executions, visualization specifications, packages, and handoffs. Platform Core retains authority over the cross-product unified research session registry and declared cross-product lineage. Only references, revisions, fingerprints, roles, and provenance metadata are bound; object bodies are not replicated into Core.

## Non-goals
This release does not automatically bind every project object, execute scientific work, infer findings, rank evidence, resolve contradictions, or make decisions. Reconciliation is explicit and user-directed.
