# Workspace v3.51.0 — Cross-Language Entity & Toponym Resolution Workspace

Adds provenance-aware entity and toponym resolution across languages, scripts, transliterations, historical names, exonyms/endonyms, temporal contexts, geographic regions, and external identifiers. Resolution remains candidate-based: the runtime can return resolved, ambiguous, or unresolved outcomes and never automatically merges research entities.

## Backend
- New bounded cross-language entity resolution runtime with six operations.
- Candidate search for general entities and place/toponym-only searches.
- Evidence-bearing scoring using name forms, identifiers, type, temporal overlap, region, language and script context.
- Decision generation preserves ambiguity rather than forcing identity.
- Resolution lineage records original query context and human/research decisions.

No database or storage schema migration is required. Rollback target: v3.50.0.
