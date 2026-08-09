# Sustainable Catalyst Workspace

Sustainable Catalyst Workspace is the free personal working environment across Sustainable Catalyst.

## Current release: **v0.13.0 — Responsible AI Assistance**

**v0.13.0 — Responsible AI Assistance**

Workspace supports a connected personal workflow across Guide, Research, Evidence, Analysis, Decision, Canvas, Traceability, Briefing, reusable Workspace Objects, Personal Knowledge, and cross-product handoffs. v0.13.0 adds Responsible AI Assistance as an explicit grounding-and-review layer: users select the Workspace Objects that form the request basis, review returned output as a draft, and must explicitly accept it before it can become a canonical Document. Workspace does not automatically send project content to a model or grant AI decision or publication authority.

## WordPress shortcodes

```text
[sc_workspace]
[sc_workspace_entry]
[sc_workspace_platform]
```

## Persistence boundary

Workspace remains usable without signing in. Projects and the Personal Knowledge index remain device-local. The cross-project index is derived in the browser from existing project objects; collections store only stable project/object references. Optional WordPress authentication identifies the account session only; Workspace does not automatically upload or synchronize project content.

## Contracts

- Project: `sc-workspace-project/10.0`
- Object: `sc-workspace-object/1.0`
- Research: `sc-workspace-research/1.0`
- Analysis: `sc-workspace-analysis/1.0`
- Decision: `sc-workspace-decision/1.0`
- Canvas: `sc-workspace-canvas/1.0`
- Traceability: `sc-workspace-traceability/1.0`
- Briefing: `sc-workspace-briefing/1.0`
- Guided Workflows: `sc-workspace-guided-workflows/1.0`
- Personal Knowledge: `sc-workspace-personal-knowledge/1.0`
- Identity: `sc-workspace-identity/1.0`
- Storage schema: `13`
- Handoff: `sc-workspace-handoff/2.0`

## Public routes

- Workspace: `/platform/`
- Knowledge Library: `/knowledge-libraries/`

## Product Registry

Canonical ID `sustainable-catalyst-workspace`, family `commercial`, free public access, lifecycle `experimental`.

See `docs/PERSONAL_KNOWLEDGE_ENVIRONMENT_V0120.md`.


## v0.13.0 — Responsible AI Assistance
Prepare grounded AI requests from selected Workspace Objects, review responses locally, and explicitly accept useful output as traceable working Documents. Workspace does not automatically submit project content to a model or delegate decision authority.
