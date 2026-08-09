# Sustainable Catalyst Workspace

Sustainable Catalyst Workspace is the free personal working environment across Sustainable Catalyst.

## Current release

**v0.12.0 — Personal Knowledge Environment**

Workspace supports a connected personal workflow across Guide, Research, Evidence, Analysis, Decision, Canvas, Traceability, Briefing, reusable Workspace Objects, and cross-product handoffs. v0.12.0 adds a device-local Personal Knowledge Environment that makes canonical objects discoverable and reusable across projects without copying project content into a second knowledge store.

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
