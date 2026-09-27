# Workspace v3.22.0 — Neural Training Job Runtime

Workspace v3.22.0 activates bounded PyTorch training as a first-class Workspace job capability while preserving the v3.21 tensor/dataset/transformation interchange contracts.

## Runtime operations added
- `workspace.neural.training-plan`
- `workspace.neural.train-linear`
- `workspace.neural.train-mlp`

## Guardrails
Training is declarative, CPU-only, deterministic-seed controlled, resource bounded, and limited to linear/MLP models with registered activations, optimizers, and losses. Client Python, package installation, runtime URLs, serialized PyTorch modules, checkpoint paths, and arbitrary code remain prohibited.

Checkpoint persistence and resume are intentionally deferred to v3.23.0. v3.22 returns a governed trained model specification and a training-run record, but does not create a resumable checkpoint artifact.
