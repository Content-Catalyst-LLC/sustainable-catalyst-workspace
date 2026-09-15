# Workspace v2.15.0 — Predictive Analytics & Machine Learning Runtime

Workspace v2.15.0 adds an independently sandboxed Python/scikit-learn specialist runtime for bounded predictive modeling. It extends the v2.14 runtime fabric without weakening the Python, R, Julia, SQL, or WASM execution controls.

## Bounded operations

- linear regression
- logistic classification
- random-forest regression
- random-forest classification
- gradient-boosting regression
- gradient-boosting classification
- deterministic cross-validation
- bounded prediction from canonical linear/logistic model specifications

## Reproducibility and provenance

Training receipts persist dataset fingerprints, ordered feature names, target, preprocessing configuration, bounded hyperparameters, random seed, train/test counts, evaluation metrics, result artifact lineage, and trusted model-artifact SHA-256. Model binaries are generated inside the trusted ML runtime and stored through Workspace content-addressed artifact storage. Client-supplied serialized models are not deserialized.

## Security

The runtime is internal-only, read-only, capability-dropped, resource-bounded, and service-token authenticated. Arbitrary Python, packages, shell commands, client runtime URLs, client credentials, and client-supplied pickle/joblib payloads remain disabled.

## Persistence and APIs

Migration 015 adds predictive-model and model-evaluation receipt registries. Backend APIs expose ML runtime status and per-user read-only receipt discovery, and the WordPress bridge exposes corresponding authenticated proxy routes.

## Operational release gate

The VPS deployment script preserves the repaired v2.14 Julia executable/cache contract and adds a real durable linear-regression smoke with model artifact, predictive model receipt and holdout evaluation receipt verification before v2.15 can be considered operationally closed.
