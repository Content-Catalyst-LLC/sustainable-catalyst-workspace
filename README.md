# Sustainable Catalyst Workspace

Sustainable Catalyst Workspace is a free, local-first personal environment for structured research, evidence, analysis, decisions, visual reasoning, briefing, knowledge organization, recovery, review, and governed handoff across the Sustainable Catalyst ecosystem.

## Current release

**v0.30.0 — Public Beta & Product Readiness**

v0.30.0 is the first public-beta consolidation milestone. Workspace now opens on a Start environment that foregrounds the work rather than the software, supports blank projects and four guided first-project pathways, surfaces recent work and local runtime capability status, and strengthens keyboard navigation, focus behavior, empty states, responsive presentation, reduced-motion support, and forced-colors resilience. It introduces no new project database and no automatic telemetry, cloud upload, lifecycle advancement, or hidden readiness score.

## Data boundary

- Workspace storage schema: **27** (unchanged from v0.29.0)
- Project schema: **`sc-workspace-project/12.0`** (unchanged)
- Canonical object schema: **`sc-workspace-object/1.0`**
- Lifecycle schema: **`sc-workspace-project-lifecycle/1.0`**
- Public-beta readiness schema: **`sc-workspace-public-beta-readiness/1.0`**
- Canonical public route: **`/platform/`**
- Canonical Knowledge Library route: **`/knowledge-libraries/`**

Guest/local Workspace remains fully functional. Account backup and explicitly enrolled cross-device sync remain optional. Institutional governance remains a separate Catalyst Intelligence boundary.

## Start pathways

- Research Investigation
- Analytical Assessment
- Decision Case
- Publication Preparation
- Blank project
- Continue recent project

## Public contracts

Workspace exposes versioned REST contracts under `/wp-json/sc-workspace/v1/`, including `/project-contract`, `/change-review-contract`, `/safe-actions-contract`, `/reconciliation-contract`, `/audit-trail-contract`, `/project-lifecycle-contract`, and `/public-beta-contract`.

## Principles

- human judgment stays visible;
- AI assists but does not decide;
- provenance and evidence remain inspectable;
- higher-risk actions require explicit review;
- local work stays useful without an account;
- public beta does not change the storage, privacy, or institutional boundary;
- organizational governance belongs in Catalyst Intelligence rather than being silently introduced into personal Workspace.
