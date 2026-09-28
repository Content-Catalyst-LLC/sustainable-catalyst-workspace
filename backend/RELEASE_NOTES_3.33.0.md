# Workspace v3.33.0 — Graph Neural Network Runtime Foundation

Adds governed graph tensors, explicit graph-dataset projection, GCN and GraphSAGE-mean execution adapters, bounded GNN forward execution, and node-level inference provenance to the existing PyTorch neural runtime.

The release intentionally does **not** add GNN training, arbitrary graph code, external graph reads, client-supplied runtime URLs, serialized modules, or inferred evidence relationships. GNN outputs remain model-derived analytical artifacts rather than observed evidence.

Required predecessor and rollback baseline: v3.32.0. Database migration: none. Runtime operation count: 57 (52 preserved from v3.32.0 plus 5 GNN-foundation operations).
