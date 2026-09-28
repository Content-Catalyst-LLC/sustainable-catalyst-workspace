# Workspace v3.30.0 — Neural Batch, Trial & Hyperparameter Execution

v3.30.0 adds bounded, reproducible neural experiment execution on top of v3.29 device orchestration.

## Operations
- `workspace.neural.trial-plan`
- `workspace.neural.trial-execute`
- `workspace.neural.batch-execute`
- `workspace.neural.hyperparameter-grid`
- `workspace.neural.hyperparameter-random`

## Governed objects
- `sc-workspace-neural-trial-plan/1.0`
- `sc-workspace-neural-trial-artifact/1.0`
- `sc-workspace-neural-batch-artifact/1.0`
- `sc-workspace-neural-hyperparameter-search-artifact/1.0`

Searches accept only a whitelist of training hyperparameters: optimizer name, learning rate, weight decay, batch size, and epochs. Arbitrary model code, import paths, packages, serialized modules, arbitrary parameter paths, and client runtime URLs remain prohibited.

Each trial gets a deterministic seed derived from the batch seed and trial index. Trial artifacts bind hyperparameters, objective, dataset fingerprints, trained-model fingerprint, checkpoint fingerprint, device, and training metrics. Batch/search artifacts retain compact trial lineage and a ranked best-trial reference rather than duplicating every checkpoint.

CPU remains the safe device default. All trials inherit the governed v3.29 device plan. Accelerator execution remains opt-in through operator policy and exposed devices.

No database migration is required; Workspace persists trial/batch/search objects through the existing artifact store and execution-output/receipt lineage.
