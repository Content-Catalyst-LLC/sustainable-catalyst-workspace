# Workspace Objects & Artifact Model — v0.3.0

## Purpose

The Workspace Object model gives every project a common, typed container for reusable work. The object model is intentionally broad enough to bridge research, analysis, decision, publication, and data workflows without binding Workspace to one product's internal format.

## Canonical object types

| Type | Intended role |
| --- | --- |
| `source` | A reference, publication, webpage, interview, filing, or other origin of information. |
| `evidence` | A claim-supporting excerpt, observation, finding, or evidentiary item. |
| `dataset` | A structured data asset, dataset description, query result, or data handoff. |
| `analysis` | Analytical reasoning, model output, interpretation, comparison, or calculation result. |
| `decision` | A decision record, option assessment, recommendation, or resolved choice. |
| `document` | Drafts, briefs, memos, reports, outlines, or other authored material. |
| `export` | A generated or packaged output intended to leave the active workflow. |

## Object contract

Each object has:

- stable ID;
- type;
- title;
- summary;
- content;
- lifecycle status (`draft`, `working`, `ready`);
- tags;
- provenance fields;
- created/updated/archive timestamps.

The schema is `sc-workspace-object/1.0`.

## Persistence and migration

Storage schema v3 embeds objects inside each device-local Workspace Project. v0.2 projects are normalized into `sc-workspace-project/2.0` with `objects: []` and `activeObjectId: null`. A project is bounded to 250 objects in this release to keep the browser-local persistence model explicit.

## Handoff contract

When an object is active, Workspace may add `sc_workspace_object=<stable object id>` alongside the existing project ID. Object content is never serialized into the URL. A matching session-storage handoff record uses `sc-workspace-handoff/1.1`.

## Non-goals

v0.3.0 does not introduce server persistence, accounts, cloud synchronization, collaboration, binary attachment storage, automatic publication, or cross-product object conversion. Those remain later concerns.
