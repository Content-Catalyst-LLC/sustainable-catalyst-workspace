# GNN Evaluation, Explainability & Graph Embeddings — v3.35.0

## Operations
- `workspace.neural.gnn-evaluate`
- `workspace.neural.gnn-calibration-report`
- `workspace.neural.gnn-explain-gradient`
- `workspace.neural.gnn-explain-occlusion`
- `workspace.neural.gnn-embedding-extract`
- `workspace.neural.gnn-embedding-similarity`
- `workspace.neural.gnn-embedding-neighbors`

The runtime supports v3.34 node, graph and link-prediction tasks. Explainability in this release is bounded to node-output sensitivity and perturbation, deliberately avoiding causal interpretations. Embedding extraction returns both per-node representations and mean-pooled graph embeddings, with cosine, Euclidean, and dot-product analyses.
