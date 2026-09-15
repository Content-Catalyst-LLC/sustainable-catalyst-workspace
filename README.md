# Sustainable Catalyst Workspace v2.13.0 — R Statistical & Econometric Runtime

Workspace is the governed research execution environment for Sustainable Catalyst. v2.13.0 extends the v2.12 polyglot scientific fabric by deploying a real R specialist runtime alongside the existing Python and bounded SQL execution paths.

## Active scientific runtimes

- **Python** — NumPy, Pandas, SciPy and SymPy bounded operations
- **SQL** — bounded aggregate and grouped analytical operations
- **R** — bounded statistical, inferential, time-series and econometric operations
- **Julia** — registered server-configured adapter, not yet deployed
- **WASM** — registered server-configured adapter, not yet deployed

## R operations

`workspace.polyglot.r.describe`, `workspace.polyglot.r.t-test`, `workspace.polyglot.r.correlation`, `workspace.polyglot.r.linear-model`, `workspace.polyglot.r.logistic-model`, `workspace.polyglot.r.anova`, `workspace.polyglot.r.arima`, and `workspace.polyglot.r.econometric-ols`.

Every R result is persisted as a content-addressed artifact with a polyglot execution receipt. Model-producing operations additionally create a statistical model receipt carrying the model kind, outcome/predictor metadata, metrics, request fingerprint and result SHA-256.

Arbitrary code execution remains disabled. Runtime URLs and credentials remain server-side only.
