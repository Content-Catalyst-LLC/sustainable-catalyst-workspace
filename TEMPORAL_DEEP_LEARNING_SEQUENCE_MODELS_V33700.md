# Temporal Deep Learning & Sequence Models — v3.37.0

## Runtime scope
The v3.37 runtime accepts only bounded in-memory numeric sequence tensors using TF layout (time × features). It does not read files, URLs, databases, or external sequence stores directly.

## Governed adapters
- `tanh-rnn`: explicit input, recurrent, bias, and output matrices.
- `gru`: explicit update/reset/candidate gate matrices plus output projection.

Both adapters are declarative. No Python class path, import path, TorchScript, state-dict, pickle, or executable model payload is accepted.

## Operations
1. `sequence-tensor-contract`
2. `sequence-window-plan`
3. `sequence-dataset-project`
4. `sequence-model-summary`
5. `sequence-forward`
6. `sequence-infer`
7. `sequence-embedding-extract`
8. `sequence-forecast`

## Forecast semantics
`sequence-forecast` is a bounded point-forecast primitive. Recursive multi-step forecasts require `outputFeatures == inputFeatures`. v3.37 does not claim calibrated uncertainty; that remains a later temporal-model capability.

## Provenance
Sequence contracts, projections, executions, predictions, embeddings, and forecasts receive canonical fingerprints and are persisted through the Workspace artifact/result/receipt lineage when executed through the job fabric.
