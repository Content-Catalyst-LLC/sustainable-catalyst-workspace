# Research Collections & Dynamic Views — v0.43.0

## Purpose

v0.43.0 makes the Integrated Knowledge Workspace easier to organize after retrieval. It deliberately avoids introducing a second research database.

A smart collection is a named retrieval definition. A saved view is a retrieval definition plus presentation preferences. Both are stored as browser-local preferences. The actual result set is recalculated from canonical Workspace records whenever Research renders.

## Smart collections

Smart collections can capture the current query, kind, subtype, project, tag, origin, provenance, scope, and sort criteria. The collection stores those criteria, not the matching records.

This means a collection can change naturally as canonical research evolves. Adding an Evidence object that matches an existing collection causes it to appear the next time the collection is evaluated; no collection membership table needs to be synchronized.

## Saved views

Saved views add explicit presentation preferences to retrieval criteria:

- group by project
- group by kind
- group by subtype
- group by origin
- no grouping
- compact density
- comfortable density

Views remain browser-local and do not mutate projects.

## Built-in research lenses

The Research workspace includes six built-in dynamic lenses:

1. Sources
2. Evidence
3. Decisions
4. Analysis
5. Notebooks
6. Documented

Applying a built-in lens preserves the user's current project and active/archive scope. This makes the same controls useful both across the full Workspace and as project-wide Sources/Evidence/Decision views.

## Derived dashboard

The dashboard is calculated from the same canonical Integrated Knowledge corpus and reports Sources, Evidence, Decisions, records with documented provenance, projects, and total records within the current project/scope lens.

There is no hidden dashboard score and no server analytics pipeline.

## Governance boundary

v0.43.0 does not:

- duplicate canonical research records into collections;
- store dynamic membership snapshots;
- infer semantic collection membership;
- run automatic AI classification;
- mutate projects when a collection or view is saved or deleted;
- introduce a server collection/search index.

The v0.42 Advanced Retrieval layer remains the source of truth for filtering and explainable ranking.
