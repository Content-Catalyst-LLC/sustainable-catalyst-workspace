# Workspace v3.18.0 — Causal Analysis & Alternative Explanation Workspace — Release Notes

## Release summary

Workspace v3.18.0 introduces a first-class causal-analysis and alternative-explanation layer on top of v3.17 uncertainty/sensitivity/probabilistic investigation and v3.16 quantitative reconstruction/scientific-analysis handoffs.

### Added

- versioned causal questions and immutable revisions
- explicit researcher-authored causal structures, including DAG and partial-DAG contracts
- causal variable roles and human-authored directed relations
- explicit competing/alternative explanations linked by reference to hypotheses and fingerprint-pinned evidence
- explicit identification assumptions with asserted/supported/challenged/violated/unknown states
- causal-analysis handoffs for difference-in-differences, instrumental variables, matching, weighting, regression discontinuity, interrupted time series, g-formula, targeted learning, Bayesian causal analysis, structural equation models, negative controls, and custom methods
- specialist destinations for Workbench, Research Lab, Catalyst Analytics R, and Platform Core
- fingerprint-pinned causal result bindings for effect estimates, intervals, falsification/placebo tests, robustness checks, sensitivity diagnostics, balance diagnostics, causal graphs, and identification diagnostics
- deterministic causal manifest, graph, diagnostics, combined project analysis, and immutable snapshots
- Unified Research Context integration
- 18 new typed endpoints
- WordPress server-proxy routes and v3.18 browser adapter
- PostgreSQL migration 049

### Preserved

v3.17 uncertainty/sensitivity/probabilistic investigation, v3.16 quantitative reconstruction/scientific-analysis handoffs, v3.15 investigative search, v3.14 source integrity, v3.13 media provenance, v3.12 spatial evidence, v3.11 documentary evidence, v3.10 entity resolution, v3.9 timeline reconstruction, and Catalyst Analytics R 2.2 remain in the release lineage.

### Epistemic controls

The release does not automatically discover a causal graph, infer causality, select confounders, claim identification, rank alternative explanations, rank evidence, determine truth, infer culpability, or select a narrative. Returned causal estimates remain model- and assumption-conditional research objects requiring human interpretation.

### Release identity

- Version: `3.18.0`
- Baseline: `3.17.0`
- Migration: `049_causal_analysis_alternative_explanation_workspace.sql`
- Typed endpoints: `272`
- New endpoints: `18`
- Rollback runtime: `3.17.0`
