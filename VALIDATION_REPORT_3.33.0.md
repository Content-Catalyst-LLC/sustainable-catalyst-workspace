# Validation report — Workspace v3.33.0

The release validator checks the following invariants after applying the v3.33.0 patch to a v3.32.0 repository/backend baseline:

1. Backend and neural runtime version markers are `3.33.0`.
2. All five GNN operations are registered in both the neural runtime and Workspace runtime registry.
3. The runtime operation count advances from 52 to 57.
4. All five governed GNN/graph schemas are present.
5. GCN and GraphSAGE-mean adapters are present with bounded graph limits.
6. GNN training is disabled in v3.33.0.
7. External graph reads, arbitrary graph code, runtime URLs, credentials, and serialized neural modules remain prohibited.
8. Graph projection explicitly records `inferredEdges=false` and `inferredFeatures=false`.
9. GNN prediction artifacts declare `isObservedEvidence=false` and reject target semantics.
10. Workspace artifact persistence and receipt lineage are wired for graph projection, GNN execution, and GNN prediction artifacts.
11. The v3.32 production-certification and remote-GPU operations are preserved.
12. No database migration is introduced.

Executable PyTorch tests run on systems where PyTorch/NumPy are available; the Contabo deployer always runs the GNN smoke suite inside the hardened neural-runtime container before switching production containers.
