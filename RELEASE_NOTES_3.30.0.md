# Workspace v3.30.0 — Neural Batch, Trial & Hyperparameter Execution

Adds governed neural trial planning/execution, explicit trial batches, deterministic grid search, and seeded random hyperparameter search.

Key constraints: bounded trial count, bounded total epoch budget, whitelisted hyperparameter paths, explicit objective/direction, deterministic per-trial seeds, governed device selection, no arbitrary code or serialized model ingestion, and Workspace artifact/receipt provenance.

Rollback baseline: v3.29.0. Database migration: none.
