# Sustainable Catalyst Workspace v1.8.0 — Shared Review Rooms & Controlled Collaboration

Current release: **v1.8.0 — Shared Review Rooms & Controlled Collaboration**

## Shared Review Rooms & Controlled Collaboration

Workspace v1.8.0 adds controlled, browser-local review rooms over the existing collaboration, policy, comments, proposals, and frozen review-handoff foundation. Project owners can create a room around an explicit project scope, invite named local review actors with descriptive roles, freeze an immutable review snapshot, collect comments, move the room through explicit review states, and export a portable room package and event ledger.

Review rooms preserve canonical project ownership. Invitations are deliberate records rather than automatic messages or account creation; permissions describe capabilities inside the portable review model rather than server-enforced access control. Imported review material never edits the source project automatically, and only the room owner can close the room.

Workspace does not introduce live co-editing, a shared tenant, team cloud storage, background synchronization, automatic proposal application, automatic AI, behavioral telemetry, query telemetry, or canonical schema migration. Storage remains 35, Project remains `sc-workspace-project/20.0`, and Project Export remains `sc-workspace-project-export/20.0`.

See `RELEASE_NOTES_1.8.0.md` and `docs/SHARED_REVIEW_ROOMS_CONTROLLED_COLLABORATION_V180.md`.

## Cross-Device Continuity & Account Sync Productionization

Workspace v1.7.0 productionized the existing account-sync foundation without changing Workspace's local-first ownership model. Authenticated users can explicitly enroll an individual project for continuity, inspect a deterministic sync plan, run manual synchronization, preserve both sides of conflicts, recover interrupted operations, and export a metadata-only continuity receipt.

The continuity planner distinguishes local-only work, first enrollment, safe push, guarded pull, remote-copy recovery, cloud-copy recreation, no-op, and conflict states. Revision preconditions and unchanged-local-baseline checks remain mandatory; silent last-write-wins behavior is prohibited. The local project remains canonical on the current device and the cloud head remains a continuity copy rather than a replacement canonical store.

Guest Workspace remains first-class. Account sign-in does not automatically enroll projects, background synchronization is off, automatic upload is off, and continuity receipts exclude project contents, query text, source URLs, device identifiers, and account-profile data. Workspace does not introduce device fingerprinting, team/institutional sync, automatic AI, behavioral telemetry, query telemetry, or canonical schema migration.

See `RELEASE_NOTES_1.7.0.md` and `docs/CROSS_DEVICE_CONTINUITY_ACCOUNT_SYNC_PRODUCTIONIZATION_V170.md`.

## Workbench & Decision Studio Round-Trip Workflows

Workspace v1.6.0 turns the existing Workbench and Decision Studio handoffs into explicit, governed round trips. Users choose the project context to export, open the specialist tool with stable IDs only, and can later import typed return packages that must match the originating project, handoff, and destination before anything is materialized.

Workbench supports calculation, simulation, optimization, engineering analysis, data transformation, and sensitivity analysis. Decision Studio supports decision packets, scenario comparison, tradeoff analysis, option assessment, risk review, and decision briefs. Returned artifacts preserve method, parameters, constraints, assumptions, scenarios, risks, units, uncertainty, and environment notes where supplied, and Workspace records deterministic `derived-from` traceability back to the explicitly selected outbound context.

Workbench and Decision Studio remain the specialist execution environments. Workspace does not automatically upload context, execute specialist workflows, invoke AI, commit unmatched returns, emit behavioral/query telemetry, mutate canonical specialist records, or migrate Storage 35 / Project 20.0 / Export 20.0.

See `RELEASE_NOTES_1.6.0.md` and `docs/WORKBENCH_DECISION_STUDIO_ROUNDTRIP_V160.md`.

## Lab & Scientific Workspace Integration

Workspace v1.5.0 adds an explicit scientific round trip between Workspace and Lab. Users select the exact source, evidence, dataset, analysis, document, or export objects to carry into Lab; the portable context package preserves project/handoff identity, provenance, methodology, units, uncertainty, and relevant traceability. Lab returns are imported explicitly and materialize as canonical Workspace dataset, analysis, export, or document objects with deterministic derived-from lineage back to the selected context.

The bridge does not automatically upload context, execute Lab workflows, commit returned artifacts, invoke AI, emit behavioral/query telemetry, or mutate canonical Lab records. Storage remains 35, Project remains `sc-workspace-project/20.0`, and Project Export remains `sc-workspace-project-export/20.0`.

See `RELEASE_NOTES_1.5.0.md` and `docs/LAB_SCIENTIFIC_WORKSPACE_INTEGRATION_V150.md`.

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
