# Neural-Symbolic Artifact Persistence Repair v3.39.0.1

## Defect
The v3.39.0 Workspace worker constructed neural-symbolic artifact requests with the obsolete `sc-workspace-artifact-store-request/1.0` shape (`role`, `label`, `contentJson`). Current `ArtifactStoreRequest` requires `sc-workspace-artifact-store/1.0`, `artifactId`, and `contentBase64`.

## Repair
The neural-symbolic persistence path now mirrors the established GNN, vision, sequence, and multimodal persistence contract: deterministic artifact ID, JSON canonicalization, Base64 content, revision-safe overwrite, media type mapping, and governed metadata.

## Epistemic boundary
Persisted symbolic artifacts retain `truthValueAssigned=false` and `isObservedEvidence=false`. Persistence does not convert model-derived inference into evidence or truth adjudication.
