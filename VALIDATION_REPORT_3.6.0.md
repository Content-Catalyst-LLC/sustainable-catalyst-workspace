# Workspace v3.6.0 Validation Report

Release: **Platform Core Visual Analysis & Research Object Workspace**

## Build strategy
v3.6.0 is a guarded incremental overlay on the exact v3.5.0 Catalyst Analytics R repository/deployment. The overlay refuses to apply unless both `036_catalyst_analytics_r_runtime_adapter.sql` and `backend/app/analytics_r_provider.py` are present. This prevents the earlier version/migration collision from recurring.

## Packaging validation
- overlay patcher Python compilation: PASS
- Mac release script shell syntax: PASS
- VPS deployment script shell syntax: PASS
- migration numbering: PASS (`036` Analytics R preserved, `037` visual research added)

## Integration validation
The v3.6 overlay was exercised against a v3.5-shaped baseline constructed from the verified v3.4 source and the documented v3.5 Analytics R contract boundaries.

- overlay baseline guard: PASS
- v3.6 static validator: PASS
- focused visual-research tests: **4 passed**
- FastAPI/OpenAPI typed-contract projection: PASS
- missing typed OpenAPI operations: **0**
- Python compileall: PASS
- WordPress PHP lint: PASS
- JavaScript syntax checks: PASS
- rollback baseline: `3.5.0`
- release migration lineage: `037_platform_core_visual_analysis_research_object_workspace.sql`

## Production gates built into deploy script
The VPS script will not mark the release successful unless it verifies all of the following on the exact merged production tree:
- Workspace backend reports `3.6.0`
- Catalyst Analytics R adapter remains enabled
- Catalyst Analytics R provider remains installed at `2.1.0`
- Core analytical-provider contract remains `sc.core.analytical-runtime-provider.v1`
- analytical-provider receipts remain enabled
- Platform Core visual-analysis/research-object Workspace is enabled
- visual scene graph, explicit Core binding, and immutable snapshot flags are enabled
- migration lineage is `037_platform_core_visual_analysis_research_object_workspace.sql`
- visual-research OpenAPI endpoints resolve
- Catalyst Analytics R package/provider runtime check passes
- R runtime remains non-root/read-only
- visual-research snapshot table exists
