# Workspace v2.26.0 — Server-Side Notebook & Artifact Orchestration

- Adds durable notebook execution plans and orchestration receipts.
- Resolves explicit artifact inputs to revision + SHA-256 bindings.
- Topologically validates notebook execution dependencies and rejects cycles.
- Queues only ready steps and advances downstream jobs after successful dependencies.
- Keeps browser scheduling authority disabled and arbitrary-code execution disabled.
- Preserves the restored v2.24.1/v2.25 full interface asset lineage.
