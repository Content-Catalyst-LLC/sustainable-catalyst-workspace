# Multimodal Neural Runtime — v3.38.0

## Runtime scope
v3.38 composes two already-governed Workspace modalities: in-memory image tensors from the v3.36 vision runtime and in-memory temporal tensors from the v3.37 sequence runtime. It does not fetch external images, sequences, models, or embeddings.

## Alignment
Every multimodal sample carries an explicit operator-declared alignment policy. Workspace records the image and sequence fingerprints independently; it does not infer that spatial or temporal alignment is correct.

## Encoders and fusion
The multimodal model specification embeds existing declarative vision and sequence model specifications. Fusion is limited to transparent `concat` and normalized `weighted-mean` modes. A bounded linear head maps the fused representation to outputs.

## Operations
1. `multimodal-sample-contract`
2. `multimodal-dataset-project`
3. `multimodal-model-summary`
4. `multimodal-embedding-fuse`
5. `multimodal-representation-extract`
6. `multimodal-forward`
7. `multimodal-infer`
8. `multimodal-similarity`

## Evidence semantics
Multimodal outputs are analytical/model-derived. Similarity is explicitly not semantic, causal, or evidentiary proof.

## Provenance
Artifacts preserve modality fingerprints, fusion/model fingerprints, canonical artifact fingerprints, job lineage, and Workspace receipt/output bindings.
