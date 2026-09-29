# Cross-Runtime ML / Neural Workflow Orchestration — v3.44.0

## Architecture
Workspace v3.44.0 coordinates registered classical ML and neural operations through immutable typed workflow objects. The orchestration layer plans and validates; server-managed Workspace job/runtime infrastructure remains responsible for actual execution.

## Operations
- cross-runtime-workflow-contract
- cross-runtime-step-contract
- cross-runtime-dependency-validate
- cross-runtime-handoff-plan
- cross-runtime-execution-plan
- cross-runtime-run-receipt
- cross-runtime-reproducibility-manifest
- cross-runtime-lineage

## Guardrails
Workflows are DAGs with at most 64 steps. Only registered `workspace.ml.*` and pre-existing `workspace.neural.*` operations can be referenced. Arbitrary code, package requests, shell commands, runtime URLs, credentials, and serialized opaque models are rejected. Execution plans are deterministic and do not themselves initiate remote execution.
