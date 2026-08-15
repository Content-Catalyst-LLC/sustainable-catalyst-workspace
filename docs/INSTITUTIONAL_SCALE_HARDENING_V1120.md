# Workspace v1.12.0 — Large Workspace & Institutional Scale Hardening

This release productionizes bounded behavior for very large Workspace states. It extends the existing Scale & Performance and Long-Session systems rather than adding a second datastore.

## Scale envelope

The browser-local planner evaluates explicit project, object, notebook-block, search-index, graph, citation, storage, and export-volume thresholds. Findings are advisory and deterministic. There is no hidden score.

## Pressure handling

At higher pressure Workspace recommends smaller render windows, chunked local indexing, bounded graph neighborhoods, sharded exports, cooperative yielding, and recovery checkpoints before heavy operations. Critical pressure never authorizes automatic deletion, compaction, archival, migration, upload, server offload, or canonical mutation.

## Institutional exports

Large exports receive a manifest describing bounded shards. The manifest does not itself embed project content and never uploads or merges shards automatically.

## Recovery

Critical-mode guidance requires the existing operation journal and last-known-good recovery state. Recovery remains explicit and user-controlled.
