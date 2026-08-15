# Sustainable Catalyst Workspace v1.4.0 — Knowledge Graph & Relationship Explorer

Current release: **v1.4.0 — Knowledge Graph & Relationship Explorer**

## Knowledge Graph & Relationship Explorer

Workspace v1.4.0 upgrades the existing deterministic research graph with explicit path tracing, incoming/outgoing backlink ledgers, visible edge explanations, Knowledge Library provenance pointer nodes, and portable graph snapshots. The graph remains derived at runtime from canonical local records; it does not create a server graph database or infer hidden semantic relationships.

Path tracing is bounded to five hops and uses recorded relationships only. Snapshot export carries graph identifiers, labels, relationship metadata, filters, and an optional traced path without copying canonical object bodies.

See `RELEASE_NOTES_1.4.0.md` and `docs/KNOWLEDGE_GRAPH_RELATIONSHIP_EXPLORER_V140.md`.

## Research Projects & Library Continuity

Workspace v1.3.0 connects research projects with Knowledge Library saved searches, watchlists, research-queue items, source bundles, and private personal recommendations without creating a second Library datastore or account. Library context is staged browser-locally, preserves canonical Library identity and provenance, and requires an explicit **Add to project** action before promotion into a Workspace source object.

The canonical Knowledge Library remains `/knowledge-libraries/`. Guest Workspace remains first-class; authenticated continuity reuses the existing WordPress identity. The continuity layer does not automatically pull Library data, run background synchronization, expose private recommendations, invoke AI, emit behavioral/query telemetry, or mutate canonical Library records.

## Universal Workspace Search

Workspace v1.2.0 added one local-first retrieval surface across projects, Workspace objects, notebooks and notebook blocks, research questions and claims, analysis questions, decisions, briefing drafts, Citation Library references, and explicit Research Tasks.

The search corpus is derived in-browser from existing records rather than copied into a second canonical datastore. It reuses Workspace's deterministic, explainable Advanced Retrieval ranking and keeps result origins inspectable so a search result can route back to the project or specialized surface that owns it.

Search remains deliberately bounded: no server index, semantic embeddings, hidden personalization, query telemetry, automatic AI, automatic semantic inference, or canonical record mutation. Storage remains 35, Project remains `sc-workspace-project/20.0`, and Project Export remains `sc-workspace-project-export/20.0`.

See `RELEASE_NOTES_1.2.0.md` and `docs/UNIVERSAL_WORKSPACE_SEARCH_KNOWLEDGE_RETRIEVAL_V120.md`.

## General Availability

Sustainable Catalyst Workspace is a free, local-first environment for carrying questions, evidence, analysis, decisions, composition, review, and deliberate handoff across Sustainable Catalyst.

v1.0.0 establishes the stable General Availability contract after the v0.84.0 production-sign-off closure and readiness gate. It does not introduce a new project subsystem or canonical schema migration. Storage remains 35, Project remains `sc-workspace-project/20.0`, and Project Export remains `sc-workspace-project-export/20.0`.

General Availability remains explicitly human-controlled. The v0.84.0 readiness dossier is predecessor evidence; the v1.0.0 release certificate stays on HOLD until the required live checks, release operator, production URL, and final attestation are complete.

Workspace does not automatically certify a release, inspect project contents, purge caches, roll back, migrate canonical project data, or emit behavioral telemetry.

See `RELEASE_NOTES_1.0.0.md` and `docs/GENERAL_AVAILABILITY_V100.md`.
