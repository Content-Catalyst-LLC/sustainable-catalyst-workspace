# Workspace v3.26.0 — Embedding & Representation Runtime

Workspace v3.26.0 extends the governed PyTorch runtime with portable embedding and representation compute.

## Bounded operations
- `workspace.neural.embedding-generate`
- `workspace.neural.representation-summary`
- `workspace.neural.embedding-similarity`
- `workspace.neural.embedding-neighbors`

## Representation contract
Embedding generation accepts only declarative Workspace neural model specifications and bounded feature matrices. MLP representations may be selected from `input`, `hidden`, `penultimate`, or `output`; linear models support `input` and `output`. Optional L2 normalization is deterministic.

Each embedding artifact records model/checkpoint fingerprints, representation dataset fingerprint, row identifiers, layer selector, normalization, dimensions, vector norms, vectors, and its canonical artifact fingerprint. Similarity, neighborhood, and summary operations accept only a fingerprint-valid governed embedding artifact.

## Security and provenance
No arbitrary Python, client-supplied packages, raw serialized models, filesystem model paths, dynamic hooks, or accelerator execution are introduced. The hardened numeric UID/read-only container contract remains unchanged. Workspace separately persists embedding/representation artifacts and adds their fingerprints and source lineage to polyglot receipts.
