# Sustainable Catalyst Workspace

Sustainable Catalyst Workspace is the free personal working environment across Sustainable Catalyst.

## Current release: **v0.21.0 — Accounts & Cloud Persistence Foundation**

Workspace supports Guided Workflows, Research, Evidence, Analysis, Decision, Canvas, Traceability, Briefing, Personal Knowledge, Responsible AI Assistance, Import & Interoperability, Share & Portable Projects, Search & Knowledge Graph, Workflow & Activity Intelligence, Collaboration Foundation, and Institutional Handoff. v0.21.0 adds optional manual account cloud recovery on top of the hardened local-first runtime. Guest use remains first-class; signed-in users choose exactly when a project backup is created.

## WordPress shortcodes

```text
[sc_workspace]
[sc_workspace_entry]
[sc_workspace_platform]
```

## Persistence boundary

Workspace remains usable without signing in. Projects and Workspace-level state remain device-local by default. Optional WordPress authentication unlocks explicit per-project cloud recovery backups; sign-in itself never uploads project content and background synchronization remains disabled.

v0.21.0 retains the v0.20.0 recovery safeguards and adds manual account backups stored privately per WordPress user, with restore-as-copy semantics and explicit size/count guardrails.

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
- Account Persistence: `sc-workspace-account-persistence/1.0`
- Cloud Backup: `sc-workspace-cloud-backup/1.0`
- Storage schema: `21`

## v0.21.0 data boundary

- Storage schema advances from `20` to `21`.
- Project schema remains `sc-workspace-project/11.0`.
- Guest/local Workspace remains fully functional.
- Signed-in users can explicitly create manual cloud backups.
- Automatic upload and background cloud sync remain disabled.
- Cloud restore always creates a new local copy.
- Team storage and institutional permissions remain outside Workspace.

## Accessibility target

v0.21.0 sets WCAG 2.2 AA as the public release target and adds an application skip link, stronger visible focus, focus movement between top-level Workspace views, reduced-motion handling, and forced-colors resilience.

## Public routes

- Workspace: `/platform/`
- Knowledge Library: `/knowledge-libraries/`

## Product Registry

Canonical ID `sustainable-catalyst-workspace`, family `commercial`, free public access, lifecycle `experimental`.

See `docs/ACCOUNTS_CLOUD_PERSISTENCE_FOUNDATION_V0210.md`.
