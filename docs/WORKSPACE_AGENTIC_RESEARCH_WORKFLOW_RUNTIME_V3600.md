# Workspace v3.60.0 — Agentic Research Workflow Runtime

v3.60.0 turns the existing v3.56 research-pipeline composition capability and the v3.57–v3.59 dataset/experiment/model lineage into a bounded workflow execution layer.

## Runtime

`sc-workspace-agentic-research-workflow-runtime/1.0`

Endpoints:

- `GET /v1/agentic-research-workflow-runtime`
- `GET /v1/agentic-research-workflow-runtime/operations`
- `POST /v1/agentic-research-workflow-runtime/execute`

Bounded operations:

- `workspace.agent.validate`
- `workspace.agent.plan`
- `workspace.agent.next-step`
- `workspace.agent.record-result`
- `workspace.agent.review`
- `workspace.agent.replan`
- `workspace.agent.snapshot`

## Architectural rule

The runtime may coordinate registered Workspace capabilities; it does not bypass them. It preserves existing execution, provenance, research-project, model-lineage, and persistence authority.

## Hard boundaries

The release does not enable arbitrary code execution, automatic claim promotion, automatic evidence mutation, automatic model approval, or automatic external side effects.

Human review can gate execution before a step, after a step, or both.

## Relationship to prior builds

- v3.56.0 provides explicit research-pipeline composition.
- v3.57.0 provides dataset and feature-engineering lineage.
- v3.58.0 provides training/evaluation experiment lineage.
- v3.59.0 provides model registry and research-model lineage.
- v3.60.0 composes those bounded capabilities into an auditable agentic research workflow.

No new database migration is required for this release.
