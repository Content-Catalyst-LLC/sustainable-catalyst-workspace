# Workspace v3.35.0 Validation Report

Release: **Workspace v3.35.0 — GNN Evaluation, Explainability & Graph Embeddings**

## Local certification

- Python compilation: PASS
- New v3.35 GNN analysis tests: 5/5 PASS
- v3.33 foundation + v3.34 training + v3.35 analysis compatibility suite: 18/18 PASS
- Neural runtime version: 3.35.0
- Bounded neural operation registry: 69 operations
- Database migration: none

## Certified capabilities

- node, graph, and link-prediction evaluation
- bounded classification calibration reports
- node-output input-gradient explainability
- bounded feature-occlusion explainability
- node embeddings and mean-pooled graph embeddings
- cosine, Euclidean, and dot-product embedding analysis
- bounded nearest-neighbor queries
- governed Workspace artifact persistence and execution-receipt lineage

## Guardrails

Explainability outputs are model-derived sensitivity/perturbation artifacts, not causal evidence. Artifacts carry `isObservedEvidence=false`. Client-supplied code, packages, runtime URLs, credentials, and opaque serialized PyTorch modules remain disabled.
