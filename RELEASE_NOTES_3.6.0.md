# Sustainable Catalyst Workspace v3.6.0

## Platform Core Visual Analysis & Research Object Workspace

Workspace v3.6.0 adds the visual-analysis and research-object layer on top of the verified v3.5.0 Catalyst Analytics R Runtime Adapter. This release is intentionally incremental: migration 036 remains the Analytics R migration, and the new visual layer advances the release lineage with migration 037.

### Added
- `GET /v1/visual-research-workspace`
- `GET /v1/visual-research-workspace/projects/{project_id}`
- `GET /v1/visual-research-workspace/projects/{project_id}/visualizations/{visualization_id}`
- `POST /v1/visual-research-workspace/projects/{project_id}/visualizations/{visualization_id}/bind`
- `POST /v1/visual-research-workspace/projects/{project_id}/snapshots`
- `GET /v1/visual-research-workspace/projects/{project_id}/snapshots`
- reference-first visual research graph projection
- explicit visualization/source-to-Core bindings
- linked-view relationships and source provenance pinning
- immutable visual-research snapshots
- Unified Research Project Context visual graph projection
- WordPress server proxy and browser adapter
- migration `037_platform_core_visual_analysis_research_object_workspace.sql`

### Preserved from v3.5.0
- Catalyst Analytics R v2.1.0 provider installation
- `sc.core.analytical-runtime-provider.v1`
- durable analytical-provider receipts
- migration `036_catalyst_analytics_r_runtime_adapter.sql`
- hardened non-root/read-only R runtime

### Authority boundary
Workspace remains authoritative for project state, visualization specifications, scientific objects, execution records, Analytics R receipts, and Workspace-side bindings. Platform Core remains authoritative for unified Core research-session registration and Core-side cross-product bindings. Canonical specialist object bodies are not replicated into Core.
