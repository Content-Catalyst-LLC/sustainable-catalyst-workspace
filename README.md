# Sustainable Catalyst Workspace

Sustainable Catalyst Workspace is the free personal working environment across the Sustainable Catalyst platform.

## Current release

**v0.7.0 — Canvas & Structured Thinking**

Workspace now supports a connected personal workflow:

- Research — questions, sources, reading queues, evidence, and claims.
- Analysis — datasets, variables, assumptions, methods, comparisons, and findings.
- Decision — options, criteria, assessments, risks, rationale, and confidence.
- Canvas — boards, structured nodes, typed relationships, frames, and synthesis.

The dedicated `/platform/` Workspace experience and reversible administrator-controlled Platform conversion from v0.6.1 remain intact.

## WordPress shortcodes

```text
[sc_workspace]
[sc_workspace_entry]
[sc_workspace_platform]
```

## Persistence boundary

Workspace remains usable without signing in. Projects, objects, research, analysis, decisions, and Canvas boards are stored on the current device. Optional WordPress authentication identifies the account session only; v0.7.0 does not upload, claim, or synchronize local project content.

## Contracts

- Project: `sc-workspace-project/6.0`
- Object: `sc-workspace-object/1.0`
- Research: `sc-workspace-research/1.0`
- Analysis: `sc-workspace-analysis/1.0`
- Decision: `sc-workspace-decision/1.0`
- Canvas: `sc-workspace-canvas/1.0`
- Identity: `sc-workspace-identity/1.0`
- Storage schema: `8`
- Handoff: `sc-workspace-handoff/1.5`

## Product Registry

Canonical ID `sustainable-catalyst-workspace`, family `commercial`, free public access, lifecycle `experimental`, canonical product URL `/platform/`.

See `docs/CANVAS_STRUCTURED_THINKING_V070.md`.
