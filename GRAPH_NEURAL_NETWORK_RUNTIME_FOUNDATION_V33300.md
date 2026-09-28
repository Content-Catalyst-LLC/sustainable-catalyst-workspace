# Workspace v3.33.0 — Graph Neural Network Runtime Foundation

Workspace v3.33.0 extends the existing PyTorch `neural-runtime` with a bounded graph-neural execution foundation. It preserves the product boundary already established across the neural series: Platform Core owns governed model/provenance contracts; Workspace executes and records runtime work; Research Lab may later experiment with higher-level graph-learning workflows.

## New bounded operations

- `workspace.neural.graph-tensor-contract`
- `workspace.neural.graph-dataset-project`
- `workspace.neural.gnn-model-summary`
- `workspace.neural.gnn-forward`
- `workspace.neural.gnn-infer`

## Governed schemas

- `sc-workspace-neural-graph-tensor-contract/1.0`
- `sc-workspace-neural-graph-dataset-projection/1.0`
- `sc-workspace-neural-gnn-model-spec/1.0`
- `sc-workspace-neural-gnn-execution-artifact/1.0`
- `sc-workspace-neural-gnn-prediction-artifact/1.0`

## Runtime adapters

The foundation provides two dependency-free adapters inside the existing PyTorch runtime:

- **GCN** — normalized message aggregation followed by a governed linear projection.
- **GraphSAGE mean** — bounded mean-neighbor aggregation followed by a governed self+neighbor projection.

No PyTorch Geometric, DGL, arbitrary Python module, import path, package install, serialized `torch.nn.Module`, client-supplied runtime URL, or client-supplied credential is accepted.

## Graph projection boundary

`graph-dataset-project` converts an explicit node/edge object into a tensor-ready representation. It never invents missing edges, node features, entities, identities, or evidentiary relationships. The projection retains node order, source fingerprint (when supplied), graph fingerprint, and a reproducible artifact fingerprint.

## Inference boundary

v3.33.0 supports bounded forward execution and node-level regression, binary classification, and multiclass classification. Predictions are explicitly marked as model-derived outputs and **not source evidence**. Targets are not accepted by inference operations.

## Limits and defaults

- CPU remains the safe default device; governed v3.29+ device orchestration remains authoritative.
- Default maximum graph nodes: 4,096.
- Default maximum graph edges: 32,768.
- Default maximum GNN output features: 1,024.
- v3.33.0 is a **single-layer execution foundation**. GNN training is deliberately disabled in this release.
- Database migration: none.
- Required predecessor: Workspace v3.32.0 production-certified backend.
- Rollback baseline: Workspace v3.32.0.
