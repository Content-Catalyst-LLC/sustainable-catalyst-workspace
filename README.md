# Sustainable Catalyst Workspace

Sustainable Catalyst Workspace is the free personal working environment across Sustainable Catalyst.

## Current release: **v0.17.0 — Workflow & Activity Intelligence**

Workspace supports Guided Workflows, Research, Evidence, Analysis, Decision, Canvas, Traceability, Briefing, Personal Knowledge, Responsible AI Assistance, Import & Interoperability, Share & Portable Projects, Search & Knowledge Graph, and Workflow & Activity Intelligence. v0.17.0 adds an inspectable, device-local activity layer that surfaces explicit next actions, workflow progress, recent changes, and explainable attention conditions without productivity scoring, behavioral telemetry, or server analytics.

## WordPress shortcodes

```text
[sc_workspace]
[sc_workspace_entry]
[sc_workspace_platform]
```

## Persistence boundary

Workspace remains usable without signing in. Projects, Personal Knowledge, AI review state, interoperability/share history, graph preferences, and Activity Intelligence state remain device-local. Optional WordPress authentication identifies the account session only; Workspace does not automatically upload or synchronize project content.

## Contracts

- Project: `sc-workspace-project/11.0`
- Object: `sc-workspace-object/1.0`
- Research: `sc-workspace-research/1.0`
- Analysis: `sc-workspace-analysis/1.0`
- Decision: `sc-workspace-decision/1.0`
- Canvas: `sc-workspace-canvas/1.0`
- Traceability: `sc-workspace-traceability/1.0`
- Briefing: `sc-workspace-briefing/1.0`
- Guided Workflows: `sc-workspace-guided-workflows/1.0`
- Personal Knowledge: `sc-workspace-personal-knowledge/1.0`
- Responsible AI: `sc-workspace-ai-assistance/1.0`
- Interoperability: `sc-workspace-interoperability/1.0`
- Portable interchange: `sc-workspace-interchange/1.0`
- Share: `sc-workspace-share/1.0`
- Portable project: `sc-workspace-portable-project/1.0`
- Knowledge Graph: `sc-workspace-knowledge-graph/1.0`
- Activity Intelligence: `sc-workspace-activity-intelligence/1.0`
- Identity: `sc-workspace-identity/1.0`
- Handoff: `sc-workspace-handoff/2.0`
- Storage schema: `18`

## Workflow & Activity Intelligence boundary

Activity Intelligence is derived from explicit Workspace state. The stored workspace-level layer contains only user-created next actions, dismissed-signal IDs, and view/filter preferences. There is no productivity score, time-on-page measurement, behavioral telemetry, server activity analytics, or automatic workflow/task completion.

## Public routes

- Workspace: `/platform/`
- Knowledge Library: `/knowledge-libraries/`

## Product Registry

Canonical ID `sustainable-catalyst-workspace`, family `commercial`, free public access, lifecycle `experimental`.

See `docs/WORKFLOW_ACTIVITY_INTELLIGENCE_V0170.md`.
