# Workspace v2.19.0 — Validation Report

## Release

**Workspace v2.19.0 — Probabilistic & Bayesian Runtime**

Built from the corrected **v2.18.0 job-result-repair** baseline.

## Source validation

- Backend regression suite: **51 passed**
- Probabilistic/Bayesian focused tests: **5 passed**
- Python compile validation: **PASS**
- VPS deployment script shell syntax: **PASS**
- Probability runtime: six registered bounded operations
- Dedicated migration `019_probabilistic_bayesian_runtime.sql`
- Dedicated internal runtime token and server-configured URL
- Runtime boundary: no arbitrary Python, package installation, client-selected runtime URL, or client credentials

## New v2.19 runtime operations

1. `workspace.probability.normal-summary`
2. `workspace.probability.beta-binomial-update`
3. `workspace.probability.normal-normal-update`
4. `workspace.probability.gamma-poisson-update`
5. `workspace.probability.posterior-predictive-binomial`
6. `workspace.probability.uncertainty-propagate`

## Persistence

v2.19 adds `workspace_probabilistic_inference_receipts` while retaining the corrected v2.18 language-neutral job-result persistence path. Probabilistic jobs persist both the normal polyglot execution receipt and a specialist probabilistic inference receipt.

## Production gate

Production closure requires the v2.19 VPS deployer to apply migration 019, start the sandboxed probability runtime, run a durable Beta-Binomial job, confirm the job result includes a `probabilisticInferenceReceiptId`, confirm the receipt is discoverable through the API, and verify the runtime's read-only/internal-network sandbox.
