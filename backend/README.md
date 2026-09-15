# Sustainable Catalyst Workspace Backend v2.12.0

Workspace v2.12.0 adds the first bounded in-process scientific compute runtime to the existing durable Worker/API architecture.

## Scientific compute engines

- NumPy — matrix algebra and polynomial roots
- Pandas — descriptive statistics and declarative table transforms
- SciPy — sampled-series integration and bounded quadratic optimization
- SymPy — restricted symbolic simplification, differentiation, integration, and equation solving

The compute runtime exposes a finite operation registry. It does **not** accept arbitrary Python source, shell commands, client-supplied modules, runtime URLs, host filesystem paths, Docker socket access, or privileged execution.

## Execution path

Scientific operations use the normal durable Workspace job queue and separate worker. During execution the worker records progress events and checks the durable cancellation flag. Successful results are serialized as canonical JSON, stored in content-addressed Workspace object storage, linked to an execution run when one is present, and recorded by an immutable compute execution receipt containing engine/version, request fingerprint, artifact SHA-256, byte count, and wall time.

The worker container is globally bounded with a 2 CPU / 2 GiB / 256 PID envelope, read-only root filesystem, dropped Linux capabilities, and `no-new-privileges`; `/tmp` is an isolated bounded tmpfs and `/data` remains the explicit result-artifact volume.

## Compatibility

- previous release: v2.10.0
- rollback release: v2.10.0
- PostgreSQL migration: `011_python_scientific_compute_runtime.sql`
- host API binding remains `127.0.0.1:8094`
- browser-local storage schema remains 35
- project schema remains `sc-workspace-project/20.0`


## v2.12 polyglot runtime fabric
Python and bounded SQL are in-process. R, Julia, and WASM use optional server-configured HTTP runtime adapters. Client-supplied runtime URLs, credentials, and arbitrary source execution remain disabled.
