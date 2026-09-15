# Workspace v2.13.0 — R Statistical & Econometric Runtime

v2.13.0 turns the R identity introduced by the v2.12 polyglot fabric into a real, independently sandboxed runtime service.

## Registered operations

- `workspace.polyglot.r.describe`
- `workspace.polyglot.r.t-test`
- `workspace.polyglot.r.correlation`
- `workspace.polyglot.r.linear-model`
- `workspace.polyglot.r.logistic-model`
- `workspace.polyglot.r.anova`
- `workspace.polyglot.r.arima`
- `workspace.polyglot.r.econometric-ols`

The econometric OLS result includes Durbin–Watson, Breusch–Pagan and Jarque–Bera diagnostics computed with bounded base-R/statistics primitives.

## Security boundary

Workspace does not accept R source code, formulas, package names, runtime URLs, shell commands, or runtime credentials from the browser. The Python orchestration worker sends a language-neutral v2.12 execution envelope to a server-configured R service. The R sidecar invokes a fixed runner only and is deployed with a read-only root filesystem, dropped capabilities, no-new-privileges, bounded CPU/memory/PIDs, and an internal-only Docker network with no host port.

## Persistence

Every R job receives the existing content-addressed result artifact and polyglot execution receipt. Model-producing operations additionally write `workspace_statistical_model_receipts`, preserving model kind, outcome, predictor list, metrics, request fingerprint, artifact ID, and result SHA-256.
