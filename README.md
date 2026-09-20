# Current release: v2.35.0 — Backend Policy, Identity & Authorization Consolidation

Workspace now resolves principal identity and authorization policy in the backend. The WordPress proxy authenticates with the server-side service credential; the backend resolves the human WordPress user, maps every protected route to a bounded action under a default-deny policy, and can persist authorization decision receipts with deterministic fingerprints. Browser roles/scopes remain non-authoritative.

# Sustainable Catalyst Workspace v2.24.0

Workspace is the local-first research and analysis environment for Sustainable Catalyst. It connects projects, evidence, datasets, analysis, decisions, portable artifacts, and governed scientific execution without turning the browser client into an arbitrary-code runtime.

## Current scientific runtime fabric

- Python scientific compute
- SQL bounded analytics
- R statistical/econometric runtime
- Julia numerical simulation runtime
- scikit-learn predictive analytics runtime
- Arrow / Parquet interchange runtime
- cross-runtime reproduction verification
- forecasting and time-series runtime

## v2.18.0 — Forecasting & Time-Series Runtime

The v2.18 line adds an internal Python/Statsmodels service with eight bounded operations: naive, seasonal-naive, linear trend, exponential smoothing, Holt-Winters, ARIMA, rolling-origin backtesting, and forecast evaluation. Forecast runs preserve dataset fingerprints, horizon, model parameters, intervals, evaluation metrics, result artifacts, and durable receipts.

The forecasting service is server-configured, internal-only, read-only, resource-bounded, and does not accept arbitrary Python, package installation, client-supplied runtime URLs, filesystem paths, or executable model code.

See `RELEASE_NOTES_2.18.0.md`, `docs/FORECASTING_TIME_SERIES_RUNTIME_V2180.md`, and `docs/DEPLOY_WORKSPACE_BACKEND_V2180.md`.


## v2.22.0 Robust Decision Optimization & Pareto Analysis
Workspace now supports bounded, provenance-aware decision analysis over optimization, uncertainty, and scenarios, including Pareto fronts, minimax regret, robust constraints, dominance, stress ranking, and value of information.


## v2.23.0 Reliability, Survival & Failure-Time Analysis
Workspace now supports bounded, provenance-aware survival and reliability analysis for failure-time data, component/system reliability, repairable availability, and accelerated-life relationships.


## v2.24.0 Backend Authority & Domain Service Consolidation
Workspace now explicitly treats the Python/PostgreSQL backend as canonical for project/notebook validation, revision policy, fingerprints, provenance, persistence, and mutation receipts. The browser remains responsible for presentation, interaction, local drafts, and rendering rather than canonical domain truth.
