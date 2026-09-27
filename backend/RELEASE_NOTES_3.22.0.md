# Sustainable Catalyst Workspace v3.22.0

**Release:** Neural Training Job Runtime

Adds bounded deterministic PyTorch training jobs for linear and MLP models, training-plan validation, epoch/loss telemetry, optional validation-loss telemetry, task-aware final metrics, training-data/model fingerprints, and generic Workspace execution receipt enrichment. Training remains CPU-only. Checkpoint persistence/resume and accelerator execution remain disabled for later roadmap releases.

The v3.21 governed tensor, dataset manifest, batch-plan, and transformation-lineage capabilities are preserved. The classical scikit-learn runtime remains separate.

No database migration is required.
