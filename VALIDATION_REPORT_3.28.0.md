# Workspace v3.28.0 Validation Report

## Release
**Workspace v3.28.0 — Reproducible Neural Model Packages**

## Focused neural regression
- 73 passed
- 0 failed
- 83 inherited Pydantic warnings
- Includes v3.20.0 through v3.28.0 neural runtime tests
- v3.28.0 adds 9 package/reproducibility tests

## Full backend regression
- 287 passed
- 46 failed
- 83 warnings
- The 46 failures are the established historical suite failures tied to old release-version assertions, historical endpoint counts, legacy package-provider identity expectations, or historical migration cutoffs.
- No new v3.28.0 failure category was introduced.

## v3.28.0 contracts verified
- Backend and neural runtime version: 3.28.0
- Typed endpoint count: 291
- Neural bounded operation count: 35
- `sc-workspace-neural-model-package/1.0`
- `sc-workspace-neural-model-package-manifest/1.0`
- `sc-workspace-neural-reproducible-model-package/1.0`
- `sc-workspace-neural-runtime-contract/1.0`
- Workspace model-package media type: `application/vnd.sc.workspace.neural-model-package+json`
- Dependency pins: PyTorch 2.10.0; NumPy 2.2.6
- Package creation, verification, inspection, packaged inference
- Canonical package fingerprint and package ID verification
- Model/checkpoint lineage verification
- Feature/input/output contract verification
- Packaged prediction provenance
- Prediction/evidence/evaluation boundary preserved
- Arbitrary code and serialized PyTorch model loading disabled
- CPU-only hardened runtime preserved
- No database migration
- Rollback baseline: v3.27.0

## Security/runtime invariants
- numeric UID/GID `65532:65532`
- read-only root filesystem
- `cap_drop: ALL`
- `no-new-privileges:true`
- explicit writable `/tmp` PyTorch cache contract
- no arbitrary code, package installation, runtime URLs, model paths, pickle, TorchScript, or raw state-dict inputs
