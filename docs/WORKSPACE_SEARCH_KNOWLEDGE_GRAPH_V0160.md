# Sustainable Catalyst Workspace v0.16.0

## Workspace Search & Knowledge Graph

v0.16.0 turns the Personal Knowledge Environment into an explicit, inspectable graph across device-local Workspace projects. The graph is derived from canonical projects, Workspace Objects, provenance, traceability lineage, research evidence links, analysis inputs, decision inputs, and deterministic same-source relationships.

### Changes

- Adds a top-level **Graph** environment beside Projects, Knowledge, Import & Interoperability, and Share.
- Adds cross-project graph search with node-type, relationship, project, scope, and one/two-hop depth filters.
- Adds project, provenance, Source, Evidence, Dataset, Analysis, Decision, Document, and Export nodes.
- Adds explicit relationship types including contains, sourced-from, same-source, evidence-from, uses, informs, supports, contradicts, derived-from, produced-by, supersedes, and cites.
- Adds an accessible focused-neighborhood SVG plus a parallel relationship list explaining each visible connection.
- Derives the graph locally from canonical objects; it does not copy project content into a second graph database.
- Adds deterministic cross-project same-source links based on identical provenance URL/title keys.
- Adds `sc-workspace-knowledge-graph/1.0` and `/wp-json/sc-workspace/v1/knowledge-graph-contract`.

### Data boundary

Storage advances from schema 16 to 17. Project schema remains `sc-workspace-project/11.0`. The release adds only workspace-level graph preferences and focus state. No semantic embeddings, server graph database, remote search index, or hidden relationship inference are introduced.
