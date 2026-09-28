# Workspace v3.25.0 — Neural Explainability Compute Runtime

Workspace v3.25.0 adds bounded PyTorch-native explainability compute while preserving the principle that **Core defines, Workspace computes, Lab experiments, products consume**.

## Bounded operations

- `workspace.neural.explain-gradient` — input-gradient attribution.
- `workspace.neural.explain-integrated-gradients` — path-integrated attribution with bounded steps and a completeness diagnostic.
- `workspace.neural.explain-occlusion` — feature replacement/occlusion impact.
- `workspace.neural.explain-global-sensitivity` — dataset-level mean-absolute, RMS, and maximum absolute gradients.

## Governance and lineage

Each result emits `sc-workspace-neural-explainability-artifact/1.0` with the model specification fingerprint, optional checkpoint fingerprint, explanation-dataset fingerprint, target-selection policy, method parameters, feature names, and attribution/sensitivity outputs. Workspace persists this separately as `application/vnd.sc.workspace.neural-explainability+json` and records its identity in the polyglot execution receipt.

## Safety boundaries

Explainability is declarative and bounded. No arbitrary Python, dynamic forward/backward hooks, package installation, raw serialized model loading, filesystem paths, accelerator execution, or unbounded integrated-gradient paths are accepted. v3.25 remains CPU-only and preserves numeric UID 65532, read-only root filesystem, dropped Linux capabilities, and no-new-privileges.

## Interpretation boundary

Gradient, integrated-gradient, occlusion, and sensitivity outputs describe the configured model's local numerical behavior. They are not causal effects, proof of feature importance in the data-generating process, or evidence that a model explanation is substantively correct.
