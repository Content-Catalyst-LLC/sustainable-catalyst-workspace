# Workspace v2.15.0 Validation Report

Release: **Predictive Analytics & Machine Learning Runtime**

## Release gates

- v2.15 static release validator: PASS
- current backend + ML runtime test suite: **38 passed**
- Python compileall for `backend/app` + `backend/ml-runtime`: PASS
- VPS deploy script shell syntax (repository + backend copies): PASS
- WordPress PHP syntax: **31 files PASS**

## Forward-compatible runtime regressions

Historical release tests that intentionally hard-code an older current-version identity were excluded from cross-release regression runs. Their functional contracts were retained and tested independently.

- v2.10 trust/compliance functional regression: **7 passed, 1 release-lineage assertion deselected**
- v2.11 Python compute regression: **10 passed, 1 release-identity assertion deselected**
- v2.12 polyglot regression: **6 passed, 2 superseded catalog/version assertions deselected**
- v2.13 R runtime regression: **9 passed, 1 release-version assertion deselected**
- v2.14 Julia functional regression: **6 passed, 3 superseded pre-repair path/version assertions deselected**
- v2.14 executable-path and read-only-cache repairs are covered by current backend regression tests.

Functional historical regression total: **38 passed, 8 deliberately deselected**. Combined with the current v2.15 suite: **76 passed**.

## v2.15 ML operation coverage

All eight bounded operations execute in the current test suite:

1. `workspace.ml.linear-regression`
2. `workspace.ml.logistic-classification`
3. `workspace.ml.random-forest-regression`
4. `workspace.ml.random-forest-classification`
5. `workspace.ml.gradient-boosting-regression`
6. `workspace.ml.gradient-boosting-classification`
7. `workspace.ml.cross-validate`
8. `workspace.ml.predict`

The suite checks authentication, deterministic model execution, metrics, model-artifact generation, cross-validation, bounded prediction, and rejection of client-supplied serialized models.

## Persistence and provenance

Migration `015_predictive_analytics_machine_learning_runtime.sql` adds:

- `workspace_predictive_model_receipts`
- `workspace_model_evaluation_receipts`

Training results carry dataset fingerprint, ordered features, target, preprocessing configuration, bounded hyperparameters, seed, train/test counts, metrics, model artifact identity/SHA-256, result artifact identity/SHA-256, polyglot receipt lineage, job identity and execution-run identity.

## Runtime isolation

The deployment contract requires the ML sidecar to be:

- internal-network only
- no host port
- read-only root filesystem
- 2 CPU
- 2 GiB memory
- 128 PID limit
- `cap_drop: ALL`
- `no-new-privileges`
- service-token authenticated

Arbitrary Python, client package installation, shell execution, client runtime URLs, credentials, and client-supplied pickle/joblib payloads are rejected.

## VPS release smoke contract

The v2.15 deployer additionally requires a live server-side smoke before closure:

- migrations through 015 apply
- v2.15 backend health identity
- R + repaired Julia + ML runtimes become available
- Julia executable/cache/RK4 smoke remains green
- real durable ML linear regression succeeds with R² > 0.999
- trusted model artifact persists with SHA-256
- predictive model receipt persists and is discoverable
- model evaluation receipt persists and is discoverable
- ML and worker sandbox assertions pass

The package is build-validated locally. VPS deployment remains pending until the deployment script is run on the Sustainable Catalyst server.
