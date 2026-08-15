# Workspace v1.4.0 — Knowledge Graph & Relationship Explorer

v1.4.0 upgrades the existing deterministic knowledge graph rather than introducing a second graph store.

## Added
- explicit path tracing between any two graph nodes, bounded to five hops;
- incoming/outgoing backlink ledger for the focused node;
- visible edge explanations showing the recorded relationship source;
- Knowledge Library pointer nodes when Library continuity provenance is explicit;
- portable graph snapshot export containing identifiers, labels, relationship metadata, filters, and optional traced path;
- current Universal Search / Library continuity integration while preserving canonical origin ownership.

## Boundaries
The graph remains derived at runtime from browser-local Workspace records. It does not use embeddings, hidden semantic similarity, automatic relationship inference, a server graph database, automatic AI, behavioral/query telemetry, or canonical record mutation. Graph snapshots do not copy canonical object bodies.

Storage 35, Project `sc-workspace-project/20.0`, and Export `sc-workspace-project-export/20.0` remain frozen.
