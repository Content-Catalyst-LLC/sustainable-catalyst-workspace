# Sustainable Catalyst Workspace

Sustainable Catalyst Workspace is a free, local-first personal environment for structured research, evidence, analysis, decisions, visual reasoning, briefing, knowledge organization, recovery, review, and governed handoff across the Sustainable Catalyst ecosystem.

## Current release

**v0.29.0 — Governance Milestones & Project Lifecycle**

v0.29.0 adds a human-controlled Lifecycle environment with seven explicit project states: Draft, Evidence-ready, Analysis-ready, Decision-ready, Review-ready, Publication-ready, and Institutional-ready. Workspace derives visible readiness conditions from the work already in the project, but never advances a lifecycle automatically and never converts readiness into a hidden score or certification. Every declaration requires acknowledgement and rationale, and the recorded readiness snapshot becomes portable project governance history.

## Data boundary

- Workspace storage schema: **27**
- Project schema: **`sc-workspace-project/12.0`**
- Canonical object schema: **`sc-workspace-object/1.0`**
- Lifecycle schema: **`sc-workspace-project-lifecycle/1.0`**
- Governance milestone schema: **`sc-workspace-governance-milestone/1.0`**
- Canonical public route: **`/platform/`**
- Canonical Knowledge Library route: **`/knowledge-libraries/`**

Guest/local Workspace remains fully functional. Account backup and explicitly enrolled cross-device sync remain optional. Institutional governance remains a separate Catalyst Intelligence boundary.

## Public contracts

Workspace exposes versioned REST contracts under `/wp-json/sc-workspace/v1/`, including:

- `/project-contract`
- `/object-contract`
- `/traceability-contract`
- `/change-review-contract`
- `/safe-actions-contract`
- `/reconciliation-contract`
- `/reconciliation-receipts-contract`
- `/audit-trail-contract`
- `/project-lifecycle-contract`

## Principles

- human judgment stays visible;
- AI assists but does not decide;
- provenance and evidence remain inspectable;
- high-risk actions require explicit review;
- local work stays useful without an account;
- organizational governance belongs in Catalyst Intelligence rather than being silently introduced into personal Workspace.
