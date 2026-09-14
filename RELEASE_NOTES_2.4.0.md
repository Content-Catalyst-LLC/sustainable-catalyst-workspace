# Sustainable Catalyst Workspace v2.4.0
## Dataset, Model & Execution Run Registry

**Release date:** 2026-09-14  
**Previous release:** v2.3.0 — Background Jobs & Compute Orchestration Foundation

### Added

- PostgreSQL-backed dataset registry with revision history and optimistic revision preconditions.
- PostgreSQL-backed model registry with model type, framework, algorithm, configuration, schemas, lineage, source artifact, and optional execution route metadata.
- Revisioned parameter-set registry for named model/run parameters.
- Durable execution-run registry with frozen dataset/model/parameter references.
- Deterministic SHA-256 input and reproducibility fingerprints.
- Execution-run event history and output registry.
- Workspace artifact linkage for run outputs.
- `executionRunId` linkage from durable jobs to registered runs.
- Worker-driven propagation of job lifecycle state into linked execution runs.
- WordPress server-proxy routes for datasets, models, parameter sets, runs, events, and outputs.
- Additive PostgreSQL migration `004_dataset_model_execution_run_registry.sql`.

### Preserved

- Local-first Workspace project semantics.
- Project schema `sc-workspace-project/20.0`.
- Notebook schema `sc-workspace-notebook/3.0`.
- v2.3.0 durable jobs and separate worker architecture.
- Server-configured orchestration routes only; browsers still cannot select arbitrary backend URLs.
- Existing PostgreSQL project/notebook/artifact/job/recovery data.

### Deliberate limits

- Registry records describe models; they do not establish scientific validity or quality.
- Creating a run does not automatically execute it.
- A reproducibility fingerprint records deterministic lineage; it is not a claim that an external environment can necessarily be reconstructed without its referenced dependencies.
- No automated model selection or automatic approval is introduced.
