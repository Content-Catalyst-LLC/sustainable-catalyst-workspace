# Platform Core Visual Analysis & Research Object Workspace — v3.6.0

This release turns Workspace visualizations into provenance-aware, reference-first research objects that can participate in the Platform Core v3 research session without shifting specialist authority.

## Contract
- Graph schema: `sc-workspace-visual-research-object-graph/1.0`
- Workspace schema: `sc-workspace-platform-core-visual-analysis-research-object-workspace/1.0`
- New migration: `037_platform_core_visual_analysis_research_object_workspace.sql`
- Rollback baseline: `3.5.0`
- Analytics R migration `036_catalyst_analytics_r_runtime_adapter.sql` remains unchanged.

## Research-object projection
A project can project visualization specs, views, linked views, source references, execution/scientific-object references, Workspace-side Core bindings, and the mapped Platform Core research session into a deterministic graph with SHA-256 fingerprints.

## Core boundary
The bridge sends references, fingerprints, identifiers, roles, and provenance metadata. It does not copy canonical Workspace datasets, models, results, inline visualization data, or evidence bodies into Core. Binding is explicit rather than automatic.

## Human-control boundary
v3.6.0 adds no automatic scientific interpretation, evidence ranking, decision authority, mass binding, or unrestricted code execution.
