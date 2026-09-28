# Workspace v3.27.0 — Neural Inference & Prediction Provenance

Workspace v3.27.0 extends the governed PyTorch runtime with bounded inference and prediction provenance.

## Bounded operations
- `workspace.neural.infer-regression`
- `workspace.neural.infer-binary`
- `workspace.neural.infer-multiclass`
- `workspace.neural.prediction-inspect`

## Prediction contract
Inference accepts only declarative Workspace neural model specifications, optional governed checkpoint artifacts, bounded feature matrices, and governed row identifiers. Inference operations reject `targets`; observed outcomes belong to evaluation jobs. Every prediction artifact binds model, optional checkpoint, inference dataset, row IDs, decision policy, output semantics, uncertainty semantics, and the predictions themselves under a canonical fingerprint.

Regression inference explicitly records uncertainty as `not-estimated` for a deterministic forward pass. Binary and multiclass inference may expose model-derived probabilities, confidence, entropy, and class margins; these are labeled model outputs whose calibration has not been assessed unless a separate calibration workflow establishes it.

## Evidence boundary
A prediction is not source evidence and is not evaluation. The governed artifact records `isObservedEvidence=false`, `isEvaluation=false`, and `targetsAccepted=false`. This lets downstream research products preserve the distinction between evidence, model output, and interpretation.

## Security
No arbitrary Python, client packages, raw serialized models, filesystem model paths, dynamic hooks, external runtime URLs, or accelerator execution are introduced. The hardened numeric UID/read-only container contract remains unchanged.
