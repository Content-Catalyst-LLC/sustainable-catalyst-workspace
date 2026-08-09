# Sustainable Catalyst Workspace v0.29.0

## Governance Milestones & Project Lifecycle

v0.29.0 adds a human-controlled project lifecycle across Workspace. Projects can be explicitly declared Draft, Evidence-ready, Analysis-ready, Decision-ready, Review-ready, Publication-ready, or Institutional-ready. Workspace derives a visible readiness checklist for each state from existing project evidence and governance records, but it never advances a project automatically and never converts readiness into a hidden score or certification.

### Changes

- Adds the top-level **Lifecycle** Workspace environment.
- Adds `sc-workspace-project-lifecycle/1.0` and `sc-workspace-governance-milestone/1.0`.
- Adds seven human-declared lifecycle states.
- Requires explicit acknowledgement and rationale for every lifecycle declaration.
- Captures a point-in-time readiness snapshot with met and unmet conditions.
- Allows backward transitions and allows a human to declare a milestone even when visible conditions remain unmet.
- Stores milestone history with the project so it remains portable through local export, account backup, sync, restore copies, sharing, and reconciliation.
- Adds Project Lifecycle as an explicit source in the derived Audit Trail.
- Keeps account identity separate from decision responsibility; lifecycle attribution is not inferred from login identity.

### Data boundary

Storage advances from schema 26 to 27. Projects advance from `sc-workspace-project/11.0` to `sc-workspace-project/12.0` to carry portable lifecycle history. Migration is non-destructive and preserves canonical objects, account persistence, cross-device sync, version history, Safe Actions, reconciliation receipts, collaboration, and institutional handoffs.
