# Reproducible Deep Learning Research Packages v3.40.0

## Package contract
- Package schema: `sc-workspace-neural-research-package/1.0`
- Manifest: `sc-workspace-neural-research-package-manifest/1.0`
- Format: `sc-workspace-reproducible-deep-learning-research-package/1.0`
- Reproduction plan: `sc-workspace-neural-research-reproduction-plan/1.0`
- Reproduction verification: `sc-workspace-neural-research-reproduction-verification/1.0`

Each component is pinned by artifact ID, schema, role, SHA-256, byte count, source operation, required/optional status, and dependency edges. The package records a deterministic seed, runtime/dependency contract, closure fingerprint, and reproduction policy.

## Safety and epistemic boundary
The package is manifest-first. It does not embed arbitrary Python, external package installers, runtime URLs, credentials, host paths, TorchScript, pickles, or opaque serialized model modules. Package creation and verification do not claim that model-derived outputs are observed evidence. Automatic reproduction execution remains disabled; v3.40 produces plans and verification receipts only.

## Relationship to existing Workspace reproducibility
The v3.40 neural package complements the existing Workspace scientific-study package and reproduction-plan substrate. It gives deep-learning artifacts an explicit content-addressed closure that can later be incorporated into broader project/study packages.
