# Sustainable Catalyst Workspace v0.12.0

## Personal Knowledge Environment

This release turns accumulated project work into a navigable personal knowledge layer while preserving canonical Workspace Objects and the local-first privacy boundary.

### Changes

- Adds Projects / Knowledge as top-level Workspace views.
- Builds a browser-local cross-project index from existing canonical Workspace Objects.
- Adds search and filters across titles, summaries, content, tags, provenance, project, type, and archived scope.
- Adds provenance inspection, internal reference counts, and deterministic related-work signals with visible reasons.
- Adds reusable knowledge collections storing only stable project/object references.
- Opens results back in the originating project/object editor.
- Exports portable knowledge collection JSON packages.
- Cleans collection references on object/project deletion.
- Adds `/wp-json/sc-workspace/v1/personal-knowledge-contract`.
- Retains `/knowledge-libraries/` as the canonical Knowledge Library route.

### Data boundary

Storage advances from schema 12 to schema 13. Project schema remains `sc-workspace-project/10.0`; existing project content is not rewritten. No server index, embeddings, cloud synchronization, or duplicate knowledge object store is introduced.
