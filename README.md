# Sustainable Catalyst Workspace v2.15.0 — Predictive Analytics & Machine Learning Runtime

Workspace is the governed research execution environment for Sustainable Catalyst. v2.15.0 extends the polyglot scientific fabric with a bounded Python/scikit-learn predictive analytics runtime while preserving the Python, SQL, R, repaired Julia, and registered WASM runtime contracts.

## Active scientific runtimes

- **Python scientific compute** — NumPy, Pandas, SciPy and SymPy bounded operations
- **SQL** — bounded aggregate and grouped analytical operations
- **R** — statistical, inferential, time-series and econometric operations
- **Julia** — numerical simulation, optimization, eigen-analysis, Monte Carlo, numerical integration and parameter sweeps
- **ML** — bounded regression, classification, ensembles, cross-validation and prediction
- **WASM** — registered server-configured adapter, not yet deployed

## Predictive analytics operations

- `workspace.ml.linear-regression`
- `workspace.ml.logistic-classification`
- `workspace.ml.random-forest-regression`
- `workspace.ml.random-forest-classification`
- `workspace.ml.gradient-boosting-regression`
- `workspace.ml.gradient-boosting-classification`
- `workspace.ml.cross-validate`
- `workspace.ml.predict`

Every training execution records a dataset fingerprint, ordered features, target, preprocessing configuration, bounded hyperparameters, random seed, evaluation metrics, result-artifact lineage and a trusted model-artifact SHA-256. Training creates predictive-model and evaluation receipts; cross-validation creates an evaluation receipt.

The ML sidecar is internal-only and sandboxed. Arbitrary Python, client package installation, shell execution, runtime URLs, credentials and client-supplied serialized models remain disabled.

See `RELEASE_NOTES_2.15.0.md`, `docs/PREDICTIVE_ANALYTICS_MACHINE_LEARNING_RUNTIME_V2150.md`, and `docs/DEPLOY_WORKSPACE_BACKEND_V2150.md`.
