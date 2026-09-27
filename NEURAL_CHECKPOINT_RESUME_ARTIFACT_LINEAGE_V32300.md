# Neural Checkpoint, Resume & Artifact Lineage — v3.23.0

## Contract

A checkpoint is a governed Workspace research artifact, not a path to a PyTorch file. The neural runtime emits a portable checkpoint containing bounded model state, optimizer state, training position, dataset/spec fingerprints, and lineage metadata.

The state payload is canonical JSON compressed with zlib and base64 encoded. The runtime verifies compressed-state SHA-256, uncompressed JSON SHA-256, artifact fingerprint, checkpoint ID, schema, runtime identity, compatibility fingerprint, and dataset fingerprint before restoring state.

## Resume policy

v3.23.0 uses `same-dataset-only`. A resume job must use the same training-dataset fingerprint, model architecture, task, optimizer configuration, batch size, shuffle policy, and seed as its parent checkpoint. The requested `epochs` value represents additional epochs to execute. Validation data may be supplied or omitted independently.

## Lineage

Every checkpoint records:

- checkpoint ID and artifact fingerprint;
- parent checkpoint fingerprint;
- lineage depth;
- starting epoch, segment epochs, and cumulative epochs;
- training-spec and dataset fingerprints;
- trained-model fingerprint;
- runtime and runtime version.

Workspace persists the checkpoint as `application/vnd.sc.workspace.neural-checkpoint+json`, adds it as an execution-run output when an execution run is present, and places its artifact ID/SHA and lineage metadata into the polyglot execution receipt.

## Explicit exclusions

v3.23.0 does not accept `checkpointPath`, raw `stateDictBase64`, pickle/joblib, arbitrary Torch modules, TorchScript, client code, client packages, or client-selected runtime URLs. Cross-dataset fine-tuning and accelerators remain later milestones.
