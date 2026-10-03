# Workspace v3.62.0 — Multi-Agent Orchestration & Specialist Coordination

## Purpose

Workspace v3.62.0 adds a bounded coordination layer above the v3.60 Agentic Research Workflow Runtime and beneath the v3.61 Human Governance, Approval & Intervention Runtime. It allows a coordinator to assemble specialist teams, delegate capability-bound assignments, collect specialist result receipts, preserve disagreements, synthesize cross-specialist findings, and create explicit governance handoffs for sensitive actions.

## Specialist role families

- Research / evidence
- Data and quantitative analysis
- Modeling / forecasting
- Scientific computing
- Linguistics / corpus
- Investigation / provenance
- Visualization
- Synthesis

Roles are descriptive coordination identities, not unrestricted autonomous agents. Every specialist must declare capability IDs, and assignments are rejected when the requested capability is not granted to that specialist.

## Bounded operations

1. `workspace.multi-agent.validate`
2. `workspace.multi-agent.register-specialist`
3. `workspace.multi-agent.create-team`
4. `workspace.multi-agent.delegate`
5. `workspace.multi-agent.record-result`
6. `workspace.multi-agent.reconcile`
7. `workspace.multi-agent.governance-handoff`
8. `workspace.multi-agent.snapshot`

## Governance rule

Neither coordinators nor specialists receive approval authority. Sensitive actions such as claim promotion, evidence mutation, model approval, external side effects, high-impact decisions, and irreversible operations produce a governance requirement. v3.62 can construct a handoff to `workspace.governance.request-approval`, but it cannot approve, bypass, or resume on behalf of a human.

## Conflict handling

Reconciliation preserves dissent as explicit unresolved conflict records. It does not rank evidence automatically, determine truth, or give the coordinator decision authority. A conflict can be marked as requiring human resolution.

## Production boundaries

- Arbitrary code execution: disabled
- Automatic external side effects: disabled
- Coordinator approval authority: disabled
- Specialist approval authority: disabled
- Governance bypass: disabled
- Automatic truth determination: disabled
- Automatic evidence ranking: disabled
- Dissent preservation: enabled
- Provenance preservation: enabled
- Max specialists: 16
- Max assignments: 64
- Max coordination rounds: 8

No database migration is required for this release. Runtime objects are portable and provenance-bearing.
