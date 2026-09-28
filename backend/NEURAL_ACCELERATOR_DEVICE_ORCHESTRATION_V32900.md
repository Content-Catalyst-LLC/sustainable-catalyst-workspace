# Workspace v3.29.0 — Accelerator & Device Orchestration

Workspace v3.29.0 introduces explicit, governed neural device selection while preserving CPU as the safe default.

## Device contract

Each neural execution resolves a `deviceRequest` into a fingerprinted `sc-workspace-neural-device-plan/1.0`. Supported request preferences are `cpu`, `auto`, `accelerator`, and an allowed explicit CUDA device such as `cuda:0`.

The runtime exposes four bounded operations:

- `workspace.neural.device-inventory`
- `workspace.neural.device-plan`
- `workspace.neural.device-verify`
- `workspace.neural.accelerator-smoke`

## Safety and policy

Accelerator use requires all three conditions: operator policy enables accelerators, the device is listed in `SC_WORKSPACE_NEURAL_ALLOWED_DEVICES`, and the device is actually visible to PyTorch inside the container. The base Compose file defaults to CPU-only policy. GPU exposure is supplied through `docker-compose.neural-gpu.example.yml` and is intentionally opt-in.

Strict accelerator requests fail if the device is unavailable. `auto` may fall back to CPU and records the fallback reason in the device plan. All neural responses carry the selected device and device-plan fingerprint, and Workspace copies device selection into the polyglot execution receipt.

## Reproducibility boundary

The runtime requests deterministic algorithms, but v3.29 explicitly does not claim bitwise identity across different device classes or hardware. Reproduction packages therefore preserve device-selection metadata so CPU-vs-GPU execution remains visible in lineage.

## Security

The hardened runtime remains numeric UID/GID `65532:65532`, read-only, capability-dropped, no-new-privileges, with no arbitrary code, client package installation, raw serialized PyTorch loading, or client-provided runtime URLs.
