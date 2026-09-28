# Workspace v3.31.0 — Remote GPU Worker Deployment

A v3.31 remote GPU worker is the same hardened neural runtime running in worker mode on a separate NVIDIA-capable host. The Workspace/Contabo broker remains disabled until the operator explicitly configures a worker registry.

## Security contract

- No client-supplied worker URLs. Worker endpoints are loaded only from `SC_WORKSPACE_NEURAL_REMOTE_WORKERS_JSON` on the broker host.
- Dispatches use `sc-workspace-neural-remote-dispatch-envelope/1.0` with HMAC-SHA256 signatures, timestamps, expiry, nonce replay protection, payload fingerprints, and dispatch-plan fingerprints.
- A worker accepts only the bounded `REMOTE_ALLOWED_OPERATIONS` set and cannot dispatch another broker operation.
- The worker forces execution onto its operator-configured `SC_WORKSPACE_NEURAL_REMOTE_WORKER_DEVICE` and does not honor a client-selected remote device.
- The worker returns a signed `sc-workspace-neural-remote-execution-receipt/1.0` binding worker, operation, payload, result, device plan, runtime, and timing.
- The worker must be exposed through HTTPS. The provided Compose file binds only to `127.0.0.1:18101`; use a TLS reverse proxy such as Caddy or nginx on the GPU host.

## Worker environment

Required values include:

```text
SC_WORKSPACE_RUNTIME_NEURAL_TOKEN=<worker internal runtime token>
SC_WORKSPACE_NEURAL_REMOTE_WORKER_ID=gpu-east-1
SC_WORKSPACE_NEURAL_REMOTE_WORKER_DEVICE=cuda:0
SC_WORKSPACE_NEURAL_REMOTE_HMAC_SECRET=<same high-entropy secret as broker>
SC_WORKSPACE_NEURAL_ALLOWED_DEVICES=cpu,cuda:0
```

Use `backend/docker-compose.neural-remote-worker.example.yml` on an NVIDIA host with Docker GPU passthrough configured.

## Broker environment

On the Workspace broker host, after the worker is reachable over HTTPS:

```text
SC_WORKSPACE_NEURAL_REMOTE_BROKER_ENABLED=true
SC_WORKSPACE_NEURAL_REMOTE_HMAC_SECRET=<same high-entropy secret>
SC_WORKSPACE_NEURAL_REMOTE_WORKERS_JSON=[{"workerId":"gpu-east-1","url":"https://gpu.example.org","device":"cuda:0","enabled":true,"tags":["gpu"]}]
```

Do not place worker credentials or URLs in browser requests. They are server-side operator configuration only.
