# Workspace v3.35.0 — GNN Evaluation, Explainability & Graph Embeddings

Extends the v3.34 GNN training runtime with governed post-training analysis. Adds seven bounded neural operations for evaluation, calibration, explainability, embedding extraction, similarity, and nearest-neighbor analysis. No database migration. Rollback baseline: v3.34.0.

## Boundaries
- no arbitrary model code or package loading
- no opaque serialized modules
- explanation artifacts are explicitly model-derived and `isObservedEvidence=false`
- labels are used for evaluation/calibration but are not persisted inside analysis artifacts
- embedding search is bounded by pair/query/top-k limits
