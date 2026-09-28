# Graph Neural Network Training Runtime

## Scope
- GCN and GraphSAGE-mean training using the existing PyTorch neural runtime.
- Node regression, binary classification, and multiclass classification.
- Graph regression, binary classification, and multiclass classification via mean pooling.
- Link prediction using explicit labeled link examples.
- Deterministic train/validation/test split planning.
- Governed full-batch SGD, bounded epochs, learning rate, weight decay, and gradient clipping.
- JSON-native checkpoint artifacts; no pickle, torch.save, torch.load, arbitrary modules, package loading, or client-supplied runtime URLs.
- Exact continuation semantics for same-input full-batch SGD checkpoints because optimizer momentum is fixed to zero.

## Architectural boundary
Platform Core remains the semantic/model/provenance authority. Workspace executes training. Research Lab remains the experimentation surface. Downstream products consume governed model and training artifacts.
