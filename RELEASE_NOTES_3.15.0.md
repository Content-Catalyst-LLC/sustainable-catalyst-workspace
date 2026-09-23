# Workspace v3.15.0 Release Notes

**Release:** Investigative Search, Discovery & Cross-Case Retrieval Workspace

Workspace v3.15.0 introduces cross-object and cross-case investigative retrieval on top of the v3.14 source provenance/evidence-integrity layer.

### Added

- 18 typed search/discovery operations, bringing the typed endpoint contract to 218 operations.
- Saved search heads and immutable revision history.
- Search execution records with deterministic result fingerprints.
- Project-scoped and cross-case retrieval across statements, events, entities, documents, testimony, spatial observations, media artifacts, and source records.
- Search facets, descriptive retrieval diagnostics, retrieval discovery graphs, curated result collections, and immutable search snapshots.
- Unified Research Context integration.
- WordPress thin-client/server-proxy support.
- Migration 046.

### Preserved boundaries

Search relevance is lexical retrieval relevance only. v3.15 does not automatically rank evidence, score source reliability or credibility, infer relationships, determine truth, infer culpability, or choose a narrative.

### Rollback baseline

v3.14.0. Migration 046 is additive.
