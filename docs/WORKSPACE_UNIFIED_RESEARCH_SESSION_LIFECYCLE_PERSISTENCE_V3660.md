# Workspace v3.66.0 — Unified Research Session & Lifecycle Persistence

v3.66.0 makes the v3.64 Integrated Research OS lifecycle durable and resumable as a versioned research-session contract.

Lifecycle: `projects → sources → analysis → models → agents → governance → visualizations → decisions → publication`.

Capabilities include versioned unified research-session objects, cross-session parent lineage, cross-stage bindings, explicit lifecycle transition history, immutable checkpoints, state-only resume, portable read-only snapshots, portable session export, a backend persistence adapter contract, continuity with the existing PostgreSQL/Platform Core research-session binding runtime, and WordPress/standalone parity.

Resume restores state and references only. It does not rerun models or agents, approve or bypass governance, publish, rank evidence, determine truth, choose narratives, perform external side effects, or make decisions.

This release does not replace `research_session_bindings.py`; that runtime remains the backend/Platform Core binding authority.
