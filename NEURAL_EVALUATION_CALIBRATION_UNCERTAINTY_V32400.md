# Workspace v3.24.0 — Neural Evaluation, Calibration & Uncertainty Runtime

This release extends the bounded PyTorch runtime from governed training/checkpoint lineage into governed post-training analysis.

## New bounded operations

- `workspace.neural.evaluate-regression`
- `workspace.neural.evaluate-binary`
- `workspace.neural.evaluate-multiclass`
- `workspace.neural.calibration-report`
- `workspace.neural.uncertainty-summary`

## Evaluation

Regression reports MSE, RMSE, MAE, and R². Binary classification reports accuracy, log loss, Brier score, precision, recall, F1, ROC-AUC when defined, and confusion counts. Multiclass evaluation reports accuracy, log loss, Brier score, macro precision/recall/F1, and a confusion matrix.

## Calibration

Classification calibration uses bounded uniform reliability bins and reports expected calibration error (ECE) and maximum calibration error (MCE). Multiclass calibration is top-label confidence calibration.

## Uncertainty

Classification uncertainty uses predictive entropy, normalized entropy, confidence, and class-margin summaries. Regression intentionally reports **empirical residual uncertainty**, not epistemic uncertainty or probabilistic predictive intervals. This avoids overstating what a deterministic network can infer.

## Provenance and lineage

Every analysis object binds the declarative model fingerprint, optional checkpoint fingerprint, and evaluation-dataset fingerprint. If a checkpoint is supplied, its recorded trained-model fingerprint must match the supplied model specification. Workspace stores the analysis object separately from the generic polyglot result and records its artifact ID/SHA in the execution receipt.

## Boundaries

No arbitrary Python, arbitrary packages, client runtime URLs, raw PyTorch serialization, arbitrary filesystem paths, or accelerator execution are enabled. v3.24 remains CPU-only and retains the v3.23 checkpoint/resume contract.
