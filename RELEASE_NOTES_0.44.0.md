# Sustainable Catalyst Workspace v0.44.0

## Citation Library & Reference Management

v0.44.0 builds on Advanced Retrieval and Dynamic Research Views with a reusable, first-class reference-management surface inside the Research workspace.

### Added

- Browser-local Workspace Reference Library with up to 1,500 normalized bibliographic references.
- Manual reference creation/editing for articles, books, chapters, reports, webpages, datasets, theses, conference material, and other sources.
- Explicit **Add selected research result** action that creates a reference only from bibliographic/provenance fields already recorded on the selected canonical research result.
- DOI and URL normalization without remote metadata lookup.
- Deterministic duplicate detection using normalized DOI first and a bibliographic fingerprint otherwise.
- Collision-safe citation-key generation based on recorded author/year/title fields.
- Citation previews for APA 7, Chicago author-date, MLA 9, and IEEE using only recorded fields.
- Canonical-origin references linking library entries back to Workspace research records.
- Browser-local citation-style preferences.
- Portable JSON export/import with deterministic per-reference fingerprints.
- Search by title, author, DOI, identifier, citation key, and tags.
- `/wp-json/sc-workspace/v1/citation-library-contract`.
- `sc-workspace-reference/1.0`, `sc-workspace-reference-library/1.0`, `sc-workspace-citation-preferences/1.0`, and `sc-workspace-reference-library-export/1.0` contracts.

### Architecture boundary

This is another schema-stable release:

- Storage: 35 → 35
- Project: 20.0 → 20.0
- Project Export: 20.0 → 20.0
- Notebook Workspace: 8.0 → 8.0
- Notebook Export: 8.0 → 8.0

The Reference Library is Workspace-level browser-local data, not a new Project object store. References may point back to canonical research records, but adding, editing, importing, or deleting a reference does not mutate those records.

Workspace does not query Crossref/DOI services, scrape source pages, infer missing authors/dates/publishers, automatically merge duplicate candidates, or automatically create references. Missing metadata remains visibly missing until a user records it.

### Preserved

The complete v0.32–v0.43 Notebook, Integrated Knowledge, Unified Research Navigation, Advanced Retrieval, and Dynamic Research Views lineage remains active.
