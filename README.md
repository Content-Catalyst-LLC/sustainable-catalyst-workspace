# Sustainable Catalyst Workspace

Sustainable Catalyst Workspace is the free personal working environment across Sustainable Catalyst.

## Current release: **v0.20.0 — Stability, Accessibility & Release Readiness**

Workspace supports Guided Workflows, Research, Evidence, Analysis, Decision, Canvas, Traceability, Briefing, Personal Knowledge, Responsible AI Assistance, Import & Interoperability, Share & Portable Projects, Search & Knowledge Graph, Workflow & Activity Intelligence, Collaboration Foundation, and Institutional Handoff. v0.20.0 consolidates that capability into a more resilient public runtime with local recovery, diagnostics, accessibility hardening, and release-readiness checks.

## WordPress shortcodes

```text
[sc_workspace]
[sc_workspace_entry]
[sc_workspace_platform]
```

## Persistence boundary

Workspace remains usable without signing in. Projects and Workspace-level state remain device-local. Optional WordPress authentication identifies the account session only; Workspace does not automatically upload or synchronize project content.

v0.20.0 adds a last-known-good local snapshot before verified writes, read-after-write persistence verification, visible fallback after corrupted state is quarantined, privacy-minimized local diagnostics, and an explicit emergency backup export.

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
- Share: `sc-workspace-share/1.0`
- Knowledge Graph: `sc-workspace-knowledge-graph/1.0`
- Activity Intelligence: `sc-workspace-activity-intelligence/1.0`
- Collaboration: `sc-workspace-collaboration/1.0`
- Institutional Handoff: `sc-workspace-institutional-handoff/1.0`
- Release Readiness: `sc-workspace-release-readiness-contract/1.0`
- Diagnostic Report: `sc-workspace-diagnostic-report/1.0`
- Emergency Backup: `sc-workspace-emergency-backup/1.0`
- Storage schema: `20`

## v0.20.0 data boundary

This is intentionally a schema-stable release:

- Storage schema remains `20`.
- Project schema remains `sc-workspace-project/11.0`.
- Cloud sync remains disabled.
- Server project storage remains disabled.
- Automatic telemetry remains disabled.
- Diagnostic exports exclude project content, source URLs, and device identifiers.
- Emergency backup export is explicit and contains project content.

## Accessibility target

v0.20.0 sets WCAG 2.2 AA as the public release target and adds an application skip link, stronger visible focus, focus movement between top-level Workspace views, reduced-motion handling, and forced-colors resilience.

## Public routes

- Workspace: `/platform/`
- Knowledge Library: `/knowledge-libraries/`

## Product Registry

Canonical ID `sustainable-catalyst-workspace`, family `commercial`, free public access, lifecycle `experimental`.

See `docs/STABILITY_ACCESSIBILITY_RELEASE_READINESS_V0200.md`.
