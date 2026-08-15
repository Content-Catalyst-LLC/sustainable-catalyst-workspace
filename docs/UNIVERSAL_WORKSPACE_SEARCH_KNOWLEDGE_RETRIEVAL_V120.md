# Workspace v1.2.0 — Universal Workspace Search & Knowledge Retrieval

## Purpose
Provide one deterministic, local-first retrieval surface across the Workspace without creating a second canonical datastore.

## Indexed record families
Projects; Workspace Objects; notebooks and notebook blocks; research questions and claims; analysis questions; decision records; briefing drafts; citation references; and explicit research-task records.

## Retrieval model
The universal index is derived at runtime from existing browser-local project state plus the browser-local Citation Library and Research Tasks library. Existing Advanced Retrieval scoring remains deterministic and inspectable. Search results retain canonical origin metadata and route back to the source surface.

## Boundaries
No server search index. No semantic embeddings. No hidden personalization. No query telemetry. No automatic AI. No automatic relationship inference. No canonical content mutation. Storage schema 35, project schema 20.0, and export schema 20.0 remain unchanged.
