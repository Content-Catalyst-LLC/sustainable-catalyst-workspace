# Workspace v3.20.0 — Neural Runtime Foundation & PyTorch Adapter

Workspace v3.20.0 introduces the first bounded deep-learning execution capability in Sustainable Catalyst Workspace while preserving the existing classical scikit-learn runtime as a separate service.

## Architecture

The release follows the platform boundary:

- **Platform Core defines** neural model/provenance contracts.
- **Workspace computes** bounded neural operations.
- **Research Lab experiments** with training, comparison, ablation, and explainability in later releases.
- **Downstream products consume** governed neural results without converting model inference into evidence.

The existing `sc-workspace-ml-runtime` remains the classical `python-sklearn-predictive` service. v3.20.0 adds a new `sc-workspace-neural-runtime` service using the runtime identity `python-pytorch-neural`.

## Runtime operations

The v3.20.0 neural runtime exposes four bounded operations through the existing Workspace job and polyglot execution fabric:

- `workspace.neural.tensor-summary`
- `workspace.neural.model-summary`
- `workspace.neural.linear-forward`
- `workspace.neural.mlp-forward`

The runtime accepts only declarative `sc-workspace-neural-model-spec/1.0` model descriptions. It does not accept arbitrary Python, package installation, import paths, pickle/joblib payloads, serialized PyTorch modules, TorchScript payloads, client-supplied runtime URLs, or client-supplied credentials.

## Device boundary

v3.20.0 is deliberately **CPU-only**. The runtime reports the device policy `cpu-only-foundation`. Accelerator orchestration (MPS, CUDA, and remote GPU) remains a later Workspace milestone so the execution contract is established before device complexity is introduced.

## Training boundary

Neural training is intentionally disabled in v3.20.0. This release establishes execution contracts, deterministic seed control, safe model-spec validation, model fingerprinting, tensor bounds, runtime health, and forward inference. Training jobs, epochs, loss telemetry, and checkpoint production belong to the later Neural Training Job Runtime milestone.

## Provenance behavior

Every neural operation executes through the existing Workspace job fabric and produces the normal polyglot execution artifact/receipt. The receipt records `language=neural`, runtime identity, operation, request fingerprint, result artifact, transport, and timestamps. A neural result is therefore traceable as a model-derived computation and does not become an evidence edge or evidence object automatically.

## Runtime hardening

The neural container runs with the same bounded-service posture as the existing specialist runtimes:

- non-root container user;
- read-only root filesystem;
- dropped Linux capabilities;
- `no-new-privileges`;
- internal-only runtime network;
- server-configured bearer credential;
- bounded payload, tensor, batch, feature, layer, and parameter limits;
- no arbitrary code execution.

## Database

No new database migration is required for v3.20.0. Neural executions use the existing `workspace_polyglot_execution_receipts` and execution artifact infrastructure. The v3.19.0 migration lineage remains authoritative.
