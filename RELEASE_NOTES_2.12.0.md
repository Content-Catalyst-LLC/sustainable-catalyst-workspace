# Workspace v2.12.0 — Polyglot Scientific Runtime Fabric

v2.12.0 generalizes the v2.11 scientific execution engine into a language-neutral runtime fabric.

## Runtime languages
- Python — existing in-process scientific compute runtime.
- SQL — new bounded in-process analytical runtime; raw SQL text is never accepted.
- R — server-configured research/statistics runtime adapter.
- Julia — server-configured numerical/simulation runtime adapter.
- WebAssembly — server-configured portable sandbox runtime adapter.

## Interchange
All runtimes use the `sc-workspace-polyglot-execution-envelope/1.0` contract and an Arrow-compatible table descriptor (`sc-workspace-arrow-compatible-table/1.0`). v2.12 uses bounded records JSON as the canonical transport representation while preserving language-neutral logical column types for later Arrow IPC expansion.

## Security boundary
Runtime URLs and credentials are configured only on the server. Browser/job payloads cannot provide runtime endpoints or service credentials. v2.12 does not add arbitrary Python, R, Julia, SQL, shell, or WebAssembly code execution.

## Durability
Migration 012 adds immutable polyglot execution receipts linked to job IDs, execution runs, result artifacts, SHA-256 digests, language/runtime identity, and transport.
