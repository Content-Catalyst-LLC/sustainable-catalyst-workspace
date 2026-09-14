# Sustainable Catalyst Workspace v2.7.0

## v2.7.0 — Reproduction Execution Plans & Controlled Runtime Handoffs

Workspace v2.7.0 adds a bounded execution-preparation layer on top of v2.6 reproducibility verification. Reproduction execution plans freeze a reproduction run, environment revision, runtime-adapter revision, target product, operation, job payload, and readiness checks before any work is queued. Dispatch requires a separate human-authorized handoff call and can only use server-configured routes. Client-supplied runtime URLs, credentials, and arbitrary shell commands remain prohibited.


## Runtime Adapter Registry & Reproduction Verification

Workspace remains local-first in the browser while its Python backend now records revisioned runtime adapters and immutable reproduction verification receipts.

### v2.6.0
- revisioned runtime adapter descriptors for Python, R, Julia, and bounded custom runtimes
- runtime/environment compatibility and readiness checks
- exact runtime-adapter revision/fingerprint frozen into execution runs
- reproduction plans derived from frozen execution-run provenance
- deterministic rerun comparison using input, environment, runtime-adapter, and output SHA-256 evidence
- verification classifications: `exact`, `compatible`, `divergent`, or `incomplete`
- no arbitrary shell/command execution and no automatic re-execution

Storage schema remains 35. Project schema remains `sc-workspace-project/20.0`. Export schema remains `sc-workspace-project-export/20.0`.
