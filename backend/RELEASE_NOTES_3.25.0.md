# Sustainable Catalyst Workspace v3.25.0

## Neural Explainability Compute Runtime

Adds four bounded PyTorch explainability operations: input gradients, integrated gradients, feature occlusion, and global gradient sensitivity. Explainability outputs become governed Workspace artifacts with model/checkpoint/dataset lineage and execution-receipt metadata.

The release preserves v3.24 evaluation/calibration/uncertainty, v3.23 checkpoint/resume, v3.22 bounded training, CPU-only execution, stable WordPress packaging, and the hardened numeric-UID runtime.

No database migration is required. Rollback baseline: v3.24.0.
