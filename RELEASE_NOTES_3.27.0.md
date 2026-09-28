# Workspace v3.27.0 — Neural Inference & Prediction Provenance

- Adds governed regression, binary-classification, and multiclass neural inference.
- Adds fingerprint-valid prediction inspection.
- Introduces `sc-workspace-neural-prediction-artifact/1.0`.
- Persists predictions separately as `application/vnd.sc.workspace.neural-prediction+json`.
- Adds model/checkpoint/input dataset/row-ID lineage to polyglot receipts.
- Separates inference from evaluation by rejecting targets.
- Labels classification probabilities/confidence as model-derived and calibration-not-assessed.
- Labels deterministic regression uncertainty as not estimated.
- Keeps CPU-only hardened execution and 291 typed endpoints.
- No database migration. Rollback baseline: v3.26.0.
