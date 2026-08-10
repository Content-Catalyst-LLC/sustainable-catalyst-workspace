# Sustainable Catalyst Workspace v0.42.0

## Knowledge Search & Advanced Retrieval

v0.42.0 strengthens the Integrated Knowledge Workspace with fielded, cross-project retrieval while retaining the schema-stable architecture introduced in v0.40 and the unified navigation introduced in v0.41.

### Added

- Advanced retrieval across Workspace Objects, Notebooks, Notebook blocks, Research questions, and Research claims.
- Fields for kind, subtype, project, tag, origin, provenance, active/archive scope, and sort order.
- Quoted-phrase query tokenization.
- Browser-local saved searches with explicit save/load/delete controls.
- Deterministic provenance-aware relevance ordering with visible score and ranking reasons.
- Provenance filters for documented records, explicit links, source URLs, and bibliographic context.
- Related-material navigation from explicit relationships, notebook containment, promotion lineage, Research evidence relationships, and the same recorded source.
- `/wp-json/sc-workspace/v1/knowledge-search-contract`.
- `sc-workspace-knowledge-search/1.0` and `sc-workspace-saved-search/1.0` contracts.

### Architecture boundary

This is a schema-stable release:

- Storage: 35 → 35
- Project: 20.0 → 20.0
- Project Export: 20.0 → 20.0
- Notebook Workspace: 8.0 → 8.0
- Notebook Export: 8.0 → 8.0

Advanced Retrieval derives from the existing Integrated Knowledge corpus. It does not introduce a server search index, semantic embeddings, automatic AI, automatic relationship inference, a duplicate knowledge store, or canonical record mutation.

### Preserved

v0.42.0 retains the complete v0.32–v0.41 Notebook and Integrated Knowledge lineage, including Source Capture, collections/backlinks, promotion, synthesis/citations, Grounded Assistance, portable/conflict-safe Notebook sync, Notebook Review & Provenance, Integrated Knowledge, and Unified Research Navigation.
