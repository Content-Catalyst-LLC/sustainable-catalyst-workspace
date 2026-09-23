# Workspace v3.15.0 — Investigative Search, Discovery & Cross-Case Retrieval Workspace

## Purpose

Workspace v3.15.0 adds a backend-authoritative discovery layer across the existing investigative object graph without creating a second authority for evidence bodies. It supports project-scoped and cross-case lexical retrieval over statements, events, entities, documents, testimony, spatial observations, media artifacts, and source records.

## Durable objects

- versioned saved searches
- immutable search executions/result sets
- researcher-curated search collections
- immutable project search snapshots

## Retrieval semantics

Search hits contain canonical object references, object fingerprints, short retrieval snippets, matched fields, project identity, and a deterministic lexical score. The lexical score is only a text-retrieval relevance signal. It is not an evidence-quality, reliability, credibility, authenticity, or truth score.

## Searchable canonical kinds

- statement
- event
- entity
- document
- testimony
- spatial-observation
- media-artifact
- source

## v3.15 capabilities

- deterministic lexical retrieval across supported investigative objects
- cross-case/project retrieval with explicit project scope
- kind and review-state filtering
- deterministic saved search revisions
- search execution provenance and immutable result fingerprints
- descriptive facets and coverage diagnostics
- retrieval discovery graph where query→result edges are explicitly marked as retrieval matches, not investigative relationships
- researcher-curated cross-case collections
- immutable project search snapshots
- Unified Research Context search-facet/diagnostic integration
- WordPress server-proxy and thin-client adapter support

## Epistemic boundaries

- `automaticEvidenceRanking=false`
- `automaticSourceReliabilityScoring=false`
- `automaticCredibilityScoring=false`
- `automaticTruthDetermination=false`
- `automaticRelationshipInference=false`
- `automaticCulpabilityInference=false`
- `automaticNarrativeSelection=false`

The system may order results by lexical match relevance. That ordering must never be represented as evidentiary strength or source quality.

## Migration

`046_investigative_search_discovery_cross_case_retrieval_workspace.sql`

Tables:

- `workspace_investigation_saved_search_heads`
- `workspace_investigation_saved_search_revisions`
- `workspace_investigation_search_executions`
- `workspace_investigation_search_collections`
- `workspace_investigation_search_snapshots`

## Rollback

Runtime rollback baseline: Workspace v3.14.0. Migration 046 is additive and may remain in place during runtime rollback.
