# Sustainable Catalyst Workspace

Sustainable Catalyst Workspace is the free personal working environment across Sustainable Catalyst.

## Current release: **v0.14.0 — Import & Interoperability**

Workspace supports Guide, Research, Evidence, Analysis, Decision, Canvas, Traceability, Briefing, Personal Knowledge, Responsible AI Assistance, and cross-product handoffs. v0.14.0 adds a browser-local interoperability boundary for staging external files, reviewing what will be created, preserving imported provenance, and exporting portable structured packages.

## WordPress shortcodes

```text
[sc_workspace]
[sc_workspace_entry]
[sc_workspace_platform]
```

## Persistence boundary

Workspace remains usable without signing in. Projects, Personal Knowledge, AI review state, and interoperability activity remain device-local. Optional WordPress authentication identifies the account session only; Workspace does not automatically upload or synchronize project content.

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
- Import & Interoperability: `sc-workspace-interoperability/1.0`
- Portable interchange: `sc-workspace-interchange/1.0`
- Identity: `sc-workspace-identity/1.0`
- Storage schema: `15`
- Handoff: `sc-workspace-handoff/2.0`

## Interoperability boundary

Supported staged imports: JSON, CSV/TSV, Markdown, HTML, and plain text. Imports require explicit target-project selection and human commit. Imported artifacts are draft canonical Workspace Objects with `imported` provenance. Incoming IDs are remapped rather than overwriting existing objects. Interchange packages can carry traceability lineage, which is reconstructed against the new local IDs on commit.

## Public routes

- Workspace: `/platform/`
- Knowledge Library: `/knowledge-libraries/`

## Product Registry

Canonical ID `sustainable-catalyst-workspace`, family `commercial`, free public access, lifecycle `experimental`.

See `docs/IMPORT_INTEROPERABILITY_V0140.md`.
