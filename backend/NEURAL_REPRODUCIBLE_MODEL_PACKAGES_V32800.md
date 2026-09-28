# Workspace v3.28.0 — Reproducible Neural Model Packages

Workspace v3.28.0 introduces a governed, portable neural model package object for deterministic inference handoff.

## Package contract
- Schema: `sc-workspace-neural-model-package/1.0`
- Manifest: `sc-workspace-neural-model-package-manifest/1.0`
- Format: `sc-workspace-neural-reproducible-model-package/1.0`
- Runtime contract: `sc-workspace-neural-runtime-contract/1.0`
- Workspace media type: `application/vnd.sc.workspace.neural-model-package+json`

Packages contain only declarative model specifications and an optional governed portable checkpoint. They record the exact model/checkpoint fingerprints, task, feature contract, decision policy, PyTorch/NumPy dependency pins, runtime contract fingerprint, and inference contract fingerprint. Raw pickle, TorchScript, arbitrary Python, package installation, model paths, and runtime URLs remain prohibited.

## Operations
- `workspace.neural.package-create`
- `workspace.neural.package-verify`
- `workspace.neural.package-inspect`
- `workspace.neural.package-infer`

Packaged inference produces the existing governed prediction artifact with additional source-model-package lineage. Prediction remains distinct from observed evidence and evaluation.
