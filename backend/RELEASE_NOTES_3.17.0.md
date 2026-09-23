# Workspace v3.17.0 — Uncertainty, Sensitivity & Probabilistic Investigation Workspace — Release Notes

## Release summary

Workspace v3.17.0 introduces a first-class uncertainty, sensitivity, and probabilistic-investigation layer on top of v3.16 quantitative reconstruction and scientific-analysis handoffs.

### Added

- versioned uncertainty assessments and immutable revisions
- evidence-fingerprint-pinned uncertainty parameters
- explicit distribution families and distribution parameters
- scenario/ensemble objects with evidence references
- Sobol, Morris, local, OAT, variance-decomposition, regression, correlation, and custom sensitivity requests
- specialist handoff targets for Workbench, Research Lab, Catalyst Analytics R, and Platform Core
- fingerprint-pinned probabilistic result bindings
- deterministic project manifest, graph, diagnostics, and immutable snapshots
- Unified Research Context integration
- 18 new typed endpoints
- WordPress server-proxy routes and v3.17 browser adapter
- PostgreSQL migration 048

### Preserved

v3.16 quantitative reconstruction/scientific-analysis handoffs, v3.15 investigative search, v3.14 source integrity, v3.13 media provenance, v3.12 spatial evidence, v3.11 documentary evidence, v3.10 entity resolution, v3.9 timeline reconstruction, and Catalyst Analytics R 2.2 remain in the release lineage.

### Epistemic controls

The release does not automatically infer probability distributions, execute sensitivity analyses, rank evidence, select truth, infer causality or culpability, or choose a narrative. Probabilistic output is explicitly not treated as factual truth.

### Release identity

- Version: `3.17.0`
- Baseline: `3.16.0`
- Migration: `048_uncertainty_sensitivity_probabilistic_investigation_workspace.sql`
- Typed endpoints: `254`
- New endpoints: `18`
- Rollback runtime: `3.16.0`
