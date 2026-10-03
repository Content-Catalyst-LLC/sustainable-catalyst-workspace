# Workspace v3.61.0 — Human Governance, Approval & Intervention Runtime

v3.61.0 adds an explicit human-governance control plane above the bounded v3.60 Agentic Research Workflow Runtime.

## Runtime

`sc-workspace-human-governance-approval-intervention-runtime/1.0`

Endpoints:

- `GET /v1/human-governance-approval-intervention-runtime`
- `GET /v1/human-governance-approval-intervention-runtime/operations`
- `POST /v1/human-governance-approval-intervention-runtime/execute`

Bounded operations:

- `workspace.governance.validate`
- `workspace.governance.register-policy`
- `workspace.governance.request-approval`
- `workspace.governance.decide`
- `workspace.governance.intervene`
- `workspace.governance.resume`
- `workspace.governance.snapshot`

## Governance model

Policies identify actions that require human approval and the roles authorized to approve them. Approval requests are explicit objects. Decisions are separately recorded, immutable audit objects. Human interventions can pause, cancel, request revision, or escalate a governed subject. Resume is an explicit human action rather than an automatic consequence of a runtime state transition.

## Hard boundaries

- Agents do not receive approval authority.
- Self-approval is prohibited.
- Required approvals cannot be bypassed by this runtime.
- Rejected approval does not silently become approved.
- Automatic resume is disabled.
- Arbitrary code execution remains disabled.
- External side effects are not enabled by this release.
- Governance decisions and interventions preserve provenance references.

## Relationship to v3.60

v3.60 provides bounded agentic workflow planning, step progression, review, replanning, receipts and snapshots. v3.61 does not replace those controls. It adds a human authority layer that can gate higher-impact actions and explicitly interrupt or resume governed research workflows.

No new database migration is required for this release; the v3.61 objects are runtime contracts and portable audit records.
