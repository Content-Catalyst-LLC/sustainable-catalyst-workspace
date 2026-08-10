# Workspace v0.42.0 — Knowledge Search & Advanced Retrieval

## Purpose

v0.42.0 turns the v0.40 Integrated Knowledge corpus and v0.41 unified Research surface into a stronger retrieval environment without introducing a second canonical knowledge store.

## Retrieval model

The search corpus is derived at runtime from the canonical Integrated Knowledge index. Retrieval spans Workspace Objects, Notebooks, Notebook blocks, Research questions, and Research claims across local projects.

Available retrieval fields are query, kind, subtype, project, tag, origin, provenance, scope, and sort. Quoted phrases are treated as phrase tokens. Search remains deterministic and browser-local.

## Provenance-aware ordering

Relevance ordering uses inspectable deterministic signals: title matches, tags, recorded source fields, summary/content matches, project matches, recorded provenance, and explicit relationships. The interface displays the deterministic retrieval score and the reasons that produced it. There is no semantic embedding index or opaque AI ranker.

## Saved searches

Saved searches are browser-local preferences under `sc_workspace_saved_searches_v1`. They are not written into Project 20.0 data, do not affect portable project exports, and do not create account/cloud state.

## Related material

Related navigation uses only recorded structure and provenance: explicit notebook links, Research evidence relationships, promotion lineage, same recorded source, and notebook containment. It does not infer semantic similarity.

## Release boundary

v0.42.0 remains schema-stable at Storage 35 / Project 20.0 / Project Export 20.0 / Notebook Workspace 8.0. No project migration or canonical data rewrite is required.
