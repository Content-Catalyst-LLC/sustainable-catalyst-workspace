# Release Notes — Workspace v3.20.0

## Neural Runtime Foundation & PyTorch Adapter

Workspace v3.20.0 adds a dedicated PyTorch neural runtime without replacing the existing scikit-learn machine-learning runtime.

### Added

- `backend/neural-runtime/` with a hardened PyTorch service.
- Four bounded neural operations: tensor summary, model summary, linear forward inference, and MLP forward inference.
- Declarative neural model contract `sc-workspace-neural-model-spec/1.0`.
- Deterministic seed control and canonical input/model fingerprints.
- Runtime registration under language `neural` and identity `python-pytorch-neural`.
- `SC_WORKSPACE_RUNTIME_NEURAL_URL` and `SC_WORKSPACE_RUNTIME_NEURAL_TOKEN` server configuration.
- `GET /v1/polyglot/runtimes/neural/status`.
- Workspace job routing and notebook orchestration support for `workspace.neural.*` operations.
- Neural runtime label support in cross-runtime provenance views.
- Docker Compose service `sc-workspace-neural-runtime` on the internal runtime network.
- Typed-client endpoint `neuralRuntimeStatus`; typed endpoint count is now 291.

### Preserved

- `sc-workspace-ml-runtime` remains `python-sklearn-predictive` with all eight existing bounded classical-ML operations.
- Existing predictive, forecasting, probabilistic, uncertainty, optimization, decision, reliability, R, Julia, and interchange services are unchanged.
- Existing polyglot receipt/artifact persistence remains the execution provenance layer.
- No database migration is added.

### Explicitly not enabled in v3.20.0

- neural training;
- optimizer execution;
- checkpoint creation or resume;
- GPU/MPS/CUDA execution;
- remote GPU execution;
- arbitrary Python execution;
- package installation;
- serialized PyTorch module upload/loading;
- automatic conversion of model outputs into evidence or factual graph edges.
