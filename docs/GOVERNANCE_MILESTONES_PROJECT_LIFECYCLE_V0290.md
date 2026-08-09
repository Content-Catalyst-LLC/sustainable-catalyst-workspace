# Governance Milestones & Project Lifecycle — v0.29.0

## Purpose

Project Lifecycle gives a person an explicit way to state where a Workspace project stands without asking Workspace to make that judgment for them. Readiness evidence is derived from existing project records and shown as a checklist; the declaration itself remains a human governance action.

## Lifecycle states

1. Draft
2. Evidence-ready
3. Analysis-ready
4. Decision-ready
5. Review-ready
6. Publication-ready
7. Institutional-ready

States are descriptive milestones, not permissions. They do not publish work, approve a decision, synchronize content, or promote a project to Catalyst Intelligence.

## Readiness model

`sc-workspace-project-lifecycle/1.0` derives explicit conditions from canonical project state. Examples include whether research purpose is defined, evidence and provenance exist, analysis methods and inputs are recorded, decision alternatives and criteria exist, contested findings remain, review threads remain open, or publication-ready outputs exist.

The readiness result contains named checks, sources, and met/unmet state. It contains no combined score and is not a certification.

## Human declaration

Every milestone declaration requires:

- a chosen target lifecycle state;
- an explicit acknowledgement that the state is being declared by a person;
- a rationale; and
- a point-in-time readiness snapshot.

Workspace permits backward transitions. It also permits a person to declare a state while some readiness checks remain unmet, but those unmet conditions are preserved in the milestone receipt.

## Audit and portability

Milestones are stored inside the project and therefore travel with project export, account backup, cross-device sync, restore copies, portable sharing, and reconciliation. The Project Audit Trail derives lifecycle events from this authoritative milestone history and does not copy them into a shadow audit database.

## Migration

- Workspace storage: 26 → 27
- Project schema: `sc-workspace-project/11.0` → `sc-workspace-project/12.0`
- Existing projects receive an empty lifecycle container with state `draft`.
- Existing project contents and canonical object IDs are preserved.
