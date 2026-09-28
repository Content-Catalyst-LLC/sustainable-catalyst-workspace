# Workspace v3.31.0 — Remote GPU Execution Broker

Workspace v3.31.0 adds an operator-governed remote GPU dispatch layer to the bounded PyTorch neural runtime.

## New bounded operations

- `workspace.neural.remote-worker-inventory`
- `workspace.neural.remote-dispatch-plan`
- `workspace.neural.remote-execute`
- `workspace.neural.remote-receipt-verify`

The neural registry contains 48 operations total.

## Contracts

- Worker inventory: `sc-workspace-neural-remote-worker-inventory/1.0`
- Dispatch plan: `sc-workspace-neural-remote-dispatch-plan/1.0`
- Signed dispatch envelope: `sc-workspace-neural-remote-dispatch-envelope/1.0`
- Signed execution receipt: `sc-workspace-neural-remote-execution-receipt/1.0`
- Remote execution artifact: `sc-workspace-neural-remote-execution-artifact/1.0`
- Worker response: `sc-workspace-neural-remote-worker-response/1.0`
- Workspace media type: `application/vnd.sc.workspace.neural-remote-execution+json`

## Broker policy

The broker is disabled by default. Worker URLs are read only from the operator-managed `SC_WORKSPACE_NEURAL_REMOTE_WORKERS_JSON` environment variable. Client-supplied runtime or worker URLs are never accepted. HTTPS is required unless an operator explicitly enables insecure HTTP for a controlled test environment.

A dispatch plan binds the registered worker ID, declared CUDA device, bounded neural operation, payload fingerprint, worker-registry fingerprint, and canonical plan fingerprint.

## Signed remote execution

`remote-execute` creates a short-lived dispatch envelope containing a dispatch ID, nonce, issued/expiry timestamps, worker identity, operation, payload fingerprint, dispatch-plan fingerprint, requested worker device, and origin runtime version. The envelope is HMAC-SHA256 signed using an operator-supplied secret.

The remote worker validates the signature, time window, worker identity, nonce replay state, operation allowlist, payload fingerprint, and device contract before invoking the existing bounded neural execution path. Broker operations cannot be recursively dispatched.

The worker signs a receipt binding the dispatch, worker, operation, payload fingerprint, result fingerprint, selected device, device-plan fingerprint, runtime/engine versions, and execution timestamps.

## Workspace persistence

A successful remote execution persists the remote execution artifact separately as `application/vnd.sc.workspace.neural-remote-execution+json`. The normal Workspace polyglot receipt carries the dispatch ID, worker ID, remote operation, dispatch-plan fingerprint, result fingerprint, remote receipt fingerprint, and persisted artifact identity/SHA.

Remote execution provenance is compute provenance. It does not transform a model output into observed evidence.

## Resource and trust boundary

The normal Contabo deployment remains CPU-safe and keeps the broker disabled. A remote GPU worker must be deliberately deployed on an NVIDIA-capable host, exposed through HTTPS, and registered server-side. See `REMOTE_GPU_WORKER_DEPLOYMENT_V33100.md`.
