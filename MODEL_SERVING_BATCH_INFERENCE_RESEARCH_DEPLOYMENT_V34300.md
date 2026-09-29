# Workspace v3.43.0 — Model Serving, Batch Inference & Research Deployment

## Purpose
Provide a bounded, reproducible serving and deployment-preparation layer for Workspace neural model packages without turning Workspace into an arbitrary hosting or infrastructure-control plane.

## Operations
1. `workspace.neural.serving-model-binding`
2. `workspace.neural.serving-compatibility-evaluate`
3. `workspace.neural.serving-infer`
4. `workspace.neural.batch-inference-plan`
5. `workspace.neural.batch-inference-execute`
6. `workspace.neural.research-deployment-readiness`
7. `workspace.neural.research-deployment-manifest`
8. `workspace.neural.research-deployment-receipt`

## Serving model
A serving binding embeds and re-verifies the existing `sc-workspace-neural-model-package/1.0` artifact. The binding is immutable, content-addressed, and records package/model/runtime fingerprints, task/shape contracts, request limits, concurrency limits, audience, and serving mode.

Serving inference delegates only to the already-governed packaged inference path. Targets are rejected. Each serving result retains the underlying prediction artifact and its model-package lineage.

## Batch inference
The batch planner validates input width, row identifiers, row count, and batch size, then emits a deterministic stable-order plan. Batch execution verifies the data fingerprint against that plan and runs bounded package inference over each planned slice. It does not call an external queue.

## Research deployment
Readiness combines a serving binding with runtime compatibility and optional batch planning. The manifest records the research context and optional v3.40 reproducible research-package lineage. The receipt records an operator-declared state. Workspace itself does not provision an endpoint, start infrastructure, or make a deployment public.

## Security / epistemic boundaries
Client-supplied serving endpoints, public endpoints, deployment URLs, container images, registry credentials, tokens, API keys, arbitrary code, and serialized neural modules are rejected. Deployment artifacts describe readiness and lineage; they are not evidence, and model predictions remain model-derived outputs rather than observed facts.
