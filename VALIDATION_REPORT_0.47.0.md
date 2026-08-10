# Sustainable Catalyst Workspace v0.47.0 Validation Report

Release: **v0.47.0 — Research Graph & Relationship Explorer**  
Baseline: **v0.46.1 — Editorial Header Rule Balance / Workspace Import & Interchange**  
Date: 2026-08-10

## Final package validation

The repository ZIP was extracted into a clean directory and validated independently from the working tree.

- 573 Python contract tests passed.
- 27 JavaScript runtime tests passed.
- 5 PHP runtime tests passed.
- 63 JavaScript syntax checks passed.
- 9 PHP syntax checks passed.
- 126 current JSON schema/release records parsed.
- Dedicated v0.47.0 release validator passed.
- Standalone WordPress ZIP independently reported `Version: 0.47.0`.
- Repository and WordPress ZIP integrity checks passed.

## v0.47.0 contract

- Knowledge Graph advances to `sc-workspace-knowledge-graph/2.0`.
- Relationship Explorer contract: `sc-workspace-relationship-explorer/1.0`.
- Added graph coverage for notebooks, notebook blocks, research questions, research claims, citation references, syntheses and Canvas promotion targets.
- Added recorded relationship coverage for explicit notebook references/support/contrast/extension/related links, promotion lineage, synthesis selection, citation origins, claim support and captured-from links.
- All graph edges are derived from recorded Workspace or Citation Library state.
- No semantic embeddings, server graph database, server search index, hidden relationship inference, automatic semantic-similarity edges, automatic AI or automatic canonical mutation.
- v0.46.1 4px editorial header rule retained.
- Storage remains 35; Project and Project Export remain 20.0; Notebook Workspace remains 8.0.
