# Workspace v3.24.0 Release Notes

**Release:** Neural Evaluation, Calibration & Uncertainty Runtime

- Adds five bounded neural post-training operations.
- Adds regression, binary, and multiclass evaluation metrics.
- Adds reliability-bin calibration with ECE/MCE.
- Adds predictive-entropy uncertainty for classification and explicitly labeled empirical-residual uncertainty for regression.
- Binds analysis outputs to model/checkpoint/dataset fingerprints.
- Persists neural analysis as a separate Workspace artifact and enriches polyglot receipts.
- Preserves v3.23 checkpoint/resume, hardened UID/cache, and CPU-only execution.
- No database migration.
- Rollback baseline: Workspace backend v3.23.0.
