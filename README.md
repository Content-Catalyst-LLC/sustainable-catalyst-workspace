# Sustainable Catalyst Workspace

Sustainable Catalyst Workspace is the free personal working environment across Sustainable Catalyst.

## Current release

**v0.10.0 — Briefing & Publication Studio**

Workspace supports a connected personal workflow across Research, Evidence, Analysis, Decision, Canvas, Traceability, Briefing, reusable Workspace Objects, and cross-product handoffs. v0.10.0 adds a local-first Briefing & Publication Studio for structured drafts, document materialization, and portable Markdown, HTML, and JSON publication packages without automatic CMS publication.

## WordPress shortcodes

```text
[sc_workspace]
[sc_workspace_entry]
[sc_workspace_platform]
```

## Persistence boundary

Workspace remains usable without signing in. Projects and their research, analysis, decisions, Canvas boards, traceability records, and reusable objects remain device-local unless explicitly exported. Optional WordPress authentication identifies the account session only; Workspace does not automatically upload or synchronize project content.

## Contracts

- Project: `sc-workspace-project/8.0`
- Object: `sc-workspace-object/1.0`
- Research: `sc-workspace-research/1.0`
- Analysis: `sc-workspace-analysis/1.0`
- Decision: `sc-workspace-decision/1.0`
- Canvas: `sc-workspace-canvas/1.0`
- Traceability: `sc-workspace-traceability/1.0`
- Identity: `sc-workspace-identity/1.0`
- Storage schema: `10`
- Handoff: `sc-workspace-handoff/2.0`

## Public routes

- Workspace: `/platform/`
- Knowledge Library: `/knowledge-libraries/`

## Product Registry

Canonical ID `sustainable-catalyst-workspace`, family `commercial`, free public access, lifecycle `experimental`.

See `docs/CLOSING_CTA_CLEANUP_ACTION_ALIGNMENT_V0901.md`.
