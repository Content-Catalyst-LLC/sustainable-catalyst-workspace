# Sustainable Catalyst Workspace v2.12.0 — Polyglot Scientific Runtime Fabric

## Polyglot Scientific Runtime Fabric

Workspace v2.12.0 generalizes the scientific execution plane across Python, SQL, R, Julia, and WebAssembly. Python and bounded SQL execute in-process. R, Julia, and WASM are represented by server-configured runtime adapters using one language-neutral execution envelope and Arrow-compatible table descriptors.

The fabric remains capability-bounded: browser requests cannot provide runtime URLs or credentials, raw SQL source is not accepted, and arbitrary Python/R/Julia/shell/WASM source execution is disabled. Every successful non-Python polyglot job persists a content-addressed result artifact and immutable execution receipt linked to job/run provenance.

Storage schema remains 35. Project schema remains `sc-workspace-project/20.0`. Export schema remains `sc-workspace-project-export/20.0`.

## v2.8.0 — Execution Policy, Resource Budgets & Runtime Sandboxing

Workspace v2.8.0 adds a policy-enforcement layer to controlled runtime handoffs. Execution policies are revisioned backend objects that define eligible target products and operations, minimum runtime-adapter trust, CPU/memory/wall-time/output/process/temp-storage ceilings, and bounded sandbox requirements. Every reproduction execution plan freezes a policy revision and produces an immutable eligibility decision before human-authorized dispatch.

Sandboxing in v2.8.0 is a **pre-dispatch policy gate and runtime requirement contract**, not an unrestricted local arbitrary-code executor. Workspace can require adapter attestation, a container adapter, a remote sandbox, pinned container identity, server-routed networking, read-only roots, no-new-privileges, dropped capabilities, and explicit denial of host filesystem, Docker socket, and privileged execution. Downstream specialist runtimes remain responsible for OS/container enforcement of strict sandbox profiles.

Resource budgets and the frozen sandbox envelope travel with the server-side job handoff, preserving policy provenance without exposing service credentials or accepting client-supplied runtime URLs.

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
