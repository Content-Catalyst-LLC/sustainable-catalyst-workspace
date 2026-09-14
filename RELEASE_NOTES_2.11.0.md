# Workspace v2.11.0 — Python Scientific Compute Runtime & Execution Engine

## Purpose
v2.11.0 is the first Workspace release that performs bounded scientific computation directly in the Python worker. It builds on the durable jobs, reproducible run registry, policy, telemetry, and compliance layers introduced in v2.3–v2.10.

## Scientific engines
- **NumPy 2.3.5** — matrix solve/inverse/determinant/eigendecomposition/multiplication and polynomial roots.
- **Pandas 2.2.3** — descriptive statistics and declarative select/filter/sort/group/aggregate transforms.
- **SciPy 1.17.0** — sampled-series integration and bounded quadratic optimization.
- **SymPy 1.14.0** — restricted symbolic simplify/differentiate/integrate/solve operations.

## Registered operations
- `workspace.compute.describe`
- `workspace.compute.transform`
- `workspace.compute.linear-algebra`
- `workspace.compute.symbolic`
- `workspace.compute.integrate-series`
- `workspace.compute.optimize-quadratic`
- `workspace.compute.roots-polynomial`

## Execution and provenance
Scientific work executes through the existing durable Workspace job queue and separate worker process. Jobs emit progress events and check the durable cancellation flag between compute stages. Successful results are encoded as canonical JSON and written to content-addressed object storage. When an `executionRunId` is present, the result artifact is registered as an execution-run output and therefore contributes to the run reproducibility fingerprint.

Every successful compute job also records a durable compute execution receipt containing the operation, engine and engine version, request fingerprint, result artifact ID, result SHA-256, result bytes, and wall time.

## Safety boundary
Workspace v2.11.0 is **not** a generic Python shell. It does not accept arbitrary Python source, shell commands, subprocess execution, client-supplied runtime URLs or credentials, host filesystem paths, Docker socket access, or privileged execution.

Operation-specific limits bound table rows/columns, matrix dimensions, symbolic expression length/complexity, optimizer iterations, polynomial degree, and result bytes. The worker container adds a global 2 CPU / 2 GiB / 256 PID envelope, read-only root filesystem, dropped Linux capabilities, `no-new-privileges`, and bounded tmpfs.

## Persistence
Migration `011_python_scientific_compute_runtime.sql` adds `workspace_compute_execution_receipts` and grants the `sc_workspace` role explicit DML access.

## Compatibility
- Previous release: v2.10.0
- Rollback release: v2.10.0
- Browser storage schema: 35 (unchanged)
- Project schema: `sc-workspace-project/20.0` (unchanged)
- Export schema: `sc-workspace-project-export/20.0` (unchanged)
- Notebook schema: `sc-workspace-notebook/3.0` (unchanged)
