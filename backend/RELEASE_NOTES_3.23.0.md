# Workspace v3.23.0 — Checkpoint, Resume & Neural Artifact Lineage

Workspace v3.23.0 advances the bounded PyTorch runtime from one-shot neural training to governed continuation of training work.

## Added

- Portable neural checkpoint artifact schema: `sc-workspace-neural-checkpoint-artifact/1.0`.
- Portable checkpoint state schema: `sc-workspace-neural-checkpoint-state/1.0`.
- Bounded `zlib+base64+canonical-json-v1` state bundles; no pickle, `torch.save`, or arbitrary model files.
- `workspace.neural.checkpoint-inspect`.
- `workspace.neural.resume-linear`.
- `workspace.neural.resume-mlp`.
- Model **and optimizer** state restoration.
- Deterministic epoch/shuffle continuation across resume boundaries.
- Parent checkpoint fingerprint and lineage-depth tracking.
- Same-dataset-only resume policy for the first checkpoint release.
- Separate Workspace checkpoint artifact persistence using the existing artifact store.
- Execution-run checkpoint outputs and enriched polyglot execution receipts.

## Security boundary

The runtime still rejects arbitrary code, package installation, runtime URLs, checkpoint filesystem paths, pickle/joblib, raw state-dict blobs, TorchScript, and arbitrary serialized PyTorch modules. The neural container remains numeric UID `65532:65532`, read-only, capability-dropped, and `no-new-privileges`.

## Compatibility

- Database migration: none.
- Typed endpoint count: unchanged at 291; neural operations use the existing job fabric.
- Rollback baseline: v3.22.0.2.
- Accelerator execution remains deferred.
